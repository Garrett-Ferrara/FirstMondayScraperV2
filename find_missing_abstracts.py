"""
Search for missing abstracts from alternative sources
"""

import json
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
import config

class AlternativeAbstractFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.stats = {
            'checked': 0,
            'found_page_text': 0,
            'found_doi': 0,
            'still_empty': 0,
            'errors': 0
        }

    def make_request(self, url: str, max_retries: int = 3):
        """Make HTTP request with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(config.REQUEST_DELAY)
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"  Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  ERROR: Failed after {max_retries} attempts: {e}")
                    return None

    def extract_abstract_from_page_content(self, url: str):
        """
        Try to extract abstract from the full article page
        Look for abstract in the article body, not just metadata
        """
        response = self.make_request(url)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'lxml')
        abstract = None

        # Method 1: Look for abstract section in article body
        # First Monday sometimes has abstracts in the article text itself
        abstract_section = soup.find('div', class_='abstract')
        if abstract_section:
            abstract = abstract_section.get_text(strip=True)
            print(f"  Found in div.abstract: {len(abstract)} chars")
            return abstract

        # Method 2: Look for first paragraph after heading "Abstract"
        headings = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
        for heading in headings:
            if heading.get_text(strip=True).lower() in ['abstract', 'abstract:', 'summary']:
                # Get next paragraph
                next_elem = heading.find_next(['p', 'div'])
                if next_elem:
                    abstract = next_elem.get_text(strip=True)
                    print(f"  Found after '{heading.get_text(strip=True)}' heading: {len(abstract)} chars")
                    return abstract

        # Method 3: For book reviews, look for first substantial paragraph
        if 'review' in url.lower() or 'book' in soup.get_text().lower()[:500]:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 100 and not text.startswith('[') and not text.startswith('http'):
                    abstract = text
                    print(f"  Found first substantial paragraph: {len(abstract)} chars")
                    return abstract

        # Method 4: Description meta tag
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta and desc_meta.get('content'):
            abstract = desc_meta.get('content').strip()
            print(f"  Found in meta description: {len(abstract)} chars")
            return abstract

        return None

    def search_crossref(self, doi: str):
        """Search CrossRef API for abstract"""
        if not doi:
            return None

        try:
            # CrossRef API
            url = f"https://api.crossref.org/works/{doi}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                abstract = data.get('message', {}).get('abstract')
                if abstract:
                    print(f"  Found via CrossRef: {len(abstract)} chars")
                    return abstract
        except Exception as e:
            print(f"  CrossRef error: {e}")

        return None

    def process_article(self, article_file: Path):
        """Try to find abstract for a single article"""
        self.stats['checked'] += 1

        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)

            # Skip if already has abstract
            if article_data.get('abstract') and len(article_data.get('abstract', '')) > 20:
                return True

            article_id = article_data.get('article_id', 'unknown')
            title = article_data.get('title', 'unknown')[:60]
            print(f"\n[{self.stats['checked']}] ID {article_id}: {title}")

            # Get URL and DOI
            url = article_data.get('url')
            doi = article_data.get('doi')

            abstract = None

            # Try method 1: Deep scrape from page
            if url:
                print(f"  Trying deep page scrape...")
                abstract = self.extract_abstract_from_page_content(url)
                if abstract and len(abstract) > 20:
                    self.stats['found_page_text'] += 1

            # Try method 2: CrossRef if we have DOI
            if not abstract and doi:
                print(f"  Trying CrossRef with DOI: {doi}")
                abstract = self.search_crossref(doi)
                if abstract:
                    self.stats['found_doi'] += 1

            # Update the article file if we found something
            if abstract and len(abstract) > 20:
                # Insert abstract before full_text
                new_data = {}
                for key, value in article_data.items():
                    if key == 'full_text':
                        new_data['abstract'] = abstract
                    new_data[key] = value

                if 'abstract' not in new_data:
                    new_data['abstract'] = abstract

                # Save
                with open(article_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)

                print(f"  ✓ UPDATED with abstract ({len(abstract)} chars)")
                return True
            else:
                print(f"  ✗ Still no abstract found")
                self.stats['still_empty'] += 1
                return False

        except Exception as e:
            print(f"  ERROR: {e}")
            self.stats['errors'] += 1
            return False

    def process_empty_abstracts(self):
        """Process all articles with empty/short abstracts"""
        articles_dir = Path("Data/articles")

        print("=" * 80)
        print("SEARCHING FOR MISSING ABSTRACTS FROM ALTERNATIVE SOURCES")
        print("=" * 80)

        # Get articles with empty or very short abstracts
        articles_to_check = []

        for folder in sorted(articles_dir.iterdir()):
            if not folder.is_dir():
                continue

            for file in sorted(folder.glob('*.json')):
                if file.name == 'issue_info.json':
                    continue

                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    abstract = data.get('abstract', '')
                    if not abstract or len(abstract) < 20:
                        articles_to_check.append(file)
                except:
                    continue

        print(f"\nFound {len(articles_to_check)} articles with missing/short abstracts")
        print(f"Starting alternative abstract search...\n")

        for article_file in articles_to_check:
            self.process_article(article_file)

        # Final stats
        print("\n" + "=" * 80)
        print("ALTERNATIVE SEARCH COMPLETE")
        print("=" * 80)
        print(f"Articles checked: {self.stats['checked']}")
        print(f"Found via page scrape: {self.stats['found_page_text']}")
        print(f"Found via CrossRef: {self.stats['found_doi']}")
        print(f"Still empty: {self.stats['still_empty']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Total found: {self.stats['found_page_text'] + self.stats['found_doi']}")
        if self.stats['checked'] > 0:
            success_rate = ((self.stats['found_page_text'] + self.stats['found_doi']) / self.stats['checked']) * 100
            print(f"Success rate: {success_rate:.1f}%")

def main():
    print("\nThis script will search for missing abstracts from alternative sources.")
    print("It will try:")
    print("  1. Deep scraping of the article page content")
    print("  2. CrossRef API (if DOI available)")
    print("\nThis may take some time depending on how many articles need checking.")

    response = input("\nProceed? (y/n): ").strip().lower()

    if response == 'y':
        finder = AlternativeAbstractFinder()
        finder.process_empty_abstracts()
        print("\n[SUCCESS] Alternative abstract search complete!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
