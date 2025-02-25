import pandas as pd
import ast
import os
import math
from datetime import datetime

today_weight = 0.6
views_weight = 0.1
responses_weight = 0.4
likes_weight = 0.5
comments_weight = 1
skips_weight = 0.4

# load file
entry_path = './wyr-entry.csv'
questions_path = './stat-output.csv'

output_file_path = './interest-output.csv'
final_output_path = "interest-viral-index-output.csv"
df1 = pd.read_csv(entry_path, encoding='utf-8')
df2 = pd.read_csv(questions_path, encoding='utf-8')

##### create interest score into array
df1['interests'] = ''

tags = [
    "Anime","Art","Business and Finance","Celebs","Cryptocurrency","Current Events","Dating","Ethics","Family","Fashion",
    "Fitness","Food and dining experiences","Friendship","Gaming","Global Politics","Horoscope","Hypothetical","Kpop", "LGBTQ+",
    "Life choices","Mental health","Movies","Music","Nature","New gadgets","News","Painting","Personal Experiences",
    "Personal finance tips","Social justice","Software updates","Sports","Stock market updates","TV shows","Travel",
    "US Politics","Writing"
]

for i, row in df1.iterrows():
    date_added = row['action_time']
    date_added = datetime.strptime(date_added, "%Y-%m-%d %H:%M:%S.%f")
    today = datetime.now()
    difference = today - date_added.replace()
    days_diff = difference.days
    if days_diff <= 0:
        time_decay_multiplier = today_weight
    elif days_diff < 1:
        time_decay_multiplier = 1
    else:
        time_decay_multiplier = math.log(days_diff)

    post_id = row['post_id']
    viewed = row['viewed']
    voted = row['voted']
    liked = row['liked']
    commented = row['commented']
    skipped = row['skipped']

    interests = [0] * 37
    
    # Filter DataFrame based on post_id
    filtered_dataframe = df2[df2['post_id'] == post_id]

    # Check if post_id exists
    if len(filtered_dataframe) == 0:
        print(f"No questions found for post_id '{post_id}'")
        tag_string = ""
    else:
        tag_string = filtered_dataframe.iloc[0]['Tags'] + ", "

    input_tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]

    for tag in input_tags:
        try:
            index = tags.index(tag)
            if viewed > 0:
                interests[index] += views_weight / time_decay_multiplier
            elif voted > 0:
                interests[index] += responses_weight / time_decay_multiplier
            elif liked > 0:
                interests[index] += likes_weight / time_decay_multiplier
            elif commented > 0:
                interests[index] += comments_weight / time_decay_multiplier
            elif skipped > 0:
                interests[index] -= skips_weight / time_decay_multiplier
        except ValueError:
            print(f"'{tag}' not found in the list")    

    print(str(i+1) + " - processing interaction")
    #assign tag
    df1.at[i, 'interests'] = interests

#df1['interests'] = df1['interests'].apply(ast.literal_eval)

# Group by persona_id and sum the Interests arrays
#result = df1.groupby('persona_id')['interests'].apply(lambda x: [round(sum(i),2) for i in zip(*x)])
result = df1.groupby('persona_id')['interests'].apply(lambda x: [max(0, round(sum(i), 2)) for i in zip(*x)]) # max is 0

# Reset the index to make persona_id a column again
result = result.reset_index()

# Write the result to a new CSV file
result.to_csv('interest-output.csv', index=False)
print("processed user interests")

""" # disabled adjusting interest by number of interactions
##### dividing the score by the number of interactions:
result_input_path = output_file_path

interest_df = pd.read_csv(result_input_path, encoding='utf-8')
wyr_df = pd.read_csv(entry_path, encoding='utf-8')

# Count the occurrences of each persona_id in the wyr-entry file
persona_counts = wyr_df['persona_id'].value_counts().to_dict()

# Function to divide interests by the count of persona_id in wyr-entry
def adjust_interests(row):
    persona_id = row['persona_id']
    if persona_id in persona_counts:
        count = persona_counts[persona_id]
        interests = ast.literal_eval(row['interests'])
        adjusted_interests = [i / count for i in interests]
        return adjusted_interests
    else:
        return row['interests']

# Apply the function to the interest-output dataframe
interest_df['adjusted_interests'] = interest_df.apply(adjust_interests, axis=1)

# Save the results to a new CSV file
interest_df.to_csv(output_file_path, index=False)

print("adjusted interests by number of interactions")
"""

##### splitting interest array into fields
result_input_path = output_file_path
df = pd.read_csv(result_input_path, encoding='utf-8')

# Create a list to hold the transformed data
rows_list = []

# Process each row in the input DataFrame
for index, row in df.iterrows():
    # Convert the interests string to a list
    interests = ast.literal_eval(row['interests'])
    
    # Create a new row dictionary
    new_row = {'persona_id': row['persona_id'], 'interests': row['interests']}
    
    # Populate the dictionary with interest values for each tag
    for i, tag in enumerate(tags):
        new_row[tag] = interests[i]
    
    # Append the new row to the list
    rows_list.append(new_row)

# Create a new DataFrame from the list of rows
output_df = pd.DataFrame(rows_list)

# Write the output DataFrame to a new CSV file
output_df.to_csv(final_output_path, encoding='utf-8', index=False)

os.remove(result_input_path)

print("finished spliiting interests into fields")