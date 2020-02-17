#!/bin/bash

echo "ENCODE AND DECODE DATA TO IMAGE"

echo "ENCODE"

python3 bti.py samples/kitty_in_a_box.jpg modified_samples/obscured_kitty_in_a_box.png --color-mode=RGB --width=360 --height=360 --padding=random

echo "DECODE"
python3 bti.py modified_samples/rescued_kitty_in_a_box.jpg modified_samples/obscured_kitty_in_a_box.png --color-mode=RGB --width=360 --height=360 --padding=random --deconvert
