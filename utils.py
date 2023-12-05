import os
import gzip
import secrets
import re
import hashlib
from urllib import request, error

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