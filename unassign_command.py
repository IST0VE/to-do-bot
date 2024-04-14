# unassign_command.py
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

def unassign_command(bot: TeleBot):
    @bot.message_handler(commands=['unassign'])
    def request_task_unassign(message):
        chat_id = message.chat.id
        if message.chat.type in ["group", "supergroup"]:
            msg = bot.send_message(chat_id, "Введите название задачи, от назначения которой хотите отказаться:")
            bot.register_next_step_handler(msg, process_task_unassign_request, chat_id, True)
        else:
            bot.send_message(chat_id, "Эта команда доступна только в групповых чатах.")

    def process_task_unassign_request(message, chat_id, is_group):
        task_name = message.text

        if is_group:
            cursor.execute("SELECT id FROM tasks WHERE name = %s AND group_id = %s", (task_name, chat_id))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT id FROM tasks WHERE name = %s AND created_by_user_id = %s", (task_name, user_id))

        task = cursor.fetchone()

        if task:
            task_id = task[0]
            # Удаляем запись о назначении задачи из таблицы task_assignments
            cursor.execute("DELETE FROM task_assignments WHERE task_id = %s", (task_id,))
            db.commit()
            bot.send_message(chat_id, "Назначение задачи успешно отменено.")
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")