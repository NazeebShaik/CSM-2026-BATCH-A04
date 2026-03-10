

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# Generate ECC private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Serialize private key to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key to PEM format
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Encrypt the file data
def encrypt_file(public_key, file_data):
    # Generate a shared key using ECDH (Elliptic Curve Diffie-Hellman)
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive a symmetric key using PBKDF2HMAC
    salt = os.urandom(16)  # Generate a random salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(shared_key)

    # Pad the file data to match AES block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    # Generate random Initialization Vector (IV) for CBC mode
    iv = os.urandom(16)

    # Encrypt the data using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Concatenate salt, IV, and encrypted data for decryption
    return salt + iv + encrypted_data



from django.http import HttpResponse
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def decrypt_file_data(private_key, encrypted_data, public_key):
    # Extract the salt (16 bytes), IV (16 bytes), and encrypted message
    salt = encrypted_data[:16]  # First 16 bytes are the salt
    iv = encrypted_data[16:32]  # Next 16 bytes are the IV
    encrypted_message = encrypted_data[32:]  # The rest is the encrypted message

    # Derive shared key using the private key and corresponding public key (ECDH)
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive symmetric AES key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # Use the same salt as during encryption
        iterations=100000,
    )
    key = kdf.derive(shared_key)

    # Decrypt the file data using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_message) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data