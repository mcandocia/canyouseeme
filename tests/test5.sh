#!/bin/bash

echo "TEST HIDING DATA IN IMAGE AS RGBA"

echo "ENCODE"

python3 bti.py samples/shrine.jpg samples/sleepy_kitty.jpg modified_samples/hidden_kitty_in_shrine.png --hide-data-as-alpha --padding=random

echo "DECODE"

python3 bti.py samples/shrine.jpg modified_samples/sleepy_kitty_from_shrine.jpg modified_samples/hidden_kitty_in_shrine.png --hide-data-as-alpha --deconvert
