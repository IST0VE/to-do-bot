# task_info_command.py
from telebot import TeleBot
import config
import mysql.connector
import os

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()

FILE_STORAGE_PATH = config.FILE_STORAGE_PATH

def task_info_command(bot: TeleBot):
    @bot.message_handler(commands=['task_info'])
    def request_task_info(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи, информацию о которой хотите получить:")
        is_group = message.chat.type in ["group", "supergroup"]
        bot.register_next_step_handler(msg, process_task_info_request, chat_id, is_group)

    def process_task_info_request(message, chat_id, is_group):
        task_name = message.text
        user_id = message.from_user.id

        # Формируем запрос
        query = """SELECT t.id, t.name, td.status, td.priority, td.completion, t.creation_date, td.long_description,
                          td2.start_date, td2.end_date, GROUP_CONCAT(tf.file_link SEPARATOR ', '),
                          GROUP_CONCAT(ta.assigned_user_id SEPARATOR ', ') as assigned_user_ids
                   FROM tasks t 
                   LEFT JOIN task_descriptions td ON t.id = td.task_id
                   LEFT JOIN task_dates td2 ON t.id = td2.task_id
                   LEFT JOIN task_files tf ON t.id = tf.task_id
                   LEFT JOIN task_assignments ta ON t.id = ta.task_id
                   WHERE t.name = %s AND (t.created_by_user_id = %s OR ta.assigned_user_id = %s)
                   GROUP BY t.id"""
        
        cursor.execute(query, (task_name, user_id, user_id))
        task = cursor.fetchone()
                   
        if task:
            task_id, name, status, priority, completion, creation_date, long_description, start_date, end_date, file_links, assigned_user_id = task
            dates_info = f"Дата начала: {start_date}, Дата окончания: {end_date}" if start_date and end_date else "Даты не заданы"
            assigned_info = f"Назначена на пользователей с ID: {assigned_user_id}" if assigned_user_id else "Назначение отсутствует"
            response = (f"Имя: {name}\nСтатус: {status}\nПриоритет: {priority}\nПроцент выполнения: {completion}%\n"
                        f"Дата создания: {creation_date}\n{dates_info}\nОписание: {long_description}\n{assigned_info}")
            
            bot.send_message(chat_id, response, parse_mode='Markdown')

            # Отправка файлов
            cursor.execute("SELECT file_link FROM task_files WHERE task_id = %s", (task_id,))
            files = cursor.fetchall()
            if files:
                bot.send_message(chat_id, "Файлы задачи:")
                for file_link in files:
                    file_path = os.path.join(FILE_STORAGE_PATH, file_link[0].split('/')[-1])
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            bot.send_document(chat_id, file)
                    else:
                        bot.send_message(chat_id, f"Файл '{file_link[0]}' не найден на сервере.")
            else:
                bot.send_message(chat_id, "У задачи нет прикрепленных файлов.")
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")
        # cursor.execute(query, (task_name,))
        # task = cursor.fetchone()

        # if task:
        #     task_id, name, status, priority, creation_date, long_description, start_date, end_date, file_links = task
        #     file_info = "Файлы: " + file_links if file_links else "Нет файлов"
        #     dates_info = f"Дата начала: {start_date}, Дата окончания: {end_date}" if start_date and end_date else "Даты не заданы"

        #     response = f"Имя: {name}\nСтатус: {status}\nПриоритет: {priority}\nДата создания: {creation_date}\n{dates_info}\nОписание: {long_description}\n{file_info}"
        #     bot.send_message(chat_id, response, parse_mode='Markdown')
        # else:
        #     bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")
        # Дополнение запроса в зависимости от типа чата
        # if is_group:
        #     cursor.execute(base_query + " AND t.group_id = %s GROUP BY t.id", (task_name, chat_id))
        # else:
        #     user_id = message.from_user.id
        #     cursor.execute(base_query + " AND t.created_by_user_id = %s GROUP BY t.id", (task_name, user_id))

        # task = cursor.fetchone()

        # if task:
        #     task_id, name, status, priority, creation_date, long_description, start_date, end_date, file_links = task
        #     file_info = "Файлы: " + file_links if file_links else "Нет файлов"
        #     dates_info = f"Дата начала: {start_date}, Дата окончания: {end_date}" if start_date and end_date else "Даты не заданы"

        #     response = f"Имя: {name}\nСтатус: {status}\nПриоритет: {priority}\nДата создания: {creation_date}\n{dates_info}\nОписание: {long_description}\n{file_info}"
        #     bot.send_message(chat_id, response, parse_mode='Markdown')
        # else:
        #     bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")
