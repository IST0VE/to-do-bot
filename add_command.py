# add_command.py
from telebot import types
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

temp_task_description = {}

def add_command(bot: TeleBot):
    # Инлайн клавиатуры для выбора статуса и приоритета
    status_markup = types.InlineKeyboardMarkup(row_width=2)
    status_markup.add(types.InlineKeyboardButton("Активная", callback_data="status_активная"),
                  types.InlineKeyboardButton("Завершенная", callback_data="status_завершенная"),
                  types.InlineKeyboardButton("Не указывать", callback_data="status_none"))

    priority_markup = types.InlineKeyboardMarkup(row_width=3)
    priority_markup.add(types.InlineKeyboardButton("Высокий", callback_data="priority_высокий"),
                    types.InlineKeyboardButton("Средний", callback_data="priority_средний"),
                    types.InlineKeyboardButton("Низкий", callback_data="priority_низкий"),
                    types.InlineKeyboardButton("Не указывать", callback_data="priority_none"))

    @bot.message_handler(commands=['add'])
    def add_task(message):
        chat_id = message.chat.id
        is_group = message.chat.type in ["group", "supergroup"]

        msg = bot.send_message(chat_id, "Введите описание задачи:")
        bot.register_next_step_handler(msg, process_task_description, chat_id, is_group)
    
    # Обработка описания задачи
    def process_task_description(message, chat_id, is_group):
        description = message.text
        user_id = message.from_user.id if not is_group else None
        temp_task_description[chat_id] = {"user_id": user_id, "description": description, "is_group": is_group}
        bot.send_message(chat_id, "Выберите статус задачи:", reply_markup=status_markup)
    
    # Обработка выбора статуса
    @bot.callback_query_handler(func=lambda call: call.data.startswith('status_'))
    def callback_status(call):
        chat_id = call.message.chat.id
        task_info = temp_task_description.get(chat_id, {})
        if task_info.get("user_id") == call.from_user.id or task_info.get("is_group"):
            status = call.data.split('_')[1]
            task_info["status"] = status
            bot.send_message(chat_id, "Выберите приоритет задачи:", reply_markup=priority_markup)
        bot.answer_callback_query(call.id)
    
    # Обработка выбора приоритета
    @bot.callback_query_handler(func=lambda call: call.data.startswith('priority_'))
    def callback_priority(call):
        chat_id = call.message.chat.id
        task_info = temp_task_description.pop(chat_id, None)

        if task_info and (task_info.get("user_id") == call.from_user.id or task_info.get("is_group")):
            user_id = task_info.get("user_id")
            description = task_info.get("description")
            status = task_info.get("status")
            priority = call.data.split('_')[1]

            if task_info.get("is_group"):
                cursor.execute("INSERT INTO tasks (group_id, description, status, priority) VALUES (%s, %s, %s, %s)",
                           (chat_id, description, status, priority))
            else:
                cursor.execute("INSERT INTO tasks (user_id, description, status, priority) VALUES (%s, %s, %s, %s)",
                           (user_id, description, status, priority))

            db.commit()
            bot.send_message(chat_id, f"Задача добавлена с статусом {status} и приоритетом {priority}!")
        bot.answer_callback_query(call.id)