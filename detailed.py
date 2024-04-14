from telebot import types, TeleBot
import config
import mysql.connector
from save_file import save_file
from datetime import datetime

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)

cursor = db.cursor()
temp_task_edit = {}

def detailed_edit_command(bot: TeleBot):
    @bot.message_handler(commands=['detailed'])
    def start_detailed_edit(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи для редактирования:")
        bot.register_next_step_handler(msg, select_field_for_edit)

    def select_field_for_edit(message):
        task_name = message.text
        chat_id = message.chat.id
        user_id = message.from_user.id
        is_group = message.chat.type in ["group", "supergroup"]
        
        if is_group:
            cursor.execute("SELECT id FROM tasks WHERE name = %s AND group_id = %s", (task_name, chat_id))
        else:
            cursor.execute("SELECT id FROM tasks WHERE name = %s AND created_by_user_id = %s", (task_name, user_id))
        task = cursor.fetchone()
        if task:
            temp_task_edit[chat_id] = {"task_id": task[0], "task_name": task_name}
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Статус", callback_data="edit_status"))
            markup.add(types.InlineKeyboardButton("Приоритет", callback_data="edit_priority"))
            markup.add(types.InlineKeyboardButton("Описание", callback_data="edit_description"))
            markup.add(types.InlineKeyboardButton("Процент выполнения", callback_data="edit_completion"))
            markup.add(types.InlineKeyboardButton("Добавить файл", callback_data="edit_file"))
            markup.add(types.InlineKeyboardButton("Дата начала", callback_data="begin_dates"))
            markup.add(types.InlineKeyboardButton("Дата окончания", callback_data="end_dates"))
            bot.send_message(chat_id, "Выберите, что хотите редактировать:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "Задача не найдена.")
            
    @bot.callback_query_handler(func=lambda call: call.data == "edit_status")
    def handle_edit_status(call):
        chat_id = call.message.chat.id
        status_markup = types.InlineKeyboardMarkup()
        status_markup.add(
            types.InlineKeyboardButton("Активная", callback_data="set_status_Активная"),
            types.InlineKeyboardButton("Завершенная", callback_data="set_status_Завершенная"),
            types.InlineKeyboardButton("В ожидании", callback_data="set_status_В ожидании")
        )
        bot.send_message(chat_id, "Выберите новый статус задачи:", reply_markup=status_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_status_"))
    def set_status(call):
        chat_id = call.message.chat.id
        task_info = temp_task_edit.get(chat_id, {})
        new_status = call.data.split("_")[2]

        if task_info:
            task_id = task_info.get("task_id")
            cursor.execute("SELECT * FROM task_descriptions WHERE task_id = %s", (task_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO task_descriptions (task_id, status) VALUES (%s, %s)", (task_id, new_status))
        else:
            cursor.execute("UPDATE task_descriptions SET status = %s WHERE task_id = %s", (new_status, task_id))
        db.commit()
        bot.send_message(chat_id, f"Статус задачи обновлен на {new_status}.")

    @bot.callback_query_handler(func=lambda call: call.data == "edit_priority")
    def handle_edit_priority(call):
        chat_id = call.message.chat.id
        priority_markup = types.InlineKeyboardMarkup()
        priority_markup.add(
            types.InlineKeyboardButton("Высокий", callback_data="set_priority_Высокий"),
            types.InlineKeyboardButton("Средний", callback_data="set_priority_Средний"),
            types.InlineKeyboardButton("Низкий", callback_data="set_priority_Низкий")
        )
        bot.send_message(chat_id, "Выберите новый приоритет задачи:", reply_markup=priority_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_priority_"))
    def set_priority(call):
        chat_id = call.message.chat.id
        task_info = temp_task_edit.get(chat_id, {})
        new_priority = call.data.split("_")[2]

        if task_info:
            task_id = task_info.get("task_id")
            cursor.execute("SELECT * FROM task_descriptions WHERE task_id = %s", (task_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO task_descriptions (task_id, priority) VALUES (%s, %s)", (task_id, new_priority))
        else:
            cursor.execute("UPDATE task_descriptions SET priority = %s WHERE task_id = %s", (new_priority, task_id))
        db.commit()
        bot.send_message(chat_id, f"Приоритет задачи обновлен на {new_priority}.")

    @bot.callback_query_handler(func=lambda call: call.data == "edit_description")
    def handle_edit_description(call):
        chat_id = call.message.chat.id
        msg = bot.send_message(chat_id, "Введите новое длинное описание задачи:")
        bot.register_next_step_handler(msg, set_description)

    def set_description(message):
        chat_id = message.chat.id
        task_info = temp_task_edit.get(chat_id, {})
        new_description = message.text
        task_id = temp_task_edit[chat_id].get("task_id")

        if task_info:
            task_id = task_info.get("task_id")
            cursor.execute("SELECT * FROM task_descriptions WHERE task_id = %s", (task_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO task_descriptions (task_id, long_description) VALUES (%s, %s)", (task_id, new_description))
        else:
            cursor.execute("UPDATE task_descriptions SET long_description = %s WHERE task_id = %s", (new_description, task_id))
        db.commit()
        bot.send_message(chat_id, "Описание задачи обновлено.")
    
    @bot.callback_query_handler(func=lambda call: call.data == "edit_completion")
    def handle_edit_completion(call):
        chat_id = call.message.chat.id
        completion_markup = types.InlineKeyboardMarkup()
        completion_markup.add(
            types.InlineKeyboardButton("0%", callback_data="set_completion_0"),
            types.InlineKeyboardButton("25%", callback_data="set_completion_25"),
            types.InlineKeyboardButton("50%", callback_data="set_completion_50"),
            types.InlineKeyboardButton("75%", callback_data="set_completion_75"),
            types.InlineKeyboardButton("100%", callback_data="set_completion_100")
        )
        bot.send_message(chat_id, "Выберите процент выполнения задачи:", reply_markup=completion_markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set_completion_"))
    def set_completion(call):
        chat_id = call.message.chat.id
        task_info = temp_task_edit.get(chat_id, {})
        new_completion = int(call.data.split("_")[2])

        if task_info:
            task_id = task_info.get("task_id")
            cursor.execute("SELECT * FROM task_descriptions WHERE task_id = %s", (task_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO task_descriptions (task_id, completion) VALUES (%s, %s)", (task_id, new_completion))
            else:
                cursor.execute("UPDATE task_descriptions SET completion = %s WHERE task_id = %s", (new_completion, task_id))
        db.commit()
        bot.send_message(chat_id, f"Завершенность задачи обновлена на {new_completion}%.")
        
    @bot.callback_query_handler(func=lambda call: call.data == "edit_file")
    def handle_edit_file(call):
        chat_id = call.message.chat.id
        task_info = temp_task_edit.get(chat_id, {})
        task_id = task_info.get("task_id")

        if task_id:
            msg = bot.send_message(chat_id, "Пожалуйста, прикрепите файл (не более 5 МБ):")
            bot.register_next_step_handler(msg, process_file_upload, task_id)
        else:
            bot.send_message(chat_id, "Произошла ошибка. Попробуйте начать редактирование задачи заново.")

    def process_file_upload(message, task_id):
        if message.content_type == 'document':
            if message.document.file_size <= 5 * 1024 * 1024:  # Проверка на размер файла в байтах
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
        
                file_link = save_file(downloaded_file, message.document.file_name)
        
                cursor.execute("INSERT INTO task_files (task_id, file_link) VALUES (%s, %s)", (task_id, file_link))
        
                db.commit()
                bot.send_message(message.chat.id, "Файл успешно добавлен к задаче.")
            else:
                bot.send_message(message.chat.id, "Файл не должен превышать 5 МБ.")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, прикрепите файл.")
            
            
    @bot.callback_query_handler(func=lambda call: call.data == "begin_dates")
    def handle_begin_dates(call):
        chat_id = call.message.chat.id
        msg = bot.send_message(chat_id, "Введите новую дату начала задачи (формат ГГГГ-ММ-ДД ЧЧ:ММ:СС).")
        bot.register_next_step_handler(msg, set_begin_date)

    def set_begin_date(message):
        chat_id = message.chat.id
        try:
            start_date = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
            task_id = temp_task_edit[chat_id].get("task_id")

            # Проверяем, существует ли запись
            cursor.execute("SELECT * FROM task_dates WHERE task_id = %s", (task_id,))
            if cursor.fetchone() is None:
            # Если записи нет, создаем ее
                cursor.execute("INSERT INTO task_dates (task_id, start_date) VALUES (%s, %s)", (task_id, start_date))
            else:
            # Если запись есть, обновляем ее
                cursor.execute("UPDATE task_dates SET start_date = %s WHERE task_id = %s", (start_date, task_id))

            db.commit()
            bot.send_message(chat_id, "Дата начала задачи обновлена.")
        except ValueError:
            bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД ЧЧ:ММ:СС.")

    @bot.callback_query_handler(func=lambda call: call.data == "end_dates")
    def handle_end_dates(call):
        chat_id = call.message.chat.id
        msg = bot.send_message(chat_id, "Введите новую дату окончания задачи (формат ГГГГ-ММ-ДД ЧЧ:ММ:СС).")
        bot.register_next_step_handler(msg, set_end_date)

    def set_end_date(message):
        chat_id = message.chat.id
        try:
            end_date = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
            task_id = temp_task_edit[chat_id].get("task_id")

            # Проверяем, существует ли запись
            cursor.execute("SELECT * FROM task_dates WHERE task_id = %s", (task_id,))
            if cursor.fetchone() is None:
            # Если записи нет, создаем ее
                cursor.execute("INSERT INTO task_dates (task_id, end_date) VALUES (%s, %s)", (task_id, end_date))
            else:
            # Если запись есть, обновляем ее
                cursor.execute("UPDATE task_dates SET end_date = %s WHERE task_id = %s", (end_date, task_id))

            db.commit()
            bot.send_message(chat_id, "Дата окончания задачи обновлена.")
        except ValueError:
            bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД ЧЧ:ММ:СС.")
        
