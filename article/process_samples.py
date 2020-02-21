import os
import shutil
import re
import shlex

sample_folders = [
    os.path.join('article_samples', path)
    for path in os.listdir('article_samples')
]

os.makedirs('article_samples_processed', exist_ok=True)

for folder in sample_folders:
    filenames = os.listdir(folder)
    new_folder = os.path.join('article_samples_processed',folder)
    os.makedirs(new_folder, exist_ok=True)
    for filename in filenames:
        output_filename = filename + '.bw.png'
        command = (
            'python3 ../bti.py {folder}/{filename} '
            '{new_folder}/{output_filename} --width=720'.format(
                filename=shlex.quote(filename),
                output_filename=output_filename.replace(' ','_'),
                folder=folder,
                new_folder=new_folder
                
            )
        )
        print(command)
        status = os.system(command)
        if status != 0:
            raise RuntimeError('Status code %d returned!' % status)

print('Done!')

