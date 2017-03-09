from config import  Config
import json
import pprint
import copy

class Recipes:
    def __init__(self, file_recipes):
        with open(file_recipes) as f:
            self.recipes = json.load(f)

    def all(self):
        return self.recipes

    def all_raw_recipes(self):
        raw_res = []
        for res in self.recipes:
            if res not in self.recipes:

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
