from argon2 import argon2_hash
from uuid import uuid4
import os
import argparse
from getpass import getpass
try:
    from Cryptodome.Cipher import AES
except ImportError:
    from Crypto.Cipher import AES

def get_options():
    parser = argparse.ArgumentParser(
        description='Encrypt and decrypt files securely with hashed passwords'
    )

    parser.add_argument('mode', choices=['decrypt','encrypt'], help='mode of operations (encrypt/decrypt)')
    parser.add_argument('filename', help='Target file to encrypt/decrypt')
    parser.add_argument('--output-filename', help='Output filename if you do not want to overwrite input file', required=False, default='')
    parser.add_argument('--rounds', default=16, type=int, help='Number of rounds for hashing')
    parser.add_argument('--memory', default=8, type=int, help='Memory used in KiB')
    parser.add_argument('--buflen', default=32, type=int, help='Length of buffer')
    parser.add_argument('-p', default=1, type=int, help='Degree of parallelism')
    parser.add_argument('--salt', default='caMERA5@%'*20, help='salt to use for password hashing')
    parser.add_argument('--heavy', action='store_true', help='Makes the algorithm more computationally expensive by choosing a fixed set of parameters.')
    parser.add_argument('--password', required=False, default='',help='Supplied password (not recommended)')

    args = parser.parse_args()
    options = vars(args)
    if options['heavy']:
        options['rounds'] = 128
        options['memory'] = 2 ** 14
    return options

def hash_password(password, **kwargs):
    return argon2_hash(password, **kwargs)

pad_str = bytes(range(17))
def pad(x):
    modulo = len(x) % 16
    return x + pad_str[:16-modulo]

def unpad(x):
    # remove all text after last null byte
    return x[:x.rfind(b'\x00')]

def encrypt(data, pwhash):
    #print(type(pwhash))
    cipher = AES.new(pwhash, AES.MODE_EAX)
    #print(data)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return (cipher.nonce, tag, ciphertext)

def encrypt_file(filename, pwhash, output_filename=None):
    if not output_filename:
        output_filename = filename
        
    with open(filename, 'rb') as f:
        text = f.read()
    nonce, tag, ciphertext = encrypt(pad(text), pwhash)

    with open(output_filename, 'wb') as f:
        f.write(nonce)
        f.write(tag)
        f.write(ciphertext)

    print('Encrypted')

def decrypt_file(filename, pwhash, output_filename=None):
    if output_filename is None:
        output_filename = filename
    with open(filename, 'rb') as f:
        nonce, tag, ciphertext = [
            f.read(x) for x in (16,16,-1)
        ]
    cipher = AES.new(pwhash, AES.MODE_EAX, nonce)
    data = unpad(
        cipher.decrypt_and_verify(ciphertext, tag)
    )
    with open(output_filename, 'wb') as f:
        f.write(data)
    print('Decrypted')


def main(options):
    if not options['password']:
        password = getpass('password: ')
    else:
        password = options['password']
    pwhash = hash_password(password, t=options['rounds'], p=options['p'], m=options['memory'], buflen=options['buflen'], salt=options['salt'])
    if options['mode'] == 'encrypt':
        encrypt_file(
            options['filename'],
            pwhash,
            options['output_filename']
        )
    else:
        decrypt_file(
            options['filename'],
            pwhash,
            options['output_filename']
        )
    


if __name__=='__main__':
    options = get_options()
    main(options)
