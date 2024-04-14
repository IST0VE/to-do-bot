# tasks_command.py
from telebot import TeleBot, types

import config
import mysql.connector

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

def create_tasks_keyboard(tasks, page=0):
    keyboard = types.InlineKeyboardMarkup()
    page_size = 7
    start = page * page_size
    end = start + page_size

    for task in tasks[start:end]:
        keyboard.add(types.InlineKeyboardButton(text=task[0], callback_data=f"task_{task[0]}"))

    # Кнопки управления на одной строке
    buttons = []
    if page > 0:
        buttons.append(types.InlineKeyboardButton(text="<< Назад", callback_data=f"page_{page-1}"))
    if end < len(tasks):
        buttons.append(types.InlineKeyboardButton(text="Вперед >>", callback_data=f"page_{page+1}"))
    
    if buttons:
        keyboard.row(*buttons)

    return keyboard


def tasks_command(bot: TeleBot):
    @bot.message_handler(commands=['tasks'])
    def send_tasks(message):
        chat_id = message.chat.id
        is_group = message.chat.type in ["group", "supergroup"]
    
        if is_group:
            cursor.execute("SELECT name FROM tasks WHERE group_id = %s", (chat_id,))
        else:
            user_id = message.from_user.id
            cursor.execute("SELECT name FROM tasks WHERE created_by_user_id = %s", (user_id,))
    
        tasks = cursor.fetchall()
    
        if tasks:
            keyboard = create_tasks_keyboard(tasks)
            bot.send_message(chat_id, "Выберите задачу:", reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "У вас пока нет задач.")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_query(call):
        if call.data.startswith("page_"):
            page = int(call.data.split("_")[1])
            # Повторный запрос к БД для получения задач (можно оптимизировать, чтобы избежать повторных запросов)
            if call.message.chat.type in ["group", "supergroup"]:
                cursor.execute("SELECT name FROM tasks WHERE group_id = %s", (call.message.chat.id,))
            else:
                cursor.execute("SELECT name FROM tasks WHERE created_by_user_id = %s", (call.from_user.id,))
            tasks = cursor.fetchall()

            keyboard = create_tasks_keyboard(tasks, page)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text="Выберите задачу:", reply_markup=keyboard)