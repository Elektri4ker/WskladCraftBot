# -*- coding: utf-8 -*-

import re
from config import Config

class MessageParser:
    def __init__(self):
        #regex for string like this:
        #/s_101 Нитки (106) x 2💰
        #use http://pythex.org/ to compose and check regex'es
        self.dwarfs_parser = re.compile(r'^/s.+?\s(.+)\s\((\d+)\)\sx\s(\d+)')

        #this one matches for strings like this:
        #Шкура животного (5)
        self.simple_parser = re.compile(r'^(.+)\s\((\d+)\)')

        self.yield_res_parser = re.compile(r'Получено:\s*(\W*)\((\d+)')
        self.yield_exp_parser = re.compile(r'\s*(\d+) опыт\W*\s*')
        self.yield_gold_parser = re.compile(r'\s+(\d+) золот\W* монет')

        #Geroy patterns
        self.geroy_name_parser = re.compile(r'\s(..)(.+),\s(.+)\s.+замка')
        self.geroy_level_parser = re.compile(r'Уровень:\s(\d+)')
        self.geroy_combat_parser = re.compile(r'Атака:\s(\d+).+Защита:\s(\d+)')
        self.geroy_exp_parser = re.compile(r'Опыт:\s(\d+)/(\d+)')
        self.geroy_stamina_parser = re.compile(r'Выносливость:\s(\d+)/(\d+)')
        self.geroy_mining_cap_parser = re.compile(r'\+(\d+)⛏')
        self.geroy_lucky_parser = re.compile(r'\+(\d+)🍀')


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

    def parseGerojMessage(self, text, timestamp):
        geroy_descriptor = {}

        geroy_descriptor['timestamp'] = timestamp

        # m = self.geroy_name_parser.match(text)
        # if m is None:
        #     return {}
        # geroy_descriptor['fraction'] = m.group(1)
        # geroy_descriptor['name'] = m.group(2)
        # geroy_descriptor['prof'] = m.group(3)

        m = self.geroy_level_parser.match(text)
        if m is None:
            return {}
        geroy_descriptor['level'] = m.group(1)

        m = self.geroy_combat_parser.match(text)
        if m is None:
            return {}
        geroy_descriptor['attack'] = m.group(1)
        geroy_descriptor['def'] = m.group(2)

        m = self.geroy_mining_cap_parser.match(text)
        if m is not None:
            geroy_descriptor['mining_cap'] = m.group(1)

        m = self.geroy_lucky_parser.match(text)
        if m is not None:
            geroy_descriptor['lucky'] = m.group(1)

        return geroy_descriptor





        

    def parseQuestMessage(self, text, timestamp):
        quest_descriptor = {}
        yield_res = {}
        yield_gold = 0
        yield_exp = 0
        used_lines = []
        is_quest_message = False

        lines = text.split("\n")

        # fill in resource yield
        for line in lines:
            m = self.yield_res_parser.match(line)
            if not m or len(m.groups()) != 2:
                continue

            res_name = m.group(1)
            res_count = int(m.group(2))
            yield_res[res_name] = res_count

            is_quest_message = True
            used_lines.append(line)

        # fill in exp and gold yield
        for line in lines:
            if 'Ты заработал:' not in line:
                continue

            m_exp = self.yield_exp_parser.match(line)
            m_gold = self.yield_gold_parser.match(line)

            if m_exp:
                yield_exp = m_exp.group(1)
            if m_gold:
                yield_gold = m_gold.group(1)

            is_quest_message = True
            used_lines.append(line)

        if not is_quest_message:
            return {}

        # extract residual text
        residual_lines = [x for x in lines if x != '' and x not in used_lines]
        residual_text = ' '.join(residual_lines)

        # fill in descriptor
        quest_descriptor['timestamp'] = timestamp
        quest_descriptor['type'] = ''
        quest_descriptor['yield_res'] = yield_res
        quest_descriptor['yield_exp'] = yield_exp
        quest_descriptor['yield_gold'] = yield_gold
        quest_descriptor['residual_text'] = residual_text

        return quest_descriptor



