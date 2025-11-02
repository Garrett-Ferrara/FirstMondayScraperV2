import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import re
import os
from collections import defaultdict
from scipy import stats

# Set up professional style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']
plt.rcParams['font.size'] = 9
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['grid.color'] = '#e0e0e0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.4

# Create the analysis folder structure
analysis_folder = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\Analysis\frequency_trends"
os.makedirs(analysis_folder, exist_ok=True)

excel_path = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\all_articles_with_issue_info.xlsx"

# Load the data
df = pd.read_excel(excel_path)

# Define words and phrases to track
words = ['rhetoric', 'composition', 'discourse', 'writing', 'identity']
phrases = ['digital media', 'public sphere', 'civic engagement', 'digital divide', 'online communities']

# All terms to track
all_terms = words + phrases

# Initialize frequency dict by year
frequency_by_year = {}
for year in range(1996, 2026):
    frequency_by_year[str(year)] = {term: 0 for term in all_terms}

# Process each article
for idx, row in df.iterrows():
    year = str(row['year'])
    full_text = str(row['full_text']).lower() if pd.notna(row['full_text']) else ""

    if full_text and full_text != 'nan' and year in frequency_by_year:
        # Count single words
        for word in words:
            pattern = r'\b' + word + r'\b'
            count = len(re.findall(pattern, full_text))
            frequency_by_year[year][word] += count

        # Count phrases
        for phrase in phrases:
            count = full_text.count(phrase)
            frequency_by_year[year][phrase] += count

# Convert to DataFrame for easier plotting
years = sorted(frequency_by_year.keys(), key=int)
years_numeric = np.arange(len(years))
data_for_plot = {term: [] for term in all_terms}

for year in years:
    for term in all_terms:
        data_for_plot[term].append(frequency_by_year[year][term])

# Professional color palette
colors_words = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
colors_phrases = ['#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# 1. Combined graph for all terms (stacked area with visible lines)
fig, ax = plt.subplots(figsize=(7, 5))

all_data = [data_for_plot[term] for term in all_terms]
colors_combined = colors_words + colors_phrases

# Calculate cumulative sums for stacking
cumulative = np.zeros(len(years))
for i, (term_data, color) in enumerate(zip(all_data, colors_combined)):
    term_array = np.array(term_data)
    # Fill the area between cumulative and cumulative+term_data
    ax.fill_between(range(len(years)), cumulative, cumulative + term_array,
                     color=color, alpha=0.15, label=all_terms[i].title())
    # Draw a line at the top of this stacked section
    ax.plot(range(len(years)), cumulative + term_array, color=color, linewidth=1.5, alpha=0.9)
    cumulative += term_array

# Convert x-axis back to year labels
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years, rotation=45)

ax.set_xlabel('Year', fontsize=10, fontweight='bold')
ax.set_ylabel('Frequency (Raw Count)', fontsize=10, fontweight='bold')
ax.set_title('Frequency Trends of Rhetoric/Composition and Digital Terms\nin First Monday Journal (1996–2025)',
             fontsize=11, fontweight='bold', pad=12)
ax.legend(loc='upper left', fontsize=8, framealpha=0.95, edgecolor='gray', ncol=2)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
output_path = os.path.join(analysis_folder, "01_all_terms_combined.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: 01_all_terms_combined.png")

# 2. Graph for just words (stacked area with visible lines)
fig, ax = plt.subplots(figsize=(7, 5))

words_data = [data_for_plot[word] for word in words]

# Calculate cumulative sums for stacking
cumulative = np.zeros(len(years))
for i, (word_data, color) in enumerate(zip(words_data, colors_words)):
    word_array = np.array(word_data)
    # Fill the area between cumulative and cumulative+word_data
    ax.fill_between(range(len(years)), cumulative, cumulative + word_array,
                     color=color, alpha=0.15, label=words[i].title())
    # Draw a line at the top of this stacked section
    ax.plot(range(len(years)), cumulative + word_array, color=color, linewidth=1.5, alpha=0.9)
    cumulative += word_array

# Convert x-axis back to year labels
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years, rotation=45)

ax.set_xlabel('Year', fontsize=10, fontweight='bold')
ax.set_ylabel('Frequency (Raw Count)', fontsize=10, fontweight='bold')
ax.set_title('Rhetoric and Composition Terms: Frequency Trends\nin First Monday Journal (1996–2025)',
             fontsize=11, fontweight='bold', pad=12)
ax.legend(loc='upper left', fontsize=8, framealpha=0.95, edgecolor='gray')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
output_path = os.path.join(analysis_folder, "02_words_only.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: 02_words_only.png")

# 3. Graph for just phrases (stacked area with visible lines)
fig, ax = plt.subplots(figsize=(7, 5))

phrases_data = [data_for_plot[phrase] for phrase in phrases]

# Calculate cumulative sums for stacking
cumulative = np.zeros(len(years))
for i, (phrase_data, color) in enumerate(zip(phrases_data, colors_phrases)):
    phrase_array = np.array(phrase_data)
    # Fill the area between cumulative and cumulative+phrase_data
    ax.fill_between(range(len(years)), cumulative, cumulative + phrase_array,
                     color=color, alpha=0.15, label=phrases[i].title())
    # Draw a line at the top of this stacked section
    ax.plot(range(len(years)), cumulative + phrase_array, color=color, linewidth=1.5, alpha=0.9)
    cumulative += phrase_array

# Convert x-axis back to year labels
ax.set_xticks(range(len(years)))
ax.set_xticklabels(years, rotation=45)

ax.set_xlabel('Year', fontsize=10, fontweight='bold')
ax.set_ylabel('Frequency (Raw Count)', fontsize=10, fontweight='bold')
ax.set_title('Digital and Internet Studies Terms: Frequency Trends\nin First Monday Journal (1996–2025)',
             fontsize=11, fontweight='bold', pad=12)
ax.legend(loc='upper left', fontsize=8, framealpha=0.95, edgecolor='gray')
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
output_path = os.path.join(analysis_folder, "03_phrases_only.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: 03_phrases_only.png")

# 4. Individual graphs for each word
for i, word in enumerate(words):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(years, data_for_plot[word], marker='o', color=colors_words[i],
            linewidth=1.5, markersize=4, alpha=0.85, label='Observed')
    ax.fill_between(years, data_for_plot[word], alpha=0.15, color=colors_words[i])

    # Add trend line
    z = np.polyfit(years_numeric, data_for_plot[word], 1)
    p = np.poly1d(z)
    trend_values = p(years_numeric)
    ax.plot(years, trend_values, color=colors_words[i], linestyle='--', linewidth=1, alpha=0.6, label='Trend')

    ax.set_xlabel('Year', fontsize=10, fontweight='bold')
    ax.set_ylabel('Frequency (Raw Count)', fontsize=10, fontweight='bold')
    ax.set_title('"{0}" Frequency Trend in First Monday Journal (1996–2025)'.format(word.title()),
                 fontsize=11, fontweight='bold', pad=12)
    ax.legend(loc='best', fontsize=8, framealpha=0.95, edgecolor='gray')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = os.path.join(analysis_folder, "04_word_{0}.png".format(word))
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Saved: 04_word_{0}.png".format(word))

# 5. Individual graphs for each phrase
for i, phrase in enumerate(phrases):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    safe_phrase = phrase.replace(' ', '_')
    ax.plot(years, data_for_plot[phrase], marker='o', color=colors_phrases[i],
            linewidth=1.5, markersize=4, alpha=0.85, label='Observed', linestyle='-')
    ax.fill_between(years, data_for_plot[phrase], alpha=0.15, color=colors_phrases[i])

    # Add trend line
    z = np.polyfit(years_numeric, data_for_plot[phrase], 1)
    p = np.poly1d(z)
    trend_values = p(years_numeric)
    ax.plot(years, trend_values, color=colors_phrases[i], linestyle='--', linewidth=1, alpha=0.6, label='Trend')

    ax.set_xlabel('Year', fontsize=10, fontweight='bold')
    ax.set_ylabel('Frequency (Raw Count)', fontsize=10, fontweight='bold')
    ax.set_title('"{0}" Frequency Trend in First Monday Journal (1996–2025)'.format(phrase.title()),
                 fontsize=11, fontweight='bold', pad=12)
    ax.legend(loc='best', fontsize=8, framealpha=0.95, edgecolor='gray')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()
    output_path = os.path.join(analysis_folder, "05_phrase_{0}.png".format(safe_phrase))
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Saved: 05_phrase_{0}.png".format(safe_phrase))

print("\nAll files saved to: {0}".format(analysis_folder))
