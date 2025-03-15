import os
import matplotlib.pyplot as plt
import seaborn as sns
import sys


# Get the parent directory (Interns_Groups)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the DATA folder to sys.path
sys.path.append(os.path.join(parent_dir, "DATA"))

# Import the PeerReviewData class
from data_creation import PeerReviewData

# Initialize PeerReviewData and get DataFrame
peer_data = PeerReviewData()
df = peer_data.get_dataframe()

# Sort and get top 10 mutual graders
top_10_mutual_graders = df.sort_values(by="Mutual Grades Received", ascending=False).head(5)

# Set path relative to interns_groups
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
interns_groups_dir = os.path.dirname(current_dir)  # Go back to interns_groups
figures_dir = os.path.join(interns_groups_dir, "GRAPHS", "FIGURES")

# Ensure directory exists
os.makedirs(figures_dir, exist_ok=True)

# Define file path
file_path = os.path.join(figures_dir, "top_10_mutual_graders.png")

# Plot
plt.figure(figsize=(12, 6))
sns.barplot(x="Name", y="Mutual Grades Received", data=top_10_mutual_graders, palette="viridis")
plt.xticks(rotation=45)
plt.title("Top 10 Mutual Graders")
plt.xlabel("Intern")
plt.ylabel("Mutual Grades Received")

# Save the figure
plt.savefig(file_path, bbox_inches="tight")
plt.show()

print(f"Graph saved at: {file_path}")
