import sys
from unittest import TestCase
import json

sys.path.append("..")
from craft_bot.recipes_tree import RecipesTree


class TestRecipesTree(TestCase):
    test_cases = None
    def setUp(self):
        with open('test_recipes.json') as f:
            self.test_cases = json.load(f)

    def get_resource_counted_one_case(self, case_name, params_idx, recipes, params):
        # Arrange
        rt = RecipesTree(recipes)

        # Act
        rc = rt.get_resource_counted(params['in_parent_nodes'], params['in_user_stock'])

        #Assert
        self.assertEqual(rc.number_of_nodes(), len(params['out_graph_attrib']))

        for res, props in params['out_graph_attrib'].items():
            self.assertEqual(rc.node[res], props, f"failed for case: {case_name}.param[{params_idx}].{res}")


    def test_get_resource_counted(self):
        for name, case in self.test_cases.items():
            recipes = case['recipes']

            params_idx = 0
            for params in case['params']:
                self.get_resource_counted_one_case(name, params_idx, recipes, params)
                params_idx += 1
