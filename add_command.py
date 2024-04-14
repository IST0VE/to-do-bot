# add_command.py
from telebot import TeleBot
import config
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

def add_command(bot: TeleBot):
    @bot.message_handler(commands=['add'])
    def add_task(message):
        chat_id = message.chat.id
        is_group = message.chat.type in ["group", "supergroup"]
        msg = bot.send_message(chat_id, "Введите название задачи:")
        bot.register_next_step_handler(msg, process_task_name, chat_id, is_group)

    def process_task_name(message, chat_id, is_group):
        task_name = message.text
        user_id = message.from_user.id 
        # if not is_group else None
        creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Добавление задачи в базу данных
        if is_group:
            cursor.execute("INSERT INTO tasks (name, creation_date, group_id) VALUES (%s, %s, %s)", (task_name, creation_date, chat_id))
        else:
            cursor.execute("INSERT INTO tasks (name, creation_date, created_by_user_id) VALUES (%s, %s, %s)", (task_name, creation_date, user_id))
        
        db.commit()
        bot.send_message(chat_id, f"Задача '{task_name}' успешно добавлена!")
