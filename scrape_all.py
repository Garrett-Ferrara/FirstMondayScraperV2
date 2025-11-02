"""
Full corpus scraper - Non-interactive mode
Scrapes all 359 issues from First Monday
"""
from scraper_by_issue import IssueBasedScraper
import sys

def main():
    print("\n" + "="*60)
    print("First Monday - Full Corpus Scraping")
    print("="*60 + "\n")

    scraper = IssueBasedScraper()

    # Get all issues
    print("Fetching archive index...")
    all_issues = scraper.get_all_issues()

    if not all_issues:
        print("Error: No issues found!")
        return

    print(f"\nFound {len(all_issues)} total issues")
    print(f"From: {all_issues[-1]['title']}")  # Oldest
    print(f"To: {all_issues[0]['title']}")      # Newest

    # Check how many already processed
    already_processed = len(scraper.checkpoint_data.get('processed_issues', []))
    remaining = len(all_issues) - already_processed

    print(f"\nAlready processed: {already_processed} issues")
    print(f"Remaining: {remaining} issues")

    if remaining == 0:
        print("\nAll issues already scraped!")
        return

    print(f"\n{'='*60}")
    print("Starting full corpus scrape...")
    print(f"{'='*60}\n")

    # Statistics tracking
    total_articles = 0
    total_successful = 0
    total_failed = 0
    total_words = 0
    total_skipped = 0

    # Scrape all issues
    for i, issue in enumerate(all_issues, 1):
        print(f"\n{'='*60}")
        print(f"Progress: {i}/{len(all_issues)} ({i/len(all_issues)*100:.1f}%)")
        print(f"{'='*60}")

        stats = scraper.scrape_single_issue(issue)

        # Update totals
        if stats.get('skipped'):
            total_skipped += 1
            print(f"[SKIP] Issue already processed")
        elif stats.get('error'):
            print(f"[ERROR] {stats.get('error')}")
        else:
            total_articles += stats.get('total_articles', 0)
            total_successful += stats.get('successful', 0)
            total_failed += stats.get('failed', 0)
            total_words += stats.get('total_words', 0)

        # Print running totals every 10 issues
        if i % 10 == 0:
            print(f"\n{'='*60}")
            print(f"RUNNING TOTALS (after {i} issues):")
            print(f"{'='*60}")
            print(f"Total articles processed: {total_articles}")
            print(f"Successful: {total_successful}")
            print(f"Failed: {total_failed}")
            print(f"Total words: {total_words:,}")
            print(f"Skipped issues: {total_skipped}")
            print(f"{'='*60}\n")

    # Final summary
    print(f"\n{'='*60}")
    print("FULL CORPUS SCRAPING COMPLETE!")
    print(f"{'='*60}")
    print(f"\nFinal Statistics:")
    print(f"  Total issues: {len(all_issues)}")
    print(f"  Issues processed: {len(all_issues) - total_skipped}")
    print(f"  Issues skipped: {total_skipped}")
    print(f"  Total articles: {total_articles}")
    print(f"  Successful: {total_successful}")
    print(f"  Failed: {total_failed}")
    print(f"  Success rate: {(total_successful/total_articles*100):.1f}%" if total_articles > 0 else "N/A")
    print(f"  Total words: {total_words:,}")
    print(f"\nOutput located in:")
    print(f"  - data/Full Text/[YYYYMMDD]/")
    print(f"  - data/metadata/[YYYYMMDD]/")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
