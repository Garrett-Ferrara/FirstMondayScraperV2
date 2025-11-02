"""
Add abstract field to existing article JSON files
Re-scrapes only the abstract metadata from each article URL
Inserts abstract field before full_text in the JSON structure
"""

import json
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import config

class AbstractAdder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        self.stats = {
            'total': 0,
            'success': 0,
            'no_abstract': 0,
            'already_has': 0,
            'failed': 0
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

    def extract_abstract(self, url: str):
        """Extract abstract from article page"""
        response = self.make_request(url)

        if not response:
            return None

        soup = BeautifulSoup(response.content, 'lxml')

        # Try multiple methods to extract abstract
        abstract = None

        # Method 1: Meta tag
        meta_abstract = soup.find('meta', attrs={'name': 'citation_abstract'})
        if meta_abstract and meta_abstract.get('content'):
            abstract = meta_abstract.get('content').strip()

        # Method 2: Abstract div
        if not abstract:
            abstract_div = soup.find('div', class_='item abstract')
            if abstract_div:
                # Remove the label/heading
                label = abstract_div.find('h3')
                if label:
                    label.decompose()
                abstract = abstract_div.get_text(strip=True)

        # Method 3: Try DC.Description meta tag
        if not abstract:
            dc_desc = soup.find('meta', attrs={'name': 'DC.Description'})
            if dc_desc and dc_desc.get('content'):
                abstract = dc_desc.get('content').strip()

        return abstract if abstract else ""

    def add_abstract_to_file(self, article_file: Path):
        """Add abstract field to a single article JSON file"""
        self.stats['total'] += 1

        try:
            # Load existing article data
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)

            # Check if abstract already exists
            if 'abstract' in article_data and article_data['abstract']:
                print(f"  SKIP: Already has abstract")
                self.stats['already_has'] += 1
                return True

            # Get article URL
            article_url = article_data.get('url')
            if not article_url:
                print(f"  ERROR: No URL in file")
                self.stats['failed'] += 1
                return False

            # Extract abstract
            print(f"  Fetching abstract from {article_url}")
            abstract = self.extract_abstract(article_url)

            if abstract:
                print(f"  SUCCESS: Abstract found ({len(abstract)} chars)")
                self.stats['success'] += 1
            else:
                print(f"  NO ABSTRACT: Setting empty string")
                self.stats['no_abstract'] += 1

            # Create new ordered dict with abstract before full_text
            new_data = {}
            for key, value in article_data.items():
                if key == 'full_text':
                    # Insert abstract before full_text
                    new_data['abstract'] = abstract
                new_data[key] = value

            # If full_text wasn't found, add abstract at the end
            if 'abstract' not in new_data:
                new_data['abstract'] = abstract

            # Save updated file
            with open(article_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"  ERROR: {e}")
            self.stats['failed'] += 1
            return False

    def process_all_articles(self):
        """Process all article files in the articles directory"""
        articles_dir = Path("Data/articles")

        if not articles_dir.exists():
            print(f"ERROR: {articles_dir} does not exist!")
            return

        print("=" * 80)
        print("ADDING ABSTRACTS TO ARTICLE FILES")
        print("=" * 80)

        # Get all article JSON files
        article_files = []
        for folder in articles_dir.iterdir():
            if folder.is_dir():
                for file in folder.glob('*.json'):
                    if file.name != 'issue_info.json':
                        article_files.append(file)

        print(f"\nFound {len(article_files)} article files to process")
        print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Process each file
        for i, article_file in enumerate(sorted(article_files), 1):
            # Use safe encoding for filenames with special characters
            try:
                filename = f"{article_file.parent.name}/{article_file.name}"
                print(f"\n[{i}/{len(article_files)}] {filename}")
            except UnicodeEncodeError:
                # Fallback for filenames with problematic characters
                print(f"\n[{i}/{len(article_files)}] {article_file.parent.name}/[file with special chars]")
            self.add_abstract_to_file(article_file)

            # Progress update every 100 articles
            if i % 100 == 0:
                self.print_stats(interim=True)

        # Final stats
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        self.print_stats(interim=False)

    def print_stats(self, interim=False):
        """Print statistics"""
        if interim:
            print(f"\n--- Progress Update ({self.stats['total']} processed) ---")
        print(f"  Total processed: {self.stats['total']}")
        print(f"  Abstracts added: {self.stats['success']}")
        print(f"  No abstract found: {self.stats['no_abstract']}")
        print(f"  Already had abstract: {self.stats['already_has']}")
        print(f"  Failed: {self.stats['failed']}")
        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] + self.stats['already_has']) / self.stats['total'] * 100
            print(f"  Success rate: {success_rate:.1f}%")
        if interim:
            print("---")

def main():
    print("\nThis script will add abstract fields to all article JSON files.")
    print("It will re-scrape the abstract from each article's URL.")
    print("\nThe abstract field will be inserted BEFORE full_text in the JSON structure.")

    response = input("\nProceed? (y/n): ").strip().lower()

    if response == 'y':
        adder = AbstractAdder()
        adder.process_all_articles()
        print("\n[SUCCESS] Abstract addition complete!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
