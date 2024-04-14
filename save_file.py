import os
import uuid
import config

# Путь к папке, где будут храниться файлы
FILE_STORAGE_PATH = config.FILE_STORAGE_PATH

def save_file(downloaded_file, original_filename):
    # Создаем уникальное имя файла
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Путь для сохранения файла
    file_path = os.path.join(FILE_STORAGE_PATH, unique_filename)

    # Сохраняем файл
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Генерируем ссылку на файл (зависит от вашей конфигурации сервера)
    file_link = f"file://{file_path}"
    
    return file_link