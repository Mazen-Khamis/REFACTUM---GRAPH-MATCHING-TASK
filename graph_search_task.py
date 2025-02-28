import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
import webbrowser
from networkx.algorithms import isomorphism
from IPython.display import display
from pyvis.network import Network

# ##################################################
# 1) Load JSON and Create Graph
# ##################################################

def load_graph(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    data = data[0] if isinstance(data, list) else data

    G = nx.Graph()
    G.add_nodes_from((node_id, attrs) for node_id, attrs in data["nodes"])
    G.add_edges_from((src, tgt, attrs) for src, tgt, attrs in data["edges"])

    return G

workpiece_graph = load_graph("workpiece_graph.json")
feature_graph = load_graph("feature_graph.json")

os.makedirs("Results/Graphs", exist_ok=True)
os.makedirs("Results/Tables", exist_ok=True)
os.makedirs("Results/HTML", exist_ok=True)

graph_layout = nx.spring_layout(workpiece_graph, seed=60)

# ##################################################
# 2) Graph Visualization
# ##################################################

def draw_graph(G, title, labels=True, edge_labels=True, save_path=None):
    plt.figure(figsize=(10, 8))

    node_labels = {n: G.nodes[n].get("type", str(n)) for n in G.nodes()} if labels else {n: str(n) for n in G.nodes()}
    edge_labels_map = {(src, tgt): "CX" if edge_labels and G.edges[src, tgt].get("angular_type", "").lower() == "convex" else "CC"
                        for src, tgt in G.edges()} if edge_labels else {}

    nx.draw(G, graph_layout, with_labels=True, labels=node_labels,
            node_color="lightblue", edge_color="gray", node_size=1000, font_size=8)
    
    if edge_labels:
        nx.draw_networkx_edge_labels(G, graph_layout, edge_labels=edge_labels_map, font_size=7, label_pos=0.5)

    plt.title(title)
    if save_path:
        plt.savefig(save_path)

def save_html_graph(G, filename):
    nt = Network(notebook=False)
    nt.from_nx(G)
    nt.write_html(f"Results/HTML/{filename}")

draw_graph(workpiece_graph, "Workpiece Graph (Labels)", save_path="Results/Graphs/workpiece_graph_labels.png")
draw_graph(feature_graph, "Feature Graph (Labels)", save_path="Results/Graphs/feature_graph_labels.png")
draw_graph(workpiece_graph, "Workpiece Graph (Nummern)", labels=False, edge_labels=False, save_path="Results/Graphs/workpiece_graph_numbers.png")
draw_graph(feature_graph, "Feature Graph (Nummern)", labels=False, edge_labels=False, save_path="Results/Graphs/feature_graph_numbers.png")

save_html_graph(workpiece_graph, "workpiece_graph.html")
save_html_graph(feature_graph, "feature_graph.html")

# ##################################################
# 3) Find Subgraph Isomorphisms
# ##################################################

def find_subgraph(G_large, G_small):
    GM = isomorphism.GraphMatcher(
        G_large, G_small, 
        node_match=isomorphism.categorical_node_match("type", None),
        edge_match=isomorphism.categorical_edge_match("angular_type", None)
    )
    matches = list(GM.subgraph_isomorphisms_iter())
    print(f"Feature-Graph als Subgraph gefunden - Anzahl der Übereinstimmungen: {len(matches)}" if matches else "Feature-Graph NICHT als Subgraph gefunden.")
    return matches

matching_subgraphs = find_subgraph(workpiece_graph, feature_graph)

# ##################################################
# 4) Highlight Matching Subgraphs
# ##################################################

def draw_colored_subgraphs(G_large, matches):
    plt.figure(figsize=(10, 8))

    node_colors = {node: "lightgray" for node in G_large.nodes()}
    edge_colors = {edge: "gray" for edge in G_large.edges()}
    node_labels = {node: G_large.nodes[node].get("type", str(node)) for node in G_large.nodes()}

    if not matches:
        nx.draw(G_large, graph_layout, with_labels=True, labels=node_labels, font_size=6,
                node_color=list(node_colors.values()), edge_color=list(edge_colors.values()), node_size=800)
        plt.title("Workpiece Graph (Keine Übereinstimmung gefunden)")
        plt.savefig("Results/Graphs/workpiece_no_match.png")
        return

    colors = ["red", "blue", "green", "orange", "purple", "pink", "brown", "cyan"]
    table_data = []

    for i, match in enumerate(matches):
        sub_nodes = set(match.keys())  
        sub_edges = {(match[src], match[tgt]) for src, tgt in feature_graph.edges() if src in match and tgt in match}
        color = colors[i % len(colors)]

        for node in sub_nodes:
            node_colors[node] = color
        for edge in sub_edges:
            edge_colors[edge] = color

        table_data.append({
            "Subgraph #": i + 1,
            "Knoten (Nummern)": ", ".join(map(str, sub_nodes)) if sub_nodes else "-",  
            "Knoten (Typen)": ", ".join(node_labels[n] for n in sub_nodes) if sub_nodes else "-", 
            "Kanten (Namen)": ", ".join(f"({node_labels[src]} - {node_labels[tgt]})" for src, tgt in sub_edges) if sub_edges else "-",
            "Kanten (Art)": ", ".join(
                "CX" if G_large.edges[src, tgt].get("angular_type", "").lower() == "convex" else "CC"
                for src, tgt in sub_edges
            ) if sub_edges else "-",
            "Farbe": color
        })

    nx.draw(G_large, graph_layout, with_labels=True, labels=node_labels, font_size=6,
            node_color=[node_colors[n] for n in G_large.nodes()],
            edge_color=[edge_colors[e] for e in G_large.edges()], node_size=800)

    plt.title("Workpiece Graph mit markierten Subgraphen")
    plt.savefig("Results/Graphs/workpiece_colored_subgraphs.png")

    df = pd.DataFrame(table_data)
    df.to_csv("Results/Tables/subgraph_results.csv", index=False)
    print("Tabelle der gefundenen Subgraphen:")
    display(df)

draw_colored_subgraphs(workpiece_graph, matching_subgraphs)

# ##################################################
# 5) Save Results Summary as HTML
# ##################################################

def save_results_html():
    """Generate an HTML file summarizing all results including tables and images."""
    html_content = """
    <html>
    <head>
        <title>Graph Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .image-container { display: flex; flex-wrap: wrap; }
            .image-container img { margin: 10px; width: 45%; border: 1px solid #ddd; border-radius: 5px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
        </style>
    </head>
    <body>
        <h1>Graphische Ergebnisse</h1>
        <h2>Workpiece Graph</h2>
        <div class='image-container'>
            <img src='../Graphs/workpiece_graph_labels.png'/>
            <img src='../Graphs/workpiece_graph_numbers.png'/>
        </div>
        <h2>Feature Graph</h2>
        <div class='image-container'>
            <img src='../Graphs/feature_graph_labels.png'/>
            <img src='../Graphs/feature_graph_numbers.png'/>
        </div>
        <h2>Interaktive Graphen</h2>
        <ul>
            <li><a href='workpiece_graph.html'>Workpiece Graph (Interaktiv)</a></li>
            <li><a href='feature_graph.html'>Feature Graph (Interaktiv)</a></li>
        </ul>
        <h2>Gefundene Subgraphen</h2>
        <table>
    """
    df = pd.read_csv("Results/Tables/subgraph_results.csv")
    html_content += df.to_html(index=False)
    html_content += """
        </table>
    </body>
    </html>
    """
    result_file = "Results/HTML/results_summary.html"
    with open(result_file, "w") as f:
        f.write(html_content)
    
    webbrowser.open(os.path.abspath(result_file))

save_results_html()