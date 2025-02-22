import os
import sys

# Ensure UTF-8 encoding for Windows
sys.stdout.reconfigure(encoding="utf-8")

# Folders to ignore
EXCLUDED_FOLDERS = {"node_modules", ".venv", "__pycache__", ".git"}


def generate_tree(directory, prefix=""):
    try:
        files = sorted(os.listdir(directory))
        files = [
            f for f in files if f not in EXCLUDED_FOLDERS
        ]  # Exclude unwanted folders

        for index, file in enumerate(files):
            path = os.path.join(directory, file)
            is_last = index == len(files) - 1
            connector = "└── " if is_last else "├── "

            print(prefix + connector + file)

            if os.path.isdir(path):
                extension = "    " if is_last else "│   "
                generate_tree(path, prefix + extension)

    except PermissionError:
        print(prefix + "└── [Access Denied]")


generate_tree("..")  # Change "." to a specific folder if needed
