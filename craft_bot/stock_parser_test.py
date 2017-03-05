# -*- coding: utf-8 -*-

import unittest
from stock_parser import StockParser
from config import Config

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

        self.stock_parser = StockParser()

    def test_parseSimpleMessage_validtext(self):
        #act
        found_resources = self.stock_parser.parseSimpleMessage(self.validtextsimple)

        #assert
        self.assertEqual(found_resources[0]['name'], 'Нитки')
        self.assertEqual(found_resources[0]['count'], 106)

        self.assertEqual(found_resources[1]['name'], 'Алюминиевая руда')
        self.assertEqual(found_resources[1]['count'], 26)

    def test_parseSimpleMessage_validtextadvanced(self):
        #act
        found_resources = self.stock_parser.parseSimpleMessage(self.validtextadvancedsimple)

        #assert
        self.assertEqual(found_resources[0]['name'], '🗃Сундучок')
        self.assertEqual(found_resources[0]['count'], 4)

        self.assertEqual(found_resources[1]['name'], 'Плотная ткань')
        self.assertEqual(found_resources[1]['count'], 8)

    def test_parseSimpleMessage_invalidtext(self):
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.invalidtext)
        #assert
        self.assertEqual(len(found_resources), 0)

    def test_parseMessageFromDwarfs_validtext(self):
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.validtext)

        #assert
        self.assertEqual(found_resources[0]['name'], 'Нитки')
        self.assertEqual(found_resources[0]['count'], 106)
        self.assertEqual(found_resources[0]['cost'], 2)

        self.assertEqual(found_resources[1]['name'], Config.abbreviation_mapping['Алюм.руда'])
        self.assertEqual(found_resources[1]['count'], 26)
        self.assertEqual(found_resources[1]['cost'], 15)

    def test_parseMessageFromDwarfs_validtextadvanced(self):
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.validtextadvanced)

        #assert
        self.assertEqual(found_resources[0]['name'], '🗃Сундучок')
        self.assertEqual(found_resources[0]['count'], 4)
        self.assertEqual(found_resources[0]['cost'], 1)

        self.assertEqual(found_resources[1]['name'], 'Плотная ткань')
        self.assertEqual(found_resources[1]['count'], 8)
        self.assertEqual(found_resources[1]['cost'], 4)

    def test_parseMessageFromDwarfs_invalidtext(self):
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.invalidtext)
        #assert
        self.assertEqual(len(found_resources), 0)

if __name__ == '__main__':
    unittest.main()
