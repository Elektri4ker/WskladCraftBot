# -*- coding: utf-8 -*-

from config import Config
from stock import Stock
from recipes import Recipes
from database_proxy import *
from common import *

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
                "keyboard": [["Гайды"], ["Крафт"], ["Стата"]],
                "resize_keyboard": True
            },

            "craft_menu": {
                "keyboard": [["Расчет стоимости /stock"], ["Список рецептов"], ["Главное меню"]],
                "resize_keyboard": True
            }
        }

    @staticmethod
    def intro(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('intro.txt').render(),
                        reply_markup=MsgHandlers.keyboard_markups["main_menu"])

    @staticmethod
    def showCraftMenu(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('craft_menu.txt').render(),
                        reply_markup=MsgHandlers.keyboard_markups["craft_menu"])

    @staticmethod
    def showGuidesMenu(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('guides_menu.txt').render())

    @staticmethod
    def showStatMenu(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('stat_menu.txt').render())

    @staticmethod
    def _handle_user_resources(update):
        user_stock = {}
        unknown_res_names = []

        if not Users.getUserStock(update.message.from_user.username, user_stock, unknown_res_names):
            update.message.reply_text(env.get_template('nostock.txt').render())
            return

        subtract(unknown_res_names, Config.ignore_not_found_resources)

        if len(unknown_res_names) != 0:
            update.message.reply_text(env.get_template('noresourcesinfo.txt').render(unknown_res_names=unknown_res_names))

        return user_stock, unknown_res_names

    @staticmethod
    def plainMessage(bot, update):
        resources = {}
        new_resources = {}
        updated_resources = {}

        if MsgHandlers.stock.processMessageFromDwarfs(update.message, resources, new_resources, updated_resources):
            # clear resources from 'cost' field
            for res, props in resources.items():
                if 'cost' in props:
                    del props['cost']

            Users.resetUserStock(update.message.from_user.username, resources)

            bot.sendMessage(chat_id=update.message.chat_id,
                            parse_mode='Markdown',
                            text=env.get_template('sklad_updated.txt').render(new_resources=new_resources, updated_resources=updated_resources))

            return

        resources = {}
        not_found_resources_names = []

        if MsgHandlers.stock.processSimpleMessage(update.message, resources, not_found_resources_names):
            # clear resources from 'cost' field
            for res, props in resources.items():
                if 'cost' in props:
                    del props['cost']

            Users.resetUserStock(update.message.from_user.username, resources)
            bot.sendMessage(chat_id=update.message.chat_id,
                            parse_mode='Markdown',
                            text=env.get_template('sklad_updated.txt').render())

            if len(not_found_resources_names) != 0:
                bot.sendMessage(chat_id=update.message.chat_id,
                                parse_mode='Markdown',
                                text=env.get_template('noresourcesinfo.txt').render(unknown_res_names=not_found_resources_names))

            return

        update.message.reply_text('Nothing happened')

    @staticmethod
    def calcCost(bot, update):
        user_stock, unknown_res_names = MsgHandlers._handle_user_resources(update)
        if user_stock is None:
            return
        cost = Users.calcStockCost(user_stock)
        update.message.reply_text(u'Стоимость вашего /stock = ' + str(cost))

    @staticmethod
    def getCraftList(bot, update):
        weapon_list, intermediate_list = MsgHandlers.recipes.list_all()
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=env.get_template('craft_list.txt').render(weapon_list=weapon_list, intermediate_list=intermediate_list, map_id=MsgHandlers.recipes_name_to_id_map))


    @staticmethod
    def getCraftRecipes(bot, update):
        recipe_item_id = int(update.message.text.split('_')[1])
        recipe_item, unused = find_dict(MsgHandlers.recipes_name_to_id_map, lambda k, v: v == recipe_item_id)

        # /craft_<itemid> command
        user_stock, unknown_res_names = MsgHandlers._handle_user_resources(update)
        if user_stock is None:
            return

        #transform user stock to Counter-like container
        user_stock_counted = {}
        for res, props in user_stock.items():
            user_stock_counted[res] = props['count']
        try:
            need_prim_resources, need_base_resources = MsgHandlers.recipes.calc_recipe_for_user(recipe_item, user_stock_counted)
        except Exception:
            update.message.reply_text(f"Ресурса \"{recipe_item}\" не существует.")
            return

        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('craft_item.txt').render(recipe_item=recipe_item,
                                                                       need_prim_resources=need_prim_resources,
                                                                       need_base_resources=need_base_resources,
                                                                       map_id=MsgHandlers.recipes_name_to_id_map))




