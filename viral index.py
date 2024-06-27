import pandas as pd
import math
from datetime import datetime, timezone

# weights
today_weight = 0.6
views_weight = 0.2
responses_weight = 0.4
likes_weight = 0.5
comments_weight = 1
bookmarks_weight = 0.6
skips_weight = 0.3

polarization_weight = 0.25
engagement_weight = 0.75

# Input and output file names
input_file = './wyr-output.csv'
output_file = './stat-output.csv'
input_file2 = './wyr-output-separated.csv'
output_file2 = './stat-output-separated.csv'

df = pd.read_csv(input_file, encoding='utf-8')
df['Polarization Score'] = '' # This index ranges from 0 to 1, where 0 means no polarization (everyone chose the same option) and 1 means maximum polarization (50-50 split).
df['Engagement Score'] = ''
df['Virality Index'] = ''

for index, row in df.iterrows():

    date_added = row['Date Added']
    date_added = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
    today = datetime.now()
    difference = today - date_added.replace()
    days_diff = difference.days
    if days_diff <= 0:
        time_decay_multiplier = today_weight
    elif days_diff < 1:
        time_decay_multiplier = 1
    else:
        time_decay_multiplier = math.log(days_diff)        

    views = row['# Views']
    responses = row['# Resps']
    percent_responses = row['% R/V']
    percent_opt1 = row['% Opt1']
    percent_opt2 = row['% Opt2']
    likes = row['# Likes']
    comments = row['# Comments']
    bookmarks = row['# Bookmarks']
    skips = row['# Skips']

    polarization_score = 1 - abs(percent_opt1-percent_opt2)
    engagement_score = (views*views_weight + responses*responses_weight + likes*likes_weight + comments*comments_weight + bookmarks*bookmarks_weight - skips*skips_weight)/time_decay_multiplier
    virality_index = polarization_score*responses*polarization_weight + engagement_score*engagement_weight    
    
    df.at[index, 'Polarization Score'] = polarization_score
    df.at[index, 'Engagement Score'] = engagement_score
    df.at[index, 'Virality Index'] = virality_index

# output file to new csv
df.to_csv(output_file, index=False)

df = pd.read_csv(input_file2, encoding='utf-8')
df['Polarization Score'] = '' # This index ranges from 0 to 1, where 0 means no polarization (everyone chose the same option) and 1 means maximum polarization (50-50 split).
df['Engagement Score'] = ''
df['Virality Index'] = ''

for index, row in df.iterrows():

    date_added = row['Date Added']
    date_added = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S")
    today = datetime.now()
    difference = today - date_added.replace()
    days_diff = difference.days
    if days_diff <= 0:
        time_decay_multiplier = today_weight
    elif days_diff < 1:
        time_decay_multiplier = 1
    else:
        time_decay_multiplier = math.log(days_diff)        

    views = row['# Views']
    responses = row['# Resps']
    percent_responses = row['% R/V']
    percent_opt1 = row['% Opt1']
    percent_opt2 = row['% Opt2']
    likes = row['# Likes']
    comments = row['# Comments']
    bookmarks = row['# Bookmarks']
    skips = row['# Skips']

    polarization_score = 1 - abs(percent_opt1-percent_opt2)
    engagement_score = (views*views_weight + responses*responses_weight + likes*likes_weight + comments*comments_weight + bookmarks*bookmarks_weight - skips*skips_weight)/time_decay_multiplier
    virality_index = polarization_score*responses*polarization_weight + engagement_score*engagement_weight    
    
    df.at[index, 'Polarization Score'] = polarization_score
    df.at[index, 'Engagement Score'] = engagement_score
    df.at[index, 'Virality Index'] = virality_index

# output file to new csv
df.to_csv(output_file2, index=False)

print("Finished calculating stats on questions.")