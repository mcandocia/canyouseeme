#!/bin/bash

echo "TEST ENCRYPTION/DECRYPTION OF IMAGE WITH RGB MASK; padding=255"

echo "ENCRYPT"
python3 hide_in_image.py samples/shrine.jpg samples/kitty_in_a_box.jpg modified_samples/hidden_secret_kitty_255.png --padding random --password=testpass --mode=encrypt --hide-data-as-alpha --padding=255

echo "DECRYPT"
python3 hide_in_image.py samples/shrine.jpg modified_samples/revealed_kitty_in_a_box.jpg modified_samples/hidden_secret_kitty_255.png --padding random --password=testpass --mode=decrypt --hide-data-as-alpha
