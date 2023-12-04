import os

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
    for file_or_directory in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file_or_directory)
        if os.path.isfile(full_path):
            add_to_full_size = os.path.getsize(full_path)
            structure[full_path] = os.path.getsize(full_path)
        else:
            structure[full_path], add_to_full_size = get_all_files_of_directory(full_path)
        full_size += add_to_full_size
    return structure, full_size