#!/bin/bash

echo "TEST ENCRYPTION/DECRYPTION OF BASIC IMAGE IN RGB"

echo "ENCRYPT"
python3 hide_in_image.py samples/neko.jpg modified_samples/encrypted_neko.png --padding random --password=testpass --mode=encrypt --color-mode=RGB

echo "DECRYPT"

python3 hide_in_image.py modified_samples/decrypted_neko.jpg modified_samples/encrypted_neko.png --padding random --password=testpass --mode=decrypt --color-mode=RGB


echo "TEST ENCRYPTION/DECRYPTION OF BASIC IMAGE IN GRAYSCALE, PLUS WIDTH CHANGE"

echo "ENCRYPT"
python3 hide_in_image.py samples/neko.jpg modified_samples/encrypted_neko_bw.png --padding random --password=testpass --mode=encrypt --color-mode=L --width=1440

echo "DECRYPT"

python3 hide_in_image.py modified_samples/decrypted_bw_neko.jpg modified_samples/encrypted_neko_bw.png --padding random --password=testpass --mode=decrypt --color-mode=L
