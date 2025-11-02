First Monday Journal Scraper Project
Project Overview
Build a comprehensive web scraper to extract 30 years of academic content from First Monday journal (firstmonday.org) for corpus analysis and author network research.
Primary Scraping Requirements
Target Data Points to Extract:

Article Title - Full title of each published article
Special Edition Information - Any special issue/themed edition designation
Abstract - Complete abstract text
Full Text - Complete article content (HTML and/or plain text)
Publication Date - Date published (month/year at minimum)
Authors - Individual authors or author groups with affiliations if available
Additional Metadata - Any other available statistics like:

Article URL/DOI
Keywords/tags
Article length/word count
Volume and issue numbers
Subject categories
Download statistics if available



Technical Implementation Guidelines:
Site Analysis & Structure

Start by analyzing First Monday's site structure (firstmonday.org)
Identify URL patterns for different time periods (they may have changed over 30 years)
Check for robots.txt compliance
Determine if there are archive pages, issue indexes, or search endpoints

## SITE STRUCTURE ANALYSIS (Completed October 2025)

### Domain History and Migrations
- **First Issue**: May 6, 1996 (first Monday of May)
- **Original Domain**: firstmonday.dk (Copenhagen server, 1996)
- **Historical Domain**: journals.uic.edu (University of Illinois at Chicago)
- **Current Domain**: firstmonday.org
- **Current Platform**: Open Journal Systems (OJS) version 2.4.8.3

### URL Patterns by Time Period

#### Legacy Format (1996-early 2000s)
Static HTML structure organized by issue number:
- Pattern: `https://firstmonday.org/issues/issue[N]/[article-name]/index.html`
- Examples:
  - Issue 1 (May 1996): `https://firstmonday.org/issues/issue1/editorial.html`
  - Issue 2 (June 1996): `https://firstmonday.org/issues/issue2/markets/index.html`
- Structure: Simple directory-based organization with article names as slugs

#### Current OJS Format (Modern Articles)
OJS-based dynamic routing:
- **Article View**: `https://firstmonday.org/ojs/index.php/fm/article/view/{article_id}/{galley_id}`
  - Example: `https://firstmonday.org/ojs/index.php/fm/article/view/1961/1838`
  - `article_id`: Numerical identifier for the article
  - `galley_id`: Numerical identifier for specific format/version
- **Article Download**: `https://firstmonday.org/ojs/index.php/fm/article/download/{article_id}/{version_id}/{file_id}`
  - Example: `https://firstmonday.org/ojs/index.php/fm/article/download/13729/11982/90154`
  - Supports PDF downloads via PDF.js viewer
- **Journal Code**: `fm` (First Monday)

### Archive Structure
- **Main Archive**: `https://firstmonday.org/ojs/index.php/fm/issue/archive`
- **Coverage**: All issues from 1996 to present
- **Organization**: Chronological by issue, includes special editions
- **Special Editions**: Topics like "Women and STEM", "Youth, digital media, and civic engagement"

### Content Formats Available
- **HTML**: Direct viewing in browser
- **PDF**: Downloadable via OJS download endpoint
- **Full Source**: HTML source code available for published contributions
- **Metadata**: Available via HTML meta tags and OAI (Open Archives Initiative) records

### Robots.txt and Crawling Considerations
- **Location**: `https://firstmonday.org/robots.txt`
- **Access Issue**: Direct WebFetch attempts returned 403 errors (may have rate limiting or bot detection)
- **Recommended Approach**:
  - Implement respectful crawling with user-agent headers
  - Add delays between requests (2-3 seconds minimum)
  - Consider using OJS API/OAI endpoints when available
  - Monitor for rate limiting responses

### OJS API and Metadata Access
OJS provides structured metadata access through:
1. **HTML Meta Tags**: Scraped from article view pages
2. **OAI Records**: Open Archives Initiative protocol support
3. **REST API**: OJS supports REST-ful API (may require authentication token)
4. **Existing Tools**:
   - `ojsr` (R package) for crawling OJS archives and retrieving metadata
   - `ojs-toolbox` (Bash) for caching JSON files via OJS API
   - Native OJS XML import/export plugins

### Key Technical Considerations
1. **Dual Scraping Strategy Required**:
   - Legacy parser for 1996-early 2000s static HTML
   - OJS parser for modern dynamic content
2. **Content Migration**: Some old articles may have been migrated to OJS format
3. **Link Preservation**: Old URLs may redirect to new OJS equivalents
4. **Metadata Consistency**: Structure varies significantly between old and new formats

Scraping Strategy

Use respectful crawling practices (delays between requests, user-agent headers)
Handle different page layouts that may have evolved over 30 years
Implement robust error handling for missing content or broken links
Create a systematic approach to traverse all issues chronologically

### Recommended Scraping Approach (Based on Site Analysis)

1. **Start with Archive Index**:
   - Crawl `https://firstmonday.org/ojs/index.php/fm/issue/archive`
   - Extract all issue URLs and metadata (date, volume, issue number, special edition info)
   - Build a comprehensive issue list from 1996-present

2. **Dual Parser Implementation**:
   - **Legacy Parser** (1996-early 2000s):
     - Handle static HTML from `/issues/issue[N]/` structure
     - Parse simple HTML structure for title, author, abstract, full text
   - **OJS Parser** (Modern format):
     - Use OJS routing conventions
     - Extract metadata from HTML meta tags or OAI records
     - Download full text via article view or download endpoints

3. **Metadata Extraction Strategy**:
   - Primary: HTML meta tags from article view pages
   - Secondary: OAI protocol records (if available)
   - Fallback: Parse HTML structure directly
   - Consider using existing OJS tools (ojsr, ojs-toolbox) as reference

4. **Crawling Best Practices**:
   - User-Agent: Identify as academic research bot with contact info
   - Rate Limiting: 2-3 second delays between requests minimum
   - Respect 403/429 responses and implement exponential backoff
   - Session management to handle potential IP-based rate limiting

Data Storage

Design a structured data format (JSON/CSV) for the extracted content
Include metadata about the scraping process (date scraped, source URL, etc.)
Consider creating separate files for full text vs. metadata for easier processing

Code Structure Recommendations

Use a modular approach with separate functions for:

Site navigation and URL discovery
Individual article parsing
Data cleaning and standardization
Export functionality


Include comprehensive logging for debugging and progress tracking
Implement checkpointing to resume interrupted scraping sessions

Output Format
Create a structured dataset with the following fields:
{
  "article_id": "unique_identifier",
  "title": "article_title",
  "authors": ["author1", "author2"],
  "author_affiliations": ["affiliation1", "affiliation2"],
  "publication_date": "YYYY-MM-DD",
  "volume": "volume_number",
  "issue": "issue_number", 
  "special_edition": "special_edition_name_if_any",
  "abstract": "full_abstract_text",
  "full_text": "complete_article_content",
  "keywords": ["keyword1", "keyword2"],
  "url": "source_url",
  "scraped_date": "YYYY-MM-DD",
  "word_count": number,
  "additional_metadata": {}
}
Implementation Notes
Libraries to Consider:

requests or httpx for HTTP requests
BeautifulSoup or lxml for HTML parsing
pandas for data manipulation
time for rate limiting
json for data serialization
logging for progress tracking

Potential Challenges:

Site Evolution: First Monday's layout has likely changed over 30 years
Content Format Variations: Different HTML structures across time periods
Rate Limiting: Avoid overwhelming the server
Missing Content: Some older articles may have broken links or missing abstracts
Author Name Variations: Same authors may be listed differently across articles

Quality Assurance:

Implement validation checks for extracted data
Create sample outputs for manual verification
Include statistics on successful vs. failed extractions
Log any anomalies or parsing errors for review

Future Enhancement Notes
This initial scraper focuses on First Monday content extraction. The Google Scholar citation analysis will be a separate phase requiring:

Google Scholar API integration or careful scraping
Citation matching algorithms
Additional rate limiting considerations
Possible CAPTCHA handling

Deliverables

Complete Python scraper script
Documentation explaining usage and configuration
Sample output files demonstrating the data structure
Error log analysis and recommendations for handling edge cases
Statistics on coverage (total articles found, successful extractions, etc.)

Ethical Considerations

Respect robots.txt and site terms of service
Implement appropriate delays between requests
Consider reaching out to First Monday editors for permission/collaboration
Ensure compliance with academic fair use guidelines

Please build this scraper with robust error handling, clear documentation, and modular code that can be easily modified as we discover the site's structure and any changes over its 30-year history.