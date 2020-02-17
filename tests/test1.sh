#!/bin/bash

echo "TEST ENCRYPTION/DECRYPTION OF IMAGE WITH RGB MASK"

echo "ENCRYPT"
python3 hide_in_image.py samples/shrine.jpg samples/kitty_in_a_box.jpg modified_samples/hidden_secret_kitty.png --padding random --password=testpass --mode=encrypt --hide-data-as-alpha

echo "DECRYPT"
python3 hide_in_image.py samples/shrine.jpg modified_samples/revealed_kitty_in_a_box.jpg modified_samples/hidden_secret_kitty.png --padding random --password=testpass --mode=decrypt --hide-data-as-alpha
