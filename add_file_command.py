# add_file_command.py
from telebot import TeleBot
import config
import mysql.connector
from save_file import save_file

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

def add_file_command(bot: TeleBot):
    @bot.message_handler(commands=['add_file'])
    def add_file(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи, к которой хотите прикрепить файл:")
        is_group = message.chat.type in ["group", "supergroup"]
        bot.register_next_step_handler(msg, process_task_name_for_file, chat_id, is_group)

    def process_task_name_for_file(message, chat_id, is_group):
        task_name = message.text
        if is_group:
            cursor.execute("SELECT id FROM tasks WHERE description = %s AND group_id = %s", (task_name, chat_id))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT id FROM tasks WHERE description = %s AND user_id = %s", (task_name, user_id))
    
        task = cursor.fetchone()
    
        if task:
            task_id = task[0]
            msg = bot.send_message(chat_id, "Пожалуйста, прикрепите файл (не более 5 МБ):")
            bot.register_next_step_handler(msg, process_file_upload, task_id)
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")

    def process_file_upload(message, task_id):
        if message.content_type == 'document':
            if message.document.file_size <= 6 * 1024 * 1024:  # Проверка на размер файла в байтах
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
            
                file_link = save_file(downloaded_file, message.document.file_name)
            
                cursor.fetchall()  # Очищаем невостребованные результаты
                cursor.execute("UPDATE tasks SET file_link = %s WHERE id = %s", (file_link, task_id))
            
                db.commit()
                bot.send_message(message.chat.id, "Файл успешно добавлен к задаче.")
            else:
                bot.send_message(message.chat.id, "Файл не должен превышать 5 МБ.")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, прикрепите файл.")