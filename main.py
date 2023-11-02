import telebot
import config

from start_command import start_command
from help_command import help_command
from add_command import add_command
from tasks_command import tasks_command
from task_info_command import task_info_command
from edit_task_command import edit_task_command
from delete_command import delete_command
from assign_command import assign_command
from unassign_command import unassign_command
from add_file_command import add_file_command
from get_task_file_command import get_task_file_command

TOKEN = config.TELEGRAM_TOKEN
bot = telebot.TeleBot(TOKEN)

start_command(bot)
help_command(bot)
add_command(bot)
tasks_command(bot)
task_info_command(bot)
edit_task_command(bot)
delete_command(bot)
assign_command(bot)
unassign_command(bot)
add_file_command(bot)
get_task_file_command(bot)

bot.polling()
