#!/bin/bash

echo "ENCRYPTION/DECRYPTION OF REGULAR FILE WITH EXPENSIVE HASHING"

echo "ENCRYPTION"
python3 enc.py encrypt samples/message.txt --output-filename=modified_samples/encrypted_message --heavy --password=testpass

echo "DECRYPTION"
python3 enc.py decrypt modified_samples/encrypted_message --output-filename=modified_samples/decoded_message.txt --heavy --password=testpass
