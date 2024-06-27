import pandas as pd
import csv
import os
import math
from together import Together
from datetime import datetime, timezone

client = Together(api_key="2e0923315d6b076dade12be49f205ea73836ddee710bcc30365204e4f452c655")

# load file
entry_path = './wyr-entry.csv'
questions_path = './stat-output.csv'
output_file_path = './opinion-output.csv'
df1 = pd.read_csv(entry_path, encoding='utf-8')
df2 = pd.read_csv(questions_path, encoding='utf-8')

######## TAGGING
# create column Tag
df1['interests'] = ''

for index, row in df1.iterrows():
    post_id = row['post_id']
    viewed = row['viewed']
    voted = row['voted']
    liked = row['liked']
    commented = row['commented']
    skipped = row['skipped']
    
    # Filter DataFrame based on post_id
    filtered_dataframe = df2[df2['post_id'] == post_id]

    # Check if post_id exists
    if len(filtered_dataframe) == 0:
        print(f"No questions found for post_id '{post_id}'")
        tag = ""
    else:
        tag = filtered_dataframe.iloc[0]['Tags'] + ", "

    print(str(index+1) + " - Interest added: " + tag)
    #assign tag
    df1.at[index, 'interests'] = tag

# Group by persona_id, combine interests, remove duplicates, and sort
result = df1.groupby('persona_id')['interests'].apply(lambda x: ', '.join(sorted(set(interest.strip() for row in x for interest in row.split(',')))))

# Reset index to make persona_id a column again
result = result.reset_index()

# Rename the column to 'Interests'
result.columns = ['persona_id', 'interests']

# Write the result to a new CSV file
result.to_csv('interest-output.csv', index=False)

print(result.head())

print("processed user interests")