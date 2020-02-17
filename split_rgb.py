from PIL import Image
import argparse
import os
import numpy as np

def split_image(input_filename, output_filenames):
    if isinstance(output_filenames, (str, bytes)):
        output_filenames = [
            '%s.%s.png' % (output_filenames, c)
            for c in 'rgb'
        ]
        

    img = Image.open(input_filename)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    np_array = np.asarray(img)
    dims = np_array.shape[:2]

    rgb = [np_array[:,:,i] for i in range(3)]

    for fn, np_channel in zip(output_filenames, rgb):
        channel_img = Image.fromarray(np_channel, mode='L')
        channel_img.save(fn, format='PNG')

    return output_filenames, dims
    
    
    

def get_options():
    pass

def main(options):
    pass

if __name__=='__main__':
    options = get_options()
    IMPORT_MODE=0
    main(options)
else:
    IMPORT_MODE=1
