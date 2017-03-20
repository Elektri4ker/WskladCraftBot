# -*- coding: utf-8 -*-

import re
from config import Config

class StockParser:
    def __init__(self):
        #regex for string like this:
        #/s_101 Нитки (106) x 2💰
        #use http://pythex.org/ to compose and check regex'es
        self.dwarfs_parser = re.compile(r'^/s.+?\s(.+)\s\((\d+)\)\sx\s(\d+)')

        #this one matches for strings like this:
        #Шкура животного (5)
        self.simple_parser = re.compile(r'^(.+)\s\((\d+)\)')

    def parseMessageFromDwarfs(self, text):

        entries = text.split("\n")

        found_resources = {}

        for entry in entries:
            m = self.dwarfs_parser.match(entry)
            if not m or len(m.groups()) != 3:
                continue

            name = m.group(1)
            if name in Config.abbreviation_mapping:
                name = Config.abbreviation_mapping[name]

            found_resources[name] = {}
            found_resources[name]['count'] = int(m.group(2))
            found_resources[name]['cost'] = int(m.group(3))

        return found_resources

    def parseSimpleMessage(self, text):
        entries = text.split("\n")

        found_resources = {}

        for entry in entries:
            m = self.simple_parser.match(entry)
            if not m or len(m.groups()) != 2:
                continue

            name = m.group(1)
            found_resources[name] = {}
            found_resources[name]['count'] = int(m.group(2))

        return found_resources
