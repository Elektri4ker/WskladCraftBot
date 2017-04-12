# -*- coding: utf-8 -*-

from config import Config
from stock import Stock
from recipes import Recipes
import json
from database_proxy import *
from common import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('craft_bot', 'templates'),
    trim_blocks = True,
    lstrip_blocks = True
)

class MsgHandlers:
    recipes = None
    stock = None
    keyboard_markups = None
    recipes_name_to_id_map = None
    inline_keyboards = None


    @staticmethod
    def initialize():
        MsgHandlers.stock = Stock()
        MsgHandlers.recipes = Recipes(Config.recipes_file)

        #map recipe names to some generated ID for ability to make a /craft_ID link
        MsgHandlers.recipes_name_to_id_map = {}
        weapon_list, intermediate_list = MsgHandlers.recipes.list_all()
        all_list = []
        all_list.extend([w[0] for w in weapon_list])
        all_list.extend(intermediate_list)

        MsgHandlers.recipes_name_to_id_map.update({all_list[i]: i for i in range(0, len(all_list))})

        MsgHandlers.keyboard_markups = {
            "main_menu": {
                "keyboard": [[InlineKeyboardButton("Гайды", callback_data="guides")],
                             [InlineKeyboardButton("Крафт", url="telegram.me/RedWingBot")]],
                "resize_keyboard": True
            },

            "craft_menu": {
                "keyboard": [["Расчет стоимости /stock"], ["Список рецептов"], ["Главное меню"]],
                "resize_keyboard": True
            }
        }

        MsgHandlers.inline_keyboards = {
            "main_menu": [[InlineKeyboardButton("Гайды", callback_data="guides")],
                             [InlineKeyboardButton("Крафт", url="telegram.me/RedWingBot")]]
        }

    @staticmethod
    def get_main_menu_markup(user_first):
        keyboard = [["Гайды"], ["Крафт"]]
        if user_first:
            keyboard.append(["Может быть, немножко квестов? =)"])
        else:
            keyboard.append(["Ваш профиль"])

        return {
            "keyboard": keyboard,
            "resize_keyboard": True }


    @staticmethod
    def get_user_menu_markup():
        keyboard = [["Регистрация на конкурс"], ["Помощь"], ["Ваши достижения"]]
        return {
            "keyboard": keyboard,
            "resize_keyboard": True}


    @staticmethod
    def intro(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('intro.txt').render(),
                        reply_markup=MsgHandlers.get_main_menu_markup(True))

    @staticmethod
    def showCraftMenu(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('craft_menu.txt').render())

    @staticmethod
    def showGuidesMenu(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('guides_menu.txt').render())

    @staticmethod
    def showUserProfileFirst(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('user_profile_first.txt').render())

    @staticmethod
    def showUserProfile(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('user_profile.txt').render(),
                        reply_markup=MsgHandlers.get_user_menu_markup())



