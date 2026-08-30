from script_my.scanner import scanner
from script_my.analyzer import filter_large_files
import time

def main():
    print("====Быстрое сканирование папки====")

    target_dir = input(r"Введите папку для сканирования (например, C:/Windows/Temp): ")
    min_mb = int(input("Введите минимальный размер файла(в мегабайтах): "))

    time.sleep(1)
    print(f"Начинаю быстрое сканирование {r'C:\Users\lolik\Desktop\test_dir'}...")
    time.sleep(1)

    gen = scanner(target_dir)
    result = filter_large_files(gen, min_mb)
    files_size = 0

    for path, size in result:
        print(f"Найден файл: {path.name} | Размер: {round(size, 2)} mb")
        files_size += size
        time.sleep(0.3)

    print(f"Всего файлов: {len(result)} \n Общий размер: {round(files_size,2)} mb")

if __name__ == "__main__":
    main()