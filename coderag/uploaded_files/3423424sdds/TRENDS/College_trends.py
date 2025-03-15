import os
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import pandas as pd

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

# Extract peer marks dictionary
peer_marks = peer_data.peer_marks

# Dictionary to track same-college ratings
same_college_ratings = {}
college_population = df["College"].value_counts().to_dict()  # Get total students per college

# Count same-college ratings
for giver, given_marks in peer_marks.items():
    giver_college = df.loc[df["Name"] == giver, "College"].values[0]
    
    for receiver, marks in given_marks.items():
        receiver_college = df.loc[df["Name"] == receiver, "College"].values[0]
        
        if marks >= 8 and giver_college == receiver_college:
            if giver_college not in same_college_ratings:
                same_college_ratings[giver_college] = 0
            same_college_ratings[giver_college] += 1

# Convert to DataFrame and normalize by college size
college_df = pd.DataFrame(
    [(college, same_college_ratings.get(college, 0), college_population.get(college, 1)) for college in college_population],
    columns=["College", "Same College Ratings", "Total Students"]
)
college_df["Density"] = college_df["Same College Ratings"] / college_df["Total Students"]  # Normalize
college_df = college_df.sort_values(by="Density", ascending=False)  # Sort by highest density

# Ensure GRAPHS/FIGURES path exists
graphs_path = os.path.join(parent_dir, "GRAPHS", "FIGURES")
os.makedirs(graphs_path, exist_ok=True)

# Plot bar chart (Density-based)
plt.figure(figsize=(10, 5))
sns.barplot(data=college_df, x="College", y="Density", palette="viridis")
plt.xticks(rotation=45, ha="right")
plt.xlabel("College")
plt.ylabel("Density of Same-College High Ratings")
plt.title("Normalized Same-College High Ratings")

# Save the figure
plt.tight_layout()
plt.savefig(os.path.join(graphs_path, "same_college_ratings_density.png"))
plt.close()

# Pie chart for same-college vs. cross-college ratings
total_high_ratings = sum(sum(1 for marks in given_marks.values() if marks >= 8) for given_marks in peer_marks.values())
same_college_count = sum(same_college_ratings.values())
cross_college_count = total_high_ratings - same_college_count

plt.figure(figsize=(6, 6))
plt.pie(
    [same_college_count, cross_college_count],
    labels=["Same College", "Cross College"],
    autopct="%1.1f%%",
    colors=["#66b3ff", "#ff9999"]
)
plt.title("Proportion of Same-College vs Cross-College High Ratings")

# Save the figure
plt.savefig(os.path.join(graphs_path, "same_vs_cross_college.png"))
plt.close()

print(f"Graphs saved to {graphs_path}")

# =============================================================================
#
# What does this graph show?
#
# The bar chart **same_college_ratings_density.png** represents the **normalized proportion** of high ratings (8, 9, or 10) 
# exchanged between people from the same college, adjusted for the size of the college.
#
# How is the data calculated?
#
# 1️⃣ We first extract the peer review data, which tells us who gave marks to whom.  
# 2️⃣ We then check:
#    - If Person A gives Person B a score of 8, 9, or 10.
#    - If Person A and Person B belong to the same college.
#    - If both conditions hold, it counts as a same-college rating.
# 3️⃣ Instead of raw counts, we **normalize by the total number of students** in the college.
#    - Formula: **Density = (Same-College High Ratings) / (Total Students in College)**
# 4️⃣ We then plot the **density**, making comparisons fair across colleges of different sizes.
#
# How to interpret the graph?
#
# - The **X-axis** represents different colleges.
# - The **Y-axis** represents the **normalized density** of high ratings exchanged between students of the same college.
# - Higher values indicate **a stronger tendency** for students to rate their own college peers highly.
# - Lower values suggest students from that college tend to rate cross-college peers more often.
#
# Possible Insights from the Graph:
#
# ✅ **Higher bars** suggest strong internal bias—students tend to favor their own college peers.  
# ✅ **Lower bars** indicate more **cross-college** ratings, suggesting a diverse grading pattern.  
# ✅ If a few colleges have **exceptionally high density**, it may indicate a **tight-knit community**.  
# ✅ If some colleges have **zero density**, it suggests students are engaging more with peers from other institutions.  
#
# Additional Considerations:
#
# - This density-based approach ensures that **larger colleges don’t dominate unfairly**.
# - If a college has very few students, density might be artificially high—further analysis may be needed.  
#
# =============================================================================

