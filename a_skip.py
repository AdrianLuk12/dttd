import pandas as pd
import numpy as np

# Load only the wyr-entry data
wyr_entry = pd.read_csv('wyr-entry.csv')

# Convert action_time to datetime
wyr_entry['action_time'] = pd.to_datetime(wyr_entry['action_time'])

# Extract time-related features
wyr_entry['hour'] = wyr_entry['action_time'].dt.hour
wyr_entry['day_of_week'] = wyr_entry['action_time'].dt.dayofweek
wyr_entry['is_weekend'] = wyr_entry['day_of_week'].isin([5, 6]).astype(int)

# Calculate skip rates
def calculate_skip_rate(group):
    return group['skipped'].sum() / len(group)

# Time of day analysis
hourly_skip_rate = wyr_entry.groupby('hour').apply(calculate_skip_rate).reset_index()
hourly_skip_rate.columns = ['category', 'skip_rate']
hourly_skip_rate['analysis_type'] = 'hourly'

# Day of week analysis
daily_skip_rate = wyr_entry.groupby('day_of_week').apply(calculate_skip_rate).reset_index()
daily_skip_rate.columns = ['category', 'skip_rate']
daily_skip_rate['analysis_type'] = 'daily'

# Weekend vs Weekday analysis
weekend_skip_rate = wyr_entry.groupby('is_weekend').apply(calculate_skip_rate).reset_index()
weekend_skip_rate.columns = ['category', 'skip_rate']
weekend_skip_rate['analysis_type'] = 'weekend'

# Time in app session analysis
wyr_entry = wyr_entry.sort_values(['persona_id', 'action_time'])
wyr_entry['time_since_last'] = wyr_entry.groupby('persona_id')['action_time'].diff().dt.total_seconds()

# Bin the time since last action
time_bins = [0, 60, 300, 600, 1800, 3600, float('inf')]
time_labels = ['0-1min', '1-5min', '5-10min', '10-30min', '30-60min', '60min+']
wyr_entry['time_bin'] = pd.cut(wyr_entry['time_since_last'], bins=time_bins, labels=time_labels)

time_bin_skip_rate = wyr_entry.groupby('time_bin').apply(calculate_skip_rate).reset_index()
time_bin_skip_rate.columns = ['category', 'skip_rate']
time_bin_skip_rate['analysis_type'] = 'time_bin'

# New analysis: Time till next action after a skip
wyr_entry['time_to_next'] = wyr_entry.groupby('persona_id')['action_time'].diff().shift(-1).dt.total_seconds()
skipped_actions = wyr_entry[wyr_entry['skipped'] == 1].copy()  # Create a copy to avoid SettingWithCopyWarning

skipped_actions['time_to_next_bin'] = pd.cut(skipped_actions['time_to_next'], bins=time_bins, labels=time_labels)
time_to_next_distribution = skipped_actions['time_to_next_bin'].value_counts(normalize=True).reset_index()
time_to_next_distribution.columns = ['category', 'skip_rate']
time_to_next_distribution['analysis_type'] = 'time_to_next'

# Combine all analyses into a single dataframe
combined_data = pd.concat([
    hourly_skip_rate,
    daily_skip_rate,
    weekend_skip_rate,
    time_bin_skip_rate,
    time_to_next_distribution
], ignore_index=True)

# Add summary statistics
summary_stats = pd.DataFrame({
    'category': ['overall', 'total_interactions', 'total_skips'],
    'skip_rate': [
        wyr_entry['skipped'].mean(),
        len(wyr_entry),
        wyr_entry['skipped'].sum()
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
print(f"Hour with highest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmax(), 'category']} ({hourly_skip_rate['skip_rate'].max():.2%})")
print(f"Hour with lowest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmin(), 'category']} ({hourly_skip_rate['skip_rate'].min():.2%})")

# Check if time_to_next_distribution is not empty before accessing its max value
if not time_to_next_distribution.empty:
    print(f"Most common time to next action after a skip: {time_to_next_distribution.loc[time_to_next_distribution['skip_rate'].idxmax(), 'category']} ({time_to_next_distribution['skip_rate'].max():.2%})")
else:
    print("No data available for time to next action after a skip.")