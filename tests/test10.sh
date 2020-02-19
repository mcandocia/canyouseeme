#!/bin/bash

echo "HIDE 2 DATA FILES IN GREEN AND BLUE CHANNEL OF RGBA IMAGE"

echo "ENCRYPT"
python3 hide_in_image.py samples/rainbows.png samples/sleepy_kitty.jpg samples/kitty_in_a_box.jpg  modified_samples/kitties_hidden_in_rainbows.png --hide-data-in-channels green blue --padding=random --mode=encrypt --password=testpass

echo "DECRYPT"
python3 hide_in_image.py samples/rainbows.png modified_samples/sleepy_kitty_from_rainbow.png modified_samples/kitty_in_box_from_rainbow.png modified_samples/kitties_hidden_in_rainbows.png --hide-data-in-channels green blue --padding=random --mode=decrypt --password=testpass
