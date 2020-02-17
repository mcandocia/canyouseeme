#!/bin/bash

echo "TESTING CSV OUTPUT"

echo "ENCODE"
python3 bti.py samples/a_run.csv modified_samples/a_run_image.png --padding=random --width=1500

echo "DECODE"
python3 bti.py modified_samples/a_run_returned.csv modified_samples/a_run_image.png --padding=random --width=1500 --deconvert

