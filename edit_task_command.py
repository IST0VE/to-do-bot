# edit_task_command.py
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

def edit_task_command(bot: TeleBot):
    @bot.message_handler(commands=['edit_task'])
    def request_task_edit(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи, которую хотите редактировать:")
        is_group = message.chat.type in ["group", "supergroup"]
        bot.register_next_step_handler(msg, process_task_edit_request, chat_id, is_group)

    def process_task_edit_request(message, chat_id, is_group):
        task_name = message.text

        if is_group:
            cursor.execute("SELECT id FROM tasks WHERE description = %s AND group_id = %s", (task_name, chat_id))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT id FROM tasks WHERE description = %s AND user_id = %s", (task_name, user_id))

        task = cursor.fetchone()

        if task:
            task_id = task[0]
            msg = bot.send_message(chat_id, "Введите новые параметры задачи в формате: Название;Статус;Приоритет")
            bot.register_next_step_handler(msg, update_task_info, task_id)
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")

    def update_task_info(message, task_id):
        try:
            new_description, new_status, new_priority = message.text.split(';')
            cursor.execute("UPDATE tasks SET description = %s, status = %s, priority = %s WHERE id = %s", 
                       (new_description, new_status, new_priority, task_id))
            db.commit()
            bot.send_message(message.chat.id, "Задача успешно обновлена!")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при обновлении задачи: {e}")