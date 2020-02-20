#!/bin/bash

echo "TEST GPG behavior"
echo "arg 1 = sender, arg 2 = receiver; be prepared to enter password for sender/receiver"

SENDER=$1
RECIPIENT=$2

GPG_BINARY=/usr/local/opt/gpg/bin/gpg 

echo "ENCRYPT"
python3 enc.py encrypt samples/rainbows.png --output-filename=modified_samples/rainbows.png.gpg --use-gpg --gpg-sender=$SENDER --gpg-recipients $RECIPIENT --gpg-bin=$GPG_BINARY

echo "DECRYPT"
python3 enc.py decrypt modified_samples/rainbows.png.gpg --output-filename=modified_samples/rainbows_ungpg.png --use-gpg --gpg-bin=$GPG_BINARY
