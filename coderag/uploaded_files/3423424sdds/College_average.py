# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Get the parent directory (Interns_Groups)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the DATA folder to sys.path
sys.path.append(os.path.join(parent_dir, "DATA"))

# Import the PeerReviewData class
from data_creation import PeerReviewData

def calculate_college_averages(peer_marks, interns_dict):
    """Calculates average scores given and received by each college."""
    college_scores_given = {}
    college_scores_received = {}
    college_counts_given = {}
    college_counts_received = {}

    # Initialize all colleges from interns_dict
    for intern, college in interns_dict.items():
        if college not in college_scores_received:
            college_scores_received[college] = 0
            college_counts_received[college] = 0

    for giver, given_marks in peer_marks.items():
        giver_college = interns_dict.get(giver, "Unknown")

        if giver_college not in college_scores_given:
            college_scores_given[giver_college] = 0
            college_counts_given[giver_college] = 0

        for receiver, marks in given_marks.items():
            receiver_college = interns_dict.get(receiver, "Unknown")

            if receiver_college == "Unknown":
                print(f"Receiver '{receiver}' not found in interns_dict.")
            else:
                print(f"Current receiver: {receiver}")  # Add this line
                college_scores_received[receiver_college] += marks
                college_counts_received[receiver_college] += 1
            # Update scores given by giver
            college_scores_given[giver_college] += marks
            college_counts_given[giver_college] += 1

            # Update scores received by receiver
            college_scores_received[receiver_college] += marks
            college_counts_received[receiver_college] += 1

    college_averages = {}
    for college in college_scores_given:
        avg_given = college_scores_given[college] / college_counts_given[college] if college_counts_given[college] != 0 else 0
        avg_received = college_scores_received[college] / college_counts_received[college] if college_counts_received[college] != 0 else 0
        college_averages[college] = {"Average Given": avg_given, "Average Received": avg_received}

    # Add colleges that were only receivers
    for college, received_count in college_counts_received.items():
        if college not in college_averages:
            avg_received = college_scores_received[college] / received_count if received_count != 0 else 0
            college_averages[college] = {"Average Given": 0, "Average Received": avg_received}

    return college_averages

def visualize_college_averages(college_averages, save_path):
    """Visualizes college average scores using a bar graph."""

    colleges = list(college_averages.keys())
    avg_given = [college_averages[college]["Average Given"] for college in colleges]
    avg_received = [college_averages[college]["Average Received"] for college in colleges]

    x = range(len(colleges))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(x, avg_given, width, label="Average Given", color="skyblue")
    plt.bar([i + width for i in x], avg_received, width, label="Average Received", color="lightcoral")

    plt.xlabel("College")
    plt.ylabel("Average Score")
    plt.title("College Average Scores (Given vs. Received)")
    plt.xticks([i + width / 2 for i in x], colleges, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path)
    plt.close()
    print(f"College average scores graph saved to: {save_path}")

# Main execution
if __name__ == "__main__":
    peer_data = PeerReviewData()
    peer_marks = peer_data.peer_marks
    interns_dict = peer_data.interns_dict

    college_averages = calculate_college_averages(peer_marks, interns_dict)

    # Visualize
    graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
    os.makedirs(graphs_path, exist_ok=True)
    visualize_college_averages(college_averages, os.path.join(graphs_path, "college_averages_graph.png"))