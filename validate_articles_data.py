"""
Comprehensive validation script for articles directory
Checks for inconsistencies, missing fields, and data integrity issues
"""

import json
import os
from pathlib import Path
from collections import defaultdict

class ArticlesValidator:
    def __init__(self):
        self.articles_dir = Path("Data/articles")
        self.issues = []
        self.errors = []
        self.warnings = []
        self.stats = defaultdict(int)

    def validate_issue_info(self, folder_path):
        """Validate issue_info.json file"""
        issue_info_file = folder_path / "issue_info.json"
        folder_name = folder_path.name

        if not issue_info_file.exists():
            self.errors.append(f"{folder_name}: Missing issue_info.json")
            return None

        try:
            with open(issue_info_file, 'r', encoding='utf-8') as f:
                issue_info = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"{folder_name}: Invalid JSON in issue_info.json - {e}")
            return None
        except Exception as e:
            self.errors.append(f"{folder_name}: Error reading issue_info.json - {e}")
            return None

        # Check required fields
        required_fields = ['title', 'article_count']
        for field in required_fields:
            if field not in issue_info:
                self.errors.append(f"{folder_name}: Missing '{field}' in issue_info.json")

        # Check optional but expected fields
        if 'volume' not in issue_info or issue_info.get('volume') is None:
            self.warnings.append(f"{folder_name}: Missing 'volume' in issue_info.json")

        if 'issue_number' not in issue_info or issue_info.get('issue_number') is None:
            self.warnings.append(f"{folder_name}: Missing 'issue_number' in issue_info.json")

        if 'date' not in issue_info or issue_info.get('date') is None:
            self.warnings.append(f"{folder_name}: Missing 'date' in issue_info.json")

        return issue_info

    def validate_article(self, article_file):
        """Validate individual article JSON file"""
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"{article_file.name}: Invalid JSON - {e}")
            return None
        except Exception as e:
            self.errors.append(f"{article_file.name}: Error reading file - {e}")
            return None

        # Check for critical fields
        critical_fields = ['article_id', 'title']
        for field in critical_fields:
            if field not in article or not article.get(field):
                self.errors.append(f"{article_file.name}: Missing critical field '{field}'")

        # Check for important fields
        important_fields = ['authors', 'full_text', 'word_count']
        for field in important_fields:
            if field not in article:
                self.warnings.append(f"{article_file.name}: Missing '{field}'")
            elif field == 'full_text' and not article.get(field):
                self.errors.append(f"{article_file.name}: Empty full_text")
            elif field == 'word_count' and article.get(field, 0) == 0:
                self.warnings.append(f"{article_file.name}: Zero word count")

        return article

    def validate_folder(self, folder_path):
        """Validate a single issue folder"""
        folder_name = folder_path.name

        # Validate issue_info
        issue_info = self.validate_issue_info(folder_path)

        # Get all article files
        article_files = [f for f in folder_path.glob('*.json')
                        if f.name != 'issue_info.json']

        # Check article count matches
        if issue_info and 'article_count' in issue_info:
            declared_count = issue_info['article_count']
            actual_count = len(article_files)

            if declared_count != actual_count:
                self.errors.append(
                    f"{folder_name}: Article count mismatch - "
                    f"issue_info says {declared_count}, found {actual_count}"
                )

        # Validate each article
        valid_articles = 0
        for article_file in article_files:
            article = self.validate_article(article_file)
            if article:
                valid_articles += 1

        self.stats['total_folders'] += 1
        self.stats['total_articles'] += len(article_files)

        return {
            'folder_name': folder_name,
            'issue_info': issue_info,
            'article_count': len(article_files),
            'valid_articles': valid_articles
        }

    def check_folder_naming(self, folder_path):
        """Check if folder naming follows conventions"""
        folder_name = folder_path.name

        # Check for standard format: YYYYMMDD_vX_nY
        if folder_name == 'vNone_nNone':
            # This is the special container folder
            return True

        # Pattern check
        parts = folder_name.split('_')

        if len(parts) < 3:
            self.warnings.append(
                f"{folder_name}: Folder name doesn't follow YYYYMMDD_vX_nY pattern"
            )
            return False

        # Check date part
        date_part = parts[0]
        if not date_part.isdigit() or len(date_part) != 8:
            self.warnings.append(
                f"{folder_name}: Date part '{date_part}' doesn't match YYYYMMDD format"
            )

        # Check volume part
        if not parts[1].startswith('v'):
            self.warnings.append(
                f"{folder_name}: Volume part '{parts[1]}' doesn't start with 'v'"
            )

        # Check issue part
        if not parts[2].startswith('n'):
            self.warnings.append(
                f"{folder_name}: Issue part '{parts[2]}' doesn't start with 'n'"
            )

        return True

    def validate_all(self):
        """Validate all folders in articles directory"""
        print("=" * 80)
        print("ARTICLES DIRECTORY VALIDATION")
        print("=" * 80)

        if not self.articles_dir.exists():
            print(f"\nERROR: {self.articles_dir} does not exist!")
            return

        # Get all folders
        folders = [f for f in self.articles_dir.iterdir() if f.is_dir()]

        print(f"\nFound {len(folders)} folders to validate")
        print("\nValidating...\n")

        # Process vNone_nNone separately if it exists
        vnone_folder = self.articles_dir / "vNone_nNone"
        if vnone_folder.exists():
            print("Processing vNone_nNone (special editions container):")
            subfolders = [f for f in vnone_folder.iterdir() if f.is_dir()]
            print(f"  Found {len(subfolders)} special edition folders\n")

            for subfolder in sorted(subfolders):
                self.check_folder_naming(subfolder)
                self.validate_folder(subfolder)

            folders = [f for f in folders if f.name != 'vNone_nNone']

        # Validate regular folders
        for folder in sorted(folders):
            self.check_folder_naming(folder)
            self.validate_folder(folder)

        # Print results
        self.print_results()

    def print_results(self):
        """Print validation results"""
        print("\n" + "=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)

        print(f"\nTotal folders validated: {self.stats['total_folders']}")
        print(f"Total articles found: {self.stats['total_articles']}")

        # Errors
        if self.errors:
            print(f"\n{'='*80}")
            print(f"ERRORS FOUND: {len(self.errors)}")
            print("=" * 80)
            for error in self.errors[:50]:  # Show first 50 errors
                print(f"  • {error}")
            if len(self.errors) > 50:
                print(f"  ... and {len(self.errors) - 50} more errors")
        else:
            print("\n[OK] No critical errors found!")

        # Warnings
        if self.warnings:
            print(f"\n{'='*80}")
            print(f"WARNINGS: {len(self.warnings)}")
            print("=" * 80)
            for warning in self.warnings[:50]:  # Show first 50 warnings
                print(f"  - {warning}")
            if len(self.warnings) > 50:
                print(f"  ... and {len(self.warnings) - 50} more warnings")
        else:
            print("\n[OK] No warnings!")

        # Summary by issue
        print(f"\n{'='*80}")
        print("SUMMARY BY ISSUE TYPE")
        print("=" * 80)

        # Count by volume
        volume_counts = defaultdict(int)
        vnone_dir = self.articles_dir / "vNone_nNone"

        for folder in self.articles_dir.iterdir():
            if not folder.is_dir():
                continue

            if folder.name == 'vNone_nNone':
                # Count special editions
                for subfolder in vnone_dir.iterdir():
                    if subfolder.is_dir():
                        volume_counts['Special Editions'] += 1
            else:
                # Extract volume from folder name
                parts = folder.name.split('_')
                if len(parts) >= 2 and parts[1].startswith('v'):
                    vol = parts[1][1:]  # Remove 'v' prefix
                    if vol.isdigit():
                        volume_counts[f"Volume {vol}"] += 1
                    elif vol == 'SE':
                        volume_counts["Special Editions"] += 1

        for vol_label, count in sorted(volume_counts.items()):
            print(f"  {vol_label}: {count} issues")

        print("\n" + "=" * 80)
        if not self.errors:
            print("[SUCCESS] ALL VALIDATIONS PASSED!")
        else:
            print(f"[WARNING] VALIDATION COMPLETED WITH {len(self.errors)} ERRORS")
        print("=" * 80)

def main():
    validator = ArticlesValidator()
    validator.validate_all()

if __name__ == "__main__":
    main()
