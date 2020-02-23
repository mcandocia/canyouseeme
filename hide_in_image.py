import os
import argparse
from enc import main as encrypt_main
from bti import main as bti_main
from copy import deepcopy

def get_options():
    parser = argparse.ArgumentParser(
        description='Encrypt files and hide them in images',
    )

    enc_parser = parser.add_argument_group('encryption params')
    bti_parser = parser.add_argument_group('image params')

    # image args
    bti_parser.add_argument(
        'input_filename',
        nargs='+',
        help='Input filename. If multiple specified, will decompose/compose image'
        ', but requires fixed dimensions'
    )
    
    bti_parser.add_argument('output_filename', help='Output filename')
    bti_parser.add_argument('--color-mode', default='L', choices=['L','RGB','RGBA',], help='color mode')
    bti_parser.add_argument('--width', default=640, type=int, help='Width of image')
    bti_parser.add_argument('--height', default=None, required=False, type=int, help='Height of image')

    bti_parser.add_argument('--deconvert', action='store_true', help='Convert back to raw data')
    bti_parser.add_argument(
        '--reverse-input-output',
        '--rio',
        action='store_true',
        help='Reverse meaning of first two arguments'
    )

    bti_parser.add_argument(
        '--padding',
        help='character or "random"/"mask". must not be 0.',
        default='1'
    )

    # encryption/decryption args
    enc_parser.add_argument(
        '--mode',
        choices=['decrypt','encrypt'],
        help='mode of operations (encrypt/decrypt)',
        required=True
    )
    #enc_parser.add_argument('filename', help='Target file to encrypt/decrypt')
    enc_parser.add_argument('--rounds', default=16, type=int, help='Number of rounds for hashing')
    enc_parser.add_argument('--memory', default=8, type=int, help='Memory used in KiB')
    enc_parser.add_argument('--buflen', default=32, type=int, help='Length of buffer')
    enc_parser.add_argument('-p', default=1, type=int, help='Degree of parallelism')
    enc_parser.add_argument('--salt', default='caMERA5@%'*20, help='salt to use for password hashing')
    enc_parser.add_argument('--heavy', action='store_true', help='Makes the algorithm more computationally expensive')
    enc_parser.add_argument('--password', required=False, default='',help='Supplied password (not recommended)')    

    # other options
    bti_parser.add_argument(
        '--hide-data-as-alpha',
        action='store_true',
        help="Store the last argument of the input filen"
        "ames as data in alpha channel, and use first "
        "image as RGB layers"
    )

    parser.add_argument(
        '--hide-data-in-channels',
        nargs='*',
        default='',
        choices=['','red','blue','green',],
        help='Channel to hide data in if first image is RGB or RGBA'
    )    

    parser.add_argument(
        '--rgb-literal',
        action='store_true',
        help='If grayscale PNG images are loaded in the first 3 slots, '
        'use their values as RGB channels in an RGBA image'
    )

    args = parser.parse_args()
    options = vars(args)
    options['is_literal'] = (
        options['rgb_literal'] or
        options['hide_data_as_alpha'] or
        options['hide_data_in_channels']
    )
    
    if options['mode'] == 'decrypt':
        options['deconvert'] = True
    if options['deconvert']:
        options['mode'] = 'decrypt'

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

    return options

def list_wrap(x):
    if not isinstance(x, list):
        return [x]
    return x

def main(options):
    # call encryption/decryption script

    options['encrypted_input_filenames'] = [
        "%s.ag2.tmp" % fn
        for fn in list_wrap(options['input_filename'])
    ]
    
    if options['mode'] == 'decrypt':
        decryption(options)
    else:
        encryption(options)

    print('cleanup')
    for fn in options['encrypted_input_filenames']:
        if os.path.isfile(fn):
            print('removing %a' % fn)
            os.remove(fn)
        

def encryption(options):
    input_filenames = list_wrap(options['input_filename'])
    encrypted_input_filenames = options[
        'encrypted_input_filenames'
    ]

    for i, input_filename, encrypted_input_filename in zip(
            range(len(input_filenames)),
            input_filenames,
            encrypted_input_filenames
    ):

        if (
                i < len(input_filenames) - 1 and
                options['is_literal']
        ):
            continue

        options_copy = deepcopy(options)
        options_copy['filename'] = input_filename
        options_copy['output_filename'] = (
            encrypted_input_filename
        )
        
        encrypt_main(options_copy)

    # update input filenames
    options_copy = deepcopy(options)
    if options['is_literal']:
        
        options_copy['input_filename'] = list_wrap(
            options[
            'input_filename'
        ])[:-1] + [
            encrypted_input_filenames[-1]
        ]
    else:
        options_copy['input_filename'] = list_wrap(
            options_copy['input_filename']
        )
        for i, encrypted_filename in enumerate(
                encrypted_input_filenames
        ):
            options_copy['input_filename'][i] = encrypted_filename

    # now encode image
    if len(options_copy['input_filename']) == 1:
        options_copy['input_filename'] = options_copy[
            'input_filename'
        ]
    bti_main(options_copy)

def decryption(options):
    input_filenames = options['input_filename']
    encrypted_input_filenames = options[
        'encrypted_input_filenames'
    ]

    # deconvert images
    options_copy = deepcopy(options)
    options_copy['input_filename'] = (
        encrypted_input_filenames
    )
    #print(options_copy)
    
    bti_main(options_copy)
    
    # decrypt

    for i, fn in enumerate(encrypted_input_filenames):
        options_copy = deepcopy(options)
        if (
                options['is_literal'] and
                i < len(encrypted_input_filenames)-1
        ):
            continue

        options_copy['output_filename'] = list_wrap(
            options[
            'input_filename'
        ])[i]
        options_copy['filename'] = fn
        #print(options_copy)
        encrypt_main(options_copy)





if __name__=='__main__':
    options = get_options()
    main(options)
