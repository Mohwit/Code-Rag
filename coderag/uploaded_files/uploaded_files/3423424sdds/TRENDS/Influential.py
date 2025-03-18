import os
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from data_creation import PeerReviewData

# Sample data for the bar graph
data = [10, 15, 8, 12, 20]
labels = ['College A', 'College B', 'College C', 'College D', 'College E']

# Create the bar graph
plt.figure(figsize=(10, 6))
sns.barplot(x=labels, y=data)
plt.title('Influential Colleges')
plt.xlabel('College')
plt.ylabel('Influence Score')
plt.xticks(rotation=90)
plt.tight_layout()

# Save the plot
plt.savefig('influential_colleges.png')