# -*- coding: utf-8 -*-

from config import Config
from stock import Stock
from recipes import Recipes
from database_proxy import *


class MsgHandlers:
    recipes = None
    stock = None

    @staticmethod
    def initialize():
        MsgHandlers.stock = Stock()
        MsgHandlers.recipes = Recipes(Config.recipes_file)

    @staticmethod
    def _handle_user_resources(update):
        user_stock = {}
        unknown_res_names = []

        if not Users.getUserStock(update.message.from_user.username, user_stock, unknown_res_names):
            update.message.reply_text('Вы еще не отправили свой /stock')
            return

        if len(unknown_res_names) != 0:
            str_res = ""
            for res in unknown_res_names:
                str_res += res + '\n'
            rpl = u'У нас нет информации о стоимости следующих ресурсов:\n' + \
                  str_res + \
                  u'Вы можете переслать сообщение от скупщика ресурсов, чтобы добавить цены в нашу базу!'
            update.message.reply_text(rpl)

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
            update.message.reply_text('Ура! Склад обновлен!')

            if len(new_resources) != 0:
                str_res = ""
                for res in new_resources:
                    str_res += res + '\n'
                bot.sendMessage(update.message.chat_id, u'Вы нашли новые ресурсы:\n' + str_res)

            if len(updated_resources) != 0:
                str_res = ""
                for res in updated_resources:
                    str_res += res + '\n'
                bot.sendMessage(update.message.chat_id,
                                u'Вы нашли информацию о новых ценах на следующие ресурсы:\n' + str_res)

            return

        resources = {}
        not_found_resources_names = []

        if MsgHandlers.stock.processSimpleMessage(update.message, resources, not_found_resources_names):
            # clear resources from 'cost' field
            for res, props in resources.items():
                if 'cost' in props:
                    del props['cost']

            Users.resetUserStock(update.message.from_user.username, resources)
            update.message.reply_text('Ура! Склад обновлен!')

            if len(not_found_resources_names) != 0:
                str_res = ""
                for res in not_found_resources_names:
                    str_res += res + '\n'

                rpl = u'У нас нет информации о стоимости следующих ресурсов:\n' + \
                      str_res + \
                      u'Вы можете переслать сообщение от скупщика ресурсов, чтобы добавить цены в нашу базу!'

                update.message.reply_text(rpl)

            return

        update.message.reply_text('Nothing happened')

    @staticmethod
    def calcCost(bot, update):
        user_stock, unknown_res_names = MsgHandlers._handle_user_resources(update)

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
                weap_str += ")\n"
                rpl += weap_str

            rpl += "\nДоступный крафт (промежуточные ресурсы)\n"
            for i in intermediate_list:
                rpl += i + "\n"

            update.message.reply_text(rpl)
        # /craft <itemname> command
        else:
            user_stock, unknown_res_names = MsgHandlers._handle_user_resources(update)

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




