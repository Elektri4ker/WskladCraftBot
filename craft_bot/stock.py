# -*- coding: utf-8 -*-

import config
import stock_parser
import * from database_proxy

class Stock:

    def __init__(self, stock_parser = StockParser()):
        self.stock_parser = stock_parser


    def processMessageFromDwarfs(self, tg_message, resources, new_resources, updated_resources)
        #is it actually from the right bot?
        if tg_message.forward_from.username != Config.cw_bot_username:
            return false

        #is it actually the message from Dwarfs?
        if "Ресурсы на продажу" not in tg_message.text:
            return false

        found_resources = self.stock_parser.parseMessageFromDwarfs(tg_message.text)
        if len(found_resources) == 0:
            return false

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

        return true
