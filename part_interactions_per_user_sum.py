import pandas as pd

print("started per interaction analysis")

# Load the second CSV file
file_path = 'wyr-entry.csv'
df = pd.read_csv(file_path)

# Group by persona_id and compute metrics
user_behavior = df.groupby('persona_id').agg(
    num_posts_viewed=('viewed', 'sum'),
    num_posts_voted=('voted', 'sum'),
    num_posts_liked=('liked', 'sum'),
    num_posts_commented=('commented', 'sum'),
    num_posts_skipped=('skipped', 'sum')
).reset_index()

# Optional: Save the user behavior analysis to a CSV file
output_path = './retention/user_interaction_sum.csv'
user_behavior.to_csv(output_path, index=False)

print("User behavior analysis has been saved to", output_path)
print(user_behavior.head())