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

    #returns resource list for which no any recipes
    def all_raw_recipes(self, res_list):
        raw_res = []
        for res in res_list:
            if res not in self.recipes:
                raw_res.append(res)
        return raw_res

    def find_recipe(self, resource_name):
        if resource_name not in self.recipes:
            return None
        else:
            return self.recipes[resource_name]

    def find_raw_recipe(self, resource_name):
        raw_recipe = copy.deepcopy(self.find_recipe(resource_name))



if __name__ == '__main__':
    rec = Recipes('recipes.json')
    pprint.pprint(rec.recipes)
