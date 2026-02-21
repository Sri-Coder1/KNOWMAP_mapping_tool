import networkx as nx

def build_graph(triples):
    G = nx.Graph()

    for triple in triples:
        subj = triple["subject"]
        obj = triple["object"]
        rel = triple["relation"]

        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=rel)

    return G


def graph_to_json(G):
    return {
        "nodes": [{"id": n} for n in G.nodes()],
        "edges": [
            {
                "source": u,
                "target": v,
                "label": G[u][v]["label"]
            }
            for u, v in G.edges()
        ]
    }
