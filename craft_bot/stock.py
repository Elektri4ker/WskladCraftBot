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
        if tg_message.forward_from == None or tg_message.forward_from.username != Config.cw_bot_username:
            return False

        #is it actually the message from Dwarfs?
        if u"Ресурсы на продажу" not in tg_message.text:
            return False

        found_resources = self.stock_parser.parseMessageFromDwarfs(tg_message.text)
        if len(found_resources) == 0:
            return False

        new_resources = []
        updated_resources = []
        resources = []
        for res in found_resources:
            result = Resources.resetResource(res['name'], res['cost'])
            if result == 2:
                new_resources.append(res)
            if result == 1:
                updated_resources.append(res)

            resources.append(res)

        return True

    def processSimpleMessage(self, tg_message, resources, not_found_resources):
        found_resources = self.stock_parser.parseSimpleMessage(tg_message.text)
        if len(found_resources) == 0:
            return False

        not_found_resources = []
        for res in found_resources:
            res_stored = Resources.getResource(res['name'])
            if (res_stored == None):
                not_found_resources.append(res)

            resources.append(res)

        return True
