# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

from datetime import datetime

import unittest
from craft_bot.message_parser import MessageParser
from craft_bot.config import Config

class StockParserTest(unittest.TestCase):
    def setUp(self):
        self.validtext = ("Ресурсы на продажу (451/4400):\n"
                            "/s_101 Нитки (106) x 2\n"
                            "/s_111 Алюм.руда (26) x 15\n")

        self.validtextadvanced = ("/s_134 🗃Сундучок (4) x 1💰\n"
                                  "/s_109 Плотная ткань (8) x 4💰")

        self.invalidtext = ("sdqqwasdad\n"
        "sdfwe")

        self.validtextsimple = ("Нитки (106)\n"
                                "Алюминиевая руда (26)\n")
        self.validtextadvancedsimple = ("🗃Сундучок (4)\n"
                                        "Плотная ткань (8)")

        self.message_parser = MessageParser()

    def test_parseSimpleMessage_validtext(self):
        #act
        found_resources = self.message_parser.parseSimpleMessage(self.validtextsimple)

        #assert
        self.assertEqual(found_resources['Нитки']['count'], 106)
        self.assertEqual(found_resources['Алюминиевая руда']['count'], 26)

    def test_parseSimpleMessage_validtextadvanced(self):
        #act
        found_resources = self.message_parser.parseSimpleMessage(self.validtextadvancedsimple)

        #assert
        self.assertEqual(found_resources['🗃Сундучок']['count'], 4)
        self.assertEqual(found_resources['Плотная ткань']['count'], 8)

    def test_parseSimpleMessage_invalidtext(self):
        #act
        found_resources = self.message_parser.parseMessageFromDwarfs(self.invalidtext)
        #assert
        self.assertEqual(len(found_resources), 0)

    def test_parseMessageFromDwarfs_validtext(self):
        #act
        found_resources = self.message_parser.parseMessageFromDwarfs(self.validtext)

        #assert
        self.assertEqual(found_resources['Нитки']['count'], 106)
        self.assertEqual(found_resources['Нитки']['cost'], 2)

        self.assertEqual(found_resources[Config.abbreviation_mapping['Алюм.руда']]['count'], 26)
        self.assertEqual(found_resources[Config.abbreviation_mapping['Алюм.руда']]['cost'], 15)

    def test_parseMessageFromDwarfs_validtextadvanced(self):
        #act
        found_resources = self.message_parser.parseMessageFromDwarfs(self.validtextadvanced)

        #assert
        self.assertEqual(found_resources['🗃Сундучок']['count'], 4)
        self.assertEqual(found_resources['🗃Сундучок']['cost'], 1)

        self.assertEqual(found_resources['Плотная ткань']['count'], 8)
        self.assertEqual(found_resources['Плотная ткань']['cost'], 4)

    def test_parseMessageFromDwarfs_invalidtext(self):
        #act
        found_resources = self.message_parser.parseMessageFromDwarfs(self.invalidtext)
        #assert
        self.assertEqual(len(found_resources), 0)

    def test_parseQuestMessage(self):
        msg =   ("До тебя донёсся детский плач. Пойдя на звук, ты заметил пару заблудившихся детей, которые попросили отвести их к родителям.\n"
                "\n"
                "Ты заработал: 86 опыта и 1 золотых монет.\n"
                "Получено: Плотная ткань (1)\n"
                "Получено: Порошок (1)\n"
                "Получено: Ветки (1)\n")

        self.message_parser.parseQuestMessage(msg, datetime.now)


if __name__ == '__main__':
    unittest.main()
