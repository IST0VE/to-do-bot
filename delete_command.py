# delete_command.py
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

def delete_command(bot: TeleBot):
    @bot.message_handler(commands=['delete'])
    def delete_task(message):
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите название задачи, которую хотите удалить:")
        is_group = message.chat.type in ["group", "supergroup"]
        bot.register_next_step_handler(msg, process_task_name_for_deletion, chat_id, is_group)
    
    def process_task_name_for_deletion(message, chat_id, is_group):
        task_name = message.text
        if is_group:
            cursor.execute("DELETE FROM tasks WHERE description = %s AND group_id = %s RETURNING id", (task_name, chat_id))
        else:
            user_id = message.from_user.id
            cursor.execute("DELETE FROM tasks WHERE description = %s AND user_id = %s RETURNING id", (task_name, user_id))
    
        deleted_task_id = cursor.fetchone()
        db.commit()
    
        if deleted_task_id:
            bot.send_message(chat_id, "Задача успешно удалена.")
        else:
            bot.send_message(chat_id, "Задача не найдена. Пожалуйста, попробуйте еще раз.")

    # Обработка нажатия кнопки на инлайн-клавиатуре
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
    def callback_inline(call):
        task_id = call.data.split('_')[1]
        cursor.execute("UPDATE tasks SET status = 'deleted' WHERE id = %s", (task_id,))
        db.commit()
        bot.answer_callback_query(call.id, "Задача удалена")