# -*- coding: utf-8 -*-

from telegram.ext import Updater
from stock import Stock
from database_proxy import *

class MsgHandlers:
    #stock = None
    @staticmethod
    def initialize():
        MsgHandlers.stock = Stock()

    @staticmethod
    def plainMessage(bot, update):
        resources = []
        new_resources = []
        updated_resources = []

        if MsgHandlers.stock.processMessageFromDwarfs(update.message, resources, new_resources, updated_resources):
            #clear resources from 'cost' field
            for res in resources:
                if 'cost' in res: del res['cost']

            Users.resetUserStock(update.message.from_user.username, resources)
            update.message.reply_text('Ура! Склад обновлен!')

            if len(new_resources) != 0:
                str_res = ""
                for res in new_resources:
                    str_res += res['name'] + '\n'
                update.message.reply_text('Вы нашли новые ресурсы:\n' + str_res)

            if len(updated_resources) != 0:
                str_res = ""
                for res in updated_resources:
                    str_res += res['name'] + '\n'
                update.message.reply_text('Вы нашли информацию о новых ценах на следующие ресурсы:\n' + str_res)

            return

        resources = []
        not_found_resources = []

        if MsgHandlers.stock.processSimpleMessage(update.message, resources, not_found_resources):
            #clear resources from 'cost' field
            for res in resources:
                if 'cost' in res: del res['cost']

            Users.resetUserStock(update.message.from_user.username, resources)
            update.message.reply_text('Ура! Склад обновлен!')

            if len(not_found_resources) != 0:
                str_res = ""
                for res in not_found_resources:
                    str_res += res['name'] + '\n'

                rpl = u'У нас нет информации о стоимости следующих ресурсов:\n' + \
                    str_res + \
                    u'Вы можете переслать сообщение от скупщика ресурсов, чтобы добавить цены в нашу базу!'

                update.message.reply_text(rpl)

            return

        update.message.reply_text('Nothing happened')

    @staticmethod
    def calcCost(bot, update):
        user_stock = []
        unknown_res_names = []
        if not Users.getUserStock(update.message.from_user.username, user_stock, unknown_res_names):
            update.message.reply_text('Вы еще не отправили свой /stock')
            return

        if len(unknown_res_names) != 0:
            str_res = ""
            for res in not_found_resources:
                str_res += res['name'] + '\n'
            rpl = 'У нас нет информации о стоимости следующих ресурсов:\n' + \
                str_res + \
                'Вы можете переслать сообщение от скупщика ресурсов, чтобы добавить цены в нашу базу!'

        cost = Users.calcStockCost(user_stock)
        update.message.reply_text('Стоимость вашего /stock = ' + str(cost))
