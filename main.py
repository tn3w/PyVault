from sys import exit

if __name__ != "__main__":
    exit(1)

from utils import clear_console, get_all_files_of_directory, compress_structure, generate_random_string, get_password_strength,\
                  is_password_safe
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
        publ_key_path = None

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
                        CONSOLE.print("[red][Error]The given password is not strong enough")
                        input("Enter: ") # FIXME: Decision on further procedure
                        continue
                    elif not is_password_safe(inputed_password):
                        CONSOLE.print("[red][Error]Your password exists in a data leak, it is not secure")
                        input("Enter: ") # FIXME: Decision on further procedure
                        continue
                    else:
                        strength_color = "red" if password_strength < 70 else "yellow" if password_strength < 90 else "green"
                        CONSOLE.print(f"[{strength_color}]Password Strength: {str(password_strength)}/100%\n")

                        repeated_password = getpass("Repeat Password: ")
                        if not inputed_password == repeated_password:
                            CONSOLE.print("[red][Error]The given password is not strong enough")
                            input("Enter: ") # FIXME: Decision on further procedure
                            continue
                        else:
                            password = inputed_password
                            break
        continue