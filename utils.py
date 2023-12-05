import os
import gzip
import secrets
import re
import hashlib
from urllib import request, error
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as symmetric_padding

LOGO = """
░█▀▀░█▀█░█▀▀░█▀▀░█▀█░█░█░█░█░█▀█░█░█░█░░░▀█▀
░▀▀█░█▀█░█▀▀░█▀▀░█▀▀░░█░░▀▄▀░█▀█░█░█░█░░░░█░
░▀▀▀░▀░▀░▀░░░▀▀▀░▀░░░░▀░░░▀░░▀░▀░▀▀▀░▀▀▀░░▀░
"""

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)

def get_all_files_of_directory(directory_path):
    structure = {}
    full_size = 0
    try:
        for file_or_directory in os.listdir(directory_path):
            try:
                full_path = os.path.join(directory_path, file_or_directory)
                if os.path.isfile(full_path):
                    add_to_full_size = os.path.getsize(full_path)
                    structure[full_path] = {"size": add_to_full_size, "content": None}
                else:
                    structure[full_path], add_to_full_size = get_all_files_of_directory(full_path)
                full_size += add_to_full_size
            except:
                continue # FIXME: Error Handling
    except:
        pass # FIXME: Error Handling
    return structure, full_size

def compress_file(file_path):
    try:
        with open(file_path, 'rb') as readable_file:
            file_bytes = readable_file.read()
    except:
        return None # FIXME: Error Handling
    try:
        compressed_bytes = gzip.compress(file_bytes)

        return compressed_bytes
    except:
        return file_bytes # FIXME: Error Handling

def decompress_file(file_bytes):
    try:
        decompressed_bytes = gzip.decompress(file_bytes)

        return decompressed_bytes
    except:
        return None # FIXME: Error Handling

def compress_structure(structure: dict):
    for path, object in structure.items():
        if isinstance(object, dict):
            object["content"] = compress_file(path)
            structure[path] = object
        else:
            structure[path] = compress_structure(object)
    return structure

def generate_random_string(length: int, with_punctuation: bool = True, with_letters: bool = True) -> str:
    """
    Generates a random string

    :param length: The length of the string
    :param with_punctuation: Whether to include special characters
    :param with_letters: Whether letters should be included
    """

    characters = "0123456789"

    if with_punctuation:
        characters += r"!\"#$%&'()*+,-.:;<=>?@[\]^_`{|}~"

    if with_letters:
        characters += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

def get_password_strength(password: str) -> int:
    """
    Function to get a password strength from 0 (bad) to 100% (good)
    :param password: The password to check
    """
    
    strength = (len(password) * 62.5) / 16
    
    if strength > 70:
        strength = 70
        
    if re.search(r'[A-Z]', password):
        strength += 12.6
    if re.search(r'[a-z]', password):
        strength += 12.6
    if re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\]', password):
        strength += 12.6
    
    if strength > 100:
        strength = 100
    return round(strength)

def is_password_safe(password: str) -> bool:
    password_sha1_hash = hashlib.sha1(password.encode()).hexdigest()
    hash_prefix = password_sha1_hash[:5]

    try:
        url = f"https://api.pwnedpasswords.com/range/{hash_prefix}"
        with request.urlopen(url) as response:
            if response.status == 200:
                response_content = response.read().decode('utf-8')

                for sha1_hash in response_content.split("\n"):
                    sha1_hash = sha1_hash.split(":")[0]
                    if sha1_hash == password_sha1_hash:
                        return False
    except error.URLError as e:
        pass  # FIXME: Error Handling

    return True

class SymmetricEncryption:
    "Implementation of symmetric encryption with AES"

    def __init__(self, password: str, salt_length: int = 32):
        """
        :param password: A secure encryption password, should be at least 32 characters long
        :param salt_length: The length of the salt, should be at least 16
        """

        self.password = password.encode()
        self.salt_length = salt_length

    def encrypt(self, plain_data: bytes):
        salt = secrets.token_bytes(self.salt_length)

        kdf_ = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf_.derive(self.password)

        iv = secrets.token_bytes(16)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = symmetric_padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plain_data) + padder.finalize()
        cipher_data = encryptor.update(padded_data) + encryptor.finalize()

        return (salt + iv + cipher_data)

    def decrypt(self, salt, iv, cipher_data) -> str:
        kdf_ = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf_.derive(self.password)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = symmetric_padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = decryptor.update(cipher_data) + decryptor.finalize()
        plain_data = unpadder.update(decrypted_data) + unpadder.finalize()

        return plain_data