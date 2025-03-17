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

def detect_cyclic_collusion(G, mark_threshold=5, max_cycles=1000):
    """Detects cycles where all members give exactly the threshold marks in a cycle."""
    suspicious_cycles = []
    cycles_checked = 0
    
    try:
        print("Starting cycle detection...")
        for cycle in nx.simple_cycles(G):  # Find all simple cycles
            cycles_checked += 1
            if cycles_checked % 100 == 0:
                print(f"Checked {cycles_checked} cycles...")
                
            if cycles_checked >= max_cycles:  # Limit the number of cycles to check
                print(f"⚠️ Warning: Reached maximum cycle check limit ({max_cycles})")
                break
                
            if len(cycle) > 2:  # Only consider cycles of 3 or more people
                all_threshold = True
                for u, v in zip(cycle, cycle[1:] + [cycle[0]]):
                    if not G.has_edge(u, v) or G[u][v]['weight'] != mark_threshold:
                        all_threshold = False
                        break
                
                if all_threshold:
                    suspicious_cycles.append(cycle)
    except Exception as e:
        print(f"Error in cycle detection: {e}")
    
    # Debugging: Print all detected cycles
    print("\n🔍 Debugging: Found Suspicious Cycles")
    if suspicious_cycles:
        for cycle in suspicious_cycles:
            print(f"⚠️ Suspicious {mark_threshold}-mark Cycle Detected: {' → '.join(cycle)}")
    else:
        print("✅ No suspicious cycles detected.")

    return suspicious_cycles

def detect_exact_mark_collusion(G, mark_threshold=5):
    """
    Detects groups where members consistently give each other exactly the threshold mark.
    This catches collusion even when students try to randomize their review patterns.
    """
    suspicious_groups = []
    
    print("Starting exact mark collusion detection...")
    
    # Convert to undirected graph to find connected components
    undirected_G = G.to_undirected()
    
    # Find all connected components (potential collaboration groups)
    components = list(nx.connected_components(undirected_G))
    print(f"Checking {len(components)} connected components...")
    
    for i, component in enumerate(components):
        if i % 10 == 0 and i > 0:
            print(f"Checked {i}/{len(components)} components...")
            
        if len(component) < 3:  # Only consider groups of 3 or more
            continue
            
        # Create a subgraph for this component
        subgraph = G.subgraph(component)
        
        # Check if all marks within this group are exactly the threshold
        exact_marks = True
        mark_count = 0
        total_possible_marks = len(component) * (len(component) - 1)  # All possible directed edges
        
        for u in component:
            for v in component:
                if u != v:  # Don't check self-loops
                    if G.has_edge(u, v):
                        mark = G[u][v]['weight']
                        if mark != mark_threshold:
                            exact_marks = False
                            break
                        mark_count += 1
            if not exact_marks:
                break
                
        # If all marks are exactly the threshold and the group has a significant number of connections
        if total_possible_marks > 0:  # Avoid division by zero
            density = mark_count / total_possible_marks
            if exact_marks and mark_count >= 3 and density >= 0.5:  # At least 3 marks and 50% density
                suspicious_groups.append(list(component))
    
    # Debugging: Print all detected groups
    print("\n🔍 Debugging: Found Suspicious Groups with Exact Marks")
    if suspicious_groups:
        for group in suspicious_groups:
            print(f"⚠️ Suspicious Group Detected (all exactly {mark_threshold} marks): {', '.join(group)}")
    else:
        print("✅ No suspicious exact-mark groups detected.")
    
    return suspicious_groups

def visualize_collaboration_groups(G, groups, suspicious_groups, interns_dict, save_path):
    """Visualizes collaboration groups, highlighting suspicious groups."""
    print(f"Visualizing groups for {save_path}...")
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))

    # Assign colors
    colors = sns.color_palette("viridis", len(groups))
    suspicious_color = "red"  # Highlight suspicious groups in red

    # Draw normal collaboration groups
    for i, group in enumerate(groups):
        node_list = list(group)
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=colors[i], label=f"Group {i+1}")
        nx.draw_networkx_labels(G, pos, labels={node: node for node in node_list})

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Highlight suspicious groups in red
    for group in suspicious_groups:
        nx.draw_networkx_nodes(G, pos, nodelist=group, node_color=suspicious_color, edgecolors="black", linewidths=2)
        # Draw all edges between members of the suspicious group
        group_edges = [(u, v) for u in group for v in group if u != v and G.has_edge(u, v)]
        nx.draw_networkx_edges(G, pos, edgelist=group_edges, edge_color=suspicious_color, width=2)

    plt.title("Collaboration Groups and Suspicious Groups (Exact 5-Mark Patterns)")
    plt.legend()
    plt.savefig(save_path)
    plt.close()
    print(f"Visualization saved to {save_path}")

def analyze_collaboration_groups(groups, suspicious_groups, interns_dict, df):
    """Analyzes and prints details about collaboration groups and suspicious groups."""
    print("📌 Potential Collaboration Groups:")
    for i, group in enumerate(groups):
        print(f"\nGroup {i+1}:")
        for intern in group:
            try:
                college = interns_dict.get(intern, "Unknown")
                total_marks = df.loc[df["Name"] == intern, "Total Marks Earned"].values[0]
                print(f"  - {intern} (College: {college}, Total Marks: {total_marks})")
            except (KeyError, IndexError) as e:
                print(f"  - {intern} (College: Unknown, Total Marks: Unknown - Error: {e})")

    # Report suspicious collusion groups
    if suspicious_groups:
        print("\n⚠️ Suspicious Collusion Groups Detected:")
        for i, group in enumerate(suspicious_groups):
            print(f"  🔴 Group {i+1}: {', '.join(group)}")
            print("    Exact mark pattern: All members gave exactly 5 marks to others in the group")
    else:
        print("\n✅ No suspicious groups detected.")

# Main execution
if __name__ == "__main__":
    print("Loading peer review data...")
    try:
        peer_data = PeerReviewData()
        peer_marks = peer_data.peer_marks
        interns_dict = peer_data.interns_dict
        df = peer_data.get_dataframe()
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    print("\nCreating collaboration graphs...")
    # Create two graphs: one for high marks (≥8) and one for exactly 5 marks
    high_collaboration_graph = create_collaboration_graph(peer_marks, threshold=8)
    print(f"High collaboration graph created with {high_collaboration_graph.number_of_nodes()} nodes and {high_collaboration_graph.number_of_edges()} edges.")
    
    five_mark_graph = create_collaboration_graph(peer_marks, threshold=5)
    print(f"Initial five mark graph created with {five_mark_graph.number_of_nodes()} nodes and {five_mark_graph.number_of_edges()} edges.")
    
    print("Filtering five mark graph to exact 5 marks only...")
    # Filter the five_mark_graph to keep only edges with exactly 5 marks
    edges_to_remove = []
    for u, v, data in five_mark_graph.edges(data=True):
        if data['weight'] != 5:
            edges_to_remove.append((u, v))
    
    for u, v in edges_to_remove:
        five_mark_graph.remove_edge(u, v)
    
    print(f"Five mark graph filtered. Now has {five_mark_graph.number_of_nodes()} nodes and {five_mark_graph.number_of_edges()} edges.")
    
    print("\nIdentifying collaboration groups...")
    # Identify collaboration groups from the high marks graph
    collaboration_groups = identify_collaboration_groups(high_collaboration_graph)
    print(f"Found {len(collaboration_groups)} collaboration groups.")

    # If five_mark_graph is too large, skip cycle detection
    if five_mark_graph.number_of_edges() > 1000:
        print("⚠️ Five mark graph is very large. Skipping cycle detection to avoid performance issues.")
        suspicious_cycles = []
    else:
        print("\nDetecting suspicious cycles...")
        suspicious_cycles = detect_cyclic_collusion(five_mark_graph, mark_threshold=5, max_cycles=5000)
        print(f"Found {len(suspicious_cycles)} suspicious cycles.")
    
    print("\nDetecting exact mark collusion...")
    suspicious_exact_mark_groups = detect_exact_mark_collusion(five_mark_graph, mark_threshold=5)
    print(f"Found {len(suspicious_exact_mark_groups)} suspicious exact-mark groups.")

    # Combine suspicious groups (avoiding duplicates)
    all_suspicious_groups = suspicious_cycles.copy()
    for group in suspicious_exact_mark_groups:
        if group not in all_suspicious_groups:
            all_suspicious_groups.append(group)
    
    print(f"Total of {len(all_suspicious_groups)} suspicious groups identified.")

    print("\nPreparing visualizations...")
    # Visualization
    graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
    os.makedirs(graphs_path, exist_ok=True)
    
    # Save two visualizations
    visualize_collaboration_groups(high_collaboration_graph, collaboration_groups, all_suspicious_groups, 
                                  interns_dict, os.path.join(graphs_path, "high_mark_collaboration_groups.png"))
    
    five_mark_groups = identify_collaboration_groups(five_mark_graph)
    visualize_collaboration_groups(five_mark_graph, five_mark_groups, 
                                  all_suspicious_groups, interns_dict, 
                                  os.path.join(graphs_path, "five_mark_suspicious_groups.png"))

    # Analysis
    print("\n🔍 High Mark Collaboration Analysis (≥8):")
    analyze_collaboration_groups(collaboration_groups, [], interns_dict, df)
    
    print("\n🔍 Exact 5-Mark Collusion Analysis:")
    analyze_collaboration_groups(five_mark_groups, all_suspicious_groups, interns_dict, df)

    print(f"\nCollaboration group analysis complete. Graphs saved to {graphs_path}")