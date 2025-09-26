import networkx as nx
import numpy as np
from pyvis.network import Network
import streamlit as st

def create_directed_network(df, feature1, feature2, title, min_count=1000, output_file="network.html", length=500):
    """
    Create a directed network from a DataFrame and save as HTML.
    
    Parameters:
    - df: pandas DataFrame containing the data
    - feature1: column name to use as source node
    - feature2: column name to use as target node
    - title: title to display in Streamlit
    - min_count: minimum number of occurrences for a link to be included
    - output_file: HTML file to save the graph
    """
    # Count occurrences of feature1
    feature1_counts = df[feature1].value_counts()

    # Count links between feature1 and feature2
    links = df.groupby([feature1, feature2]).size().reset_index(name='counts')

    # Apply filters
    links = links[links['counts'] >= min_count]
    links = links[links[feature1] != links[feature2]]

    print(links.head())
    print(f"Number of unique links: {len(links)}")

    # Create directed graph
    G = nx.DiGraph()

    all_nodes = set(links[feature1]).union(set(links[feature2]))
    for node in all_nodes:
        count = feature1_counts.get(node, 1)
        size = np.log1p(count) * 10  # scale for PyVis
        G.add_node(node, size=size)

    for _, row in links.iterrows():
        G.add_edge(
            row[feature1], 
            row[feature2], 
            title=f"Count: {row['counts']}",
            physics=True,
            length=length
        )

    # Create PyVis network
    net = Network(height="750px", width="100%", directed=True)
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])

    # Save and display in Streamlit
    net.save_graph(output_file)