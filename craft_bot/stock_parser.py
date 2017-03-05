# -*- coding: utf-8 -*-

import re

class StockParser:
    def __init__(self):
        #regex for string like this:
        #/s_101 Нитки (106) x 2💰
        #use http://pythex.org/ to compose and check regex'es
        self.re_resource = re.compile(r'^/s.+?\s(.+)\s\((\d+)\)\sx\s(\d+)')

    def parseMessageFromDwarfs(self, text):

        entries = text.split("\n")

        found_resources = []

        for entry in entries:
            m = self.re_resource.match(entry)
            if not m or len(m.groups()) != 3:
                continue

            found_resource = {}

            found_resource['name'] = m.group(1)
            found_resource['count'] = int(m.group(2))
            found_resource['cost'] = int(m.group(3))

            found_resources.append(found_resource)

        return found_resources
