#!/bin/bash

echo "COMBINE 4 FILES AS 1 IMAGE USING RGBA MODE AND DECONSTRUCT WITH 255 PADDING (max value)"

echo "ENCODE"
python3 bti.py samples/a_run.csv samples/neko.jpg samples/kitty_on_couch.jpg samples/dragon.png modified_samples/composite_rgba.png --padding=255 --width=1980 --height=1440


echo "DECODE"

python3 bti.py modified_samples/a_run_rgba_decoded.csv modified_samples/neko_rgba_decoded.jpg modified_samples/kitty_on_couch_rgba_decoded.jpg modified_samples/dragon_rgba_decoded.png modified_samples/composite_rgba.png --padding=255 --width=1440 --height=1440 --deconvert
