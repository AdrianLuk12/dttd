import pandas as pd
import csv
import os
import math
from together import Together
from datetime import datetime

client = Together(api_key="2e0923315d6b076dade12be49f205ea73836ddee710bcc30365204e4f452c655")

# load file
#input_file_path = './Would-You-Rather_v2__1718936223855.csv'
input_file_path = './wyr-questions.csv'
output_file_path = './wyr-output.csv'
separated_output_file_path = './wyr-output-separated.csv'
df = pd.read_csv(input_file_path, encoding='utf-8')



######## TAGGING


# create column Tag
df['Tags'] = ''

# head of df before processing
print(df.head())

tags = [
    "News", "Global Politics", "US Politics", "Music", "Movies", "TV shows", "Anime", "Kpop", "Celebs", "Sports", 
    "Gaming", "Fashion", "New gadgets", "Software updates", "Personal Experiences", "Horoscope", "Dating", "Friendship", 
    "Family", "Travel", "Food and dining experiences", "Business and Finance", "Stock market updates", "Cryptocurrency", 
    "Personal finance tips", "Fitness", "Mental health", "Social justice", "LGBTQ+", "Nature", "Ethics", "Current Events", 
    "Writing", "Painting", "Art", "Hypothetical", "Life choices"
]

for index, row in df.iterrows():
    q1 = row['Option 1']
    q2 = row['Option 2']

    prompt = "Assign one or multiple tags from the following list with the closest relation/meaning to BOTH options in the question \"Would you rather " + q1 + " or " + q2 + "?\" ONLY OUTPUT THE TAG/TAGS SEPARATED BY COMMAS, ONLY USE TAGS PROVIDED FROM THE LIST. DO NOT INCLUDE TAG IF ONLY ONE OPTION IS RELATED TO THE TOPIC. Tags: 'News' 'Global Politics' 'US Politics' 'Music' 'Movies' 'TV shows' 'Anime' 'Kpop' 'Celebs' 'Sports' 'Gaming' 'Fashion' 'New gadgets' 'Software updates' 'Personal Experiences' 'Horoscope' 'Dating' 'Friendship' 'Family' 'Travel' 'Food and dining experiences' 'Business and Finance' 'Stock market updates' 'Cryptocurrency' 'Personal finance tips' 'Fitness' 'Mental health' 'Social justice' 'LGBTQ+' 'Nature' 'Ethics' 'Current Events' 'Writing' 'Painting' 'Art' 'Hypothetical' 'Life choices'"

    response = client.chat.completions.create(
        #model="mistralai/Mistral-7B-Instruct-v0.3", # less accurate
        model="meta-llama/Llama-3-70b-chat-hf", # more accurate but costs more
        messages=[{"role": "user", "content": prompt}],
    )

    result = response.choices[0].message.content
    print(str(index+1) + " - RAW: " + result)

    removed_quotes = result.replace("'", "")

    # split string
    compared = removed_quotes.split(',')
    # strip spaces
    compared = [c.strip() for c in compared]
    # filter values to ensure ai tags are tags provided
    filtered_values = [c for c in compared if c in tags]
    # sort tags alphabetically
    sorted_values = sorted(filtered_values)
    # join filtered values back into a comma-separated string
    filtered_string = ', '.join(sorted_values)
    
    if filtered_string == "":
        filtered_string = "Hypothetical"

    print(str(index+1) + " - FILTERED: " + filtered_string)
    #assign tag
    df.at[index, 'Tags'] = filtered_string

    df.to_csv(output_file_path, index=False)


# head of df after processing
print(df.head())

# output file to new csv
#df.to_csv(output_file_path, index=False)

print("Finished categorizing topics for WYR questions.")


######## SEPARATING TAGS

# read the output file
with open(output_file_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['Tag'] 

    # write the final output file
    with open(separated_output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        # split the tags by comma and space
        for row in reader:
            tags = row['Tags'].split(', ')
            for tag in tags:
                new_row = row.copy()
                new_row['Tag'] = tag
                writer.writerow(new_row)

print("Tags have been processed to be separated.")


######## CALCULATING STATS


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

os.remove(input_file)
os.remove(input_file2)

print("Finished calculating stats on questions.")