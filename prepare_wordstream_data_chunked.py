"""
Prepare First Monday data for WordStream Maker with different granularity options
"""

import os
import csv

yearly_texts_dir = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\Analysis\wordclouds\yearly_texts"

# Option 1: By Year (your current approach - most data)
print("Creating yearly dataset...")
output_path_yearly = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream\data\firstmonday-yearly.csv"

data = []
for filename in sorted(os.listdir(yearly_texts_dir)):
    if filename.endswith("_combined.txt"):
        year = filename.split("_")[0]
        filepath = os.path.join(yearly_texts_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read().strip()

        data.append({'Year': year, 'Text': full_text})

with open(output_path_yearly, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Year', 'Text'])
    writer.writeheader()
    writer.writerows(data)

print(f"Created yearly dataset: {len(data)} rows")

# Option 2: By Decade (sampled - less data for faster processing)
print("\nCreating decade dataset...")
output_path_decade = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream\data\firstmonday-by-decade.csv"

data_decade = []
decades = {}

for filename in sorted(os.listdir(yearly_texts_dir)):
    if filename.endswith("_combined.txt"):
        year = int(filename.split("_")[0])
        decade = (year // 10) * 10  # e.g., 1996 -> 1990, 2005 -> 2000
        decade_label = f"{decade}s"
        filepath = os.path.join(yearly_texts_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if decade_label not in decades:
            decades[decade_label] = text
        else:
            decades[decade_label] += " " + text

for decade, text in sorted(decades.items()):
    data_decade.append({'Decade': decade, 'Text': text})

with open(output_path_decade, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Decade', 'Text'])
    writer.writeheader()
    writer.writerows(data_decade)

print(f"Created decade dataset: {len(data_decade)} rows")

# Option 3: By 5-year periods
print("\nCreating 5-year period dataset...")
output_path_5yr = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\maker-wordstream\data\firstmonday-by-5-years.csv"

data_5yr = []
periods = {}

for filename in sorted(os.listdir(yearly_texts_dir)):
    if filename.endswith("_combined.txt"):
        year = int(filename.split("_")[0])
        period_start = (year // 5) * 5
        period_label = f"{period_start}-{period_start+4}"
        filepath = os.path.join(yearly_texts_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if period_label not in periods:
            periods[period_label] = text
        else:
            periods[period_label] += " " + text

for period, text in sorted(periods.items()):
    data_5yr.append({'Period': period, 'Text': text})

with open(output_path_5yr, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Period', 'Text'])
    writer.writeheader()
    writer.writerows(data_5yr)

print(f"Created 5-year period dataset: {len(data_5yr)} rows")

print("\n" + "="*60)
print("WORDSTREAM DATA FILES CREATED")
print("="*60)
print(f"\n1. Yearly (30 rows - MOST DATA):")
print(f"   {output_path_yearly}")
print(f"\n2. By Decade (3 rows - FASTEST, LEAST DETAIL):")
print(f"   {output_path_decade}")
print(f"\n3. By 5-Year Period (6 rows - GOOD BALANCE):")
print(f"   {output_path_5yr}")
print(f"\n→ Try importing the 5-year or decade version first!")
print("  These will load much faster while still showing trends.")
