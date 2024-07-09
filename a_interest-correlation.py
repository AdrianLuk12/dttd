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

# Calculate proportions
df['total'] = df[interest_columns].sum(axis=1)
df = df[df['total'] > 0]  # Remove rows with no interests
for col in interest_columns:
    df[col] = df[col] / df['total']

# Calculate correlation matrix
correlation_matrix = df[interest_columns].corr()

# Calculate weighted co-interest scores
def calculate_weighted_co_interest(df, interest1, interest2):
    both = (df[interest1] * df[interest2]).sum()
    either = (df[interest1] + df[interest2] - df[interest1] * df[interest2]).sum()
    return both / either if either > 0 else 0

co_interest_scores = {}
for interest1, interest2 in combinations(interest_columns, 2):
    score = calculate_weighted_co_interest(df, interest1, interest2)
    co_interest_scores[(interest1, interest2)] = score
    co_interest_scores[(interest2, interest1)] = score  # Add reverse pair for easier lookup

# Combine correlation and co-interest scores
combined_scores = []
for (int1, int2), corr in correlation_matrix.unstack().items():
    if int1 != int2:
        co_score = co_interest_scores.get((int1, int2), np.nan)
        combined_scores.append((int1, int2, corr, co_score))

# Sort primarily by co-interest score (descending), then by correlation (descending)
sorted_scores = sorted(combined_scores, key=lambda x: (x[3], x[2] if not pd.isna(x[2]) else -float('inf')), reverse=True)

# Save to CSV
output_df = pd.DataFrame(sorted_scores, columns=['Topic 1', 'Topic 2', 'Correlation', 'Co-interest Score'])
output_df = output_df[['Topic 1', 'Topic 2', 'Co-interest Score', 'Correlation']]  # Reorder columns
#output_df.to_csv('ttttt.csv', index=False)

# Calculate adjusted co-interest scores
max_co_interest = output_df['Co-interest Score'].max()
adjustment_factor = 100 / max_co_interest

output_df['Adjusted Co-interest Score'] = output_df['Co-interest Score'] * adjustment_factor

# Sort by adjusted co-interest score
output_df = output_df.sort_values('Adjusted Co-interest Score', ascending=False)

# Save updated results to CSV
output_df.to_csv('topics-co-interest.csv', index=False)
print("\nResults saved")