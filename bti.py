from __future__ import print_function
from PIL import Image
import numpy as np
import PIL
from PIL.ImageMode import getmode
import os
from split_rgb import split_image

import argparse

# padding will always be 0x00 (0x01)*
# so that if the file ends with a 1-byte, remove all 1-bytes and then the 0-byte
# if file ends with 0 byte, just remove the 0-byte

MODE_L = getmode('L')
MODE_HSV = getmode('HSV')
MODE_HSVA = None#getmode('HSVA')
MODE_RGB = getmode('RGB')
MODE_RGBA = getmode('RGBA')

def get_options():
    parser = argparse.ArgumentParser(
        description='Conversion of data to and from image representation'
    )
    parser.add_argument(
        'input_filename',
        nargs='+',
        help='Input filename. If multiple specified, will decompose/compose image'
        ', but requires fixed dimensions'
    )
    parser.add_argument('output_filename', help='Output filename')
    parser.add_argument('--color-mode', default='L', choices=['L','RGB','RGBA',], help='color mode')
    parser.add_argument('--width', default=640, type=int, help='Width of image')
    parser.add_argument('--height', default=None, required=False, type=int, help='Height of image')

    parser.add_argument(
        '--deconvert',
        action='store_true',
        help='Convert back to raw data'
    )

    parser.add_argument(
        '--padding',
        help='character or "random"/"mask". must not be 0',
        default='1'
    )

    parser.add_argument(
        '--rgb-literal',
        action='store_true',
        help='If grayscale PNG images are loaded in the first 3 slots, '
        'use their values as RGB channels in an RGBA image'
    )

    parser.add_argument(
        '--hide-data-as-alpha',
        action='store_true',
        help='First of two files is used as the RGB layer'
        's of an RGBA image that hides the data of the '
        'second. The first argument must be a valid image'
    )

    parser.add_argument(
        '--hide-data-in-channels',
        nargs='*',
        default='',
        choices=['','red','blue','green',],
        help='Channel to hide data in if first image is RGB or RGBA'
    )

    args = parser.parse_args()
    options = vars(args)       
    if options['rgb_literal'] and len(options['input_filename']) != 4:
        raise ValueError(
            'Cannot use RGB literal unless 3 PNG files and '
            '1 other file supplied as inputs.'
        )

    if len(options['input_filename']) == 1:
        options['input_filename'] = options['input_filename']
        options['n_inputs'] = 1

    else:
        options['n_inputs'] = len(options['input_filename'])
        if not options['deconvert']:
            try:
                assert (options['width'] is not None and options['height'] is not None) or options['rgb_literal'] or options['hide_data_as_alpha'] or options['hide_data_in_channels']
            except AssertionError:
                raise ValueError(
                    'Must specify both height and width when mode is not deconvert when more '
                    'than one image is specified.'
                )


    if options['padding'] not in ['random','mask']:
        try:
            pad_val = int(options['padding'])
            assert pad_val > 0 and pad_val < 256
        except ValueError:
            raise ValueError('Need to specify "random" or an integer between 1 and 255 (inclusive)')
        except AssertionError:
            raise ValueError('Integers must be between 1 and 255 (inclusive) for --padding')

    return options

def main(options):
    if options['deconvert']:
        deconvert(options)
    else:
        convert(options)

def deconvert(options):
    img = Image.open(options['output_filename'])

    if options['n_inputs'] == 1:
        raw_data = image_to_binary(img)
        with open(options['input_filename'][0], 'wb') as f:
            f.write(raw_data)
            print(
                'Wrote %a' % options['input_filename'][0]
            )
    else:
        decompose_image(
            img,
            *options['input_filename'],
            options=options
        )



def convert(options):

    masks = None

    if options['n_inputs'] == 1:
        with open(options['input_filename'][0], 'rb') as f:
            raw_data = f.read()

        image = binary_to_image(
            raw_data,
            dimensions=(options['height'], options['width']),
            mode=options['color_mode'],
            padding=options['padding']
        )

        image.save(
            options['output_filename'],
            format='PNG'
        )
        print('Wrote %a' % options['output_filename'])
    else:
        raw_arr = ['' for _ in range(options['n_inputs'])]
        if options['hide_data_as_alpha'] or options['hide_data_in_channels']:
            new_input_filenames, dims = split_image(
                options['input_filename'][0],
                options['input_filename'][0],
            )
            # create masks
            if options['padding'] == 'mask':
                if options['hide_data_as_alpha']:
                    if len(new_input_filenames) == 4:
                        masks = {'alpha': new_input_filenames[3]}
                    else:
                        masks = None
                        print(
                            'mask image is RGB, so setting padding alpha '
                            'to 255'
                        )
                        options['padding'] = 255
                elif options['hide_data_in_channels']:
                    masks = {}
                    for i, channel in enumerate(
                            ['red','green','blue','alpha']
                    ):
                        if channel in options['hide_data_in_channels']:
                            masks.update({channel:new_input_filenames[i]})
                    
            
            options['new_input_filenames'] = (
                new_input_filenames
            )

            options['width'] = dims[1]
            options['height'] = dims[0]
            # redundancy
            if options['hide_data_as_alpha']:
                options['n_inputs'] = 4
            elif 'alpha' in options['hide_data_in_channels'] or len(new_input_filenames) == 4:
                options['n_inputs'] = 4
            else:
                options['n_inputs'] = 3
                
            options['rgb_literal'] = True

            if options['hide_data_as_alpha']:
                options['input_filename'] = (
                    new_input_filenames +
                    [options['input_filename'][1]]
                )
            else:
                # r g b a
                # red blue green alpha
                # determine map, order is not important for these lists
                data_positions = [
                    ['red','green','blue','alpha'].index(channel)
                    for channel in options['hide_data_in_channels']
                ]
                remaining_positions = [
                    i for i in range(options['n_inputs'])
                    if i not in data_positions
                ]
                #print(data_positions)
                #print(remaining_positions)
                # now use above to sort in order the input filenames
                filenames = ['' for _ in range(options['n_inputs'])]
                for i in range(options['n_inputs']):
                    if i in remaining_positions:
                        filenames[i] = new_input_filenames[i]
                    elif i in data_positions:
                        # offset by 1 since first position is the mask image
                        filenames[i] = options['input_filename'][data_positions.index(i)+1]
                    else:
                        print(i)
                        print(data_positions)
                        print(options['input_filename'])
                        print(filenames)
                        raise RuntimeError('Invalid index value encountered somehow')

                options['input_filename'] = filenames
                
                
            raw_arr = [
                '' for _ in range(options['n_inputs'])
            ]

        #print('INPUT FN')
        #print(options['input_filename'])
        for i, fn in enumerate(options['input_filename']):
            if options['hide_data_in_channels']:
                # first image uses remaining channels
                # then each image is assigned its corresponding channel
                if i in data_positions:
                    with open(fn, 'rb') as f:
                        raw_data = f.read()
                        raw_arr[i] = raw_data                    
                elif i in remaining_positions:
                    literal_img = Image.open(fn)
                    if literal_img.mode != 'L':
                        literal_img = literal_img.convert(
                            mode='L'
                        )
                    np_arr = np.asarray(literal_img)
                    dims = np_arr.shape[:2]
                    options['height'] = dims[0]
                    options['width'] = dims[1]
                    raw_arr[i] = bytes(
                        np_arr.flatten().tolist()
                    )
                else:
                    raise RuntimeError(
                        'Somehow have invalid index for hiding data in channels. '
                        'Need to bugfix this.'
                    )

                
            elif options.get('rgb_literal') and i < 3:
                literal_img = Image.open(fn)
                if literal_img.mode != 'L':
                    literal_img = literal_img.convert(
                        mode='L'
                    )
                np_arr = np.asarray(literal_img)
                dims = np_arr.shape[:2]
                options['height'] = dims[0]
                options['width'] = dims[1]
                raw_arr[i] = bytes(
                    np_arr.flatten().tolist()
                )
                
            else:
                with open(fn, 'rb') as f:
                    raw_data = f.read()
                    raw_arr[i] = raw_data
        # rearrange channels if 'hide_data_in_channel'

        c_img = composite_image(*raw_arr, options=options, masks=masks)
        c_img.save(
            options['output_filename'],
            format='PNG'
        )
        print('Wrote %a' % options['output_filename'])

    if 'new_input_filenames' in options:
        for fn in options['new_input_filenames']:
            if os.path.isfile(fn):
                print('removing %a' % fn)
                os.remove(fn)

# grayscale
# mode hsv requires further transformation to be able to remap back to original
def binary_to_image(data, dimensions=(640,None), mode='L', return_numpy=False, is_literal=False, padding='1', mask=None):
    if mode is None:
        raise ValueError('Mode cannot be None!')
    
    size = len(data)
    if mode == 'L':
        factor = 1
    elif mode == 'RGB' or mode == 'HSV':
        factor = 3
    elif mode == 'RGBA' or mode == 'HSVA':
        factor = 4
    else:
        raise ValueError(
            'Unexpected value for "mode": %s' % repr(mode)
        )
        
    if dimensions[1] is None:
        dimensions = (
            dimensions[0],
            size // (factor * dimensions[0]) + 1
        )
    elif dimensions[0] is None:
        dimensions = (
            size // (factor * dimensions[1]) + 1,
            dimensions[1]
        )
    elif size > dimensions[0] * dimensions[1] * factor:
        raise ValueError('Specified dimensions are too small')

    raw = np.frombuffer(data, dtype=np.uint8)
    difference = (
        dimensions[0] * dimensions[1] * factor -
        len(raw)
    )
    if difference >= 1:
        if padding not in ['random','mask']:
            pad_val = int(padding)
            raw = np.hstack(
                [
                    raw,
                    np.uint8(
                        [0] + [pad_val]*(difference-1)
                    )
                ]
            )
        elif padding == 'mask':
            if mask is None:
                raise ValueError(
                    'mask is None. This should not happen in this mode'
                )
            # load mask
            mask_img = Image.open(mask).convert(mode='L')
            mask_arr = np.maximum(
                np.uint8(1),
                np.uint8(np.asarray(mask_img))
            ).flatten()[1-difference:]

            padding_string = np.hstack([np.uint8([0]), mask_arr])
            #print(padding_string)[:10]
            raw = np.hstack([raw, padding_string])
        else:
            padding_string = np.frombuffer(
                b'\x00' + nonzero_random_int(difference-1),
                dtype=np.uint8
            )
            raw = np.hstack([raw, padding_string])
    elif not is_literal:
        print('Difference: %s' % difference)
        raise ValueError('Padding not done correctly.')
    else:
        pass
        
    if factor != 1:
        dimensions = (dimensions[0], dimensions[1], factor)
        
    raw = raw.reshape((dimensions))
    if return_numpy:
        return raw
    img = Image.fromarray(raw, mode=mode)

    return img

def image_to_binary(img):
    # get numpy array from image
    raw = np.asarray(img)
    raw.flatten()
    byte_string = b''.join([bytes(x) for x in raw])
    # remove padding
    if byte_string[-1] == b'\x00':
        return byte_string[:-1]
    else:
        return byte_string[:byte_string.rfind(b'\x00')]

# return nonzero random bytes
# generates a few extras in case it doesn't generate enough
# also recursive calls as a failsafe, though it should never occur
def nonzero_random_int(length):
    random_values = os.urandom(int(round(length * 1.1)+10))
    random_values = random_values.replace(
        b'\x00',
        b''
    )[:length]
    if len(random_values) < length:
        random_values += nonzero_random_int(length-len(random_values))

    return random_values

def composite_image(r,g,b,a=None, options=None, masks=None):
    #print(masks)
    if masks is None:
        masks = {}
        
    if options is None:
        raise ValueError('Must supply value to "options"')
    is_literal = (
        options['rgb_literal'] or
        options['hide_data_as_alpha'] or
        options['hide_data_in_channels']
    )

    hidden_channels = options['hide_data_in_channels']
    
    base_literal = (options['rgb_literal'] or options['hide_data_as_alpha'])

    literal_red = base_literal and 'red' not in hidden_channels
    literal_green = base_literal and 'green' not in hidden_channels
    literal_blue = base_literal and 'blue' not in hidden_channels
    literal_alpha = base_literal and 'alpha' not in hidden_channels

    #print('r')
    raw_r = binary_to_image(r, dimensions=(options['width'], options['height']), return_numpy=True, is_literal=literal_red, padding=options['padding'], mask=masks.get('red'))
    #print('g')
    raw_g = binary_to_image(g, dimensions=(options['width'], options['height']), return_numpy=True, is_literal=literal_green, padding=options['padding'], mask=masks.get('green'))
    #print('b')
    raw_b = binary_to_image(b, dimensions=(options['width'], options['height']), return_numpy=True, is_literal=literal_blue, padding=options['padding'], mask=masks.get('blue'))
    if a is not None:
        #print('a')
        raw_a = binary_to_image(
            a,
            dimensions=(options['width'], options['height']),
            return_numpy=True,
            padding=options['padding'],
            is_literal = literal_alpha,
            mask=masks.get('alpha')
        )
        arr = [raw_r, raw_g, raw_b, raw_a]
        mode = 'RGBA'
    else:
        arr = [raw_r, raw_g, raw_b]
        mode='RGB'

    shape = raw_r.shape

    #print(raw_b[:10])

    full_composite = np.dstack(arr).reshape(
        (options['height'],options['width'], len(arr), )
    )

    return Image.fromarray(full_composite, mode=mode)

def decompose_image(rgba, *filenames, options={}):
    original_dimensions = rgba
    numpy_raw = np.asarray(rgba)

    n_images = len(filenames)
    try:
        assert (
            n_images == numpy_raw.shape[2] or
            options.get('rgb_literal') or
            options.get('hide_data_as_alpha') or
            options.get('hide_data_in_channels')
        )
    except AssertionError:
        raise ValueError('Need to have filenames and number of layers identical')
    except IndexError:
        raise ValueError(
            'Unexpected shape of image: %s' % ascii(
                numpy_raw.shape
            )
        )

    n_layers = numpy_raw.shape[2]
    literal_mode = (
        options.get('rgb_literal') or
        options.get('hide_data_as_alpha') or
        options.get('hide_data_in_channels')
    )
    if options['hide_data_in_channels']:
        # rearrange filenames
        # this is the numpy slice (3rd index) that each filename will take
        filename_positions = [
            ['red','green','blue','alpha'].index(channel)
            for channel in options['hide_data_in_channels']
        ]
        #print(options['hide_data_in_channels'])

    if not literal_mode:
        for j, arr, fn in zip(
                range(4),
                [
                    numpy_raw[:,:,i]
                    for i in range(n_layers)
                ],
                filenames
        ):
            if j < 3 and (
                    False # not sure what I was putting here...
            ):
                # these modes don't need to rewrite output
                continue
            raw_data = image_to_binary(arr)
            with open(fn, 'wb') as f:
                f.write(raw_data)
                print('Wrote %a' % fn)
    elif options['hide_data_in_channels']:
        for i, pos in enumerate(filename_positions):
            #print((i, pos))
            fn = options['input_filename'][i+1]
            #print(fn)
            arr = numpy_raw[:,:,pos]
            raw_data = image_to_binary(arr)
            with open(fn, 'wb') as f:
                f.write(raw_data)
                print('Wrote %a' % fn)
    else:
        fn = options['input_filename'][-1]
        arr = numpy_raw[:,:,n_layers-1]
        raw_data = image_to_binary(arr)
        with open(fn, 'wb') as f:
            f.write(raw_data)
            print('Wrote %a' % fn)
            
    

    
if __name__=='__main__':
    options = get_options()
    main(options)
