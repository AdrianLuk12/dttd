# create correlation between topics/tags by using the proportions of individual user interests

import pandas as pd
import numpy as np
from itertools import combinations

# Read the CSV file
df = pd.read_csv('interest-viral-index-output.csv')

# Get the interest columns (excluding 'persona_id' and 'interests')
interest_columns = df.columns[2:]

# Convert interest values to numeric type, replacing any non-numeric values with 0
for col in interest_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calculate the sum of all interests for each row
df['total'] = df[interest_columns].sum(axis=1)

# Balance the interests into proportions
for col in interest_columns:
    df[f'{col}_prop'] = df[col] / df['total']

# Get the proportion columns
prop_columns = [col for col in df.columns if col.endswith('_prop')]

# Calculate the correlation matrix for the proportions
correlation_matrix = df[prop_columns].corr()

# Create a list to store all correlations
all_correlations = []

# Iterate through all unique combinations of interests
for interest1, interest2 in combinations(prop_columns, 2):
    corr = correlation_matrix.loc[interest1, interest2]
    all_correlations.append((interest1.replace('_prop', ''), 
                             interest2.replace('_prop', ''), 
                             corr))

# Sort correlations from highest to lowest
sorted_correlations = sorted(all_correlations, key=lambda x: abs(x[2]), reverse=True)

# Print the sorted correlations
print("Correlations between all combinations of topics (sorted by absolute value):")
for interest1, interest2, corr in sorted_correlations:
    print(f"{interest1} - {interest2}: {corr}")

# Save the sorted correlations to a CSV file
correlation_df = pd.DataFrame(sorted_correlations, columns=['Topic1', 'Topic2', 'Correlation'])
correlation_df.to_csv('sorted_interest_correlationskk.csv', index=False)
print("\nSorted correlations saved to 'sorted_interest_correlationskk.csv'")