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
    G = nx.DiGraph()

    for giver, given_marks in peer_marks.items():
        for receiver, marks in given_marks.items():
            if marks >= threshold:
                G.add_edge(giver, receiver, weight=marks)

    return G

def identify_collaboration_groups(G):
    """Identifies collaboration groups (connected components) in the graph."""
    undirected_G = G.to_undirected()
    return list(nx.connected_components(undirected_G))

def detect_five_mark_collaborators(peer_marks):
    """
    Detects users who have given **only** 5 marks to others.
    A person qualifies **only if** they have given 5 to everyone and nothing else.
    """
    five_mark_collaborators = set()
    for giver, given_marks in peer_marks.items():
        marks_given = list(given_marks.values())  # Extract all marks given
        if marks_given and all(mark == 5 for mark in marks_given):
            five_mark_collaborators.add(giver)

    if five_mark_collaborators:
        print("\nDetected 5-mark collaborators:")
        print("  " + " , ".join(sorted(five_mark_collaborators)))
    else:
        print("✅ No 5-mark exclusive collaborators detected.")
    
    return five_mark_collaborators


def visualize_collaboration_groups(G, groups, suspicious_groups, five_mark_group, interns_dict, save_path):
    """Visualizes collaboration groups, highlighting suspicious groups and 5-mark gang."""
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(12, 8))

    # Assign colors
    colors = sns.color_palette("viridis", len(groups))
    suspicious_color = "red"
    five_mark_color = "blue"

    # Draw normal collaboration groups
    for i, group in enumerate(groups):
        node_list = list(group)
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n in node_list if n in G], node_color=colors[i], label=f"Group {i+1}")
        nx.draw_networkx_labels(G, pos, labels={node: node for node in node_list if node in G})

    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Highlight suspicious groups in red
    for group in suspicious_groups:
        nx.draw_networkx_nodes(G, pos, nodelist=[n for n in group if n in G], node_color=suspicious_color, edgecolors="black", linewidths=2)
        group_edges = [(u, v) for u in group for v in group if u != v and G.has_edge(u, v)]
        nx.draw_networkx_edges(G, pos, edgelist=group_edges, edge_color=suspicious_color, width=2)
    
    # Highlight 5-mark collaborators in blue
    nx.draw_networkx_nodes(G, pos, nodelist=[n for n in five_mark_group if n in G], node_color=five_mark_color, edgecolors="black", linewidths=2, label="5-Mark Gang")

    plt.title("Collaboration Groups and Suspicious Groups (Exact 5-Mark Patterns)")
    plt.legend()
    plt.savefig(save_path)
    plt.close()
def analyze_collaboration_groups(groups, suspicious_groups):
    """Prints details about collaboration groups and suspicious groups."""
    print("\n📌 Potential Collaboration Groups:")
    for i, group in enumerate(groups):
        print(f"Group {i+1}: {', '.join(group)}")
    
    if suspicious_groups:
        print("\n⚠️ Suspicious 5-Mark Collaborators:")
        for group in suspicious_groups:
            print(f"  🔴 {' , '.join(group)}")
    else:
        print("\n✅ No suspicious groups detected.")

def create_five_mark_graph(peer_marks, five_mark_collaborators):
    """Creates a directed graph exclusively for 5-mark collaborators."""
    G = nx.DiGraph()

    for giver in five_mark_collaborators:
        for receiver, marks in peer_marks.get(giver, {}).items():
            if marks == 5:
                G.add_edge(giver, receiver, weight=marks)

    return G


if __name__ == "__main__":
    peer_data = PeerReviewData()
    peer_marks = peer_data.peer_marks
    interns_dict = peer_data.interns_dict

    # Create a graph for high marks (≥8)
    high_collaboration_graph = create_collaboration_graph(peer_marks, threshold=8)
    collaboration_groups = identify_collaboration_groups(high_collaboration_graph)

    # Detect 5-mark exclusive givers
    five_mark_collaborators = detect_five_mark_collaborators(peer_marks)
    five_mark_graph = create_five_mark_graph(peer_marks, five_mark_collaborators)
    suspicious_exact_mark_groups = identify_collaboration_groups(five_mark_graph)

    # Visualization
    graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
    os.makedirs(graphs_path, exist_ok=True)

    visualize_collaboration_groups(
        high_collaboration_graph,
        collaboration_groups,
        suspicious_exact_mark_groups,  # Used actual detected suspicious groups
        five_mark_collaborators,
        interns_dict,
        os.path.join(graphs_path, "high_mark_collaboration_groups.png"),
    )

    visualize_collaboration_groups(
        five_mark_graph,
        suspicious_exact_mark_groups,
        suspicious_exact_mark_groups,  # Suspicious groups apply here
        five_mark_collaborators,
        interns_dict,
        os.path.join(graphs_path, "five_mark_suspicious_groups.png"),
    )

    # Analysis
    print("\n🔍 High Mark Collaboration Analysis (≥8):")
    analyze_collaboration_groups(collaboration_groups, suspicious_exact_mark_groups)

    print("\n🔍 Exact 5-Mark Collusion Analysis:")
    print(f"  📌 {', '.join(sorted(five_mark_collaborators))}" if five_mark_collaborators else "✅ No 5-mark exclusive collaborators detected.")

    print(f"\n✅ Collaboration group analysis complete. Graphs saved to {graphs_path}")

