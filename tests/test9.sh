#!/bin/bash

echo "HIDE DATA IN GREEN CHANNEL OF IMAGE"

echo "ENCRYPT"
python3 hide_in_image.py samples/shrine.jpg samples/sleepy_kitty.jpg modified_samples/kitty_hidden_elsewhere_in_shrine.png --hide-data-in-channels green --padding=random --mode=encrypt --password=testpass

echo "DECRYPT"
python3 hide_in_image.py samples/shrine.jpg modified_samples/unred_sleepy_kitty_from_shrine.png modified_samples/kitty_hidden_elsewhere_in_shrine.png --hide-data-in-channels green --padding=random --mode=decrypt --password=testpass
