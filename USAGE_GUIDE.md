# First Monday Scraper - Usage Guide

## Quick Start

### Issue-by-Issue Scraping (Recommended)

The new `scraper_by_issue.py` organizes all output by issue for easy testing and review.

```bash
python scraper_by_issue.py
```

This will:
1. Fetch all 359 issues from the archive
2. Present a menu for scraping options
3. Organize output in clean folder structure

## Output Structure

### Folder Organization

```
data/
├── Full Text/
│   └── [Issue Date]/
│       ├── [article_id]_[title].txt
│       ├── [article_id]_[title].txt
│       └── ...
├── Metadata/
│   └── [Issue Date]/
│       ├── issue_info.json
│       ├── [article_id]_[title].json
│       ├── [article_id]_[title].json
│       └── ...
├── checkpoint.json
└── scraper.log
```

### Example Structure

```
data/
├── Full Text/
│   └── 6 May 1996/
│       ├── 464_Editors' Introduction.txt
│       ├── 465_Electronic Cash and Monetary Policy.txt
│       ├── 466_The Social Life of Documents.txt
│       └── ...
├── Metadata/
│   └── 6 May 1996/
│       ├── issue_info.json
│       ├── 464_Editors' Introduction.json
│       ├── 465_Electronic Cash and Monetary Policy.json
│       └── ...
```

## Scraping Modes

### Mode 1: Single Issue (Testing)

Best for testing before full scraping.

```
Select scraping mode:
1. Scrape a single issue (for testing)
```

- Shows 10 most recent issues
- Select one to scrape
- Perfect for verifying everything works

### Mode 2: Range of Issues

Scrape a specific range.

```
2. Scrape a range of issues
Start index (1 for first): 1
End index: 10
```

- Scrapes issues 1-10
- Good for incremental scraping
- Can resume later

### Mode 3: All Issues

Full corpus scraping.

```
3. Scrape all issues
Will scrape all 359 issues
Continue? (y/n):
```

- Scrapes entire archive (359 issues)
- Takes considerable time
- Automatically checkpoints progress

## File Contents

### issue_info.json

Contains metadata about the issue:

```json
{
  "issue_id": "70",
  "title": "Volume 1, Number 1 - 6 May 1996",
  "volume": "1",
  "issue_number": "1",
  "date": "6 May 1996",
  "url": "https://firstmonday.org/ojs/index.php/fm/issue/view/70",
  "article_count": 7,
  "scraped_date": "2025-10-19T20:29:55"
}
```

### Article Metadata JSON

Each article has a metadata JSON file:

```json
{
  "article_id": "464",
  "url": "https://firstmonday.org/ojs/index.php/fm/article/view/464",
  "title": "Editors' Introduction",
  "authors": ["Edward J. Valauskas", "Esther Dyson", ...],
  "keywords": ["editorial", "First Monday", ...],
  "doi": "10.5210/fm.v1i1.464",
  "journal": "First Monday",
  "word_count": 404,
  "scraped_date": "2025-10-19T20:29:55"
}
```

### Article Full Text

Plain text file with complete article content.

## Checkpoint System

The scraper tracks progress in `data/checkpoint.json`:

```json
{
  "processed_issues": ["70", "71", ...],
  "processed_articles": ["https://...", ...],
  "last_update": "2025-10-19T20:29:55"
}
```

**Benefits:**
- Resume interrupted scraping
- Skip already-processed issues
- No duplicate downloads

## Configuration

Edit `config.py` to customize:

```python
# Crawling settings
REQUEST_DELAY = 2.5  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3

# User agent - UPDATE THIS
USER_AGENT = "FirstMondayResearchBot/1.0 (Academic Research; Contact: your-email@example.com)"

# Data extraction
EXTRACT_FULL_TEXT = True
EXTRACT_PDF = False
```

## Performance Estimates

Based on testing:

- **Single article**: ~8-10 seconds
- **Average issue**: 7-10 articles = ~1-2 minutes
- **Full archive**: 359 issues ≈ 6-12 hours

**Rate limiting:** 2.5 seconds between requests (respectful crawling)

## Tips for Testing

1. **Start small**: Test with Mode 1 (single issue)
2. **Check output**: Verify files in `data/Full Text/` and `data/Metadata/`
3. **Review logs**: Check `data/scraper.log` for any errors
4. **Test range**: Try Mode 2 with 2-3 issues from different time periods
5. **Full scrape**: Once satisfied, run Mode 3

## Common Issues

### Issue has no articles

Some issue URLs may be empty or require login. The scraper will log this and continue.

### Publication date shows "N/A"

Older articles may not have complete metadata. This is normal.

### Rate limiting (403/429 errors)

The scraper automatically retries with longer delays. If persistent, increase `REQUEST_DELAY` in `config.py`.

## Testing Workflow

```bash
# 1. Test single recent issue
python scraper_by_issue.py
# Choose option 1, select issue 1

# 2. Verify output
ls -la "data/Full Text/"
ls -la "data/Metadata/"

# 3. Test older issue
# Choose option 1, select issue 10

# 4. If all looks good, scrape a range
python scraper_by_issue.py
# Choose option 2, range 1-20

# 5. Full scrape when ready
python scraper_by_issue.py
# Choose option 3, confirm with 'y'
```

## Data Analysis

After scraping, you can:

1. **Count total articles**: `find "data/Full Text" -type f -name "*.txt" | wc -l`
2. **Total word count**: Check sum of word_count fields in metadata
3. **Author extraction**: Parse authors from all metadata JSON files
4. **Export to CSV**: Combine all metadata for analysis

## Next Steps

1. Scrape sample issues to verify quality
2. Adjust configuration if needed
3. Run full scrape
4. Analyze corpus data
5. Build author networks
6. Extract citations (future feature)

## Support

- Check `TESTING_RESULTS.md` for detailed test information
- Review `scraper.log` for execution details
- Examine `checkpoint.json` for progress tracking
