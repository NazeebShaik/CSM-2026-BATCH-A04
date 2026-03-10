import numpy as np
import hashlib
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from time import time

# --------------- Enhanced Equilibrium Optimizer (EEO) ---------------- #
def fitness(solution):
    """
    Fitness function to evaluate randomness of a key.
    """
    target = np.random.randint(0, 255, size=solution.shape)
    return np.sum(np.abs(solution - target))  # Distance from target

def eeo_optimize(population_size, dimensions, iterations):
    """
    Generate an optimized secret key using EEO.
    """
    population = np.random.randint(0, 256, size=(population_size, dimensions))
    best_solution = population[0]
    best_fitness = fitness(best_solution)

    for _ in range(iterations):
        for candidate in population:
            candidate_fitness = fitness(candidate)
            if candidate_fitness < best_fitness:
                best_fitness = candidate_fitness
                best_solution = candidate

    return best_solution.tobytes()  # Convert best solution to bytes

def generate_secret_key():
    """
    Generate a hashed secret key using EEO.
    """
    secret_key = eeo_optimize(population_size=50, dimensions=32, iterations=100)
    return hashlib.sha256(secret_key).hexdigest()  # Hashing for consistency

# ---------------- Secure Block Verification Mechanism (SBVM) ---------------- #
def create_block_data(username, email, phone, address, password_hash):
    """
    Create block data with user details.
    """
    return {
        "username": username,
        "email": email,
        "phone": phone,
        "address": address,
        "password_hash": password_hash,
        "timestamp": time()
    }

def calculate_block_hash(block_data):
    """
    Generate SHA-256 hash for the block.
    """
    block_str = json.dumps(block_data, sort_keys=True)
    return hashlib.sha256(block_str.encode('utf-8')).hexdigest()

def sign_block(block_hash, secret_key):
    """
    Create a digital signature using SHA-256.
    """
    return hashlib.sha256((block_hash + secret_key).encode('utf-8')).hexdigest()

def verify_block(block_hash, signature, secret_key):
    """
    Verify block integrity.

    """

    print(block_hash)
    expected_signature = hashlib.sha256((block_hash + secret_key).encode('utf-8')).hexdigest()
    print(expected_signature)
    print(signature)
    # print('000000000000000000000000000000000000000000')
    return expected_signature == signature

# ---------------- AES Encryption & Decryption ---------------- #
AES_KEY_SIZE = 32  # AES-256 requires 32-byte key
AES_BLOCK_SIZE = 16  # Block size for AES

def generate_aes_key():
    """
    Generate a random 32-byte AES key.
    """
    return base64.b64encode(np.random.bytes(AES_KEY_SIZE)).decode()

def encrypt_secret_key(secret_key, aes_key):
    """
    Encrypt the secret key using AES.
    """
    aes_key_bytes = base64.b64decode(aes_key)  # Decode the stored AES key
    cipher = AES.new(aes_key_bytes, AES.MODE_CBC)
    iv = cipher.iv  # Initialization Vector
    encrypted_secret_key = cipher.encrypt(pad(secret_key.encode(), AES_BLOCK_SIZE))
    return base64.b64encode(iv + encrypted_secret_key).decode()  # Encode IV + Ciphertext

def decrypt_secret_key(encrypted_secret_key, aes_key):
    """
    Decrypt the secret key using AES.
    """
    aes_key_bytes = base64.b64decode(aes_key)  # Decode AES key
    encrypted_data = base64.b64decode(encrypted_secret_key)
    iv = encrypted_data[:AES_BLOCK_SIZE]  # Extract IV
    cipher = AES.new(aes_key_bytes, AES.MODE_CBC, iv)
    decrypted_secret_key = unpad(cipher.decrypt(encrypted_data[AES_BLOCK_SIZE:]), AES_BLOCK_SIZE)
    return decrypted_secret_key.decode()
