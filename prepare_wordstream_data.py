"""
Prepare First Monday yearly text data for WordStream Maker
"""

import os
import csv

# Source data
yearly_texts_dir = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\Analysis\wordclouds\yearly_texts"

# Output file
output_path = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream\data\firstmonday-yearly-texts.csv"

# Read yearly text files and prepare data
data = []

for filename in sorted(os.listdir(yearly_texts_dir)):
    if filename.endswith("_combined.txt"):
        year = filename.split("_")[0]
        filepath = os.path.join(yearly_texts_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                full_text = f.read().strip()

            data.append({
                'Year': year,
                'FullText': full_text
            })
            print(f"Loaded {year}: {len(full_text)} characters")

        except Exception as e:
            print(f"Error loading {filename}: {e}")

# Write CSV file
try:
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Year', 'FullText']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    print(f"\nSuccessfully created WordStream data file:")
    print(f"Location: {output_path}")
    print(f"Total records: {len(data)}")
    print(f"\nYou can now import this into WordStream Maker!")

except Exception as e:
    print(f"Error writing CSV: {e}")
