# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, RegexHandler, Filters
import logging
from pymongo import MongoClient

from config import Config
from message_handlers import MsgHandlers
from database_proxy import DataBaseProxy

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    MsgHandlers.initialize()
    DataBaseProxy.setDb(MongoClient('localhost', 27017).test_database)
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(Config.bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", MsgHandlers.intro))
    dp.add_handler(CommandHandler("help", MsgHandlers.intro))
    #main menu
    dp.add_handler(RegexHandler("Крафт", MsgHandlers.showCraftMenu))
    dp.add_handler(RegexHandler("Гайды", MsgHandlers.showGuidesMenu))
    dp.add_handler(RegexHandler("Может быть, немножко квестов\? =\)", MsgHandlers.showUserProfileFirst))
    dp.add_handler(RegexHandler("Ваш профиль", MsgHandlers.showUserProfile))

    #handlers for messages from game
    dp.add_handler(RegexHandler("Битва семи замков", MsgHandlers.handleGeroyRepost))

    #try to parse other messages from the Game
    dp.add_handler(MessageHandler(Filters.all, MsgHandlers.handleOtherGameMessages))

    #craft menu
    # dp.add_handler(RegexHandler("Список рецептов", MsgHandlers.getCraftList))
    # dp.add_handler(RegexHandler("^/craft_.+", MsgHandlers.getCraftRecipes))
    # dp.add_handler(RegexHandler("Расчет стоимости /stock", MsgHandlers.calcCost))
    # dp.add_handler(RegexHandler("Главное меню", MsgHandlers.intro))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text , MsgHandlers.plainMessage))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
