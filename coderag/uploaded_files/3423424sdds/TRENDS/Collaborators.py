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

def create_collaboration_graph(peer_marks, threshold=8):
    """Creates a directed graph based on peer review marks."""
    G = nx.DiGraph()  # Directed graph to respect giver-receiver relationships

    for giver, given_marks in peer_marks.items():
        for receiver, marks in given_marks.items():
            if marks >= threshold:
                G.add_edge(giver, receiver, weight=marks)

    return G

def identify_collaboration_groups(G):
    """Identifies collaboration groups (connected components) in the graph."""
    undirected_G = G.to_undirected()  # Convert to undirected for group detection
    return list(nx.connected_components(undirected_G))

def detect_cyclic_collusion(G, mark_threshold=5):
    """Detects cycles where all members give exactly the threshold marks in a cycle."""
    suspicious_cycles = []

    for cycle in nx.simple_cycles(G):  # Find all simple cycles
        if len(cycle) > 2:  # Only consider cycles of 3 or more people
            all_fives = all(
                G[u][v]['weight'] == mark_threshold 
                for u, v in zip(cycle, cycle[1:] + [cycle[0]])
            )
            if all_fives:
                suspicious_cycles.append(cycle)

    # Debugging: Print all detected cycles
    print("\n🔍 Debugging: Found Suspicious Cycles")
    if suspicious_cycles:
        for cycle in suspicious_cycles:
            print(f"⚠️ Suspicious 5-mark Cycle Detected: {' → '.join(cycle)}")
    else:
        print("✅ No suspicious cycles detected.")

    return suspicious_cycles


def visualize_collaboration_groups(G, groups, suspicious_cycles, interns_dict, save_path):
    """Visualizes collaboration groups, highlighting suspicious cycles."""
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))

    # Assign colors
    colors = sns.color_palette("viridis", len(groups))
    cycle_color = "red"  # Highlight suspicious cycles in red

    # Draw normal collaboration groups
    for i, group in enumerate(groups):
        node_list = list(group)
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=colors[i], label=f"Group {i+1}")
        nx.draw_networkx_labels(G, pos, labels={node: node for node in node_list})

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Highlight suspicious cyclic collusion groups in red
    for cycle in suspicious_cycles:
        nx.draw_networkx_nodes(G, pos, nodelist=cycle, node_color=cycle_color, edgecolors="black", linewidths=2)
        cycle_edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle))]
        nx.draw_networkx_edges(G, pos, edgelist=cycle_edges, edge_color=cycle_color, width=2)

    plt.title("Collaboration Groups and Suspicious Cycles (5-Member Cycles)")
    plt.legend()
    plt.savefig(save_path)
    plt.close()

def analyze_collaboration_groups(groups, suspicious_cycles, interns_dict, df):
    """Analyzes and prints details about collaboration groups and suspicious cycles."""
    print("📌 Potential Collaboration Groups:")
    for i, group in enumerate(groups):
        print(f"\nGroup {i+1}:")
        for intern in group:
            college = interns_dict.get(intern, "Unknown")
            total_marks = df.loc[df["Name"] == intern, "Total Marks Earned"].values[0]
            print(f"  - {intern} (College: {college}, Total Marks: {total_marks})")

    # Report suspicious collusion groups
    if suspicious_cycles:
        print("\n⚠️ Suspicious Cyclic Collusion Groups (5 Members) Detected:")
        for i, cycle in enumerate(suspicious_cycles):
            print(f"  🔴 Group {i+1}: {' → '.join(cycle)}")
    else:
        print("\n✅ No suspicious cycles detected.")

# Main execution
if __name__ == "__main__":
    peer_data = PeerReviewData()
    peer_marks = peer_data.peer_marks
    interns_dict = peer_data.interns_dict
    df = peer_data.get_dataframe()

    collaboration_graph = create_collaboration_graph(peer_marks)
    collaboration_groups = identify_collaboration_groups(collaboration_graph)

    # Detect suspicious collusion cycles of exactly 5 members
    suspicious_groups = detect_cyclic_collusion(collaboration_graph, mark_threshold=5)

    # Visualization
    graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
    os.makedirs(graphs_path, exist_ok=True)
    visualize_collaboration_groups(collaboration_graph, collaboration_groups, suspicious_groups, interns_dict, os.path.join(graphs_path, "collaboration_groups.png"))

    # Analysis
    analyze_collaboration_groups(collaboration_groups, suspicious_groups, interns_dict, df)

    print(f"Collaboration group analysis complete. Graph saved to {graphs_path}")