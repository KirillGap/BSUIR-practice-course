import os
import tkinter as tk
import threading
import asyncio
from tkinter import Menu
from tkinter import filedialog
from tkinter import messagebox
from tksheet import Sheet

from ImageProcessor import ImageProcessor


class Application:
    def __init__(self, master=None):
        """
                Инициализация приложения.

                Args:
                    master: Главное окно приложения.
        """

        self.list_of_images = list()
        self.toplevel = None
        self.toplevel_sheet = None
        self.image_label = None
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
        """
            Открывает диалоговое окно для выбора рабочей директории.
        """
        try:
            filename = filedialog.askdirectory() # диалоговое окно для выбора рабочей директории
            if filename:
                thread1 = threading.Thread(target=self.read_dir,
                                           args=(filename,))
                thread2 = threading.Thread(target=messagebox.showinfo,
                                           args=("Загрузка", "Ваши изображения загружаются"))
                thread1.start()
                thread2.start()
            else:
                raise ValueError("Выберите директорию")
        except Exception as e:
            messagebox.showerror('Ошибка', f'{e}')

    def read_dir(self, dir_name):
        """
        Считывает изображения из указанной директории.

        Args:
            dir_name: Путь к директории с изображениями.
        """

        def reading(dir_name, start_index):
            for filename in os.listdir(dir_name)[start_index::5]:
                if filename[-4:] == '.jpg':
                    path = dir_name + f'/{filename}'
                    self.list_of_images.append({
                        'name': filename,
                        'path': path,
                        'aHash': ImageProcessor.ahash(path),
                    })
                else:
                    self.unexpected_type_filenames.append(filename)

        self.unexpected_type_filenames = []
        try:
            if self.list_of_images:
                self.list_of_images.clear()  # очистка предыдущей таблицы

            threads = [threading.Thread(target=reading, args=(dir_name, interval)) for interval in range(5)]
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            if self.unexpected_type_filenames:
                raise TypeError(f'Неподдерживаемый тип файла в директории:\n {self.unexpected_type_filenames}')
        except Exception as e:
            error_message = "Неподдерживаемый тип файла в директории:\n"
            error_message += "\n".join(self.unexpected_type_filenames)
            messagebox.showerror('Ошибка', error_message)

        self.update_data()


    def update_data(self):
        """
                Обновляет данные в таблице.
        """
        self.sheet.clear()
        data = self.get_data()  # сбор данных в один массив
        self.sheet.set_data(data=data)

    def get_data(self):
        """
                Возвращает данные для отображения в таблице.

                Returns:
                    list: Список данных для таблицы.
                """
        out = []
        for row in self.list_of_images:
            new_row = [row[key] for key in row.keys()]
            out.append(new_row)
        return out

    def create_image_label(self, parent, height, width, image):
        """
        Создает и возвращает объект Canvas.

        Args:
            parent: Родительский виджет (например, окно или фрейм).
            height: Высота Canvas.
            width: Ширина Canvas.

        Returns:
            tk.Canvas: Объект Canvas.
        """
        image_label = tk.Canvas(parent, height=height, width=width)  # инициализация пространства для изображения
        image_label.create_image(0, 0, anchor='nw', image=image)  # загрузка изображения
        return image_label

    def on_cell_click(self, event):
        """
                Обработчик события клика по ячейке таблицы.

                Args:
                    event: Событие клика.
                """
        row = event['selected'].row
        path = self.sheet.get_cell_data(row, 1)  # получение пути к выбранному изображению

        toplevel = tk.Toplevel(self.master)  # Создание нового окна
        self.toplevel = toplevel

        img = ImageProcessor.prepare_image(path)  # получение изображения по пути
        original_image = self.create_image_label(self.toplevel, 500, 500, img)  # создание лэйбла и загрузка изображения
        original_image.grid(row=0, column=0, padx=1)

        toplevel_sheet = Sheet(
            parent=toplevel,
            width=400,
            show_row_index=False,
            show_x_scrollbar=False
        )   # инициализация таблицы
        self.toplevel_sheet = toplevel_sheet
        toplevel_sheet.set_column_widths([200, 100])
        toplevel_sheet.enable_bindings('single_select')
        toplevel_sheet.extra_bindings('cell_select', self.on_cell_select)
        toplevel_sheet.headers(['name', 'similarity, %'])
        toplevel_sheet.grid(row=0, column=1, padx=1)  # Создание таблицы

        data = ImageProcessor.prepare_table_data(
            list=self.list_of_images,
            index=row
        )
        toplevel_sheet.set_data(data=data)  # Заполнение таблицы

        # Создание пустого лейбла для просмотра изображений из таблицы
        target_image = self.create_image_label(self.toplevel, 500, 500, image=None)

        self.image_label = target_image
        target_image.grid(row=0, column=2)

        toplevel.mainloop()

    def on_cell_select(self, event):
        """
                Обработчик события выбора ячейки во второй таблице.

                Args:
                    event: Событие выбора ячейки.
                """
        # получение имени интересующего изображения
        row = event['selected'].row
        filename = self.toplevel_sheet.get_cell_data(row, 0)

        # получение индекса изображения в основной таблице
        index = [item['name'] for item in self.list_of_images].index(filename)
        path = self.list_of_images[index]['path']

        # Загрузка и отображение выбранного изображения
        new_img = ImageProcessor.prepare_image(path)
        self.image_label.create_image(0, 0, anchor='nw', image=new_img)
        self.image = new_img
