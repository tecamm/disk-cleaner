import os
import send2trash
import subprocess
from script_my.analyzer import filter_large_files

def check_write_access(file_path):
    try:
        with open(file_path, 'a'):
            pass
        return True
    except PermissionError:
        return False
    except Exception:
        return False

def show_file_in_explorer(target_path):
    try:
        normalized_path = os.path.normpath(target_path)
        subprocess.run(['explorer', '/select,', normalized_path])
        return True, ''
    except Exception as e:
        return False, str(e)


def s3nd2trash(target_path):
        try:
            send2trash.send2trash(target_path)
            return True, ''
        except Exception as e:
            return False, str(e)

def scan_del(target_path):
        try:
            os.remove(target_path)
            return True,''
        except Exception as e:
            return False, str(e)
