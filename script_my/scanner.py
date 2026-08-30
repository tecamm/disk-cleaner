import os
import math
from turtledemo.penrose import start

from pathlib import Path

if os.name == 'nt':
    TEMP_DIR = [
        {
            "path": Path(os.environ.get('USERPROFILE')) / 'AppData/Local/Temp',
            "name": "Temp from Appdata",
        },
        {
            "path": "C:/Windows/Temp",
            "name": "Temp from Windows" #Check careful
        },
        {
            "path": "C:/$Recycle.Bin"
        }
    ]

dir_scanned = []
def scanner(start_path):
    path= Path(start_path)

    try:
        with os.scandir(start_path) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        file_size = entry.stat(follow_symlinks=False).st_size / (1024*1024)

                        yield Path(entry.path), file_size

                    elif entry.is_dir(follow_symlinks=False):

                        dir_scanned.append(entry.name)
                        yield from scanner(entry.path)

                except (FileNotFoundError, PermissionError, FileExistsError, OSError):
                    continue
    except (FileNotFoundError, PermissionError, FileExistsError, OSError):
        pass




