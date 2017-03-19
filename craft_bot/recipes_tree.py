import networkx as nx
import copy

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
                self.graph.add_weighted_edges_from([(rec_name, ing_name, count)])

    def get_resource_counted(self, parent_node_list):
        #Extract a subgraph which consists of nodes_of_interest
        useful_node_list = copy.copy(parent_node_list)
        for node in parent_node_list:
            useful_node_list.extend(nx.descendants(self.graph, node))
        useful_node_list = list(set(useful_node_list))
        counted_graph = copy.deepcopy(self.graph.subgraph(useful_node_list))

        pprint(counted_graph.nodes())

        #Assume that we need only one instance of `parent` resource:
        for node in parent_node_list:
            counted_graph.node[node]['count'] = 1

        #Walk around nodes in topologic order to count resources.
        for node in parent_node_list:
            for predc_node, succ_node, edge in gtr_node_tree(counted_graph, node):
                need_count = counted_graph.node[succ_node].get('count', 0)
                need_count += counted_graph.node[predc_node]['count'] * edge['weight']
                counted_graph.node[succ_node]['count'] = need_count

        return counted_graph