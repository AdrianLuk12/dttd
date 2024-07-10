import pandas as pd
import numpy as np

# Load the data
wyr_entry = pd.read_csv('wyr-entry.csv')

# Convert action_time to datetime
wyr_entry['action_time'] = pd.to_datetime(wyr_entry['action_time'])

# Extract time-related features
wyr_entry['hour'] = wyr_entry['action_time'].dt.hour
wyr_entry['day_of_week'] = wyr_entry['action_time'].dt.day_name()
wyr_entry['is_weekend'] = wyr_entry['action_time'].dt.dayofweek.isin([5, 6]).map({True: 'weekend', False: 'weekday'})

# Calculate skip rates by skip / total interaction
"""
def calculate_skip_rate(group):
    return group['skipped'].sum() / len(group) * 100
"""

# Calculate skip rates by skip / total views
def calculate_skip_rate(group):
    total_views = group['viewed'].sum()
    if total_views == 0:
        return 0
    return group['skipped'].sum() / total_views * 100

# Time of day analysis
hourly_skip_rate = wyr_entry.groupby('hour').apply(calculate_skip_rate).reset_index()
hourly_skip_rate.columns = ['hour', 'skip_rate']

# Day of week analysis
daily_skip_rate = wyr_entry.groupby('day_of_week').apply(calculate_skip_rate).reset_index()
daily_skip_rate.columns = ['day_of_week', 'skip_rate']

# Weekend vs Weekday analysis
weekend_skip_rate = wyr_entry.groupby('is_weekend').apply(calculate_skip_rate).reset_index()
weekend_skip_rate.columns = ['is_weekend', 'skip_rate']

# Time in app session analysis
wyr_entry = wyr_entry.sort_values(['persona_id', 'action_time'])
wyr_entry['time_since_last'] = wyr_entry.groupby('persona_id')['action_time'].diff().dt.total_seconds()

# Bin the time since last action
time_bins = [0, 60, 300, 600, 1800, 3600, float('inf')]
time_labels = ['0-1min', '1-5min', '5-10min', '10-30min', '30-60min', '60min+']
wyr_entry['time_bin'] = pd.cut(wyr_entry['time_since_last'], bins=time_bins, labels=time_labels)

time_bin_skip_rate = wyr_entry.groupby('time_bin').apply(calculate_skip_rate).reset_index()
time_bin_skip_rate.columns = ['category', 'skip_rate']

# New analysis: Time till next action after a skip
wyr_entry['time_to_next'] = wyr_entry.groupby('persona_id')['action_time'].diff().shift(-1).dt.total_seconds()
skipped_actions = wyr_entry[wyr_entry['skipped'] == 1].copy()  # Create a copy to avoid SettingWithCopyWarning

skipped_actions['time_to_next_bin'] = pd.cut(skipped_actions['time_to_next'], bins=time_bins, labels=time_labels)
time_to_next_distribution = skipped_actions['time_to_next_bin'].value_counts(normalize=True).reset_index()
time_to_next_distribution.columns = ['category', 'skip_rate']

# Export results to CSV files
hourly_skip_rate.to_csv('./skips/hourly_skip_rate.csv', index=False)
daily_skip_rate.to_csv('./skips/daily_skip_rate.csv', index=False)
weekend_skip_rate.to_csv('./skips/weekend_skip_rate.csv', index=False)
time_bin_skip_rate.to_csv('./skips/time_bin_skip_rate.csv', index=False)
time_to_next_distribution.to_csv('./skips/time_to_next_distribution.csv', index=False)

# Create a summary dataframe for overall statistics
summary_stats = pd.DataFrame({
    'overall_skip_rate': [calculate_skip_rate(wyr_entry)],
    #'total_interactions': [len(wyr_entry)],
    'total_skips': [wyr_entry['skipped'].sum()],
    'total_views': [wyr_entry['viewed'].sum()]
})

summary_stats.to_csv('./skips/summary_stats.csv', index=False)

print("CSV files have been created:")
print("1. hourly_skip_rate.csv")
print("2. daily_skip_rate.csv")
print("3. weekend_skip_rate.csv")
print("4. time_bin_skip_rate.csv")
print("5. time_to_next_distribution.csv")
print("6. summary_stats.csv")

# Optional: Print some insights
print("\nSome key insights:")
print(f"Overall skip rate: {summary_stats['overall_skip_rate'].values[0] / 100:.2%}")
#print(f"Total interactions: {summary_stats['total_interactions'].values[0]:.0f}")
print(f"Total skips: {summary_stats['total_skips'].values[0]:.0f}")
print(f"Total views: {summary_stats['total_views'].values[0]:.0f}")
print(f"Hour with highest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmax(), 'hour']} ({hourly_skip_rate['skip_rate'].max() / 100:.2%})")
print(f"Hour with lowest skip rate: {hourly_skip_rate.loc[hourly_skip_rate['skip_rate'].idxmin(), 'hour']} ({hourly_skip_rate['skip_rate'].min() / 100:.2%})")