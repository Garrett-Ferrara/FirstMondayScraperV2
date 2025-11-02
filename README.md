# First Monday Journal Scraper

A comprehensive web scraper for extracting 30 years of academic content from First Monday journal (firstmonday.org).

## Features

- **Dual parser system**: Handles both legacy (1996-early 2000s) and modern OJS format articles
- **Respectful crawling**: Built-in rate limiting and proper user-agent headers
- **Checkpoint system**: Resume interrupted scraping sessions
- **Comprehensive logging**: Track progress and errors
- **Structured output**: Separate metadata and full-text files in JSON format
- **Sample testing**: Test with small samples before full scraping

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to customize:

- `REQUEST_DELAY`: Time between requests (default: 2.5 seconds)
- `USER_AGENT`: Update with your contact information
- `EXTRACT_FULL_TEXT`: Enable/disable full text extraction
- `MAX_ARTICLES_PER_RUN`: Limit articles for testing

## Usage

### Sample Test (Recommended First)

```bash
python scraper.py
```

This runs a small test scraping 1 issue with 3 articles.

### Custom Sample

```python
from scraper import FirstMondayScraper

scraper = FirstMondayScraper()
scraper.scrape_sample(num_issues=2, num_articles_per_issue=5)
```

### Full Scrape (Coming Soon)

Full scraping functionality will be added after sample testing is validated.

## Output Structure

```
data/
├── metadata/          # Article metadata (JSON files)
│   └── {article_id}.json
├── fulltext/          # Full article text
│   └── {article_id}.txt
├── checkpoint.json    # Progress tracking
└── scraper.log       # Execution log
```

## Article Metadata Fields

Each article JSON file contains:
- `article_id`: Unique identifier
- `title`: Article title
- `authors`: List of authors
- `publication_date`: Publication date
- `abstract`: Article abstract
- `keywords`: Associated keywords
- `volume`, `issue`: Journal volume/issue numbers
- `doi`: Digital Object Identifier
- `url`: Source URL
- `scraped_date`: When the article was scraped
- `word_count`: Full text word count

## Notes

- The scraper respects robots.txt and implements ethical crawling practices
- First Monday has bot detection - the scraper includes appropriate delays
- Legacy format parser (for 1996-early 2000s articles) will be added based on findings from sample scraping
- Always test with samples before running full scrapes

## License

For academic research purposes only. Respect First Monday's terms of service.
