#!/bin/bash

echo "HIDE DATA IN GREEN CHANNEL OF IMAGE"

echo "ENCRYPT"
python3 hide_in_image.py samples/shrine.jpg samples/sleepy_kitty.jpg modified_samples/kitty_hidden_elsewhere_in_shrine2.png --hide-data-in-channels green --padding=mask --mode=encrypt --password=testpass

echo "DECRYPT"
python3 hide_in_image.py samples/shrine.jpg modified_samples/unred_sleepy_kitty_from_shrine2.png modified_samples/kitty_hidden_elsewhere_in_shrine2.png --hide-data-in-channels green --padding=mask --mode=decrypt --password=testpass
