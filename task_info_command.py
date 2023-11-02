# task_info_command.py
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

def task_info_command(bot: TeleBot):
    # Команда для получения всех задач пользователя
    @bot.message_handler(commands=['task_info'])
    def request_task_info(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи, информацию о которой хотите получить:")
        is_group = message.chat.type in ["group", "supergroup"]
        bot.register_next_step_handler(msg, process_task_info_request, chat_id, is_group)

    def process_task_info_request(message, chat_id, is_group):
        task_name = message.text

        if is_group:
            cursor.execute("SELECT description, status, priority, creation_date, assigned_user_id, file_link FROM tasks WHERE description = %s AND group_id = %s", (task_name, chat_id))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT description, status, priority, creation_date, assigned_user_id, file_link FROM tasks WHERE description = %s AND user_id = %s", (task_name, user_id))
    
        task = cursor.fetchone()

        if task:
            description, status, priority, creation_date, assigned_user_id, file_link = task
            assigned_info = f" | Назначена на: [Пользователь](tg://user?id={assigned_user_id})" if assigned_user_id else ""
            file_info = " | У задачи есть файл" if file_link else " | У задачи нет файлов"
            response = f"{description} | Статус: {status} | Приоритет: {priority} | Дата: {creation_date}{assigned_info}{file_info}"
            bot.send_message(chat_id, response, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")