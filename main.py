from sys import exit

if __name__ != "__main__":
    exit(1)

from utils import clear_console, get_all_files_of_directory
import os
from rich.console import Console

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
        print("")

