import os.path

from script_my.scanner import scanner
from script_my.analyzer import filter_large_files
import time



def main():
    print("====Быстрое сканирование папки====")

    target_dir = input(r"Введите папку для сканирования (например, C:/Windows/Temp): ")
    min_mb = int(input("Введите минимальный размер файла(в мегабайтах): "))

    time.sleep(1)
    print(f"Начинаю быстрое сканирование {target_dir}...")
    time.sleep(1)

    gen = scanner(target_dir)
    result = filter_large_files(gen, min_mb)
    files_size = 0

    for path, size in result:
        print(f"Найден файл: {path.name} | Размер: {round(size, 2)} mb")
        files_size += size
        time.sleep(0.3)
        print(result)

    print(f"Всего файлов: {len(result)} \nОбщий размер: {round(files_size,2)} mb")

    agreement = input('Хотите удалить их? y/n: ')

    if agreement.lower() == 'y':
        for i in range(len(result)):
           result[i][0].unlink()

        print('Начинаю удаление...')
        time.sleep(1)
        print('Файлы удалены!')

    elif agreement.lower() == 'n':
        print('Удачного дня!')



"""            file_path = i
            
            
            if isinstance(file_path, Path):
                file_path.unlink(missing_ok = True)
            else:
                if os.path.exists(file_path):
                    os.remove(file_path)
"""

if __name__ == "__main__":
    main()