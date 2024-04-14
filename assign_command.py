# assign_command.py
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

def assign_command(bot: TeleBot):
    @bot.message_handler(commands=['assign'])
    def assign_task(message):
        chat_id = message.chat.id
        if message.chat.type in ["group", "supergroup"]:
            msg = bot.send_message(chat_id, "Введите название задачи для назначения:")
            bot.register_next_step_handler(msg, process_task_name_for_assignment, chat_id)
        else:
            bot.send_message(chat_id, "Эта команда доступна только в групповых чатах.")

    def process_task_name_for_assignment(message, chat_id):
        task_name = message.text
        cursor.execute("SELECT id FROM tasks WHERE name = %s AND group_id = %s", (task_name, chat_id))
        task = cursor.fetchone()

        if task:
            task_id = task[0]
            msg = bot.send_message(chat_id, "Отправьте сообщение пользователя, которого хотите назначить на задачу:")
            bot.register_next_step_handler(msg, assign_user_to_task, task_id, chat_id)
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")

    def assign_user_to_task(message, task_id, chat_id):
        assigned_user_id = message.from_user.id
        assignment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO task_assignments (task_id, assigned_user_id, assignment_date) VALUES (%s, %s, %s)", (task_id, assigned_user_id, assignment_date))
        db.commit()
        bot.send_message(chat_id, f"Задача с ID {task_id} назначена пользователю с ID {assigned_user_id}.")