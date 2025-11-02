"""
Add article_type field to classify articles as:
- article: Regular research article
- review: Book review, software review
- editorial: Editorial content (prefaces, introductions, interviews, etc.)
"""

import json
from pathlib import Path
import re

class ArticleTypeClassifier:
    def __init__(self):
        self.stats = {
            'total': 0,
            'article': 0,
            'review': 0,
            'editorial': 0,
            'updated': 0,
            'already_classified': 0
        }

        # Keywords for classification
        self.review_keywords = [
            'book review', 'review of', 'software review', 'book and software review',
            'reviews', 'reviewing'
        ]

        self.editorial_keywords = [
            'preface', 'introduction', 'editors', 'editorial', 'interview',
            'welcome remarks', 'thanks to', 'letter from', 'letters to the editor',
            'fm interviews', 'first monday interviews', 'acknowledgment',
            'foreword', 'afterword', 'afterward', 'prologue', 'epilogue',
            'commentary', 'message from', 'note from'
        ]

    def classify_article(self, title: str, abstract: str = '', url: str = '') -> str:
        """
        Classify article based on title, abstract, and URL
        Returns: 'article', 'review', or 'editorial'
        """
        title_lower = title.lower()
        abstract_lower = abstract.lower() if abstract else ''
        url_lower = url.lower() if url else ''

        # Check for reviews
        for keyword in self.review_keywords:
            if keyword in title_lower or keyword in abstract_lower:
                return 'review'

        # Check for editorial content
        for keyword in self.editorial_keywords:
            if keyword in title_lower or keyword in abstract_lower:
                return 'editorial'

        # Default to article
        return 'article'

    def add_article_type_to_file(self, article_file: Path):
        """Add article_type field to a single article JSON file"""
        self.stats['total'] += 1

        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)

            # Check if already classified
            if 'article_type' in article_data:
                self.stats['already_classified'] += 1
                return True

            # Get data for classification
            title = article_data.get('title', '')
            abstract = article_data.get('abstract', '')
            url = article_data.get('url', '')

            # Classify
            article_type = self.classify_article(title, abstract, url)

            # Create new ordered dict with article_type near the beginning
            # Order: article_id, article_type, url, scraped_date, title, authors, ...
            new_data = {}

            for key, value in article_data.items():
                new_data[key] = value
                # Insert article_type after article_id
                if key == 'article_id':
                    new_data['article_type'] = article_type

            # If article_id wasn't found, add article_type at the beginning
            if 'article_type' not in new_data:
                temp_data = {'article_type': article_type}
                temp_data.update(new_data)
                new_data = temp_data

            # Save updated file
            with open(article_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)

            self.stats[article_type] += 1
            self.stats['updated'] += 1
            return True

        except Exception as e:
            print(f"ERROR processing {article_file.name}: {e}")
            return False

    def process_all_articles(self):
        """Process all article files"""
        articles_dir = Path("Data/articles")

        print("=" * 80)
        print("ADDING ARTICLE_TYPE FIELD TO ALL ARTICLES")
        print("=" * 80)
        print()

        if not articles_dir.exists():
            print(f"ERROR: {articles_dir} does not exist!")
            return

        # Get all article files
        article_files = []
        for folder in sorted(articles_dir.iterdir()):
            if folder.is_dir():
                for file in folder.glob('*.json'):
                    if file.name != 'issue_info.json':
                        article_files.append(file)

        print(f"Found {len(article_files)} article files to process\n")

        # Process each file
        for i, article_file in enumerate(article_files, 1):
            self.add_article_type_to_file(article_file)

            # Progress update every 500 articles
            if i % 500 == 0:
                print(f"Processed {i}/{len(article_files)} articles...")

        # Final stats
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print(f"\nTotal articles processed: {self.stats['total']}")
        print(f"Already classified: {self.stats['already_classified']}")
        print(f"Newly classified: {self.stats['updated']}")
        print(f"\nClassification breakdown:")
        print(f"  Articles: {self.stats['article']} ({self.stats['article']/self.stats['total']*100:.1f}%)")
        print(f"  Reviews: {self.stats['review']} ({self.stats['review']/self.stats['total']*100:.1f}%)")
        print(f"  Editorial: {self.stats['editorial']} ({self.stats['editorial']/self.stats['total']*100:.1f}%)")

def main():
    print("\nThis script will add an 'article_type' field to all article JSON files.")
    print("Articles will be classified as:")
    print("  - 'article': Regular research articles")
    print("  - 'review': Book reviews, software reviews")
    print("  - 'editorial': Editorials, prefaces, interviews, etc.")
    print("\nThe field will be inserted after 'article_id' in the JSON structure.")

    response = input("\nProceed? (y/n): ").strip().lower()

    if response == 'y':
        classifier = ArticleTypeClassifier()
        classifier.process_all_articles()
        print("\n[SUCCESS] Article type classification complete!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
