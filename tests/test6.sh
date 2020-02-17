#!/bin/bash

echo "TEST PLACING 3 OBJECTS AS RGB CHANNELS AND UNPACKING"

echo "ENCODE"

python3 bti.py samples/trash_pandas.jpg samples/message.txt samples/some_trees.jpg modified_samples/composite_rgb_data.png --padding=random --height=1440 --width=1440

echo "DECODE"

python3 bti.py modified_samples/trash_pandas_from_rgb.jpg modified_samples/message_from_rgb.txt modified_samples/some_trees_from_rgb.jpg modified_samples/composite_rgb_data.png --padding=random --deconvert
