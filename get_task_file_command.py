# get_task_file_command.py
from telebot import TeleBot
import config
import os
import mysql.connector

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

FILE_STORAGE_PATH = config.FILE_STORAGE_PATH

def get_task_file_command(bot: TeleBot):
    @bot.message_handler(commands=['get_task_file'])
    def request_task_name_for_file(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи для получения файла:")
        bot.register_next_step_handler(msg, send_file_for_task)

    def send_file_for_task(message):
        chat_id = message.chat.id
        task_name = message.text
        user_id = message.from_user.id

        # Ищем задачу по названию и получаем связанный с ней файл
        cursor.execute("SELECT t.id, t.name FROM tasks t WHERE t.name = %s and t.created_by_user_id = %s", (task_name, user_id))
        task = cursor.fetchone()

        if task:
            task_id = task[0]
            cursor.execute("SELECT file_link FROM task_files WHERE task_id = %s", (task_id,))
            files = cursor.fetchall()

            if files:
                bot.send_message(chat_id, f"Файлы для задачи '{task_name}':")
                for file_link in files:
                    file_path = os.path.join(FILE_STORAGE_PATH, file_link[0].split('/')[-1])
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            bot.send_document(chat_id, file)
                    else:
                        bot.send_message(chat_id, f"Файл '{file_link[0]}' не найден на сервере.")
            else:
                bot.send_message(chat_id, "У задачи нет прикрепленных файлов.")
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")