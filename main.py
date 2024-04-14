import telebot
import config

from start_command import start_command
from help_command import help_command
from add_command import add_command
from tasks_command import tasks_command
from task_info_command import task_info_command
from delete_command import delete_command
from assign_command import assign_command
from unassign_command import unassign_command
from get_task_file_command import get_task_file_command
from detailed import detailed_edit_command

TOKEN = config.TELEGRAM_TOKEN
bot = telebot.TeleBot(TOKEN)

start_command(bot)
help_command(bot)
add_command(bot)
tasks_command(bot)
task_info_command(bot)
delete_command(bot)
assign_command(bot)
unassign_command(bot)
get_task_file_command(bot)
detailed_edit_command(bot)

bot.polling()