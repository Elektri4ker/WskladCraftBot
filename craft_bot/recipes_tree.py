import networkx as nx
import copy
import collections

#yields all successors from `parent_node_name`
#It's guaranteed that predcessor node will be returned first than any of its successors.
#It will go CRASH if the graph would have cycles!!!
def gtr_node_tree(graph, parent_node_name):
    for successor in graph.successors(parent_node_name):
        yield (parent_node_name, successor, graph.edge[parent_node_name][successor])
        yield from gtr_node_tree(graph, successor)


class RecipesTree:

    def __init__(self, recipes_dict):
        self.graph = nx.DiGraph()
        self.create_graph_from_dict(recipes_dict)

    def create_graph_from_dict(self, recipes_dict):
        for rec_name, ingredients in recipes_dict.items():
            for ing_name, count in ingredients.items():
                if ing_name != 'stat':
                    self.graph.add_weighted_edges_from([(rec_name, ing_name, count)])

        #adding 'stat' data field
        for rec_name, field in recipes_dict.items():
            if 'stat' in field:
                self.graph.node[rec_name]['stat'] = field['stat']

    #in:
    #`parent_node_list` - names of node-resources, e.g. ['steel', 'aluminium']
    #`user_resources_list` - Counter of user-owned res, e.g. {'steel': 2, 'tree': 5}
    #returns:
    #graph-object of counted resources
    def get_resource_counted(self, parent_node_list, user_resources_list):
        #Extract a subgraph which consists of nodes_of_interest
        useful_node_list = copy.copy(parent_node_list)
        for node in parent_node_list:
            useful_node_list.extend(nx.descendants(self.graph, node))
        useful_node_list = list(set(useful_node_list))
        counted_graph = copy.deepcopy(self.graph.subgraph(useful_node_list))

        #Assume that we need only one instance of `parent` resource:
        for node in parent_node_list:
            counted_graph.node[node]['count'] = 1
            counted_graph.node[node]['available'] = 0

        #Walk around nodes in topologic order to count resources.
        for node in parent_node_list:
            for predc_node, succ_node, edge in gtr_node_tree(counted_graph, node):
                #check, if we already have any count for this successor node (if we had passed it before?)
                need_count = counted_graph.node[succ_node].get('count', 0)
                available_count = counted_graph.node[succ_node].get('available', 0) + user_resources_list.get(succ_node, 0)

                need_count += counted_graph.node[predc_node]['count'] * edge['weight']
                available_count += min(counted_graph.node[predc_node]['available'] * edge['weight'], need_count)

                counted_graph.node[succ_node]['count'] = need_count
                counted_graph.node[succ_node]['available'] = available_count

        return counted_graph


    #All that could be crafted
    def get_available_craft(self):
        weapon_list = []
        intermediate_list = []

        for node in self.graph.nodes(data=True):
            if 'stat' in node[1]:
                weapon_list.append(node)
            else:
                if len(self.graph.successors(node[0])) > 0:
                    intermediate_list.append(node[0])

        return weapon_list, intermediate_list

    def user_get_craft(self, craft_item, user_resources):
        counted_graph = self.get_resource_counted([craft_item], user_resources)

        need_base_resources = {}
        need_prim_resources = {}

        for node, data in counted_graph.nodes(data=True):
            count = data['count']
            avail = data['available']
            need = max(0, count - avail)

            if craft_item in counted_graph.predecessors(node):
                need_prim_resources.update({node: {'need': need, 'count': count}})

            if len(counted_graph.successors(node)) <= 0:
                need_base_resources.update({node: {'need': need, 'count': count}})

        return need_prim_resources, need_base_resources



###
#self-test:

if __name__ == '__main__':
    import  collections
    import json
    from pprint import pprint

    with open('recipes.json') as f:
        recipes = json.load(f)

    rt = RecipesTree(recipes)
    weapons, intermediate = rt.get_available_craft()

    pprint(weapons)
    pprint(intermediate)

    prim, base = rt.user_get_craft('Меч берсеркера', {"Стальная заготовка": 999})
    pprint(prim)
    pprint(base)