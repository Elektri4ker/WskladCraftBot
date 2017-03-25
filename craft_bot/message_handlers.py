# -*- coding: utf-8 -*-

from config import Config
from stock import Stock
from recipes import Recipes
from database_proxy import *

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


    @staticmethod
    def initialize():
        MsgHandlers.stock = Stock()
        MsgHandlers.recipes = Recipes(Config.recipes_file)

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
        keyboard_markup = {'keyboard': [["123"], ["456"]], 'resize_keyboard': True}
        bot.sendMessage(chat_id=update.message.chat_id,
                        parse_mode='Markdown',
                        text=env.get_template('intro.txt').render(),
                        reply_markup=MsgHandlers.keyboard_markups["main_menu"])

    @staticmethod
    def _handle_user_resources(update):
        user_stock = {}
        unknown_res_names = []

        if not Users.getUserStock(update.message.from_user.username, user_stock, unknown_res_names):
            update.message.reply_text(env.get_template('nostock.txt').render())
            return

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
    def getCraftRecipes(bot, update):
        recipe_item = update.message.text.split(' ')[1:]
        recipe_item = ' '.join(recipe_item)

        # just `/craft` command
        if len(recipe_item) == 0:
            weapon_list, intermediate_list = MsgHandlers.recipes.list_all()
            rpl = "Доступный крафт (снаряжение):\n"
            for w in weapon_list:
                weap_str = f"{w[0]} ("
                if 'attack' in w[1]['stat']:
                    weap_str += f"⚔️{w[1]['stat']['attack']}"
                if 'def' in w[1]['stat']:
                    weap_str += f"🛡️{w[1]['stat']['def']}"
                weap_str += ") "
                weap_str += f"`/craft {w[0]}`\n"
                rpl += weap_str

            rpl += "\nДоступный крафт (промежуточные ресурсы)\n"
            for i in intermediate_list:
                rpl += i + "\n"

            update.message.reply_text(rpl)
        # /craft <itemname> command
        else:
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

            rpl = ''
            rpl += "Требуется ресурсов для крафта:\n" \
                   "Имя ресура: (осталось добыть / требуется всего)\n"
            for res, props in need_prim_resources.items():
                rpl += f"{res}: ({props['need']} / {props['count']})\n"

            rpl += "\nИли требуется __базовых__ ресурсов для крафта:\n" \
                   "Имя ресура: (осталось добыть / требуется всего)\n"
            for res, props in need_base_resources.items():
                rpl += f"{res}: ({props['need']} / {props['count']})\n"

            update.message.reply_text(rpl)




