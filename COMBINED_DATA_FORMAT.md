# Combined Data Format

## Overview

The `Data/articles/` directory contains unified JSON files that combine metadata and full text for each article. This format makes it easier to work with the corpus for analysis, machine learning, or text processing.

## Directory Structure

```
Data/articles/
├── 19960506/                    # Issue folder (YYYYMMDD format)
│   ├── issue_info.json         # Issue metadata
│   ├── 464_Editors' Introduction.json
│   ├── 465_Electronic Cash and Monetary Policy.json
│   └── ...
├── 20250901/                    # Latest issue
│   ├── issue_info.json
│   └── ...
└── [353 total issue folders]
```

## JSON Structure

Each article JSON file contains:

```json
{
  "article_id": "464",
  "url": "https://firstmonday.org/ojs/index.php/fm/article/view/464",
  "scraped_date": "2025-10-19T20:28:59.896963",
  "title": "Editors' Introduction",
  "authors": [
    "Edward J. Valauskas",
    "Esther Dyson",
    "Rishab Aiyer Ghosh"
  ],
  "keywords": [
    "editorial",
    "First Monday",
    "academic journal"
  ],
  "doi": "10.5210/fm.v1i1.464",
  "journal": "First Monday",
  "galley_url": "https://firstmonday.org/ojs/index.php/fm/article/view/464/385",
  "word_count": 404,
  "full_text": "Full article text here..."
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `article_id` | string | Unique identifier from First Monday |
| `url` | string | Article landing page URL |
| `scraped_date` | string | ISO 8601 timestamp of when scraped |
| `title` | string | Article title |
| `authors` | array | List of author names |
| `publication_date` | string | Publication date (may be missing) |
| `abstract` | string | Article abstract (if available) |
| `keywords` | array | Article keywords/tags |
| `doi` | string | Digital Object Identifier |
| `volume` | string | Journal volume number |
| `issue` | string | Issue number |
| `journal` | string | Journal name ("First Monday") |
| `galley_url` | string | URL to full text HTML version |
| `word_count` | integer | Word count of full text |
| `full_text` | string | Complete article text |

## Statistics

- **Total articles**: 2,710
- **Total issues**: 353
- **Date range**: May 6, 1996 - September 1, 2025
- **Success rate**: 100% (all articles have full text)

## Usage Examples

### Python - Load a single article

```python
import json

with open('Data/articles/19960506/464_Editors\' Introduction.json', 'r', encoding='utf-8') as f:
    article = json.load(f)

print(f"Title: {article['title']}")
print(f"Authors: {', '.join(article['authors'])}")
print(f"Word count: {article['word_count']}")
print(f"\nFirst 200 characters:\n{article['full_text'][:200]}")
```

### Python - Load all articles from an issue

```python
import json
from pathlib import Path

issue_dir = Path('Data/articles/19960506')

# Get all article files (excluding issue_info.json)
article_files = [f for f in issue_dir.glob('*.json')
                 if f.name != 'issue_info.json']

articles = []
for file in article_files:
    with open(file, 'r', encoding='utf-8') as f:
        articles.append(json.load(f))

print(f"Loaded {len(articles)} articles from issue")
```

### Python - Load all articles (entire corpus)

```python
import json
from pathlib import Path

articles_dir = Path('Data/articles')
all_articles = []

for issue_dir in articles_dir.iterdir():
    if not issue_dir.is_dir():
        continue

    for article_file in issue_dir.glob('*.json'):
        if article_file.name == 'issue_info.json':
            continue

        with open(article_file, 'r', encoding='utf-8') as f:
            all_articles.append(json.load(f))

print(f"Loaded {len(all_articles)} total articles")
```

### Python - Create a pandas DataFrame

```python
import json
import pandas as pd
from pathlib import Path

articles_dir = Path('Data/articles')
articles = []

for issue_dir in articles_dir.iterdir():
    if not issue_dir.is_dir():
        continue

    for article_file in issue_dir.glob('*.json'):
        if article_file.name == 'issue_info.json':
            continue

        with open(article_file, 'r', encoding='utf-8') as f:
            article = json.load(f)
            articles.append({
                'article_id': article.get('article_id'),
                'title': article.get('title'),
                'authors': ', '.join(article.get('authors', [])),
                'publication_date': article.get('publication_date'),
                'word_count': article.get('word_count'),
                'doi': article.get('doi'),
                'full_text': article.get('full_text', '')
            })

df = pd.DataFrame(articles)
print(df.head())
print(f"\nTotal articles: {len(df)}")
print(f"Average word count: {df['word_count'].mean():.0f}")
```

## Analysis Use Cases

The combined format is ideal for:

1. **Text Analysis**: Word frequency, topic modeling, sentiment analysis
2. **Machine Learning**: Training text classification models, embeddings
3. **Bibliometric Analysis**: Citation patterns, author networks
4. **Time Series Analysis**: Tracking topic evolution over 29 years
5. **Corpus Linguistics**: Vocabulary analysis, discourse patterns
6. **Data Science**: Exploratory data analysis, visualization

## Generating Combined Data

If you need to regenerate the combined data:

```bash
python combine_metadata_fulltext.py
```

This will:
1. Read metadata from `Data/metadata/`
2. Read full text from `Data/Full Text/`
3. Combine them into `Data/articles/`
4. Process all 353 issues and 2,710 articles

## File Naming Convention

Files are named: `{article_id}_{title}.json`

Example: `464_Editors' Introduction.json`

- `article_id`: Numeric ID from First Monday
- `title`: Sanitized article title (truncated if too long)

## Notes

- All JSON files use UTF-8 encoding
- Full text includes all content from the article HTML
- Word count is calculated from full text
- Some older articles may have incomplete metadata
- The `articles/` directory is excluded from git (too large)

---

**Generated**: October 20, 2025
**Script**: `combine_metadata_fulltext.py`
