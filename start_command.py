# start_command.py
from telebot import TeleBot

def start_command(bot: TeleBot):
    # Команда для приветствия и инструкций по использованию бота
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.send_message(message.chat.id, "Привет! Я бот для управления задачами.")