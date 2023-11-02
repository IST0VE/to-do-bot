# assign_command.py
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

def assign_command(bot: TeleBot):
    @bot.message_handler(commands=['assign'])
    def assign_task(message):
        chat_id = message.chat.id
        if message.chat.type in ["group", "supergroup"]:
            msg = bot.send_message(chat_id, "Отправьте сообщение пользователя, которого хотите назначить на задачу:")
            bot.register_next_step_handler(msg, process_user_for_assignment, chat_id)
        else:
            bot.send_message(chat_id, "Эта команда доступна только в групповых чатах.")

    def process_user_for_assignment(message, chat_id):
        assigned_user_id = message.from_user.id
        msg = bot.send_message(chat_id, "Введите название задачи для назначения:")
        bot.register_next_step_handler(msg, assign_user_to_task, assigned_user_id, chat_id)

    def assign_user_to_task(message, assigned_user_id, chat_id):
        task_name = message.text
        cursor.execute("UPDATE tasks SET assigned_user_id = %s WHERE description = %s AND group_id = %s", (assigned_user_id, task_name, chat_id))
        db.commit()
        bot.send_message(chat_id, f"Задача '{task_name}' назначена пользователю с ID {assigned_user_id}.")