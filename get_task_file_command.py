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

        # Ищем задачу по названию и получаем связанный с ней файл
        cursor.execute("SELECT id, description, file_link FROM tasks WHERE description = %s", (task_name,))
        task = cursor.fetchone()

        if task and task[2]:
            # Если задача и файл найдены, отправляем файл пользователю
            file_link = task[2]
            file_path = os.path.join(FILE_STORAGE_PATH, file_link.split('/')[-1])

            if os.path.exists(file_path):
                bot.send_message(chat_id, f"Задача: {task[1]}")
                with open(file_path, 'rb') as file:
                    bot.send_document(chat_id, file)
            else:
                bot.send_message(chat_id, "Файл не найден на сервере.")
        else:
            bot.send_message(chat_id, "Задача или файл не найден. Попробуйте еще раз.")