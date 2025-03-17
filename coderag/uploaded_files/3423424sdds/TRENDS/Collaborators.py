import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def visualize_collaboration_groups(G, groups, suspicious_groups, interns_dict, df, save_path):
    """Visualizes collaboration groups, highlighting suspicious groups."""
    print(f"Visualizing groups for {save_path}...")
    pos = nx.circular_layout(G)
    plt.figure(figsize=(12, 8))

    # Assign colors based on college
    college_colors = sns.color_palette("Paired", len(set(interns_dict.values())))
    color_map = {college: color for college, color in zip(set(interns_dict.values()), college_colors)}

    # Draw normal collaboration groups
    for i, group in enumerate(groups):
        node_list = list(group)
        node_colors = [color_map[interns_dict.get(node, "Unknown")] for node in node_list]
        node_sizes = [df.loc[df["Name"] == node, "Total Marks Earned"].values[0] / 10 for node in node_list]
        node_labels = {node: f"{node}\n({interns_dict.get(node, 'Unknown')})\nTotal Marks: {df.loc[df['Name'] == node, 'Total Marks Earned'].values[0]}" for node in node_list}
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=node_colors, node_size=node_sizes, label=f"Group {i+1}")
        nx.draw_networkx_labels(G, pos, labels=node_labels)

    # Draw edges
    edge_colors = ["gray" if (u, v) not in [(u, v) for group in suspicious_groups for u, v in zip(group, group[1:] + [group[0]])] else "red" for u, v in G.edges()]
    edge_widths = [1 if (u, v) not in [(u, v) for group in suspicious_groups for u, v in zip(group, group[1:] + [group[0]])] else 2 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.5)

    # Highlight suspicious groups in red
    for group in suspicious_groups:
        node_colors = [color_map[interns_dict.get(node, "Unknown")] for node in group]
        node_sizes = [df.loc[df["Name"] == node, "Total Marks Earned"].values[0] / 10 for node in group]
        node_labels = {node: f"{node}\n({interns_dict.get(node, 'Unknown')})\nTotal Marks: {df.loc[df['Name'] == node, 'Total Marks Earned'].values[0]}" for node in group}
        nx.draw_networkx_nodes(G, pos, nodelist=group, node_color=node_colors, node_size=node_sizes, edgecolors="red", linewidths=3)
        group_edges = [(u, v) for u, v in zip(group, group[1:] + [group[0]]) if G.has_edge(u, v)]
        nx.draw_networkx_edges(G, pos, edgelist=group_edges, edge_color="red", width=2)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_color="white")

    plt.title("Collaboration Groups and Suspicious Groups (Exact 5-Mark Patterns)")
    plt.legend()
    plt.savefig(save_path)
    plt.close()
    print(f"Visualization saved to {save_path}")