import os
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import customtkinter as ctk
import send2trash
import hashlib
from script_my.analyzer import filter_large_files
from script_my.scanner import scanner
import subprocess
import json
from script_my.file_operations import *
from datetime import datetime
import csv
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {"theme": "dark", "language": "ru"}

def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=4)

system_drive = os.environ.get('SystemDrive', 'C:')
protected = [
             os.environ.get('WINDIR', f'{system_drive}\\Windows').lower(),
             os.environ.get('PROGRAMFILES', f'{system_drive}\\Program Files').lower(),
             os.environ.get('PROGRAMFILES(X86)', f'{system_drive}\\Program Files (x86)').lower(),
             os.environ.get('PROGRAMDATA', f'{system_drive}\\ProgramData').lower()
             ]

app_settings = load_settings()
ctk.set_appearance_mode(app_settings['theme'])
ctk.set_default_color_theme("blue")

is_system_dir = False

files_to_delete = []
current_screen = "main"

base_dir = getattr(sys, "base_prefix", sys.prefix)

tcl_dir = os.path.join(base_dir, "tcl", "tcl8.6")
tk_dir = os.path.join(base_dir, "tcl", "tk8.6")

if os.path.exists(tcl_dir):
    os.environ['TCL_LIBRARY'] = tcl_dir
    os.environ['TK_LIBRARY'] = tk_dir
'''DEFS'''

def get_file_hash(path):
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None

def draw_file_row(file_path, display_text):
    scan_list_row_frame = ctk.CTkFrame(scan_list)
    scan_list_row_frame.pack(fill='x', pady=3)

    scan_list_file = ctk.CTkLabel(scan_list_row_frame, text=display_text, font=('Arial', 14))
    scan_list_file.pack(side="left", padx=5, pady=3)

    delete_btn = ctk.CTkButton(scan_list_row_frame, text="❌", width=30, fg_color="#b23b3b", hover_color='#702424',
                               command=lambda p=file_path, f=scan_list_row_frame: scan_del_ui(p, f))
    delete_btn.pack(side="right", padx=2)

    trash_btn = ctk.CTkButton(scan_list_row_frame, text='🗑️', width=30, fg_color="#807575", hover_color='#524d4d',
                              command=lambda p=file_path, f=scan_list_row_frame: s3nd2trash_ui(p, f))
    trash_btn.pack(side="right", padx=2)

    folder_btn = ctk.CTkButton(scan_list_row_frame, text="📁", width=30,
                               command=lambda p=file_path: show_file_in_explorer_ui(p))
    folder_btn.pack(side="right", padx=2)

def finish_scan():
    global current_screen
    global is_system_dir
    if is_system_dir:
        messagebox.showinfo('Системные файлы!', "В этой папке находятся системнные файлы!")

    progress_bar.stop()
    progress_bar_frame.place_forget()
    scan_list_frame.place(relheight=1, relwidth=1)
    current_screen = 'scan_list'

def scan_process(path, size):
    global files_to_delete
    global is_system_dir
    files_to_delete.clear()

    ui_items_count = 0
    max_ui_items = 200

    current_time = time.time()
    days_limit = file_data_option.get()

    gen = scanner(path)
    result = filter_large_files(gen, size)

    seen_hashes = set()

    for file_path, file_size in result:

        if any(str(file_path).lower().startswith(prot) for prot in protected):
            is_system_dir = True
            continue

        try:
            file_mdata = os.path.getmtime(file_path)
        except (FileNotFoundError, OSError):
            continue

        age_in_days = (current_time - file_mdata) / 86400


        if file_type_check.get() == 1:
            allowed_types = [ext.strip() for ext in file_type_option.get().split(',')]

            if file_path.suffix not in allowed_types:
                continue


        if file_data_check.get() == 1 and float(days_limit) >= float(age_in_days):
            continue


        has_adm_access = check_write_access(file_path)
        if sys_check.get() == 1 and not has_adm_access:
            continue

        if file_twin_check.get() == 1:
            current_hash = get_file_hash(file_path)

            if current_hash is None:
                continue

            if current_hash in seen_hashes:
                pass
            else:
                seen_hashes.add(current_hash)
                continue

        files_to_delete.append(file_path)

        if ui_items_count < max_ui_items:

            max_len = 35
            file_name = file_path.name
            if len(file_name) >= max_len:
                suf = file_path.suffix
                allowed_len = max_len - len(suf) - 3

                if allowed_len > 0:
                    file_name = f'{file_path.stem[:allowed_len]}...{suf}'
                else:
                    file_name = file_name[:max_len - 3] + "..."

            size_replace = 0
            if option_menu.get() == 'КБ':
                size_replace = file_size * 1024
            elif option_menu.get() == 'МБ':
                size_replace = file_size
            elif option_menu.get() == 'ГБ':
                size_replace = file_size / 1024

            date_str = datetime.fromtimestamp(file_mdata).strftime('%d.%m.%y %H:%M')
            unit = option_menu.get()
            display_text = f"{file_name} | {round(size_replace, 2)} {unit} | {date_str}"

            time.sleep(0.01)
            root.after(0, draw_file_row, file_path, display_text)

            ui_items_count += 1



    root.after(0, finish_scan)


# def del_btn_ui():
#     path = entry_path.get()
#     size = min_size_entry.get()
#
#     if not path or not size:
#         messagebox.showwarning('Внимание!', "Заполните все поля!")
#         return
#
#     if os.path.isdir(path):
#         messagebox.askyesno('Подтверждение', f"Вы действительно хотите удалить файлы в {path}")
#         return True
#     else:
#         messagebox.showerror('Ошибка!', 'Такой папки не существует!')
#
#     entry_path.delete(0, tk.END)
#     min_size_entry.delete(0, tk.END)

def scan_btn_ui():
    path = entry_path.get()
    entry_size = min_size_entry.get()
    size_from_menu = option_menu.get()

    global current_screen

    if not path or not entry_size:
        messagebox.showwarning('Внимание!', "Заполните все поля!")
        return

    try:
        size = float(entry_size)
        if size_from_menu == 'КБ':
            size = size / 1024
        if size_from_menu == 'ГБ':
            size = size * 1024
    except ValueError:
        messagebox.showwarning('Размер должен быть числом!')
        return

    if os.path.isdir(path):

        current_screen = 'progress'
        scan_frame.place_forget()
        progress_bar_frame.place(relheight=1, relwidth=1)


        for widget in scan_list.winfo_children():
            widget.destroy()

        progress_bar.start()

        thread = threading.Thread(target=scan_process, args=(path, size), daemon=True)
        thread.start()
    else:
        messagebox.showerror('Ошибка!', 'Такой папки не существует!')

    entry_path.delete(0, tk.END)
    min_size_entry.delete(0, tk.END)

def show_file_in_explorer_ui(target_path):
    success,error_text = show_file_in_explorer(target_path)

    if not success:
        messagebox.showerror("Ошибка", f"Не удалось открыть проводник:\n{error_text}")
    else:
        show_file_in_explorer(target_path)

def s3nd2trash_ui(target_path, target_frame):
    confirm = messagebox.askyesno(
        title="Подтверждение",
        message=f"Вы действительно хотите выкинуть этот файл?\n\n{target_path.name}"
    )

    if confirm:
        success, error_text = s3nd2trash(target_path)

        if success:
            target_frame.destroy()
        else:
            messagebox.showerror("Ошибка", f"Не удалось выкинуть файл:\n{error_text}")

def scan_del_ui(target_path, target_frame):
    confirm = messagebox.askyesno(
        title="Подтверждение",
        message=f"Вы действительно хотите удалить этот файл?\n\n{target_path.name}"
    )

    if confirm:
        success, error_text = scan_del(target_path)

        if success:
            target_frame.destroy()
        else:
            messagebox.showerror("Ошибка", f"Не удалось удалить файл:\n{error_text}")

def browse_folder(entry_widget):
    folder_selected = filedialog.askdirectory(title="Выберите папку для работы")

    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_selected)

def show_scan():
    global current_screen
    current_screen = "scan"
    main_frame.place_forget()
    scan_frame.place(relheight=1, relwidth=1)

def show_settings():
    global current_screen
    current_screen = "settings"
    main_frame.place_forget()
    settings_frame.place(relwidth=1, relheight=1)

def leave_page():
    global current_screen
    if current_screen == "main":
        root.destroy()
    elif current_screen == "scan":
        scan_frame.place_forget()
        main_frame.place(relheight=1, relwidth=1)
        current_screen = "main"
    elif current_screen == "scan_list":
        scan_list_frame.place_forget()
        scan_frame.place(relheight=1, relwidth=1)
        current_screen = 'scan'
    elif current_screen == 'settings':
        settings_frame.place_forget()
        main_frame.place(relwidth=1, relheight=1)
        current_screen="main"


def finish_del(deleted_count, failed_count):
    global current_screen
    progress_bar.stop()
    progress_bar_frame.place_forget()
    scan_list_high_text.configure(text='Удаленные файлы!')
    scan_list_frame.place(relwidth=1, relheight=1)
    current_screen = 'scan_list'

    messagebox.showinfo("Готово",
                        f"Очистка завершена!\nУдалено файлов: {deleted_count}\nОшибок: {failed_count}")

def deleted_file_row(display_text):
    scan_list_row_frame = ctk.CTkFrame(scan_list)
    scan_list_row_frame.pack(fill='x', pady=3)

    scan_list_file = ctk.CTkLabel(scan_list_row_frame, text=display_text, font=('Arial', 14), text_color="#2b7a2b")
    scan_list_file.pack(side="left", padx=5, pady=3)

def delete_all():
    ui_items_count = 0
    MAX_UI_ITEMS = 200
    deleted_count = 0
    failed_count = 0

    for file_path in files_to_delete:
        try:

            os.remove(file_path)
            deleted_count += 1

            if ui_items_count < MAX_UI_ITEMS:
                display_text = f'Удалено: {file_path.name}'
                time.sleep(0.005)
                root.after(0, deleted_file_row, display_text)
                ui_items_count += 1

        except (PermissionError, OSError, FileNotFoundError):
            failed_count += 1
            continue
    files_to_delete.clear()

    root.after(0, finish_del, deleted_count, failed_count)


def del_btn():
    global current_screen
    total_files = len(files_to_delete)

    if total_files == 0:
        messagebox.showinfo("Пусто", "Нет файлов для удаления!")
        return

    confirm = messagebox.askyesno('Удаление', f"Вы действительно хотите навсегда удалить {total_files} файлов?")

    if confirm:
        current_screen = 'progress'
        scan_frame.place_forget()
        progress_bar_frame.place(relheight=1, relwidth=1)

        for widget in scan_list.winfo_children():
            widget.destroy()

        progress_bar.start()

        thread = threading.Thread(target=delete_all, daemon=True)
        thread.start()

def set_theme():
    settings = load_settings()

    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("light")
        theme_btn.configure(text='Dark')
        settings["theme"] = "light"
    else:
        ctk.set_appearance_mode("dark")
        theme_btn.configure(text='Light')
        settings["theme"] = "dark"

    save_settings(settings)





def export_results_ui():
    # Проверяем, есть ли что сохранять
    if not files_to_delete:
        messagebox.showinfo("Пусто", "Нет файлов для экспорта. Сначала проведите сканирование.")
        return

    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Текстовый файл", "*.txt"), ("CSV таблица", "*.csv")],
        title="Сохранить результаты сканирования"
    )

    if not filepath:
        return

    try:
        if filepath.endswith('.csv'):

            with open(filepath, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["Путь к файлу", "Размер (Байт)", "Дата изменения"])

                for p in files_to_delete:
                    try:
                        size = os.path.getsize(p)
                        date_str = datetime.fromtimestamp(os.path.getmtime(p)).strftime('%d.%m.%Y %H:%M')
                        writer.writerow([str(p), size, date_str])
                    except OSError:
                        continue
        else:
            with open(filepath, mode='w', encoding='utf-8') as f:
                f.write("=== Отчет очистки диска ===\n\n")
                for p in files_to_delete:
                    f.write(f"{str(p)}\n")

        messagebox.showinfo("Успех", "Отчет успешно сохранен!")
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Произошла ошибка:\n{e}")

'''ROOT'''

root = ctk.CTk()
root.geometry('1240x720')
root.title('Disk Cleaner')
root.resizable(False, False)

"""MAIN FRAME"""

main_frame = ctk.CTkFrame(root)
main_frame.place(relheight=1, relwidth=1)

high_text = ctk.CTkLabel(main_frame, text='Очистка диска', font=('Arial', 32, 'bold'))
high_text.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

btn_start = ctk.CTkButton(main_frame, text='Cканирование папки(+удаление)', font=('Arial', 18), width=250, height=50,command=show_scan)
btn_start.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

leave_page_btn_main = ctk.CTkButton(main_frame, text='Выйти', font=('Arial', 14), width=100, fg_color="#b23b3b",hover_color="#8a2d2d", command=leave_page)
leave_page_btn_main.place(x=24, y=20)

settings_btn = ctk.CTkButton(main_frame, text='Настройки', font=('Arial', 14), width=100, command = show_settings)
settings_btn.place(x=1120, y= 20)

'''SCAN FRAME'''
scan_frame = ctk.CTkFrame(root)

scan_high_text = ctk.CTkLabel(scan_frame, text='Настройки сканирования', font=('Arial', 28, 'bold'))
scan_high_text.place(relx=0.5, rely=0.15, anchor=tk.CENTER)

scan_dir_text = ctk.CTkLabel(scan_frame, text='Выберите папку', font=('Arial', 18))
scan_dir_text.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

browse_btn = ctk.CTkButton(scan_frame, text='Обзор...', width=80, height=40, command=lambda: browse_folder(entry_path))
browse_btn.place(relx=0.7, rely = 0.38, anchor=tk.CENTER)

entry_path = ctk.CTkEntry(scan_frame, font=('Arial', 16), width=400, height=40)
entry_path.place(relx=0.5, rely=0.38, anchor=tk.CENTER)

file_size_text = ctk.CTkLabel(scan_frame, text='Минимальный размер файла', font=('Arial', 18))
file_size_text.place(relx=0.5, rely=0.52, anchor=tk.CENTER)

option_menu = ctk.CTkOptionMenu(scan_frame, values=["КБ", "МБ", "ГБ"], width=80, height=40)
option_menu.place(relx=0.71, rely=0.6, anchor=tk.CENTER)

min_size_entry = ctk.CTkEntry(scan_frame, font=('Arial', 16), width=400, height=40)
min_size_entry.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

scan_infotab = ctk.CTkTextbox(scan_frame,height=300, width=250, font=('Arial', 14))
scan_infotab.insert('0.0', 'Это первая версия. В скором \nбудут еще обновления.')
scan_infotab.place(relx=0.88, rely=0.35, anchor=tk.CENTER)

btn_scan_tk = ctk.CTkButton(scan_frame, text='Начать сканирование', font=('Arial', 18), width=250, height=50, command= scan_btn_ui)
btn_scan_tk.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

tabview_scan = ctk.CTkTabview(scan_frame, height=300)
tabview_scan.place(relx=0.14, rely=0.35, anchor=tk.CENTER)
tabview_scan.add("Фильтры")

sys_check = ctk.CTkCheckBox(tabview_scan.tab("Фильтры"), text='Не учитывать системные файлы', font=('Arial', 15))
sys_check.pack(pady=20, padx=10, anchor="nw")

file_data_check = ctk.CTkCheckBox(tabview_scan.tab("Фильтры"), text='Файлы старше (в днях)', font=('Arial',15))
file_data_check.pack(pady=20, padx=10, anchor="nw")

file_data_option = ctk.CTkOptionMenu(tabview_scan.tab('Фильтры'), values=['30', '60', '90', '180'], height=25, width=70)
file_data_option.place(relx=0.74, rely=0.33)

file_type_check = ctk.CTkCheckBox(tabview_scan.tab('Фильтры'), text='По типу файлов', font=('Arial', 15))
file_type_check.pack(pady=20, padx=10, anchor="nw")

file_type_option = ctk.CTkOptionMenu(tabview_scan.tab('Фильтры'), values=['.zip, .rar', '.tmp, .log', 'mp4', 'mp3', '.png, .jpg, .jpeg'], height=25, width=70)
file_type_option.place(relx=0.55, rely=0.58)

file_twin_check = ctk.CTkCheckBox(tabview_scan.tab('Фильтры'), text='Только дубликаты', font=('Arial', 15))
file_twin_check.pack(pady=20, padx=10, anchor="nw")

leave_page_btn_scan = ctk.CTkButton(scan_frame, text='Назад', font=('Arial', 14), width=100, fg_color="#555555",hover_color="#333333", command=leave_page)
leave_page_btn_scan.place(x=24, y=20)

'''SCAN LIST FRAME'''
scan_list_frame = ctk.CTkFrame(root)

scan_list_high_text = ctk.CTkLabel(scan_list_frame, text="Результаты сканирования", font=('Arial', 24, 'bold'))
scan_list_high_text.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

scan_list = ctk.CTkScrollableFrame(scan_list_frame, width=720, height=500)
scan_list.place(relx=0.35, rely=0.5, anchor=tk.CENTER)

delete_all_btn = ctk.CTkButton(scan_list_frame, text='Удалить все файлы', font=('Arial', 15), command= del_btn)
delete_all_btn.place(relx = 0.8, rely = 0.25, anchor=tk.CENTER)

get_scan_result = ctk.CTkButton(scan_list_frame, text='Получить полный отчет',font=('Arial', 15), command= export_results_ui)
get_scan_result.place(relx = 0.8, rely= 0.3, anchor = tk.CENTER)

leave_page_btn_list = ctk.CTkButton(scan_list_frame, text='Назад', font=('Arial', 14), width=100, fg_color="#555555",hover_color="#333333", command=leave_page)
leave_page_btn_list.place(x=24, y=20)

'''PROGRESS BAR'''

progress_bar_frame = ctk.CTkFrame(root)

progress_bar = ctk.CTkProgressBar(progress_bar_frame, orientation='horizontal', mode='indeterminate', width=400)
progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

progress_bar_text = ctk.CTkLabel(progress_bar_frame, text='Сканирую...', font=('Arial', 26))
progress_bar_text.place(relx=0.5, rely=0.4, anchor = tk.CENTER)

'''SETTINGS FRAME'''

settings_frame = ctk.CTkFrame(root)

settings_high_text = ctk.CTkLabel(settings_frame, text='Настройки', font=('Arial', 35, 'bold'))
settings_high_text.place(rely=0.33, relx=0.5, anchor=tk.CENTER)

theme_text = ctk.CTkLabel(settings_frame, text='Смена темы', font=('Arial', 18))
theme_text.place(relx=0.45, rely =0.5, anchor=tk.CENTER)

initial_btn_text = 'Light' if app_settings["theme"] == "dark" else 'Dark'

theme_btn = ctk.CTkButton(settings_frame, text=initial_btn_text, font=('Arial', 15), height=40, width=130, command=set_theme)
theme_btn.place(relx=0.55, rely=0.5, anchor=tk.CENTER)

leave_page_btn_settings = ctk.CTkButton(settings_frame, text='Назад', font=('Arial', 14), width=100, fg_color="#555555", hover_color="#333333", command=leave_page)
leave_page_btn_settings.place(x=24, y=20)

root.mainloop()


