# tasks_command.py
from telebot import TeleBot
import config
import mysql.connector

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

def tasks_command(bot: TeleBot):
    # Команда для получения списка задач
    @bot.message_handler(commands=['tasks'])
    def send_tasks(message):
        chat_id = message.chat.id
        is_group = message.chat.type in ["group", "supergroup"]
    
        if is_group:
            cursor.execute("SELECT description, status, priority FROM tasks WHERE group_id = %s", (chat_id,))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT description, status, priority FROM tasks WHERE user_id = %s", (user_id,))
    
        tasks = cursor.fetchall()
    
        if tasks:  # Проверяем, есть ли задачи
            response = "\n".join([f"{description} | Статус: {status} | Приоритет: {priority}" for description, status, priority in tasks])
            bot.send_message(chat_id, response)
        else:  # Если задач нет, отправляем сообщение об этом
            bot.send_message(chat_id, "У вас пока нет задач.")