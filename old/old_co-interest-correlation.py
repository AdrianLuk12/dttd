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
    df[f'{col}_prop'] = df[col] / df['total']

# Calculate correlation matrix
prop_columns = [col for col in df.columns if col.endswith('_prop')]
correlation_matrix = df[prop_columns].corr()

# Calculate co-interest scores
def calculate_co_interest(df, interest1, interest2, threshold=0):
    both = ((df[interest1] > threshold) & (df[interest2] > threshold)).sum()
    either = ((df[interest1] > threshold) | (df[interest2] > threshold)).sum()
    return both / either if either > 0 else 0

co_interest_scores = {}
for interest1, interest2 in combinations(interest_columns, 2):
    score = calculate_co_interest(df, interest1, interest2)
    co_interest_scores[(interest1, interest2)] = score
    co_interest_scores[(interest2, interest1)] = score  # Add reverse pair for easier lookup

# Combine correlation and co-interest scores
combined_scores = []
for (int1, int2), corr in correlation_matrix.unstack().items():
    if int1 != int2:
        int1_name = int1.replace('_prop', '')
        int2_name = int2.replace('_prop', '')
        co_score = co_interest_scores.get((int1_name, int2_name), np.nan)
        combined_scores.append((int1_name, int2_name, corr, co_score))

# Sort primarily by co-interest score (descending), then by correlation (descending)
sorted_scores = sorted(combined_scores, key=lambda x: (x[3], x[2] if not pd.isna(x[2]) else -float('inf')), reverse=True)

# Print results
print("Topic 1 | Topic 2 | Co-interest Score | Correlation")
print("-" * 60)
for int1, int2, corr, co_score in sorted_scores:
    print(f"{int1:<9} | {int2:<9} | {co_score:17.3f} | {corr:11.3f}")

# Save to CSV
output_df = pd.DataFrame(sorted_scores, columns=['Topic 1', 'Topic 2', 'Correlation', 'Co-interest Score'])
output_df = output_df[['Topic 1', 'Topic 2', 'Co-interest Score', 'Correlation']]  # Reorder columns
output_df.to_csv('topic-co-interest.csv', index=False)
print("\nResults saved")

# Print summary statistics
print("\nSummary Statistics:")
print(f"Highest co-interest score: {output_df['Co-interest Score'].max():.3f}")
print(f"Lowest co-interest score: {output_df['Co-interest Score'].min():.3f}")
print(f"Average co-interest score: {output_df['Co-interest Score'].mean():.3f}")
print(f"Median co-interest score: {output_df['Co-interest Score'].median():.3f}")
print(f"\nNumber of interest pairs: {len(output_df)}")