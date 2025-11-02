"""
First Monday Scraper - Issue-by-Issue Mode
Scrapes articles organized by issue for easier testing and review
"""

import requests
import time
import logging
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import config


class IssueBasedScraper:
    """Scraper that organizes output by issue"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.setup_directories()
        self.setup_logging()
        self.checkpoint_data = self.load_checkpoint()

    def setup_directories(self):
        """Create necessary output directories"""
        Path(config.OUTPUT_DIR).mkdir(exist_ok=True)
        Path(config.ISSUES_DIR).mkdir(exist_ok=True)

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
        """Load checkpoint data"""
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

    def sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filenames"""
        # Remove/replace invalid characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Trim and limit length
        text = text.strip()[:100]
        return text

    def parse_date_to_folder_name(self, date_str: str) -> Optional[str]:
        """
        Parse date string (e.g., "1 September 2025") to YYYYMMDD format (e.g., "20250901")
        Returns None if parsing fails
        """
        if not date_str or date_str == 'unknown':
            return None

        # Month name to number mapping
        month_map = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }

        # Pattern: "D Month YYYY" or "DD Month YYYY"
        pattern = r'^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$'
        match = re.match(pattern, date_str.strip())

        if match:
            day = match.group(1).zfill(2)  # Pad with leading zero if needed
            month_name = match.group(2)
            year = match.group(3)

            month = month_map.get(month_name)
            if month:
                return f"{year}{month}{day}"

        self.logger.debug(f"Could not parse date: {date_str}")
        return None

    def make_request(self, url: str, max_retries: int = config.MAX_RETRIES) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Requesting: {url}")
                time.sleep(config.REQUEST_DELAY)

                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)

                if response.status_code == 200:
                    return response
                elif response.status_code in [403, 429]:
                    self.logger.warning(f"Rate limited ({response.status_code}) - waiting longer")
                    time.sleep(config.RETRY_DELAY * 2)
                else:
                    self.logger.warning(f"Status {response.status_code} for {url}")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(config.RETRY_DELAY)

        return None

    def get_all_issues(self) -> List[Dict]:
        """Get all issues from all archive pages"""
        self.logger.info("Fetching all issues from archive...")
        all_issues = []

        for page_num in range(1, 20):  # Check up to 20 pages
            if page_num == 1:
                url = config.ARCHIVE_URL
            else:
                url = f"{config.ARCHIVE_URL}/{page_num}"

            self.logger.info(f"Fetching archive page {page_num}...")
            response = self.make_request(url)

            if not response:
                self.logger.warning(f"Could not fetch page {page_num}, stopping")
                break

            soup = BeautifulSoup(response.content, 'lxml')
            issue_divs = soup.find_all('div', class_='obj_issue_summary')

            if not issue_divs:
                self.logger.info(f"No issues on page {page_num}, stopping")
                break

            for div in issue_divs:
                issue_data = self.parse_issue_summary(div)
                if issue_data:
                    all_issues.append(issue_data)

        self.logger.info(f"Found {len(all_issues)} total issues")
        return all_issues

    def parse_issue_summary(self, issue_div) -> Optional[Dict]:
        """Parse issue summary from archive page"""
        try:
            link = issue_div.find('a', class_='title')
            if not link:
                link = issue_div.find('a')

            if not link:
                return None

            issue_url = link.get('href')
            if not issue_url.startswith('http'):
                issue_url = config.BASE_URL + issue_url

            title = link.get_text(strip=True)

            # Extract issue ID from URL
            issue_id = issue_url.split('/view/')[-1]

            # Try to parse volume/issue from title
            # Format: "Volume X, Number Y - Date"
            volume_match = re.search(r'Volume (\d+)', title)
            issue_match = re.search(r'Number (\d+)', title)
            date_match = re.search(r'-\s*(.+)$', title)

            volume = volume_match.group(1) if volume_match else None
            issue = issue_match.group(1) if issue_match else None
            date = date_match.group(1).strip() if date_match else None

            desc_div = issue_div.find('div', class_='description')
            description = desc_div.get_text(strip=True) if desc_div else ''

            return {
                'issue_id': issue_id,
                'url': issue_url,
                'title': title,
                'volume': volume,
                'issue_number': issue,
                'date': date,
                'description': description
            }
        except Exception as e:
            self.logger.error(f"Error parsing issue summary: {e}")
            return None

    def get_articles_from_issue(self, issue_url: str) -> List[Dict]:
        """Get all articles from a specific issue"""
        response = self.make_request(issue_url)

        if not response:
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        articles = []

        article_divs = soup.find_all('div', class_='obj_article_summary')

        if not article_divs:
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

        return articles

    def parse_article_summary(self, article_div) -> Optional[Dict]:
        """Parse article summary from issue page"""
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

    def parse_article(self, article_url: str) -> Optional[Dict]:
        """Parse article and extract metadata and full text"""
        response = self.make_request(article_url)

        if not response:
            return None

        soup = BeautifulSoup(response.content, 'lxml')

        article_id = article_url.split('/view/')[-1].split('/')[0] if '/view/' in article_url else None

        article_data = {
            'article_id': article_id,
            'url': article_url,
            'scraped_date': datetime.now().isoformat(),
        }

        # Extract metadata
        article_data.update(self.extract_meta_tags(soup))
        article_data.update(self.extract_article_content(soup))

        # Get full text
        if config.EXTRACT_FULL_TEXT:
            galley_url = self.find_html_galley_url(soup, article_url)
            if galley_url:
                article_data['full_text'] = self.extract_full_text_from_galley(galley_url)
                article_data['galley_url'] = galley_url
            else:
                article_data['full_text'] = ''

            article_data['word_count'] = len(article_data['full_text'].split()) if article_data.get('full_text') else 0

        return article_data

    def extract_meta_tags(self, soup) -> Dict:
        """Extract metadata from HTML meta tags"""
        meta_data = {}

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
                    meta_data[field_name] = [tag.get('content') for tag in meta_tags if tag.get('content')]
                else:
                    meta_data[field_name] = meta_tags[0].get('content', '')

        return meta_data

    def extract_article_content(self, soup) -> Dict:
        """Extract article content from page structure"""
        content_data = {}

        title_tag = soup.find('h1', class_='page_title')
        if title_tag:
            content_data['title'] = title_tag.get_text(strip=True)

        authors_div = soup.find('div', class_='authors')
        if authors_div:
            author_links = authors_div.find_all('a')
            if author_links:
                content_data['authors'] = [a.get_text(strip=True) for a in author_links]

        abstract_div = soup.find('div', class_='item abstract')
        if abstract_div:
            content_data['abstract'] = abstract_div.get_text(strip=True)

        return content_data

    def find_html_galley_url(self, soup, article_url: str) -> Optional[str]:
        """Find HTML galley URL"""
        html_link = soup.find('a', string=lambda x: x and 'HTML' in x.upper())

        if not html_link:
            html_link = soup.find('a', class_='obj_galley_link')

        if not html_link:
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
        """Extract full text from galley page"""
        self.logger.debug(f"Fetching full text from galley: {galley_url}")
        response = self.make_request(galley_url)

        if not response:
            return ''

        soup = BeautifulSoup(response.content, 'lxml')

        # Check for iframe
        iframe = soup.find('iframe')
        if iframe:
            iframe_src = iframe.get('src')
            if iframe_src:
                iframe_src = iframe_src.strip()

                if not iframe_src.startswith('http'):
                    iframe_src = config.BASE_URL + iframe_src

                self.logger.debug(f"Content in iframe: {iframe_src}")

                iframe_response = self.make_request(iframe_src)
                if iframe_response:
                    iframe_soup = BeautifulSoup(iframe_response.content, 'lxml')

                    for element in iframe_soup(['script', 'style', 'nav', 'header', 'footer']):
                        element.decompose()

                    return iframe_soup.get_text(separator='\n', strip=True)

        # Fallback: direct extraction
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
            element.decompose()

        content = soup.find('div', id='htmlContainer') or soup.find('body')
        if content:
            return content.get_text(separator='\n', strip=True)

        return ''

    def save_issue_data(self, issue_info: Dict, articles_data: List[Dict]):
        """Save all data for an issue in organized folder structure"""
        # Create folder name from issue date in YYYYMMDD format
        date_str = issue_info.get('date', 'unknown')
        volume = issue_info.get('volume', 'unknown')
        issue_num = issue_info.get('issue_number', 'unknown')

        # Try to parse date and convert to YYYYMMDD format
        folder_date = self.parse_date_to_folder_name(date_str)
        if not folder_date:
            # Fallback to volume/issue format if date parsing fails
            folder_date = f"v{volume}_n{issue_num}"

        # Create Full Text top-level directory
        fulltext_base = Path(config.OUTPUT_DIR) / "Full Text"
        fulltext_base.mkdir(exist_ok=True)

        # Create issue-specific folder under Full Text
        issue_fulltext_dir = fulltext_base / folder_date
        issue_fulltext_dir.mkdir(exist_ok=True)

        # Create metadata directory (organized by issue)
        metadata_base = Path(config.OUTPUT_DIR) / "metadata"
        metadata_base.mkdir(exist_ok=True)

        issue_metadata_dir = metadata_base / folder_date
        issue_metadata_dir.mkdir(exist_ok=True)

        # Save issue summary
        issue_summary = {
            'issue_id': issue_info['issue_id'],
            'title': issue_info['title'],
            'volume': issue_info.get('volume'),
            'issue_number': issue_info.get('issue_number'),
            'date': issue_info.get('date'),
            'url': issue_info['url'],
            'description': issue_info.get('description', ''),
            'article_count': len(articles_data),
            'scraped_date': datetime.now().isoformat()
        }

        summary_file = issue_metadata_dir / 'issue_info.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(issue_summary, f, indent=2, ensure_ascii=False)

        # Save each article
        for article_data in articles_data:
            article_id = article_data.get('article_id', 'unknown')

            # Create safe filename from title
            title = article_data.get('title', f'article_{article_id}')
            safe_title = self.sanitize_filename(title)
            filename_base = f"{article_id}_{safe_title}"

            # Save metadata
            metadata = {k: v for k, v in article_data.items() if k != 'full_text'}
            metadata_file = issue_metadata_dir / f"{filename_base}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # Save full text to Full Text folder
            if article_data.get('full_text'):
                fulltext_file = issue_fulltext_dir / f"{filename_base}.txt"
                with open(fulltext_file, 'w', encoding='utf-8') as f:
                    f.write(article_data['full_text'])

        self.logger.info(f"Saved {len(articles_data)} articles to Full Text/{folder_date}/")

    def scrape_single_issue(self, issue_info: Dict) -> Dict:
        """Scrape a single issue and return statistics"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Scraping: {issue_info['title']}")
        self.logger.info(f"URL: {issue_info['url']}")
        self.logger.info(f"{'='*60}")

        # Check if already processed
        if issue_info['issue_id'] in self.checkpoint_data['processed_issues']:
            self.logger.info("Issue already processed (skipping)")
            return {'skipped': True}

        # Get articles
        articles = self.get_articles_from_issue(issue_info['url'])
        self.logger.info(f"Found {len(articles)} articles in issue")

        if not articles:
            return {'error': 'No articles found', 'article_count': 0}

        # Scrape each article
        articles_data = []
        success_count = 0
        failed_count = 0

        for i, article_summary in enumerate(articles, 1):
            self.logger.info(f"\n[{i}/{len(articles)}] {article_summary['title'][:60]}...")

            article_data = self.parse_article(article_summary['url'])

            if article_data and article_data.get('word_count', 0) > 0:
                articles_data.append(article_data)
                success_count += 1
                self.logger.info(f"  [OK] {article_data.get('word_count', 0)} words")
            else:
                failed_count += 1
                self.logger.warning(f"  [FAIL] Extraction failed")

        # Save issue data
        if articles_data:
            self.save_issue_data(issue_info, articles_data)

            # Update checkpoint
            self.checkpoint_data['processed_issues'].append(issue_info['issue_id'])
            for article in articles_data:
                if article['url'] not in self.checkpoint_data['processed_articles']:
                    self.checkpoint_data['processed_articles'].append(article['url'])
            self.save_checkpoint()

        stats = {
            'issue_id': issue_info['issue_id'],
            'title': issue_info['title'],
            'total_articles': len(articles),
            'successful': success_count,
            'failed': failed_count,
            'total_words': sum(a.get('word_count', 0) for a in articles_data)
        }

        self.logger.info(f"\nIssue complete: {success_count}/{len(articles)} articles scraped")
        return stats


def main():
    """Main entry point for issue-by-issue scraping"""
    print("\n" + "="*60)
    print("First Monday Scraper - Issue-by-Issue Mode")
    print("="*60 + "\n")

    scraper = IssueBasedScraper()

    # Get all issues
    all_issues = scraper.get_all_issues()

    if not all_issues:
        print("Error: No issues found!")
        return

    print(f"Found {len(all_issues)} total issues\n")
    print("Select scraping mode:")
    print("1. Scrape a single issue (for testing)")
    print("2. Scrape a range of issues")
    print("3. Scrape all issues")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == '1':
        # Show recent issues
        print("\nRecent issues:")
        for i, issue in enumerate(all_issues[:10], 1):
            print(f"{i}. {issue['title']}")

        issue_num = int(input("\nEnter issue number (1-10): ").strip())
        if 1 <= issue_num <= 10:
            stats = scraper.scrape_single_issue(all_issues[issue_num - 1])
            print(f"\n{stats}")

    elif choice == '2':
        start = int(input("Start index (1 for first): ").strip()) - 1
        end = int(input("End index: ").strip())

        for issue in all_issues[start:end]:
            stats = scraper.scrape_single_issue(issue)
            print(f"\n{stats}")

    elif choice == '3':
        print(f"\nWill scrape all {len(all_issues)} issues")
        confirm = input("Continue? (y/n): ").strip().lower()

        if confirm == 'y':
            for i, issue in enumerate(all_issues, 1):
                print(f"\n\nProgress: {i}/{len(all_issues)}")
                stats = scraper.scrape_single_issue(issue)
                print(f"{stats}")


if __name__ == "__main__":
    main()
