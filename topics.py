import pandas as pd
import csv
from together import Together

client = Together(api_key="2e0923315d6b076dade12be49f205ea73836ddee710bcc30365204e4f452c655")

# load file
input_file_path = './Would-You-Rather_v2__1718936223855.csv'
output_file_path = './wyr-output.csv'
separated_output_file_path = './wyr-output-separated.csv'
df = pd.read_csv(input_file_path, encoding='utf-8')

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

    prompt = "Assign one or multiple tags from the following list with the closest relation/meaning to the question \"Would you rather " + q1 + " or " + q2 + "?\" ONLY OUTPUT THE TAG/TAGS SEPARATED BY COMMAS, ONLY USE TAGS PROVIDED FROM THE LIST. Tags: 'News' 'Global Politics' 'US Politics' 'Music' 'Movies' 'TV shows' 'Anime' 'Kpop' 'Celebs' 'Sports' 'Gaming' 'Fashion' 'New gadgets' 'Software updates' 'Personal Experiences' 'Horoscope' 'Dating' 'Friendship' 'Family' 'Travel' 'Food and dining experiences' 'Business and Finance' 'Stock market updates' 'Cryptocurrency' 'Personal finance tips' 'Fitness' 'Mental health' 'Social justice' 'LGBTQ+' 'Nature' 'Ethics' 'Current Events' 'Writing' 'Painting' 'Art' 'Hypothetical' 'Life choices'"

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


# head of df after processing
print(df.head())

# output file to new csv
df.to_csv(output_file_path, index=False)

print("Finished categorizing topics for WYR questions.")

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