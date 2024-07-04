import unittest
from test_task.ImageProcessor import ImageProcessor  # Замените на путь к вашему модулю

class TestImageProcessor(unittest.TestCase):
    def test_ahash(self):
        # Проверяем, что метод ahash возвращает ожидаемый хеш
        image_path = 'test_images/test_image2.jpg'  # Путь к тестовому изображению
        expected_hash = '1011000000111000011110000011110000111100001110000001100000001010'  # ожидаемый хэш
        actual_hash = ImageProcessor.ahash(image_path)  # Получение хэша тестового изображение
        self.assertEqual(actual_hash, expected_hash)  # Сравнение ожидаемого и полученного хэшей

    def test_compare_images(self):
        # Проверяем, что метод compare_images возвращает ожидаемый процент схожести
        hash1 = '0101010101010101'
        hash2 = '0101010101010000'
        expected_similarity = 87.5
        actual_similarity = ImageProcessor.compare_images(hash1, hash2)
        self.assertEqual(actual_similarity, expected_similarity)

    def test_prepare_table_data(self):
        # Проверяем, что метод prepare_table_data возвращает ожидаемые данные
        image_list = [{'name': 'image1', 'aHash': '0101010101010101'},
                      {'name': 'image2', 'aHash': '0101010101010000'}]  # тестовый словарь с изображениями
        index = 0  # Выбрано первое изображение
        expected_data = [['image2', 87.5]]  # Ожидаемый результат
        actual_data = ImageProcessor.prepare_table_data(image_list, index)  # Получение результата
        self.assertEqual(actual_data, expected_data)  # Сравнение


if __name__ == '__main__':
    unittest.main()
