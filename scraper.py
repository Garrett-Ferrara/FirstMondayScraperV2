"""
First Monday Journal Scraper
Main scraper module for extracting articles from First Monday journal
"""

import requests
import time
import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import config


class FirstMondayScraper:
    """Main scraper class for First Monday journal"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.setup_directories()
        self.setup_logging()
        self.checkpoint_data = self.load_checkpoint()

    def setup_directories(self):
        """Create necessary output directories"""
        Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
        Path(config.METADATA_DIR).mkdir(exist_ok=True)
        Path(config.FULLTEXT_DIR).mkdir(exist_ok=True)

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_checkpoint(self) -> Dict:
        """Load checkpoint data to resume interrupted sessions"""
        if os.path.exists(config.CHECKPOINT_FILE):
            try:
                with open(config.CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load checkpoint: {e}")
        return {"processed_issues": [], "processed_articles": [], "last_update": None}

    def save_checkpoint(self):
        """Save checkpoint data"""
        self.checkpoint_data["last_update"] = datetime.now().isoformat()
        try:
            with open(config.CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.checkpoint_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save checkpoint: {e}")

    def make_request(self, url: str, max_retries: int = config.MAX_RETRIES) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Requesting: {url}")
                time.sleep(config.REQUEST_DELAY)  # Rate limiting

                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)

                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    self.logger.warning(f"403 Forbidden for {url} - may need to adjust user agent or add delay")
                    time.sleep(config.RETRY_DELAY * 2)
                elif response.status_code == 429:
                    self.logger.warning(f"Rate limited (429) - waiting longer")
                    time.sleep(config.RETRY_DELAY * 3)
                else:
                    self.logger.warning(f"Status {response.status_code} for {url}")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(config.RETRY_DELAY)

        return None

    def get_archive_issues(self) -> List[Dict]:
        """
        Crawl the archive page to get all issues
        Returns list of issue metadata
        """
        self.logger.info("Fetching archive index...")
        response = self.make_request(config.ARCHIVE_URL)

        if not response:
            self.logger.error("Could not fetch archive page")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        issues = []

        # Parse archive page structure
        # OJS archive pages typically have issues in divs with specific classes
        issue_divs = soup.find_all('div', class_='obj_issue_summary')

        if not issue_divs:
            # Fallback: look for any links to issue pages
            self.logger.warning("Could not find issue divs, trying alternative parsing")
            issue_links = soup.find_all('a', href=lambda x: x and '/issue/view/' in x)

            for link in issue_links:
                issue_url = link.get('href')
                if not issue_url.startswith('http'):
                    issue_url = config.BASE_URL + issue_url

                issues.append({
                    'url': issue_url,
                    'title': link.get_text(strip=True),
                    'description': ''
                })
        else:
            for div in issue_divs:
                issue_data = self.parse_issue_summary(div)
                if issue_data:
                    issues.append(issue_data)

        self.logger.info(f"Found {len(issues)} issues in archive")
        return issues

    def parse_issue_summary(self, issue_div) -> Optional[Dict]:
        """Parse an issue summary div from the archive page"""
        try:
            # Find the link to the issue
            link = issue_div.find('a', class_='title')
            if not link:
                link = issue_div.find('a')

            if not link:
                return None

            issue_url = link.get('href')
            if not issue_url.startswith('http'):
                issue_url = config.BASE_URL + issue_url

            title = link.get_text(strip=True)

            # Try to find description
            desc_div = issue_div.find('div', class_='description')
            description = desc_div.get_text(strip=True) if desc_div else ''

            return {
                'url': issue_url,
                'title': title,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing issue summary: {e}")
            return None

    def get_articles_from_issue(self, issue_url: str) -> List[Dict]:
        """
        Get all articles from a specific issue page
        Returns list of article URLs and basic metadata
        """
        response = self.make_request(issue_url)

        if not response:
            self.logger.error(f"Could not fetch issue page: {issue_url}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        articles = []

        # Find article listings - OJS uses specific classes
        article_divs = soup.find_all('div', class_='obj_article_summary')

        if not article_divs:
            # Fallback
            self.logger.warning(f"No article summaries found in {issue_url}, trying alternative")
            article_links = soup.find_all('a', href=lambda x: x and '/article/view/' in x)

            for link in article_links:
                article_url = link.get('href')
                if not article_url.startswith('http'):
                    article_url = config.BASE_URL + article_url

                articles.append({
                    'url': article_url,
                    'title': link.get_text(strip=True)
                })
        else:
            for div in article_divs:
                article_data = self.parse_article_summary(div)
                if article_data:
                    articles.append(article_data)

        self.logger.info(f"Found {len(articles)} articles in issue")
        return articles

    def parse_article_summary(self, article_div) -> Optional[Dict]:
        """Parse an article summary from issue page"""
        try:
            link = article_div.find('a', class_='title')
            if not link:
                link = article_div.find('a')

            if not link:
                return None

            article_url = link.get('href')
            if not article_url.startswith('http'):
                article_url = config.BASE_URL + article_url

            title = link.get_text(strip=True)

            # Try to find authors
            authors_div = article_div.find('div', class_='authors')
            authors = authors_div.get_text(strip=True) if authors_div else ''

            return {
                'url': article_url,
                'title': title,
                'authors_preview': authors
            }
        except Exception as e:
            self.logger.error(f"Error parsing article summary: {e}")
            return None

    def parse_ojs_article(self, article_url: str) -> Optional[Dict]:
        """
        Parse a modern OJS format article page
        Extract all metadata and full text
        """
        response = self.make_request(article_url)

        if not response:
            return None

        soup = BeautifulSoup(response.content, 'lxml')

        # Extract article ID from URL
        article_id = article_url.split('/view/')[-1].split('/')[0] if '/view/' in article_url else None

        article_data = {
            'article_id': article_id,
            'url': article_url,
            'scraped_date': datetime.now().isoformat(),
            'format': 'ojs'
        }

        # Extract metadata from HTML meta tags
        article_data.update(self.extract_meta_tags(soup))

        # Extract from page content
        article_data.update(self.extract_article_content(soup))

        # Get full text from HTML galley if available
        if config.EXTRACT_FULL_TEXT:
            galley_url = self.find_html_galley_url(soup, article_url)
            if galley_url:
                article_data['full_text'] = self.extract_full_text_from_galley(galley_url)
                article_data['galley_url'] = galley_url
            else:
                # Fallback: try to extract from landing page
                article_data['full_text'] = self.extract_full_text(soup)
                self.logger.warning(f"No HTML galley found for {article_url}, using landing page text")

            article_data['word_count'] = len(article_data['full_text'].split()) if article_data.get('full_text') else 0

        return article_data

    def find_html_galley_url(self, soup, article_url: str) -> Optional[str]:
        """
        Find the HTML galley URL from the article landing page
        HTML galleys are the full-text article pages
        """
        # Look for HTML link in the Downloads section
        # OJS typically has links with text "HTML" or class indicating galley
        html_link = soup.find('a', string=lambda x: x and 'HTML' in x.upper())

        if not html_link:
            # Try finding by class
            html_link = soup.find('a', class_='obj_galley_link')

        if not html_link:
            # Try meta tag for fulltext URL
            fulltext_meta = soup.find('meta', attrs={'name': 'citation_fulltext_html_url'})
            if fulltext_meta:
                return fulltext_meta.get('content')

        if html_link:
            galley_url = html_link.get('href')
            if galley_url:
                if not galley_url.startswith('http'):
                    galley_url = config.BASE_URL + galley_url
                return galley_url

        return None

    def extract_full_text_from_galley(self, galley_url: str) -> str:
        """
        Extract full text from the HTML galley page (the actual article content)
        OJS often loads content in iframes, so we need to check for that
        """
        self.logger.info(f"Fetching full text from galley: {galley_url}")
        response = self.make_request(galley_url)

        if not response:
            return ''

        soup = BeautifulSoup(response.content, 'lxml')

        # Check if content is in an iframe
        iframe = soup.find('iframe')
        if iframe:
            iframe_src = iframe.get('src')
            if iframe_src:
                # Clean up whitespace and tabs from URL
                iframe_src = iframe_src.strip()

                # Make absolute URL
                if not iframe_src.startswith('http'):
                    iframe_src = config.BASE_URL + iframe_src

                self.logger.info(f"Content in iframe, fetching: {iframe_src}")

                # Fetch iframe content
                iframe_response = self.make_request(iframe_src)
                if iframe_response:
                    iframe_soup = BeautifulSoup(iframe_response.content, 'lxml')

                    # Remove unwanted elements from iframe content
                    for element in iframe_soup(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()

                    # Extract text from iframe
                    full_text = iframe_soup.get_text(separator='\n', strip=True)
                    if full_text:
                        return full_text

        # If no iframe or iframe failed, try direct extraction
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
            element.decompose()

        # Try to find main content area - OJS galleys often use specific structure
        content = None

        # Try common OJS galley content containers
        content = soup.find('div', id='htmlContainer')
        if not content:
            content = soup.find('div', id='content')
        if not content:
            content = soup.find('div', class_='article-content')
        if not content:
            content = soup.find('div', class_='galley')
        if not content:
            content = soup.find('article')
        if not content:
            content = soup.find('main')
        if not content:
            # Last resort: get body content
            content = soup.find('body')

        if content:
            return content.get_text(separator='\n', strip=True)

        return ''

    def extract_meta_tags(self, soup) -> Dict:
        """Extract metadata from HTML meta tags"""
        meta_data = {}

        # Common meta tag mappings
        meta_mappings = {
            'citation_title': 'title',
            'citation_author': 'authors',
            'citation_publication_date': 'publication_date',
            'citation_abstract': 'abstract',
            'citation_keywords': 'keywords',
            'citation_doi': 'doi',
            'citation_volume': 'volume',
            'citation_issue': 'issue',
            'citation_journal_title': 'journal',
        }

        for meta_name, field_name in meta_mappings.items():
            meta_tags = soup.find_all('meta', attrs={'name': meta_name})

            if meta_tags:
                if field_name in ['authors', 'keywords']:
                    # These can have multiple values
                    meta_data[field_name] = [tag.get('content') for tag in meta_tags if tag.get('content')]
                else:
                    meta_data[field_name] = meta_tags[0].get('content', '')

        return meta_data

    def extract_article_content(self, soup) -> Dict:
        """Extract article content from page structure"""
        content_data = {}

        # Title (fallback if not in meta)
        title_tag = soup.find('h1', class_='page_title')
        if title_tag:
            content_data['title'] = title_tag.get_text(strip=True)

        # Authors (fallback)
        authors_div = soup.find('div', class_='authors')
        if authors_div:
            # Parse author names
            author_links = authors_div.find_all('a')
            if author_links:
                content_data['authors'] = [a.get_text(strip=True) for a in author_links]

        # Abstract
        abstract_div = soup.find('div', class_='item abstract')
        if abstract_div:
            content_data['abstract'] = abstract_div.get_text(strip=True)

        return content_data

    def extract_full_text(self, soup) -> str:
        """Extract full article text from HTML"""
        # Look for main article content
        article_div = soup.find('div', class_='article-details')
        if not article_div:
            article_div = soup.find('article')
        if not article_div:
            article_div = soup.find('div', id='main')

        if article_div:
            # Remove script and style elements
            for script in article_div(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()

            return article_div.get_text(separator='\n', strip=True)

        return ''

    def save_article_data(self, article_data: Dict):
        """Save article data to JSON file"""
        article_id = article_data.get('article_id', 'unknown')

        # Save metadata
        metadata_file = Path(config.METADATA_DIR) / f"{article_id}.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                # Separate full text for cleaner metadata
                metadata = {k: v for k, v in article_data.items() if k != 'full_text'}
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving metadata for {article_id}: {e}")

        # Save full text separately if available
        if article_data.get('full_text'):
            fulltext_file = Path(config.FULLTEXT_DIR) / f"{article_id}.txt"
            try:
                with open(fulltext_file, 'w', encoding='utf-8') as f:
                    f.write(article_data['full_text'])
            except Exception as e:
                self.logger.error(f"Error saving full text for {article_id}: {e}")

    def scrape_sample(self, num_issues: int = 1, num_articles_per_issue: int = 3):
        """
        Scrape a small sample for testing
        """
        self.logger.info(f"Starting SAMPLE scrape: {num_issues} issue(s), up to {num_articles_per_issue} articles per issue")

        # Get issues
        issues = self.get_archive_issues()

        if not issues:
            self.logger.error("No issues found!")
            return

        # Sample the most recent issues
        sample_issues = issues[:num_issues]

        total_articles = 0

        for issue in sample_issues:
            self.logger.info(f"Processing issue: {issue['title']}")

            # Get articles from this issue
            articles = self.get_articles_from_issue(issue['url'])

            # Sample articles
            sample_articles = articles[:num_articles_per_issue]

            for article_summary in sample_articles:
                article_url = article_summary['url']

                # Check if already processed
                if article_url in self.checkpoint_data['processed_articles']:
                    self.logger.info(f"Skipping already processed: {article_url}")
                    continue

                # Parse article
                self.logger.info(f"Parsing article: {article_summary['title']}")
                article_data = self.parse_ojs_article(article_url)

                if article_data:
                    # Save data
                    self.save_article_data(article_data)
                    total_articles += 1

                    # Update checkpoint
                    self.checkpoint_data['processed_articles'].append(article_url)
                    self.save_checkpoint()

                    self.logger.info(f"Successfully scraped article {article_data.get('article_id')}")
                else:
                    self.logger.warning(f"Failed to parse article: {article_url}")

        self.logger.info(f"Sample scrape complete! Processed {total_articles} articles")
        return total_articles


def main():
    """Main entry point"""
    scraper = FirstMondayScraper()

    # Run a small sample test
    print("\n" + "="*60)
    print("First Monday Scraper - Sample Test")
    print("="*60)
    print("\nThis will scrape 1 issue with up to 3 articles for testing.")
    print("Check the 'data' directory for output files.\n")

    scraper.scrape_sample(num_issues=1, num_articles_per_issue=3)

    print("\n" + "="*60)
    print("Sample test complete!")
    print(f"Check {config.OUTPUT_DIR}/ for results")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
