import pandas as pd
import numpy as np
from itertools import combinations

# Read the CSV file
df = pd.read_csv('interest-viral-index-output.csv')

# Print basic information about the dataset
print(f"Total number of personas: {len(df)}")
print(f"Number of interest categories: {len(df.columns) - 2}")  # Subtract 2 for 'persona_id' and 'interests'

# Get the interest columns (excluding 'persona_id' and 'interests')
interest_columns = df.columns[2:]

# Convert interest values to numeric type, replacing any non-numeric values with 0
for col in interest_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calculate the sum of all interests for each row
df['total'] = df[interest_columns].sum(axis=1)

# Check for any rows where total is 0
zero_total_rows = df[df['total'] == 0]
if not zero_total_rows.empty:
    print(f"Warning: {len(zero_total_rows)} personas have no interests recorded.")
    print("These will be excluded from the analysis.")
    df = df[df['total'] > 0]

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
    if not pd.isna(corr):  # Only add non-NaN correlations
        all_correlations.append((interest1.replace('_prop', ''), 
                                 interest2.replace('_prop', ''), 
                                 corr))

# Sort correlations from strongest positive to strongest negative
sorted_correlations = sorted(all_correlations, key=lambda x: x[2], reverse=True)

# Print the sorted correlations
print("\nCorrelations between all combinations of topics (sorted from strongest positive to strongest negative):")
for interest1, interest2, corr in sorted_correlations:
    print(f"{interest1} - {interest2}: {corr}")

# Save the sorted correlations to a CSV file
correlation_df = pd.DataFrame(sorted_correlations, columns=['Topic1', 'Topic2', 'Correlation'])
correlation_df.to_csv('sorted_interest_correlations3.csv', index=False)
print("\nSorted correlations saved to 'sorted_interest_correlations3.csv'")

# Print summary statistics
if sorted_correlations:
    print("\nSummary Statistics:")
    print(f"Strongest positive correlation: {sorted_correlations[0][0]} - {sorted_correlations[0][1]}: {sorted_correlations[0][2]}")
    print(f"Strongest negative correlation: {sorted_correlations[-1][0]} - {sorted_correlations[-1][1]}: {sorted_correlations[-1][2]}")
    print(f"Correlation closest to zero: {min(sorted_correlations, key=lambda x: abs(x[2]))[0]} - {min(sorted_correlations, key=lambda x: abs(x[2]))[1]}: {min(sorted_correlations, key=lambda x: abs(x[2]))[2]}")
else:
    print("\nNo valid correlations found.")

# Count and report NaN correlations
nan_count = sum(1 for _ in combinations(prop_columns, 2) if pd.isna(correlation_matrix.loc[_[0], _[1]]))
if nan_count > 0:
    print(f"\nWarning: {nan_count} NaN correlations were found and excluded from the analysis.")
    print("This may indicate interests with constant values or other data issues.")