from script_my.scanner import scanner
import os
from pathlib import Path

def filter_large_files(file_generator, min_size_mb):

    filtred_files = []

    for path, size in file_generator:
        if size >= int(min_size_mb):
            filtred_files.append((path,size))

    filtred_files.sort(key=lambda x: x[1], reverse=True)
    return filtred_files

