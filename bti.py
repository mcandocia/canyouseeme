from __future__ import print_function
from PIL import Image
import numpy as np
import PIL
from PIL.ImageMode import getmode
import os

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
    parser.add_argument('--mode', default='L', choices=['L','RGB','RGBA',], help='color mode')
    parser.add_argument('--width', default=640, type=int, help='Width of image')
    parser.add_argument('--height', default=None, required=False, type=int, help='Height of image')

    parser.add_argument('--deconvert', action='store_true', help='Convert back to raw data')
    parser.add_argument(
        '--reverse-input-output',
        '--rio',
        action='store_true',
        help='Reverse meaning of first two arguments'
    )

    parser.add_argument('--padding', help='character or "random". must not be 0', default='1')

    args = parser.parse_args()
    options = vars(args)

    if len(options['input_filename']) == 1:
        options['input_filename'] = options['input_filename'][0]
        options['n_inputs'] = 1
    else:
        options['n_inputs'] = len(options['input_filename'])
        if not options['deconvert']:
            try:
                assert options['width'] is not None and options['height'] is not None
            except AssertionError:
                raise ValueError(
                    'Must specify both height and width when mode is not deconvert when more '
                    'than one image is specified.'
                )

    if options['reverse_input_output']:
        options['input_filename'], options['output_filename'] = (
            options['output_filename'],
            options['input_filename']
        )

    if options['padding'] != 'random':
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
    img = Image.open(options['input_filename'])

    if options['n_inputs'] == 1:
        raw_data = image_to_binary(img)
        with open(options['output_filename'], 'wb') as f:
            f.write(raw_data)
    else:
        decompose_image(img, *options['input_filename'])



def convert(options):
    if options['n_images'] == 1:
        with open(options['input_filename'], 'rb') as f:
            raw_data = f.read()

        image = binary_to_image(
            raw_data,
            dimensions=(options['width'], options['height']),
            mode=options['mode']
        )

        image.save(options['output_filename'])
    else:
        raw_arr = ['' for _ in range(options['n_images'])]
        for i, fn in enumerate(options['input_filenames']):
            with open(fn, 'rb') as f:
                raw_data = f.read()
                raw_arr[i] = raw_data
        composite_image(*raw_arr, options)

# grayscale
# mode hsv requires further transformation to be able to remap back to original
def binary_to_image(data, dimensions=(640,None), mode='L', return_numpy=False):
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
        raise ValueError('Unexpected value for "mode": %s' % repr(mode))
        
    if dimensions[1] is None:
        dimensions = (dimensions[0], size // (factor * dimensions[0]) + 1)
    elif size > dimensions[0] * dimensions[1] * factor:
        raise ValueError('Specified dimensions are too small')

    raw = np.frombuffer(data, dtype=np.uint8)
    difference = dimensions[0] * dimensions[1] * factor - len(raw)
    if difference >= 1:
        if options['padding'] != 'random':
            pad_val = int(options['padding'])
            raw = np.hstack([raw, np.uint8([0] + [pad_val]*(difference-1))])
        else:
            padding_string = np.frombuffer(nonzero_random_int(difference-1), dtype=np.uint8)
            raw = hp.hstack([raw, padding_string])
    else:
        raise ValueError('Padding not done correctly.')
        
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
    random_values = np.urandom(int(round(length * 1.1)+10))
    random_values = b''.join([x for x in random_values if x != '\x00'])[:length]
    if len(random_values) < length:
        random_values += nonzero_random_int(length-len(random_values))

    return random_values

def composite_image(r,g,b,a, options):
    raw_r = binary_to_image(r, dimensions=(options['width'], options['height']), return_numpy=True)
    raw_g = binary_to_image(g, dimensions=(options['width'], options['height']), return_numpy=True)
    raw_b = binary_to_image(b, dimensions=(options['width'], options['height']), return_numpy=True)
    if a is not None:
        rfaw_a = binary_to_image(
            a,
            dimensions=(options['width'], options['height']),
            return_numpy=True
        )
        arr = [raw_r, raw_g, raw_b, raw_a]
        mode = 'RGBA'
    else:
        arr = [raw_r, raw_g, raw_b]
        mode='RGB'

    shape = raw_r.shape

    full_composite = np.vstack(arr).reshape(
        (options['width'],options['height'], len(arr), )
    )

    return Image.fromarray(full_composite, mode=mode)

def decompose_image(rgba, *filenames):
    original_dimensions = rgba
    numpy_raw = np.asarray(rgba)

    n_images = len(filenames)
    try:
        assert n_images == numpy_raw.shape[2]
    except AssertionError:
        raise ValueError('Need to have filenames and number of layers identical')
    except IndexError:
        raise ValueError('Unexpected shape of image: %s' % ascii(numpy_raw.shape))

    for arr, fn in zip([numpy_raw[:,:,i] for i in range(n_images)], filenames):
        raw_data = image_to_binary(arr)
        with open(fn, 'wb') as f:
            f.write(raw_data)
    

    
if __name__=='__main__':
    options = get_options()
    main(options)
