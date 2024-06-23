import cv2
from PIL import Image, ImageTk


class ImageProcessor:
    @staticmethod
    def ahash(image_path):
        # Загрузка изображения
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        # Уменьшение размера изображения до 8x8 пикселей
        resized_image = cv2.resize(image, (8, 8))

        # Вычисление среднего значения яркости пикселей
        mean_brightness = resized_image.mean()

        # Создание хэша
        hash_value = ''
        for row in resized_image:
            for pixel in row:
                hash_value += '1' if pixel >= mean_brightness else '0'

        return hash_value

    @staticmethod
    def compare_images(hash1, hash2):
        similarity = 0
        for bit1, bit2 in zip(hash1, hash2):
            if bit1 == bit2:
                similarity += 1

        return round(similarity / len(hash1) * 100, 2)

    @staticmethod
    def prepare_table_data(list, index):
        out = []
        ahash = list[index]['aHash']
        for i, item in enumerate(list):
            if i != index:
                similarity = ImageProcessor.compare_images(ahash, item['aHash'])
                out.append([item['name'], similarity])

        return sorted(out, key=lambda x: x[1], reverse=True)

    @staticmethod
    def prepare_image(path):
        image = Image.open(path)
        image = image.resize(size=(500, 500))
        image = ImageTk.PhotoImage(image)

        return image
