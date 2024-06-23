import os
import tkinter as tk
from tkinter import Menu
from tkinter import filedialog
from tksheet import Sheet

from ImageProcessor import ImageProcessor


class Application:
    def __init__(self, master=None):
        self.list_of_images = list()
        self.toplevel = None
        self.toplevel_sheet = None
        self.canvas = None
        self.master = master

        self.master.title('image classifier')
        self.master.state('zoomed')

        self.master.grid_columnconfigure(0, weight=1)

        # Создаем меню
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # Подменю "Файл"
        file_menu = Menu(menubar, tearoff=False)
        file_menu.add_command(label='Выбрать рабочую директорию', command=self.open_dir)
        file_menu.add_separator()
        menubar.add_cascade(label='Файл', menu=file_menu)

        # Подменю "Справка"
        help_menu = Menu(menubar, tearoff=False)
        help_menu.add_command(label='О программе', command=self.show_about)
        menubar.add_cascade(label='Справка', menu=help_menu)

        # Таблица
        sheet = Sheet(
            parent=self.master,
            show_row_index=False,
            show_x_scrollbar=False,
            width=1500,
        )
        self.sheet = sheet
        self.sheet.set_column_widths([100, 600, 600])
        self.sheet.enable_bindings('single_select')
        self.sheet.extra_bindings("cell_select", self.on_cell_click)
        self.sheet.headers(['name', 'path', 'aHash'])
        self.sheet.grid(row=0, column=0)

    def open_dir(self):
        filename = filedialog.askdirectory()
        if filename:
            self.read_dir(filename)
        else:
            raise ValueError("Choose direcory with images")

    def read_dir(self, dir_name):
        if self.list_of_images:
            self.list_of_images.clear()

        for filename in os.listdir(dir_name):
            if filename[-4:] == '.jpg':
                path = dir_name + f'/{filename}'
                self.list_of_images.append({
                    'name': filename,
                    'path': path,
                    'aHash': ImageProcessor.ahash(path),
                })
            else:
                raise TypeError(f'{filename}  -  unexpected type')

        self.update_data()

    def update_data(self):
        self.sheet.clear()
        data = self.get_data()
        self.sheet.set_data(data=data)

    def get_data(self):
        out = []
        for row in self.list_of_images:
            new_row = [row[key] for key in row.keys()]
            out.append(new_row)
        return out

    def on_cell_click(self, event):
        row = event['selected'].row
        path = self.sheet.get_cell_data(row, 1)

        toplevel = tk.Toplevel(self.master)
        self.toplevel = toplevel

        canvas1 = tk.Canvas(toplevel, height=500, width=500)  # Уменьшил ширину Canvas

        img = ImageProcessor.prepare_image(path)

        canvas1.create_image(0, 0, anchor='nw', image=img)
        canvas1.grid(row=0, column=0, padx=1)

        toplevel_sheet = Sheet(
            parent=toplevel,
            width=400,
            show_row_index=False,
            show_x_scrollbar=False
        )
        self.toplevel_sheet = toplevel_sheet
        toplevel_sheet.set_column_widths([200, 100])
        toplevel_sheet.enable_bindings('single_select')
        toplevel_sheet.extra_bindings('cell_select', self.on_cell_select)
        toplevel_sheet.headers(['name', 'similarity, %'])
        toplevel_sheet.grid(row=0, column=1, padx=1)

        data = ImageProcessor.prepare_table_data(
            list=self.list_of_images,
            index=row
        )
        toplevel_sheet.set_data(data=data)

        canvas2 = tk.Canvas(toplevel, height=500, width=500)
        self.canvas = canvas2
        # canvas2.create_image(0, 0, anchor='nw')
        canvas2.grid(row=0, column=2)

        toplevel.mainloop()

    def on_cell_select(self, event):
        row = event['selected'].row
        filename = self.toplevel_sheet.get_cell_data(row, 0)

        index = [item['name'] for item in self.list_of_images].index(filename)
        path = self.list_of_images[index]['path']

        new_img = ImageProcessor.prepare_image(path)
        self.canvas.create_image(0, 0, anchor='nw', image=new_img)
        self.img = new_img

    def show_about(self):
        print("О программе...")
