import json
import pprint
import copy
from recipes_tree import *
import collections

class Recipes:
    def __init__(self, file_recipes):
        with open(file_recipes) as f:
            self.recipes_tree = RecipesTree(json.load(f))

    def list_all(self):
        return self.recipes_tree.get_available_craft()

    def calc_recipe_for_user(self, recipe_name, user_stock):
        return self.recipes_tree.user_get_craft(recipe_name, user_stock)


    #returns resource list for which no any recipes
    def all_raw_recipes(self, res_list):
        raw_res = []

        return raw_res




if __name__ == '__main__':
    rec = Recipes('recipes.json')
    pprint.pprint(rec.recipes)
