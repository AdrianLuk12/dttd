import csv

# Input and output file names
input_file = './questions_tagged.csv'
output_file = './output.csv'

# Read the original CSV file
with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['Tags']  # Add a new 'Tag' field for individual tags

    # Prepare the output file
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            tags = row['Tag'].split(', ')  # Split the tags by comma and space
            for tag in tags:
                new_row = row.copy()
                new_row['Tags'] = tag
                writer.writerow(new_row)

print(f"Processed data has been written to {output_file}")