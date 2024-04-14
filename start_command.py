# start_command.py
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

# Функция для добавления записи в базу данных
def add_to_db(table, id_value):
    if table == "users":
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (id_value,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (id_value,))
            db.commit()
    elif table == "groups":
        cursor.execute("SELECT * FROM groups WHERE group_id = %s", (id_value,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO groups (group_id) VALUES (%s)", (id_value,))
            db.commit()

def start_command(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.send_message(message.chat.id, "Привет! Я бот для управления задачами.")
        
        # Проверка типа чата и добавление записи в соответствующую таблицу
        if message.chat.type == "private":
            add_to_db("users", message.from_user.id)
        else:
            add_to_db("groups", message.chat.id)