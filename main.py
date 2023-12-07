from sys import exit

if __name__ != "__main__":
    exit(1)

from utils import clear_console, get_all_files_of_directory, compress_structure, generate_random_string, get_password_strength,\
                  is_password_safe, directory_load_keys, AsymmetricEncryption
import os
from rich.console import Console
from getpass import getpass

CURRENT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

CONSOLE = Console()

while True:
    mission = None
    options = ["Encrypt file / folder", "Restore data from file", "Secure deletion of files or folders", "Exit"]
    selected_option = 0

    while True:
        clear_console()

        for i, option in enumerate(options):
            if i == selected_option:
                print(f"[>] {option}")
            else:
                print(f"[ ] {option}")
        
        key = input("\nChoose what to do (c to confirm): ")

        if not key.lower() in ["c", "confirm"]:
            if len(options) < selected_option + 2:
                selected_option = 0
            else:
                selected_option += 1
        else:
            mission = selected_option
            break

    if mission == 3:
        exit(1)
    
    if mission == 0:
        clear_console()

        path = input("Enter the file or folder path: ")
        print("")

        with CONSOLE.status("[green]Exploring the file structure..."):
            if os.path.isfile(path):
                full_size = os.path.getsize(path)
                structure = {path: {"size": full_size, "content": None}}
            else:
                structure, full_size = get_all_files_of_directory(path)
            
        CONSOLE.print("[green]~ Exploring the file structure... Done")

        with CONSOLE.status("[green]Compression of all files..."):
            structure = compress_structure(structure)

        mission = None
        options = ["Password encryption", "Public key encryption", "Password encryption and Public key encryption"]
        selected_option = 0
        while True:
            clear_console()
            print(f"Enter the file or folder path: {path}\n")
            CONSOLE.print("[green]~ Exploring the file structure... Done")
            CONSOLE.print("[green]~ Compression of all files... Done")
            print("")

            for i, option in enumerate(options):
                if i == selected_option:
                    print(f"[>] {option}")
                else:
                    print(f"[ ] {option}")
            
            key = input("\nSelect which encryption should be used (c to confirm): ")

            if not key.lower() in ["c", "confirm"]:
                if len(options) < selected_option + 2:
                    selected_option = 0
                else:
                    selected_option += 1
            else:
                mission = selected_option
                break
        
        encryption_method = options[mission]

        password = None
        public_key = None

        if mission in [0, 2]:
            while True:
                clear_console()
                print(f"Enter the file or folder path: {path}\n")
                CONSOLE.print("[green]~ Exploring the file structure... Done")
                CONSOLE.print("[green]~ Compression of all files... Done")
                print("\nUsing", encryption_method+"\n")
                inputed_password = getpass("Please enter a strong password: ")

                if inputed_password == "":
                    with CONSOLE.status("[green]Generating a secure password..."):
                        generated_password = generate_random_string(16)
                        while not get_password_strength(generated_password) == 100:
                            print(get_password_strength(generated_password))
                            generated_password = generate_random_string(16)
                    
                    clear_console()
                    CONSOLE.print("Your generated password is called:", f"[blue]{generated_password}")
                    input("Press Enter, the password will no longer be displayed:")

                    password = generated_password
                    break
                else:
                    password_strength = get_password_strength(inputed_password)
                    if password_strength < 50:
                        CONSOLE.print("[red][Error] The given password is not strong enough")
                        input("Enter: ") # FIXME: Decision on further procedure
                        continue
                    elif not is_password_safe(inputed_password):
                        CONSOLE.print("[red][Error] Your password exists in a data leak, it is not secure")
                        input("Enter: ") # FIXME: Decision on further procedure
                        continue
                    else:
                        strength_color = "red" if password_strength < 70 else "yellow" if password_strength < 90 else "green"
                        CONSOLE.print(f"[{strength_color}]Password Strength: {str(password_strength)}/100%\n")

                        repeated_password = getpass("Repeat Password: ")
                        if not inputed_password == repeated_password:
                            CONSOLE.print("[red][Error] The passwords entered do not match")
                            input("Enter: ") # FIXME: Decision on further procedure
                            continue
                        else:
                            password = inputed_password
                            break

        if mission in [1, 2]:
            with CONSOLE.status("[green]Searching and loading key files..."):
                key_files, _ = directory_load_keys(CURRENT_DIR_PATH)

            if not len(key_files) == 0:
                mission = None
                options = [key_id + " (Public Key)" for key_id in key_files.keys()]
                options.append("Enter own path")
                selected_option = 0

                while True:
                    clear_console()
                    print(f"Enter the file or folder path: {path}\n")
                    CONSOLE.print("[green]~ Exploring the file structure... Done")
                    CONSOLE.print("[green]~ Compression of all files... Done")
                    print("\nUsing", encryption_method+"\n")

                    for i, option in enumerate(options):
                        if i == selected_option:
                            print(f"[>] {option}")
                        else:
                            print(f"[ ] {option}")
                    
                    key = input("\nChoose a Publ Key (c to confirm): ")

                    if not key.lower() in ["c", "confirm"]:
                        if len(options) < selected_option + 2:
                            selected_option = 0
                        else:
                            selected_option += 1
                    else:
                        if not len(options) == selected_option + 1:
                            public_key = list(key_files.values())[selected_option]
                        break
                
            if public_key is None:
                while True:
                    clear_console()
                    print(f"Enter the file or folder path: {path}\n")
                    CONSOLE.print("[green]~ Exploring the file structure... Done")
                    CONSOLE.print("[green]~ Compression of all files... Done")
                    print("\nUsing", encryption_method+"\n")

                    inputed_public_key_path = input("Please enter the path to the folder / public key file: ")
                    if inputed_public_key_path == "":
                        print("")
                        with CONSOLE.status("[green]Generate a private and public key pair..."):
                            asymmetricencryption = AsymmetricEncryption().generate_keys()
                            public_key, private_key = asymmetricencryption.public_key, asymmetricencryption.private_key
                        CONSOLE.print("[green]~ Generate a private and public key pair... Done")

                        key_id = input("What would you like to call the key pair? ") # FIXME: Further validation of the keyid
                        if key_id == "":
                            key_id = generate_random_string(4, with_punctuation=False)

                        public_key_path = os.path.join(CURRENT_DIR_PATH, key_id + "-publ.key")
                        private_key_path = os.path.join(CURRENT_DIR_PATH, key_id + "-priv.key")

                        with open(public_key_path, "w") as writeable_file:
                            writeable_file.write(public_key)

                        with open(private_key_path, "w") as writeable_file:
                            writeable_file.write(private_key)
                        break
                    elif os.path.isfile(inputed_public_key_path):
                        with open(inputed_public_key_path, "r") as readable_file:
                            public_key = readable_file.read()
                        break
                    elif os.path.isdir(inputed_public_key_path):
                        with CONSOLE.status("[green]Searching and loading key files..."):
                            key_files, _ = directory_load_keys(inputed_public_key_path)
                        
                        if len(key_files) == 0:
                            CONSOLE.print("[red][Error] No public or private keys were found")
                            input("Enter: ")
                        elif len(key_files) == 1:
                            public_key = key_files.values()[0]
                        else:
                            mission = None
                            options = [key_id + " (Public Key)" for key_id in key_files.keys()]
                            options.append("Back")
                            selected_option = 0

                            while True:
                                clear_console()
                                print(f"Enter the file or folder path: {path}\n")
                                CONSOLE.print("[green]~ Exploring the file structure... Done")
                                CONSOLE.print("[green]~ Compression of all files... Done")
                                print("\nUsing", encryption_method+"\n")

                                for i, option in enumerate(options):
                                    if i == selected_option:
                                        print(f"[>] {option}")
                                    else:
                                        print(f"[ ] {option}")
                                
                                key = input("\nChoose a Publ Key (c to confirm): ")

                                if not key.lower() in ["c", "confirm"]:
                                    if len(options) < selected_option + 2:
                                        selected_option = 0
                                    else:
                                        selected_option += 1
                                else:
                                    if not len(options) == selected_option + 1:
                                        public_key = key_files.values()[selected_option]
                                    break
                    else:
                        CONSOLE.print("[red][Error] The given path does not exist")
                        input("Enter: ")
                            
                    if not public_key is None:
                        break
        
        key_file = None

        mission = None
        options = ["No", "Yes"]
        selected_option = 0
        while True:
            clear_console()
            print(f"Enter the file or folder path: {path}\n")
            CONSOLE.print("[green]~ Exploring the file structure... Done")
            CONSOLE.print("[green]~ Compression of all files... Done")
            print("\nUsing", encryption_method)
            CONSOLE.print("[green]~ Encryption credentials added")

            for i, option in enumerate(options):
                if i == selected_option:
                    print(f"[>] {option}")
                else:
                    print(f"[ ] {option}")
            
            key = input("\nChoose whether you want to use a key file (c to confirm): ")

            if not key.lower() in ["c", "confirm"]:
                if len(options) < selected_option + 2:
                    selected_option = 0
                else:
                    selected_option += 1
            else:
                mission = selected_option
                break
                                
        continue