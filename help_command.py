# help_command.py
from telebot import TeleBot

def help_command(bot: TeleBot):
    # Команда для помощи и информации о доступных командах
    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.send_message(message.chat.id, "Список команд:\n"
                                      "/start - Начать работу с ботом\n"
                                      "/help - Показать эту справку\n"
                                      "/add - Добавить новую задачу\n"
                                      "/tasks - Получить список всех ваших задач\n"
                                      "/task_info - Получить информацию о конкретной задаче\n"
                                      "/detailed - Редактировать задачу\n"
                                      "/delete - Удалить задачу\n"
                                      "/assign - Назначить задачу пользователю\n"
                                      "/unassign - Отменить назначение задачи\n")