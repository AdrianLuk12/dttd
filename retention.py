import pandas as pd


print("Started analyzing user retention data")
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

# Calculate daily active users (DAU)
daily_active_users = df.groupby('date')['persona_id'].nunique().reset_index()
daily_active_users.columns = ['date', 'dau']

# Calculate weekly active users (WAU)
df['week'] = df['action_time'].dt.to_period('W').apply(lambda r: r.start_time)
weekly_active_users = df.groupby('week')['persona_id'].nunique().reset_index()
weekly_active_users.columns = ['week', 'wau']

# Calculate monthly active users (MAU)
df['month'] = df['action_time'].dt.to_period('M').apply(lambda r: r.start_time)
monthly_active_users = df.groupby('month')['persona_id'].nunique().reset_index()
monthly_active_users.columns = ['month', 'mau']

# Calculate retention rates
first_date = df['date'].min()
last_date = df['date'].max()
date_range = pd.date_range(first_date, last_date)

# Initialize retention DataFrame
retention = pd.DataFrame(index=date_range)

# Calculate retention rates for each day
for start_date in date_range:
    cohort = df[df['date'] == start_date]['persona_id'].unique()
    for end_date in date_range:
        retained_users = df[(df['date'] == end_date) & (df['persona_id'].isin(cohort))]['persona_id'].nunique()
        retention.loc[end_date, start_date] = retained_users / len(cohort) if len(cohort) > 0 else 0

# Save the results to CSV files
user_activity.to_csv('./retention/user_activity.csv', index=False)
daily_active_users.to_csv('./retention/daily_active_users.csv', index=False)
weekly_active_users.to_csv('./retention/weekly_active_users.csv', index=False)
monthly_active_users.to_csv('./retention/monthly_active_users.csv', index=False)

print("User interaction analysis has been saved to CSV files.")