# -*- coding: utf-8 -*-

from config import Config
from stock_parser import *
from database_proxy import *
from telegram.ext import Updater

class Stock:

    def __init__(self, stock_parser = StockParser()):
        self.stock_parser = stock_parser


    def processMessageFromDwarfs(self, tg_message, resources, new_resources, updated_resources):
        #is it actually from the right bot?
        if not tg_message.forward_from or tg_message.forward_from.username != Config.cw_bot_username:
            return False

        #is it actually the message from Dwarfs?
        if u"Ресурсы на продажу" not in tg_message.text:
            return False

        found_resources = self.stock_parser.parseMessageFromDwarfs(tg_message.text)
        if len(found_resources) == 0:
            return False

        for res, props in found_resources.items():
            #print(res)
            result = Resources.resetResource(res, props['cost'])
            if result == 2:
                new_resources[res] = props
            if result == 1:
                updated_resources[res] = props

            #print(', result = ', result)

            resources[res] = props

        return True

    def processSimpleMessage(self, tg_message, resources, not_found_resources_names):
        found_resources = self.stock_parser.parseSimpleMessage(tg_message.text)
        if len(found_resources) == 0:
            return False

        for res, props in found_resources.items():
            res_stored = Resources.getResource(res)
            if res_stored is None and res not in Config.ignore_not_found_resources:
                not_found_resources_names.append(res)

            resources[res] = props

        return True
