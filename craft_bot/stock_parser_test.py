# -*- coding: utf-8 -*-

import unittest
from stock_parser import StockParser

class StockParserTest(unittest.TestCase):
    def setUp(self):
        self.validtext = ""
        self.invalidtext = ""
        print(self.validtext)
        self.validtext = ("Ресурсы на продажу (451/4400):\n"
                            "/s_101 Нитки (106) x 2\n"
                            "/s_111 Алюм.руда (26) x 15\n")

        self.invalidtext = ("sdqqwasdad\n"
        "sdfwe")

        self.stock_parser = StockParser()

    def test_parseMessageFromDwarfs_validtext(self):
        #print(self.validtext)
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.validtext)

        #assert
        self.assertEqual(found_resources[0]['name'], 'Нитки')
        self.assertEqual(found_resources[0]['count'], 106)
        self.assertEqual(found_resources[0]['cost'], 2)

        self.assertEqual(found_resources[1]['name'], 'Алюм.руда')
        self.assertEqual(found_resources[1]['count'], 26)
        self.assertEqual(found_resources[1]['cost'], 15)

    def test_parseMessageFromDwarfs_invalidtext(self):
        #act
        found_resources = self.stock_parser.parseMessageFromDwarfs(self.invalidtext)
        #assert
        self.assertEqual(len(found_resources), 0)

if __name__ == '__main__':
    unittest.main()
