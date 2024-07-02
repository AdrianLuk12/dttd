import pandas as pd
import ast

views_weight = 0.2
responses_weight = 0.4
likes_weight = 0.5
comments_weight = 1
bookmarks_weight = 0.6
skips_weight = 0.4

# load file
entry_path = './wyr-entry.csv'
questions_path = './stat-output.csv'
output_file_path = './opinion-output.csv'
df1 = pd.read_csv(entry_path, encoding='utf-8')
df2 = pd.read_csv(questions_path, encoding='utf-8')

######## TAGGING
# create column Tag
df1['interests'] = ''

tags = [
    "Anime","Art","Business and Finance","Celebs","Cryptocurrency","Current Events","Dating","Ethics","Family","Fashion",
    "Fitness","Food and dining experiences","Friendship","Gaming","Global Politics","Horoscope","Hypothetical","Kpop", "LGBTQ+",
    "Life choices","Mental health","Movies","Music","Nature","New gadgets","News","Painting","Personal Experiences",
    "Personal finance tips","Social justice","Software updates","Sports","Stock market updates","TV shows","Travel",
    "US Politics","Writing"
]

"""

for i, row in df1.iterrows():
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
                interests[index] += views_weight
            elif voted > 0:
                interests[index] += responses_weight
            elif liked > 0:
                interests[index] += likes_weight
            elif commented > 0:
                interests[index] += comments_weight
            elif skipped > 0:
                interests[index] -= skips_weight
        except ValueError:
            print(f"'{tag}' not found in the list")    

    print(str(i+1) + " - processing interaction")
    #assign tag
    df1.at[i, 'interests'] = interests

#df1['interests'] = df1['interests'].apply(ast.literal_eval)

# Group by persona_id and sum the Interests arrays
result = df1.groupby('persona_id')['interests'].apply(lambda x: [round(sum(i),2) for i in zip(*x)])

# Reset the index to make persona_id a column again
result = result.reset_index()

# Write the result to a new CSV file
result.to_csv('interest-output.csv', index=False)

print(result.head())

print("processed user interests")

"""
result_input_path = 'interest-output.csv'
final_output_path = "interest-viral-index-output.csv"
df = pd.read_csv(result_input_path, encoding='utf-8')

for i in range(len(tags)):
    for k, rows in df.iterrows():
        values = rows['interests']
        t = ast.literal_eval(values)
        df[tags[i]] = t[i]

df.to_csv(final_output_path, encoding='utf-8', index=False)