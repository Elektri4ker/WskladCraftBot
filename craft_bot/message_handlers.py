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
        user_exists = len(User.objects(username=update.message.from_user.username)) > 0

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

        User.objects(username=update.message.from_user.username, tg_user_id=update.message.from_user.id).update_one(upsert=True, cw_geroj_info=geroj_desc)

        update.message.reply_text("Вы зарегистрировали ваш профиль!")
        MsgHandlers.showUserProfile(bot, update)

    @staticmethod
    def processQuestDescriptor(bot, update, quest_dict):

        text_id = None
        text = None

        #connect quest to text id or write text inplace, if no such text in the database
        quest_text_doc = QuestText.objects(text=quest_dict['residual_text']).first()
        if not quest_text_doc:
            text = quest_dict['residual_text']
        else:
            text_id = quest_text_doc

        #creating new quest in the db
        quest_desc_doc = QuestDescriptor(timestamp=update.message.forward_date,
                        yield_res=quest_dict.get('yield_res'),
                        yield_exp=quest_dict.get('yield_exp'),
                        yield_gold=quest_dict.get('yield_gold'),
                        text=text,
                        text_id=text_id
                        )

        #validating for uniquity
        if quest_desc_doc.find_the_same():
            update.message.reply_text("Сорян, но именно этот форвард уже есть у нас в базе =(")
            return

        #selecting user from the db
        user_doc = User.objects(tg_user_id=update.message.from_user.id).first()
        if not user_doc:
            update.message.reply_text("Вы еще не зарегистрировались")
            return

        quest_desc_doc.save(force_insert=True)

        #tieing up quest descriptor with the user.
        if text_id is None:
            user_doc.found_new_text_quest_ids.append(quest_desc_doc)
            user_doc.save()
            bot.sendMessage(chat_id=update.message.chat_id,
                            parse_mode='Markdown',
                            text=env.get_template('new_quest_message.txt').render())
        else:
            user_doc.quest_ids.append(quest_desc_doc)
            update.message.reply_text("Сообщение учтено.")

    @staticmethod
    def processQuestTypeMessage(bot, update):
        type = MsgHandlers.message_parser.parseQuestTypeMessage(update.message.text)
        timestamp = update.message.forward_date
        if not type:
            return False

        # selecting user from the db
        user_doc = User.objects(tg_user_id=update.message.from_user.id).first()
        if not user_doc:
            update.message.reply_text("Вы еще не зарегистрировались")
            return False

        # find quest message 5 minutes earlier.
        quest_docs = user_doc.found_new_text_quest_ids
        found_doc = None
        for doc in quest_docs:
            delta_ts = doc.timestamp - timestamp
            if delta_ts.seconds >= 4*60+30 and delta_ts.seconds <= 5*60+30 and not doc.text_id:
                found_doc = doc
                break

        if not found_doc:
            update.message.reply_text('На ваш форвард не нашлось подходящего сообщения...')
        else:
            if found_doc.text_id:
                update.message.reply_text(f'На ваш форвард не нашлось подходящего сообщения.')
            else:
                text_doc = QuestText(type=type, text=found_doc.text)
                text_doc.save()
                found_doc.text = None
                found_doc.text_id = text_doc
                found_doc.save()

                update.message.reply_text(f'Спасибо! Вы нашли новый текст:\n\n{text_doc.text}\n\nВы подтвердили его, это сообщение из {text_doc.type}')

        return True





    @staticmethod
    def handleOtherGameMessages(bot, update):
        if update.message.forward_from.username != Config.cw_bot_username:
            return
        print(str(update))

        if MsgHandlers.processQuestTypeMessage(bot, update):
            return

        quest_dict = MsgHandlers.message_parser.parseQuestMessage(update.message.text, update.message.forward_date)
        if quest_dict != {}:
            MsgHandlers.processQuestDescriptor(bot, update, quest_dict)




