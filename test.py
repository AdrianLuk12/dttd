import pandas as pd
import csv
import os
import math
from together import Together
from datetime import datetime, timezone

class WYRProcessor:
    def __init__(self, api_key, input_file_path, output_file_path, separated_output_file_path):
        self.client = Together(api_key=api_key)
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.separated_output_file_path = separated_output_file_path
        self.df = pd.read_csv(input_file_path, encoding='utf-8')
        self.tags = [
            "News", "Global Politics", "US Politics", "Music", "Movies", "TV shows", "Anime", "Kpop", "Celebs", "Sports", 
            "Gaming", "Fashion", "New gadgets", "Software updates", "Personal Experiences", "Horoscope", "Dating", "Friendship", 
            "Family", "Travel", "Food and dining experiences", "Business and Finance", "Stock market updates", "Cryptocurrency", 
            "Personal finance tips", "Fitness", "Mental health", "Social justice", "LGBTQ+", "Nature", "Ethics", "Current Events", 
            "Writing", "Painting", "Art", "Hypothetical", "Life choices"
        ]

    def add_tags(self):
        self.df['Tags'] = ''

        for index, row in self.df.iterrows():
            q1 = row['Option 1']
            q2 = row['Option 2']

            prompt = (
                "Assign one or multiple tags from the following list with the closest relation/meaning to BOTH options "
                "in the question 'Would you rather {} or {}?' ONLY OUTPUT THE TAG/TAGS SEPARATED BY COMMAS, "
                "ONLY USE TAGS PROVIDED FROM THE LIST. DO NOT INCLUDE TAG IF ONLY ONE OPTION IS RELATED TO THE TOPIC. "
                "Tags: {}".format(q1, q2, ' '.join([f"'{tag}'" for tag in self.tags]))
            )

            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",
                messages=[{"role": "user", "content": prompt}],
            )

            print("tagging")

            result = response.choices[0].message.content
            removed_quotes = result.replace("'", "")

            compared = removed_quotes.split(',')
            compared = [c.strip() for c in compared]
            filtered_values = [c for c in compared if c in self.tags]
            sorted_values = sorted(filtered_values)
            filtered_string = ', '.join(sorted_values)

            if not filtered_string:
                filtered_string = "Hypothetical"

            self.df.at[index, 'Tags'] = filtered_string

        self.df.to_csv(self.output_file_path, index=False)

    def separate_tags(self):
        with open(self.output_file_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['Tag']

            with open(self.separated_output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    tags = row['Tags'].split(', ')
                    for tag in tags:
                        new_row = row.copy()
                        new_row['Tag'] = tag
                        writer.writerow(new_row)

    def calculate_stats(self, input_file, output_file):
        df = pd.read_csv(input_file, encoding='utf-8')
        df['Polarization Score'] = ''
        df['Engagement Score'] = ''
        df['Virality Index'] = ''

        today_weight = 0.6
        views_weight = 0.2
        responses_weight = 0.4
        likes_weight = 0.5
        comments_weight = 1
        bookmarks_weight = 0.6
        skips_weight = 0.3
        polarization_weight = 0.25
        engagement_weight = 0.75

        for index, row in df.iterrows():
            date_added = datetime.strptime(row['Date Added'], "%Y-%m-%d %H:%M:%S")
            today = datetime.now()
            days_diff = (today - date_added).days
            time_decay_multiplier = (
                today_weight if days_diff <= 0 else 
                1 if days_diff < 1 else 
                math.log(days_diff)
            )

            views = row['# Views']
            responses = row['# Resps']
            percent_responses = row['% R/V']
            percent_opt1 = row['% Opt1']
            percent_opt2 = row['% Opt2']
            likes = row['# Likes']
            comments = row['# Comments']
            bookmarks = row['# Bookmarks']
            skips = row['# Skips']

            polarization_score = 1 - abs(percent_opt1 - percent_opt2)
            engagement_score = (
                (views * views_weight + responses * responses_weight + likes * likes_weight + 
                comments * comments_weight + bookmarks * bookmarks_weight - skips * skips_weight) / 
                time_decay_multiplier
            )
            virality_index = (polarization_score * responses * polarization_weight + 
                              engagement_score * engagement_weight)

            df.at[index, 'Polarization Score'] = polarization_score
            df.at[index, 'Engagement Score'] = engagement_score
            df.at[index, 'Virality Index'] = virality_index

        df.to_csv(output_file, index=False)

    def process(self):
        self.add_tags()
        print("Finished categorizing topics for WYR questions.")
        self.separate_tags()
        print("Tags have been processed to be separated.")
        self.calculate_stats(self.output_file_path, './stat-output.csv')
        self.calculate_stats(self.separated_output_file_path, './stat-output-separated.csv')
        os.remove(self.output_file_path)
        os.remove(self.separated_output_file_path)
        print("Finished calculating stats on questions.")

if __name__ == "__main__":
    processor = WYRProcessor(
        api_key="2e0923315d6b076dade12be49f205ea73836ddee710bcc30365204e4f452c655",
        #input_file_path='./Would-You-Rather_v2__1718936223855.csv',
        input_file_path='./wyr-questions.csv',
        output_file_path='./wyr-output.csv',
        separated_output_file_path='./wyr-output-separated.csv'
    )
    processor.process()