# canyoufindme

* in progress *

The scripts here will allow you to do a few things:

1. Convert files to PNG images, and convert them back.

2. Encrypt files using Argon2, and decrypt them.

3. Combine the two of the above to hide data in images.

See the scripts under `tests/` for some examples. Data is provided under `samples` to test the code, and output/intermediate files will appear in `modified_samples`

You can use the `--help` documentation for each script to see more details about the options.

# bti.py

This script converts data into PNG format (grayscale, RGB, or RGBA) and can convert it back with the simple addition of the `--deconvert` argument.

You can also hide data as the alpha channel when providing an RGB image as first input and the data as second input when specifying `--hide-data-as-alpha`.

See tests 4-8 in the `tests/` directory for examples using this script.

# enc.py

This script can encrypt/decrypt data using the [Argon2 algorithm](https://en.wikipedia.org/wiki/Argon2) for hashing a password. If you set the parameters to make the hashing expensive enough (or just use `--heavy`, which takes a few seconds on a regular computer to compute a single hash), it is quite difficult to brute-force this algorithm. 

The password can either be user-supplied or argument-supplied.

The first positional argument is "encrypt" or "decrypt", which specifies the mode it uses.

See `tests/test3.sh` for an example of how to use this script, specifically.

Note that you can only encrypt/decrypt files when you use the same exact hashing parameters for both (memory, buflen, p, salt, rounds).

# hide_in_image.py

This script combines `bti.py` and `enc.py` to both hash data and then place that raw data in an image, was well as perform the reverse operations.

See tests 1-2 in the `tests/` directory for examples of how this is used.