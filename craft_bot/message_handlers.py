# -*- coding: utf-8 -*-

from config import Config
from stock import Stock
from recipes import Recipes
import json
from common import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from jinja2 import Environment, PackageLoader, select_autoescape

from odm_classes import *

from message_parser import *

from pprint import *

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
    message_parser = None


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

        MsgHandlers.message_parser = MessageParser()

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
        user_exists = User.objects(username=update.message.from_user.username) is not None

        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('intro.txt').render(),
                        reply_markup=MsgHandlers.get_main_menu_markup(not user_exists))

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
        user_exists = User.objects(username=update.message.from_user.username) is not None

        if user_exists:
            bot.sendMessage(chat_id=update.message.chat_id,
                            parse_mode='Markdown',
                            text=env.get_template('user_profile.txt').render(),
                            reply_markup=MsgHandlers.get_user_menu_markup())
        else:
            MsgHandlers.showUserProfileFirst(bot, update)


    #Handlers for messages from the Game

    @staticmethod
    def handleGeroyRepost(bot, update):
        if update.message.forward_from.username != Config.cw_bot_username:
            return

        geroj_desc = MsgHandlers.message_parser.parseGerojMessage(update.message.text, update.message.date)
        if geroj_desc == {}:
            return

        User.objects(username=update.message.from_user.username).update_one(upsert=True, cw_geroj_info=geroj_desc)

        update.message.reply_text("Вы зарегистрировали ваш профиль!")
        MsgHandlers.showUserProfile(bot, update)

    @staticmethod
    def processQuestDescriptor(bot, update, quest_dict):
        if QuestDescriptor.objects(message_id=update.message.forward_from_message_id) is not None:
            update.message.reply_text("Сорян, но именно этот форвард уже есть у нас в базе =(")

        text_id = None
        text = None

        quest_text_doc = QuestText.objects(text=quest_dict['residual_text'])
        if quest_text_doc is None:
            text = quest_dict['residual_text']
        else:
            text_id = quest_text_doc.id

        quest_desc_doc = QuestDescriptor(message_id=update.message.forward_from_message_id,
                        yield_res=quest_dict.get('yield_res'),
                        yield_exp=quest_dict.get('yield_exp'),
                        yield_gold=quest_dict.get('yield_gold'),
                        text=text,
                        text_id=text_id
                        )

        quest_desc_doc.save(force_insert=True)

        if text_id is None:
            update.message.reply_text("")


    @staticmethod
    def handleOtherGameMessages(bot, update):
        print(str(update))
        quest_dict = MsgHandlers.message_parser.parseQuestMessage(update.message.text, update.message.forward_date)
        if quest_dict != {}:
            MsgHandlers.processQuestDescriptor(bot, update, quest_dict)




