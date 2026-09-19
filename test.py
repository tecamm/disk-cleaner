import os
import threading
import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
from pathlib import Path
import time

from script_my.analyzer import filter_large_files
from script_my.scanner import scanner


current_screen = "main"

base_path = r"C:\Users\lolik\AppData\Local\Programs\Python\Python313\tcl"
os.environ['TCL_LIBRARY'] = os.path.join(base_path, 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(base_path, 'tk8.6')

'''LEAVE PAGE BUTTON'''

def leave_page():
    global current_screen

    if current_screen == "main":
        root.destroy()

    if current_screen == "scan":
        scan_frame.place_forget()
        main_frame.place(relheight=1, relwidth=1)
        current_screen = "main"

    if current_screen == 'del':
        del_frame.place_forget()
        main_frame.place(relheight=1, relwidth=1)
        current_screen = "main"

    if current_screen == "scan_list":
        scan_list_frame.place_forget()
        scan_frame.place(relheight=1, relwidth=1)
        current_screen = 'scan'

'''FRAMES SETTINGS'''

def show_del():
    global current_screen
    current_screen = "del"

    main_frame.place_forget()
    del_frame.place(relheight=1, relwidth=1)

def show_scan():
    global current_screen
    current_screen = "scan"

    main_frame.place_forget()
    scan_frame.place(relheight=1, relwidth=1)


def scan_process(path, size):

    gen = scanner(path)
    result = filter_large_files(gen, size)
    for path, size in result:
        scan_list.insert(END, path.name)


def scan_btn():
    path = entry_path.get()
    size = min_size_entry.get()

    global current_screen

    if not path or not size:
        messagebox.showwarning('Внимание!', "Заполните все поля!")
        return

    if os.path.isdir(path):
        current_screen = 'scan_list'
        scan_frame.place_forget()
        scan_list_frame.place(relheight=1, relwidth=1)

        thread = threading.Thread(target=scan_process, args=(path, size), daemon=True)
        thread.start()

    else:
        messagebox.showerror('Ошибка!', 'Такой папки не существует!')



    entry_path.delete(0, END)
    min_size_entry.delete(0, END)



def del_btn():

    path = entry_path_del.get()
    size = min_size_entry_del.get()

    if not path or not size:
        messagebox.showwarning('Внимание!', "Заполните все поля!")
        return

    if os.path.isdir(path):
        messagebox.showinfo('Сканирование', f'Начинаю удаление в {entry_path_del.get()}...')
    else:
        messagebox.showerror('Ошибка!', 'Такой папки не существует!')

    entry_path_del.delete(0, END)
    min_size_entry_del.delete(0, END)

'''ROOT'''

root = ctk.CTk()
root.geometry('800x600')
root.title('Disk Cleaner')
root.resizable(height=False, width=False)

'''MAIN FRAME'''

main_frame = ctk.CTkFrame(master=root, bg_color="#929c84")
main_frame.place(relheight=1, relwidth=1)

high_text = Label(main_frame, bg='#1a1a1a', fg='white', text='Очистка диска', font=('Arial', 30, 'bold'))
high_text.place(x=400,y=200,anchor=CENTER)

btn_start = Button(main_frame, bg='white', text='Сканирование папки', font=('Arial', 20, 'italic'), command=show_scan)
btn_start.place(x=100,y=350)

btn_del_tk = Button(main_frame, bg='white', text='Удаление файлов', font=('Arial', 20, 'italic'), command=show_del)
btn_del_tk.place(x=450,y=350)

leave_page_btn_main = Button(main_frame, bg='white', text='Выйти', command=leave_page)
leave_page_btn_main.place(x=15,y=15)

'''SCAN FRAME'''

scan_frame = Frame(root, bg='#1a1a1a')

scan_high_text = Label(scan_frame, bg='#1a1a1a', fg='white', text='Сканирование папки', font=('Arial',30, 'bold'))
scan_high_text.place(relx=0.25, rely=0.15)

scan_dir_text = Label(scan_frame, bg='#1a1a1a', fg='white', text='Введите путь к папке', font=('Arial', 20))
scan_dir_text.place(relx=0.1, rely=0.3)

entry_path = Entry(scan_frame, bg='white', font=('Arial', 20), width=40)
entry_path.place(relx=0.1, rely=0.4)

file_size_text = Label(scan_frame, bg='#1a1a1a', fg='white', text='Введите минимальный размер файла (МБ)', font=('Arial', 20))
file_size_text.place(relx=0.1, rely=0.55)

min_size_entry = Entry(scan_frame, bg='white', font=('Arial', 20), width=40)
min_size_entry.place(relx=0.1, rely=0.65)

btn_scan_tk = Button(scan_frame, bg='white', text='Начать сканирование', font=('Arial', 20), command=scan_btn)
btn_scan_tk.place(relx=0.3, rely=0.80)

leave_page_btn_main = Button(scan_frame, bg='white', text='Назад', command=leave_page)
leave_page_btn_main.place(x=15,y=15)

'''DELETE FRAME'''

del_frame = Frame(root, bg='#1a1a1a')

del_high_text = Label(del_frame, bg='#1a1a1a', fg='white', text='Удаление файлов', font=('Arial', 30, 'bold'))
del_high_text.place(relx=0.3, rely=0.15)

del_dir_text = Label(del_frame, bg='#1a1a1a', fg='white', text='Введите путь к папке', font=('Arial', 20))
del_dir_text.place(relx=0.1, rely=0.3)

entry_path_del = Entry(del_frame, bg='white', font=('Arial', 20), width=40)
entry_path_del.place(relx=0.1, rely=0.4)

file_size_text = Label(del_frame, bg='#1a1a1a', fg='white', text='Введите минимальный размер файла (МБ)', font=('Arial', 20))
file_size_text.place(relx=0.1, rely=0.55)

min_size_entry_del = Entry(del_frame, bg='white', font=('Arial', 20), width=40)
min_size_entry_del.place(relx=0.1, rely=0.65)

btn_del_tk = Button(del_frame, bg='white', text='Начать удаление', font=('Arial', 20), command=del_btn)
btn_del_tk.place(relx=0.3, rely=0.80)

leave_page_btn_main = Button(del_frame, bg='white', text='Назад', command=leave_page)
leave_page_btn_main.place(x=15,y=15)

'''SCAN LISTBOX'''

scan_list_frame = Frame(root, bg = '#1a1a1a')

scan_list_scroll = Scrollbar(scan_list_frame, orient=VERTICAL)
scan_list_scroll.place(x=700, y=130, height=400)

scan_list = Listbox(scan_list_frame, bg='white', fg='#1a1a1a', font=('Arial', 14), yscrollcommand=scan_list_scroll.set)
scan_list.place(x=100, y= 130, height=400, width = 600)
scan_list_scroll.config(command=scan_list.yview)

scan_list_high_text = ctk.CTkLabel(scan_list_frame, fg_color='#1a1a1a', text= "Результаты сканирования", font=('Arial', 30, 'bold'))
scan_list_high_text.pack(pady=70)

leave_page_btn_main = Button(scan_list_frame, bg='white', text='Назад', command=leave_page)
leave_page_btn_main.place(x=15,y=15)

root.mainloop()

#
#
# from tkinter import *
#
# root = Tk()
# root.title("Disk Cleaner - Результаты")
# root.geometry("800x600")
# root.configure(bg='#1a1a1a') # Темный фон как на вашем скриншоте
#
# # Главный контейнер для списка (заменяет старый scan_list_frame)
# scan_list_frame = Frame(root, bg='#1a1a1a')
# scan_list_frame.place(x=100, y=130, height=400, width=600)
#
# # Заголовок
# scan_list_high_text = Label(root, bg='#1a1a1a', fg='white', text="Результаты сканирования", font=('Arial', 20, 'bold'))
# scan_list_high_text.pack(pady=30)
#
# # --- СОЗДАНИЕ КАСТОМНОГО СПИСКА С ПРОКРУТКОЙ ---
#
# # 1. Создаем Canvas для прокрутки
# canvas = Canvas(scan_list_frame, bg='#262626', highlightthickness=0)
# canvas.pack(side=LEFT, fill=BOTH, expand=True)
#
# # 2. Создаем и привязываем Scrollbar
# scrollbar = Scrollbar(scan_list_frame, orient=VERTICAL, command=canvas.yview)
# scrollbar.pack(side=RIGHT, fill=Y)
# canvas.configure(yscrollcommand=scrollbar.set)
#
# # 3. Фрейм внутри Canvas, где будут находиться строки с файлами
# scrollable_frame = Frame(canvas, bg='#262626')
# # Помещаем фрейм на холст
# canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=580)
#
# # Функция для динамического изменения области прокрутки
# def update_scroll_region(event):
#     canvas.configure(scrollregion=canvas.bbox("all"))
#
# scrollable_frame.bind("<Configure>", update_scroll_region)
#
# # --- ФУНКЦИЯ УДАЛЕНИЯ СТРОКИ ---
# def delete_file_row(row_frame, file_name):
#     # Здесь можно прописать реальное удаление файла с диска:
#     # os.remove(file_name)
#     row_frame.destroy() # Удаляет строку из графического интерфейса
#
# # --- ФУНКЦИЯ ДЛЯ ДОБАВЛЕНИЯ ФАЙЛА В СПИСОК ---
# def add_file_item(container, file_text):
#     # Создаем контейнер-строку
#     row = Frame(container, bg='#262626')
#     row.pack(fill=X, pady=4, padx=10) # pady задает вертикальный отступ между файлами
#
#     # Текст файла (с отступом слева через padx)
#     file_label = Label(row, text=file_text, bg='#262626', fg='white', font=('Arial', 12), anchor='w')
#     file_label.pack(side=LEFT, fill=X, expand=True, padx=(10, 5)) # padx=(слева, справа)
#
#     # Кнопка-корзинка "Удалить"
#     # Символ 🗑 встроен в большинство шрифтов Windows. fg='red' сделает её заметной.
#     del_btn = Button(row, text="🗑", font=('Arial', 12), bg='#333333', fg='#ff4d4d',
#                      activebackground='#ff4d4d', activeforeground='white',
#                      bd=0, relief=FLAT, cursor="hand2",
#                      command=lambda: delete_file_row(row, file_text))
#     del_btn.pack(side=RIGHT, padx=10, pady=2)
#
# # --- ЗАПОЛНЕНИЕ ДАННЫМИ ---
# # Имитируем ваш список файлов со скриншота
# test_files = [
#     "TgWsProxy_windows.exe | 23.55 MB",
#     "#1 Kisuke Stan_Image.gif | 7.08 MB",
#     "лаба 19-20.docx | 4.77 MB",
#     "Без названия.gif | 3.74 MB",
#     "disk_cleaner_icon.png | 3.53 MB",
#     "osori9080-hdd-4861120.ai | 1.83 MB",
#     "Архив_РПП_2026_10.03.01.zip | 1.54 MB",
#     "лаба 13.docx | 0.27 MB",
#     "image.png | 0.13 MB"
# ]
#
# for file_info in test_files:
#     add_file_item(scrollable_frame, file_info)
#
# root.mainloop()
#
#
#

'''DEL FRAME'''
del_frame = ctk.CTkFrame(root)

del_high_text = ctk.CTkLabel(del_frame, text='Настройки удаления', font=('Arial', 28, 'bold'))
del_high_text.place(relx=0.5, rely=0.15, anchor=tk.CENTER)

del_dir_text = ctk.CTkLabel(del_frame, text='Введите путь к папке', font=('Arial', 18))
del_dir_text.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

browse_btn_del = ctk.CTkButton(del_frame, text='Обзор...', width=80, height=40, command=lambda: browse_folder(entry_path_del))
browse_btn_del.place(relx=0.7, rely = 0.38, anchor=tk.CENTER)

entry_path_del = ctk.CTkEntry(del_frame, font=('Arial', 16), width=400, height=40)
entry_path_del.place(relx=0.5, rely=0.38, anchor=tk.CENTER)

file_size_text_del = ctk.CTkLabel(del_frame, text='Минимальный размер файла', font=('Arial', 18))
file_size_text_del.place(relx=0.5, rely=0.52, anchor=tk.CENTER)

option_menu = ctk.CTkOptionMenu(del_frame, values=["КБ", "МБ", "ГБ"], width=80, height=40)
option_menu.place(relx=0.71, rely=0.6, anchor=tk.CENTER)

min_size_entry_del = ctk.CTkEntry(del_frame, font=('Arial', 16), width=400, height=40)
min_size_entry_del.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

btn_del_tk = ctk.CTkButton(del_frame, text='Начать удаление', font=('Arial', 18), width=250, height=50,fg_color="#b23b3b", hover_color="#8a2d2d", command=del_btn_ui)
btn_del_tk.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

leave_page_btn_del = ctk.CTkButton(del_frame, text='Назад', font=('Arial', 14), width=100, fg_color="#555555",hover_color="#333333", command=leave_page)
leave_page_btn_del.place(x=24, y=20)

#
#
#
