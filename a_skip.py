import pandas as pd

# Load the data
wyr_entry = pd.read_csv('wyr-entry.csv')
stat_output = pd.read_csv('stat-output.csv')

# Convert action_time to datetime
wyr_entry['action_time'] = pd.to_datetime(wyr_entry['action_time'])

# Extract time-related features
wyr_entry['hour'] = wyr_entry['action_time'].dt.hour
wyr_entry['day_of_week'] = wyr_entry['action_time'].dt.dayofweek
wyr_entry['is_weekend'] = wyr_entry['day_of_week'].isin([5, 6]).astype(int)

# Merge datasets
merged_data = pd.merge(wyr_entry, stat_output[['post_id', 'Caption']], on='post_id', how='left')

# Calculate skip rates
def calculate_skip_rate(group):
    return group['skipped'].sum() / len(group)

# Time of day analysis
hourly_skip_rate = merged_data.groupby('hour').apply(calculate_skip_rate).reset_index()
hourly_skip_rate.columns = ['hour', 'skip_rate']
hourly_skip_rate['analysis_type'] = 'hourly'

# Day of week analysis
daily_skip_rate = merged_data.groupby('day_of_week').apply(calculate_skip_rate).reset_index()
daily_skip_rate.columns = ['day_of_week', 'skip_rate']
daily_skip_rate['analysis_type'] = 'daily'

# Weekend vs Weekday analysis
weekend_skip_rate = merged_data.groupby('is_weekend').apply(calculate_skip_rate).reset_index()
weekend_skip_rate.columns = ['is_weekend', 'skip_rate']
weekend_skip_rate['analysis_type'] = 'weekend'

# Time in app session analysis
merged_data = merged_data.sort_values(['persona_id', 'action_time'])
merged_data['time_since_last'] = merged_data.groupby('persona_id')['action_time'].diff().dt.total_seconds()

# Bin the time since last action
merged_data['time_bin'] = pd.cut(merged_data['time_since_last'], 
                                 bins=[0, 60, 300, 600, 1800, 3600, float('inf')],
                                 labels=['0-1min', '1-5min', '5-10min', '10-30min', '30-60min', '60min+'])

time_bin_skip_rate = merged_data.groupby('time_bin').apply(calculate_skip_rate).reset_index()
time_bin_skip_rate.columns = ['time_bin', 'skip_rate']
time_bin_skip_rate['analysis_type'] = 'time_bin'

# New analysis: Time till next action after a skip
merged_data['time_to_next'] = merged_data.groupby('persona_id')['action_time'].diff().shift(-1).dt.total_seconds()
skipped_actions = merged_data[merged_data['skipped'] == 1]

time_to_next_bins = [0, 60, 300, 600, 1800, 3600, float('inf')]
time_to_next_labels = ['0-1min', '1-5min', '5-10min', '10-30min', '30-60min', '60min+']

skipped_actions['time_to_next_bin'] = pd.cut(skipped_actions['time_to_next'], bins=time_to_next_bins, labels=time_to_next_labels)
time_to_next_distribution = skipped_actions['time_to_next_bin'].value_counts(normalize=True).reset_index()
time_to_next_distribution.columns = ['time_to_next_bin', 'proportion']
time_to_next_distribution['analysis_type'] = 'time_to_next'

# Combine all analyses into a single dataframe
combined_data = pd.concat([
    hourly_skip_rate.rename(columns={'hour': 'category'}),
    daily_skip_rate.rename(columns={'day_of_week': 'category'}),
    weekend_skip_rate.rename(columns={'is_weekend': 'category'}),
    time_bin_skip_rate.rename(columns={'time_bin': 'category'}),
    time_to_next_distribution.rename(columns={'time_to_next_bin': 'category', 'proportion': 'skip_rate'})
], ignore_index=True)

# Add summary statistics
summary_stats = pd.DataFrame({
    'category': ['overall', 'total_interactions', 'total_skips'],
    'skip_rate': [
        merged_data['skipped'].mean(),
        len(merged_data),
        merged_data['skipped'].sum()
    ],
    'analysis_type': ['summary'] * 3
})

combined_data = pd.concat([combined_data, summary_stats], ignore_index=True)

# Export combined data to a single CSV file
combined_data.to_csv('combined_skip_analysis.csv', index=False)

print("Combined CSV file has been created: combined_skip_analysis.csv")

# Print some insights
print("\nSome key insights:")
print(f"Overall skip rate: {summary_stats.loc[summary_stats['category'] == 'overall', 'skip_rate'].values[0]:.2%}")
print(f"Total interactions: {summary_stats.loc[summary_stats['category'] == 'total_interactions', 'skip_rate'].values[0]:.0f}")
print(f"Total skips: {summary_stats.loc[summary_stats['category'] == 'total_skips', 'skip_rate'].values[0]:.0f}")
print(f"Hour with highest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmax(), 'hour']} ({hourly_skip_rate['skip_rate'].max():.2%})")
print(f"Hour with lowest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmin(), 'hour']} ({hourly_skip_rate['skip_rate'].min():.2%})")
print(f"Most common time to next action after a skip: {time_to_next_distribution.loc[time_to_next_distribution['proportion'].idxmax(), 'category']} ({time_to_next_distribution['proportion'].max():.2%})")