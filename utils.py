from sys import exit

if __name__ == "__main__":
    exit(1)

import os
from typing import Tuple, Optional, Union
import gzip
import secrets
import re
import hashlib
from urllib import request, error
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as symmetric_padding
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
import json

LOGO = """
░█▀█░█░█░█░█░█▀█░█░█░█░░░▀█▀
░█▀▀░░█░░▀▄▀░█▀█░█░█░█░░░░█░
░▀░░░░▀░░░▀░░▀░▀░▀▀▀░▀▀▀░░▀░
"""

def clear_console():
    "Deletes all elements in the console and sends the logo"

    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)

def get_all_files_of_directory(directory_path: str) -> Tuple[dict, int]:
    """
    Returns the contents of a directory recursively as a list

    :param directory_path: Path to directory
    """

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

def compress_file(file_path: str) -> bytes:
    """
    Compresses a file

    :param file_path: Path to file
    """

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

def decompress_file(file_bytes: bytes) -> bytes:
    """
    Decompresses a file

    :param file_bytes: compressed file bytes
    """

    try:
        decompressed_bytes = gzip.decompress(file_bytes)

        return decompressed_bytes
    except:
        return None # FIXME: Error Handling

def compress_structure(structure: dict) -> dict:
    """
    Loads all files of a given file structure, compresses them and inserts them into the structure

    :param structure: file structure generated by get_all_files_of_directory(directory_path)
    """

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
    """
    Ask pwnedpasswords.com if password is available in data leak

    :param password: Password to check against
    """

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

def compress_dict_or_list(object: Union[dict, list]) -> bytes:
    """
    Compiles a json object dict or list to bytes and compresses it

    :param object: The json object, dict or list
    """

    object_str = json.dumps(object, separators=(',', ':'))
    compressed_bytes = gzip.compress(object_str.encode('utf-8'))
    return compressed_bytes

def decompress_bytes_to_dict_or_list(compressed_data: bytes) -> Union[dict, list]:
    """
    Decompresses bytes and converts them to a json dictionary or list.

    :param compressed_data: Compressed bytes
    :return: Decompressed Python dictionary or list
    """

    decompressed_data = gzip.decompress(compressed_data)
    decoded_json_str = decompressed_data.decode('utf-8')

    if decoded_json_str.startswith(('{', '[')):
        return json.loads(decoded_json_str)
    raise ValueError("Invalid JSON data.")

class SymmetricEncryption:
    "Implementation of symmetric encryption with AES"

    def __init__(self, password: Union[str, bytes], salt_length: int = 32):
        """
        :param password: A secure encryption password, should be at least 32 characters long
        :param salt_length: The length of the salt, should be at least 16
        """
        
        if isinstance(password, str):
            password = password.encode()

        self.password = password
        self.salt_length = salt_length

    def encrypt(self, plain_data: bytes) -> bytes:
        """
        Encrypts data with the specified password

        :param plain_data: The plain data in bytes
        """

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

        return compress_dict_or_list([salt.hex(), iv.hex(), cipher_data.hex()])

    def decrypt(self, compressed_data: bytes) -> bytes:
        """
        Decrypts data with the specified password

        :param compressed_data: All data required for decryption
        """

        decompressed_data = decompress_bytes_to_dict_or_list(compressed_data)
        salt, iv, cipher_data = bytes.fromhex(decompressed_data[0]), bytes.fromhex(decompressed_data[1]), bytes.fromhex(decompressed_data[2])

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

class AsymmetricEncryption:
    "Implementation of secure asymmetric encryption with RSA"

    def __init__(self, public_key: Optional[str] = None, private_key: Optional[str] = None):
        """
        :param public_key: The public key to encrypt a message / to verify a signature
        :param private_key: The private key to decrypt a message / to create a signature
        """
        
        self.public_key, self.private_key = public_key, private_key

        if not public_key is None:
            public_key_bytes = base64.b64decode(public_key.encode('utf-8'))
            self.publ_key = serialization.load_der_public_key(public_key_bytes, backend=default_backend())
        else:
            self.publ_key = None

        if not private_key is None:
            private_key_bytes = base64.b64decode(private_key.encode('utf-8'))
            self.priv_key = serialization.load_der_private_key(private_key_bytes, password=None, backend=default_backend())
        else:
            self.priv_key = None

    def generate_keys(self, key_size: int = 2048) -> "AsymmetricEncryption":
        """
        Generates private and public key

        :param key_size: The key size of the private key
        """

        if self.priv_key is None:
            self.priv_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            private_key_bytes = self.priv_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            self.private_key = base64.b64encode(private_key_bytes).decode('utf-8')
        
        if self.publ_key is None:
            self.publ_key = self.priv_key.public_key()
            public_key_bytes = self.publ_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.public_key = base64.b64encode(public_key_bytes).decode('utf-8')

        return self

    def encrypt(self, plain_data: bytes) -> Tuple[bytes]:
        """
        Encrypts data with public key

        :param plain_data: The plain data in bytes
        """

        if self.publ_key is None:
            raise ValueError("The public key cannot be None in encode, this error occurs because no public key was specified when initializing the AsymmetricCrypto function and none was generated with generate_keys.")

        symmetric_key = secrets.token_bytes(64)

        symmetric_compressed_data = SymmetricEncryption(symmetric_key).encrypt(plain_data)

        cipher_symmetric_key = self.publ_key.encrypt(
            symmetric_key,
            asymmetric_padding.OAEP(
                mgf = asymmetric_padding.MGF1(
                    algorithm = hashes.SHA256()
                ),
                algorithm = hashes.SHA256(),
                label = None
            )
        )

        compressed_data = compress_dict_or_list([symmetric_compressed_data.hex(), cipher_symmetric_key.hex()])
        return compressed_data

    def decrypt(self, compressed_data: bytes) -> bytes:
        """
        Decrypts data with private key

        :param compressed_data: All data required for decryption
        """

        decompressed_list = decompress_bytes_to_dict_or_list(compressed_data)
        symmetric_compressed_data, cipher_symmetric_key = bytes.fromhex(decompressed_list[0]), bytes.fromhex(decompressed_list[1])

        if self.priv_key is None:
            raise ValueError("The private key cannot be None in decode, this error occurs because no private key was specified when initializing the AsymmetricCrypto function and none was generated with generate_keys.")

        symmetric_key = self.priv_key.decrypt(
            cipher_symmetric_key, 
            asymmetric_padding.OAEP(
                mgf = asymmetric_padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm = hashes.SHA256(),
                label = None
            )
        )

        plain_text = SymmetricEncryption(symmetric_key).decrypt(symmetric_compressed_data)

        return plain_text

def directory_load_keys(directory_path: str) -> Tuple[dict, dict]:
    """
    Function to get all keys (public and private) that are stored in a dict as a file (not recursive)

    :param directory_path: Path to directory  
    """
    
    publ_key_files = {}
    priv_key_files = {}

    for file_or_directory in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file_or_directory)

        if os.path.isfile(full_path):
            if file_or_directory.endswith(("-priv.key", "-publ.key")):
                file_id = file_or_directory.replace("-priv.key", "").replace("-publ.key", "")
                is_private_key = file_or_directory.endswith("-priv.key")

                with open(full_path, "r") as readable_file:
                    key = readable_file.read()

                try:
                    file_public_key = AsymmetricEncryption(private_key=key).generate_keys().public_key if is_private_key else key # FIXME: Validating publ key / loading it
                except:
                    continue # FIXME: Error Handling

                publ_key_files[file_id] = file_public_key

                if is_private_key:
                    priv_key_files[file_id] = key
    
    return publ_key_files, priv_key_files

def directory_load_key_files(directory_path: str) -> dict:
    """
    Function for retrieving all key files that are saved as a file in a dict (not recursive)

    :param directory_path: Path to directory
    """

    key_files = {}

    for file_or_directory in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file_or_directory)

        if os.path.isfile(full_path):
            if file_or_directory.endswith(".keyfile"):
                file_id = file_or_directory.replace(".keyfile", "")

                with open(full_path, "r") as readable_file:
                    key = readable_file.read()

                key_files[file_id] = key
    
    return key_files

class HexEncoding:
    "Implementation of hex encoding"

    def encrypt(self, plain_data: bytes) -> str:
        """
        Encodes bytes to string

        :param plain_data: The plain data in bytes
        """

        return plain_data.hex()

    def decrypt(self, encoded_data: str) -> bytes:
        """
        Decodes bytes to string

        :param encoded_data: The data encoded to string
        """

        return bytes.fromhex(encoded_data)
        

def encrypt_structure(structure: dict, encryption: Optional[Union[SymmetricEncryption, AsymmetricEncryption, HexEncoding]] = None) -> dict:
    """
    Encrypts a file structure

    :param structure: The file structure
    :param encryption: The encryption class used for encryption
    """

    if encryption is None:
        return structure

    new_structure = {}

    for file_or_directory, information in structure.items():
        if information.get("object") is None:
            new_structure[file_or_directory] = encrypt_structure(information, encryption)
        else:
            information["object"] = encryption.encrypt(information["object"])
            new_structure[file_or_directory] = information
    
    return new_structure

def decrypt_structure(structure: dict, encryption: Optional[Union[SymmetricEncryption, AsymmetricEncryption, HexEncoding]] = None) -> dict:
    """
    Decrypts a file structure

    :param structure: The file structure
    :param encryption: The encryption class used for decryption
    """

    if encryption is None:
        return structure

    new_structure = {}

    for file_or_directory, information in structure.items():
        if information.get("object") is None:
            new_structure[file_or_directory] = decrypt_structure(information, encryption)
        else:
            information["object"] = encryption.decrypt(information["object"])
            new_structure[file_or_directory] = information
    
    return new_structure