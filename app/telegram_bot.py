from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext
from telegram.ext import CommandHandler, MessageHandler, Filters
from config.config import TELEGRAM_TOKEN, API_PRIVAT
from datetime import datetime
import mysql_database
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
"""Uncomment 2 rows below this comment if you need to debug this code and to comment above 4 ones"""
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""Background scheduler will update the database every n minutes"""
scheduler = BackgroundScheduler()
scheduler.add_job(mysql_database.update_database, 'interval', minutes=10)
scheduler.start()


def button(update: Update, context: CallbackContext):
    """Function returns the data of specific inline keyboard button"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Selected option: {}".format(query.data))


def start(update: Update, context: CallbackContext):
    """When '/start' is executed this function returns reply markup keyboard
    with 2 buttons ['New employees preparation'], ['Other functions']"""
    reply_keyboard = [['New employees preparation'], ['Other functions']]
    markup = ReplyKeyboardMarkup(keyboard=reply_keyboard,
                                 resize_keyboard=True,
                                 one_time_keyboard=False)
    context.bot.send_message(chat_id=update.message.chat_id, text='Start', reply_markup=markup)


def get_menu(update, context: CallbackContext):
    """After 'New employees preparation' appears in a text field of
    Telegram the function returns inline keyboard with main menu"""
    keyboard = [[InlineKeyboardButton("New employees", callback_data='/new_employees')],
                [InlineKeyboardButton("All the data \ud83d\udd51", callback_data='/all_the_data')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def get_other_func_menu(update, context: CallbackContext):
    """After 'Other functions' appears in a text field of
    Telegram the function returns inline keyboard with other functions menu"""
    keyboard = [[InlineKeyboardButton("Exchange", callback_data='/exchange')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def get_all_the_data(update: Update, context: CallbackContext):
    """Function gets data from a database and returns it to text field of telegram bot"""
    data = mysql_database.get_data_from_table()
    for el in data:
        date = datetime.strftime(el[0], '%d-%m-%Y')
        context.bot.send_message(chat_id=update.message.chat_id, text=date + '\n' + '\n'.join(el[1:]))


def get_new_users(update: Update, context: CallbackContext):
    """This function figures out current time and also get some
    data from the database and after that return it to Telegram"""
    time_now = datetime.now()
    str_time = time_now.strftime('%Y.%m.%d')
    new_employees = mysql_database.get_date_of_new_employees(str_time)
    for el in new_employees:
        date = datetime.strftime(el[0], '%d-%m-%Y')
        context.bot.send_message(chat_id=update.message.chat_id, text=date + '\n' + '\n'.join(el[1:]))


def get_human_ccy_mask(ccy):
    """Function that convert exchange to human-readable format"""
    # {"ccy":"USD","base_ccy":"UAH","buy":"24.70000","sale":"25.05000"}
    return "{} / {} : {} / {}".format(ccy["ccy"], ccy["base_ccy"], ccy["buy"], ccy["sale"])


def print_exchange(update: Update, context: CallbackContext):
    """Function make a request to PrivatBank API and get some info
    about current exchange"""
    response = requests.get(API_PRIVAT)
    list_ccy = response.json()
    human_ccy = '\n'.join(list(map(get_human_ccy_mask, list_ccy)))
    context.bot.send_message(chat_id=update.message.chat_id, text=human_ccy)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='I don\'t know such a command!)')


def main():
    """Main function"""
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)  # Создаем updater как экземпляр класса Updater

    # Add various events handlers
    start_handler = CommandHandler('start', start)
    menu_handler = MessageHandler(Filters.text(['New employees preparation']), get_menu)
    other_functions_menu_handler = MessageHandler(Filters.text(['Other functions']), get_other_func_menu)
    all_the_data_handler = CommandHandler('all_the_data', get_all_the_data)
    exchange_handler = CommandHandler('exchange', print_exchange)
    new_users_handler = CommandHandler('new_employees', get_new_users)
    unknown_handler = MessageHandler(Filters.command, unknown)

    # Зарегистрируем обработчик в диспетчере который будет сортировать обновления извлеченные в Updater в соответствии
    # с зарегистрированными обработчиками и доставлять их в функцию обратного вызова callback

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(menu_handler)
    updater.dispatcher.add_handler(other_functions_menu_handler)
    updater.dispatcher.add_handler(all_the_data_handler)
    updater.dispatcher.add_handler(exchange_handler)
    updater.dispatcher.add_handler(new_users_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(unknown_handler)
    updater.dispatcher.add_error_handler(error)

    # Start downloading updates from Telegram
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


# Write a code to make our bot to run only from this module
if __name__ == '__main__':
    main()

