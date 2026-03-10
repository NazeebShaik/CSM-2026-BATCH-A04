
from django.shortcuts import render
from django.http import HttpResponse
# from .models import EvidenceDetails
from django.core.files.base import ContentFile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import hashlib


# Function to generate an optimal key using Enhanced Equilibrium Optimizer (EEO) approach
def generate_optimal_key(password: str, salt: bytes) -> bytes:
    # This is a placeholder for the EEO model key generation
    # In practice, this would be replaced with the actual EEO algorithm implementation
    return generate_key(password, salt)


# Check if a file hash already exists in the database for the given user
# def is_duplicate(file_hash, useremail):
#     return EvidenceDetails.objects.filter(file_hash=file_hash, owneremail=useremail).exists()



# Generate a secure AES-256 encryption key
def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())






import tenseal as ts


# Function to generate MHE keys using TenSEAL
def generate_mhe_keys():
    context = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=8192, plain_modulus=1032193)
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    public_key = context.serialize(save_secret_key=False)  # Save public context (without secret key)
    private_key = context.serialize()  # Save full context (with secret key)
    return public_key, private_key

# Encrypt the data using MHE
def encrypt_data_mhe(data, public_key):
    context = ts.context_from(public_key)
    # Convert data to a list of integers or bytes if necessary
    data_list = list(data)
    encrypted_data = ts.bfv_vector(context, data_list)
    return encrypted_data.serialize()

# Decrypt the data using MHE
def decrypt_data_mhe(encrypted_data, private_key):
    context = ts.context_from(private_key)
    encrypted_data = ts.bfv_vector_from(context, encrypted_data)
    decrypted_data = encrypted_data.decrypt()
    return bytes(decrypted_data)  # Convert back to bytes if necessary