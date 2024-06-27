import pandas as pd

views_weight = 0.2
responses_weight = 0.4
likes_weight = 0.5
comments_weight = 1
bookmarks_weight = 0.6
skips_weight = 0.3

print("Starting user activity analysis")

# Load the second CSV file
file_path = 'wyr-entry.csv'
df = pd.read_csv(file_path)

# Convert action_time to datetime format
df['action_time'] = pd.to_datetime(df['action_time'])

# Extract date from action_time
df['date'] = df['action_time'].dt.date

# Calculate first and last interaction date for each user
user_activity = df.groupby('persona_id').agg(
    first_interaction=('date', 'min'),
    last_interaction=('date', 'max')
).reset_index()

# Calculate the number of unique days each user interacted with the app
user_activity['num_active_days'] = df.groupby('persona_id')['date'].nunique().values

# Calculate engagement metrics per user
user_engagement = df.groupby('persona_id').agg(
    num_views=('viewed', 'sum'),
    num_responses=('voted', 'sum'),
    num_likes=('liked', 'sum'),
    num_bookmarks=('commented', 'sum'),
    num_comments=('commented', 'sum'),
    num_skips=('skipped', 'sum')
).reset_index()

# Calculate a total user engagement index
user_activity['Engagement_Score'] = (
    user_engagement['num_views'] * views_weight + 
    user_engagement['num_responses'] * responses_weight +
    user_engagement['num_likes'] * likes_weight +
    user_engagement['num_bookmarks'] * bookmarks_weight +
    user_engagement['num_comments'] * comments_weight -
    user_engagement['num_skips'] * skips_weight
)

# Calculate daily active users (DAU)
daily_active_users = df.groupby('date')['persona_id'].nunique().reset_index()
daily_active_users.columns = ['date', 'dau']

# Calculate weekly active users (WAU)
df['week'] = df['action_time'].dt.to_period('W').apply(lambda r: r.start_time)
weekly_active_users = df.groupby('week')['persona_id'].nunique().reset_index()
weekly_active_users.columns = ['date', 'wau']

# Calculate monthly active users (MAU)
df['month'] = df['action_time'].dt.to_period('M').apply(lambda r: r.start_time)
monthly_active_users = df.groupby('month')['persona_id'].nunique().reset_index()
monthly_active_users.columns = ['date', 'mau']

# Ensure all date columns are in datetime format
daily_active_users['date'] = pd.to_datetime(daily_active_users['date'])
weekly_active_users['date'] = pd.to_datetime(weekly_active_users['date'])
monthly_active_users['date'] = pd.to_datetime(monthly_active_users['date'])

# Create a date range for the entire period of the dataset
first_date = df['date'].min()
last_date = df['date'].max()
date_range = pd.date_range(first_date, last_date)

# Initialize a DataFrame with the date range
combined_df = pd.DataFrame(date_range, columns=['date'])

# Merge daily, weekly, and monthly active users into the combined DataFrame
combined_df = pd.merge(combined_df, daily_active_users, on='date', how='left')
combined_df = pd.merge(combined_df, weekly_active_users, on='date', how='left')
combined_df = pd.merge(combined_df, monthly_active_users, on='date', how='left')

# Save the combined DataFrame to a CSV file
user_activity.to_csv('./retention/user-activity.csv', index=False)
combined_df.to_csv('./retention/user-retention.csv', index=False)

print("Completed user activity analysis.")
print(user_activity.head(30))