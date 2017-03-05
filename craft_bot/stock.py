# -*- coding: utf-8 -*-

import config
import stock_parser

class Stock:

    def __init__(self, db, stock_parser = StockParser()):
        self.db = db
        self.stock_parser = stock_parser


    def processMessageFromDwarfs(self, bot, tg_message, resources, new_resources)
        #is it actually from the right bot?
        if tg_message.forward_from.username != Config.cw_bot_username:
            return false

        #is it actually the message from Dwarfs?
        if "Ресурсы на продажу" not in tg_message.text:
            return false

        found_resources = self.stock_parser.parseMessageFromDwarfs(tg_message.text)
        if len(found_resources) == 0:
            return false

        for res in found_resources:
            doc_existinig_resource = self.db.Resources.find_one({'name': res['name']})
            if not doc_existinig_resource:
                doc_new_resource = {}








        return true
