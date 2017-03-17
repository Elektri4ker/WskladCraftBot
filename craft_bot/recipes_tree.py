import networkx as nx


def create_graph_from_dict(recipes_dict):
    g = nx.DiGraph()
    for rec_name, ingredients in recipes_dict.items():
        for ing_name, count in ingredients.items():
            g.add_weighted_edges_from([(rec_name, ing_name, count)])

    return g

rec = {
    "Сталь": {
            "Порошок": 3,
            "Железная руда": 3
    },

    "Металлическое волокно": {
        "Стальная нить": 9,
        "Серебряная руда":6
    },

    "Стальная нить": {
        "Нитки": 10,
        "Сталь": 1
    }
}

import matplotlib.pyplot as plt

g = create_graph_from_dict(rec)
nx.draw_networkx(g, pos=nx.spring_layout(g))
nx.draw_networkx_edge_labels(g, pos=nx.spring_layout(g))
plt.savefig("path.png")



