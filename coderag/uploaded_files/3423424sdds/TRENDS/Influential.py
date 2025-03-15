# -*- coding: utf-8 -*-

import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Get the parent directory (Interns_Groups)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the DATA folder to sys.path
sys.path.append(os.path.join(parent_dir, "DATA"))

# Import the PeerReviewData class
from data_creation import PeerReviewData

def create_directed_graph(peer_marks):
    """Creates a directed graph from peer review marks."""
    G = nx.DiGraph()
    for giver, given_marks in peer_marks.items():
        for receiver, marks in given_marks.items():
            G.add_edge(giver, receiver, weight=marks)
    return G

def calculate_centrality(G):
    """Calculates degree, betweenness, and eigenvector centrality."""
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality(G, weight="weight") # using weights

    return degree_centrality, betweenness_centrality, eigenvector_centrality

def visualize_centrality(G, degree_centrality, betweenness_centrality, eigenvector_centrality, save_path):
    """Visualizes the network with node sizes representing centrality."""
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(18, 6))

    # Degree Centrality
    plt.subplot(1, 3, 1)
    node_sizes = [degree_centrality[node] * 2000 for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color="skyblue", alpha=0.7)
    plt.title("Degree Centrality")

    # Betweenness Centrality
    plt.subplot(1, 3, 2)
    node_sizes = [betweenness_centrality[node] * 5000 for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color="lightgreen", alpha=0.7)
    plt.title("Betweenness Centrality")

    # Eigenvector Centrality
    plt.subplot(1, 3, 3)
    node_sizes = [eigenvector_centrality[node] * 5000 for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color="lightcoral", alpha=0.7)
    plt.title("Eigenvector Centrality")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Centrality visualization saved to: {save_path}")

def identify_influential_interns(degree_centrality, betweenness_centrality, eigenvector_centrality):
    """Identifies and prints influential interns based on centrality measures."""
    print("Influential Interns:")

    # Degree Centrality
    print("\nTop 3 by Degree Centrality:")
    for intern, score in sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:3]:
        print(f"  - {intern}: {score:.4f}")

    # Betweenness Centrality
    print("\nTop 3 by Betweenness Centrality:")
    for intern, score in sorted(betweenness_centrality.items(), key=lambda item: item[1], reverse=True)[:3]:
        print(f"  - {intern}: {score:.4f}")

    # Eigenvector Centrality
    print("\nTop 3 by Eigenvector Centrality:")
    for intern, score in sorted(eigenvector_centrality.items(), key=lambda item: item[1], reverse=True)[:3]:
        print(f"  - {intern}: {score:.4f}")

# Main execution
if __name__ == "__main__":
    peer_data = PeerReviewData()
    peer_marks = peer_data.peer_marks

    G = create_directed_graph(peer_marks)
    degree_centrality, betweenness_centrality, eigenvector_centrality = calculate_centrality(G)

    # Visualize
    graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
    os.makedirs(graphs_path, exist_ok=True)
    visualize_centrality(G, degree_centrality, betweenness_centrality, eigenvector_centrality, os.path.join(graphs_path, "centrality_visualization.png"))

    # Identify influential interns
    identify_influential_interns(degree_centrality, betweenness_centrality, eigenvector_centrality)
    
    
# =============================================================================
# 
# 
# 1. Degree Centrality:
# 
# What it measures: The number of connections a node has. In a directed graph (like ours), it can be further divided into in-degree (number of incoming connections) and out-degree (number of outgoing connections).
# Interpretation:
# A high degree centrality means an intern has many connections, either giving or receiving reviews.
# High out-degree suggests an intern who actively reviews many others.
# High in-degree suggests an intern who is frequently reviewed.
# In our context: Interns with high degree centrality are those who are very active in the peer review process.
# 2. Betweenness Centrality:
# 
# What it measures: How often a node lies on the shortest path between other nodes in the network.
# Interpretation:
# A high betweenness centrality means an intern acts as a "bridge" between different parts of the network.
# These interns are crucial for information flow and can have significant influence.
# In our context: Interns with high betweenness centrality are those who connect different groups of reviewers. They might be the ones who facilitate communication or collaboration between otherwise disconnected individuals.
# 3. Eigenvector Centrality:
# 
# What it measures: The influence of a node based on the influence of its neighbors.
# Interpretation:
# A high eigenvector centrality means an intern is connected to other influential interns.
# It's not just about having many connections, but about having connections to other important nodes.
# In our context: Interns with high eigenvector centrality are those who are connected to other highly rated or influential interns. They are part of a network of "key players."
# Key Differences Summarized:
# 
# Degree: Focuses on the sheer number of connections.
# Betweenness: Focuses on the role of a node as a connector or bridge.
# Eigenvector: Focuses on the influence of a node's connections.
# In simpler terms:
# 
# Degree: "How popular is this person?"
# Betweenness: "How much control does this person have over information flow?"
# Eigenvector: "How influential are this person's connections?"
# By analyzing these different measures, you gain a more complete understanding of the social dynamics within your intern group.
# =============================================================================

# =============================================================================
# 
# Absolutely, let's illustrate these centrality measures with more concrete examples within the context of your intern peer review data.
# 
# Imagine your intern network as a map of roads connecting cities.
# 
# 1. Degree Centrality: "The Popular Intersection"
# 
# Example:
# Let's say "Intern A" has given reviews to 15 other interns and received reviews from 12 others.
# "Intern B" has only given and received reviews from 3 others.
# "Intern A" has a much higher degree centrality than "Intern B."
# Interpretation:
# "Intern A" is like a busy intersection where many roads meet. They are very involved in the review process.
# "Intern B" is like a quiet side street with very little traffic.
# In your context:
# Interns with high degree centrality are very active in the peer review process. They are likely very well known by the other interns.
# 2. Betweenness Centrality: "The Crucial Bridge"
# 
# Example:
# Imagine "Intern C" is the only person who has given and received reviews from two distinct groups of interns who otherwise have no interaction.
# If you were to remove "Intern C," those two groups would be completely disconnected.
# "Intern C" has a high betweenness centrality.
# Interpretation:
# "Intern C" is like a crucial bridge that connects two sides of a river. They are essential for information to flow between the two groups.
# In your context:
# Interns with high betweenness centrality are the "connectors." They might be the ones who facilitate communication or collaboration between otherwise separate groups. They are very important for the flow of information.
# 3. Eigenvector Centrality: "The Influential Circle"
# 
# Example:
# "Intern D" has given and received reviews from 5 other interns.
# Those 5 interns are all highly rated and considered very influential themselves.
# "Intern E" also has given and received reviews from 5 other interns.
# Those 5 interns are not considered very influential.
# "Intern D" has a higher eigenvector centrality than "Intern E."
# Interpretation:
# "Intern D" is like a person who is connected to other very important people. Their influence is amplified by their connections.
# "Intern E" is connected to people who are not very influential.
# In your context:
# Interns with high eigenvector centrality are part of an "influential circle." They are connected to other highly rated or well-connected interns. Their influence is not just about their own connections, but about the quality of those connections.
# Real-World Analogy:
# 
# Degree: Think of a popular social media user with many followers and follows.
# Betweenness: Think of a social media influencer who connects different niche communities.
# Eigenvector: Think of someone who is connected to other high profile social media influencers.
# By understanding these distinctions, you can gain a deeper understanding of the dynamics of your intern network.
# =============================================================================
