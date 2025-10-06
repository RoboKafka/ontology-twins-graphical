import json
import os
import networkx as nx
import matplotlib.pyplot as plt

# Paths
MODELS_DIR = "models"
TWINS_DIR = "twins"

# Load models (ontology)
def load_models():
    models = {}
    for f in os.listdir(MODELS_DIR):
        with open(os.path.join(MODELS_DIR, f)) as file:
            model = json.load(file)
            models[model["@id"]] = model
    return models

# Load twins (instances)
def load_twins():
    twins = {}
    for f in os.listdir(TWINS_DIR):
        with open(os.path.join(TWINS_DIR, f)) as file:
            twin = json.load(file)
            twins[twin["$dtId"]] = twin
    return twins

# Example relationships (normally you’d generate dynamically)
relationships = [
    {
        "$relationshipId": "cell1-hasDevice-robot1",
        "$sourceId": "cell1",
        "$relationshipName": "hasDevice",
        "$targetId": "robot1"
    }
]

# Build graph
def build_graph(twins, relationships):
    G = nx.DiGraph()
    for twin_id in twins:
        G.add_node(twin_id, label=twins[twin_id]["$metadata"]["$model"])
    for rel in relationships:
        G.add_edge(rel["$sourceId"], rel["$targetId"], label=rel["$relationshipName"])
    return G

# Visualize graph
def visualize_graph(G):
    pos = nx.spring_layout(G, seed=42)
    labels = {n: f"{n}\n{G.nodes[n]['label']}" for n in G.nodes}
    edge_labels = nx.get_edge_attributes(G, 'label')

    nx.draw(G, pos, with_labels=False, node_size=3000, node_color="lightblue", font_size=8)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    plt.show()

RELATIONSHIPS_DIR = "relationships"

def load_relationships():
    rels = []
    for f in os.listdir(RELATIONSHIPS_DIR):
        if f.endswith(".json"):
            with open(os.path.join(RELATIONSHIPS_DIR, f)) as file:
                rels.extend(json.load(file))
    return rels

if __name__ == "__main__":
    models = load_models()
    twins = load_twins()
    relationships = load_relationships()
    G = build_graph(twins, relationships)
    visualize_graph(G)
