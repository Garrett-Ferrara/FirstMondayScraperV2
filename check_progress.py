"""
Quick progress checker for ongoing scrape
"""
import json
import os
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("First Monday Scraper - Progress Check")
    print("="*60 + "\n")

    # Check checkpoint
    checkpoint_file = "data/checkpoint.json"
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

        processed_issues = len(checkpoint.get('processed_issues', []))
        processed_articles = len(checkpoint.get('processed_articles', []))
        last_update = checkpoint.get('last_update', 'Unknown')

        print(f"Checkpoint Status:")
        print(f"  Issues processed: {processed_issues} / 359 ({processed_issues/359*100:.1f}%)")
        print(f"  Articles processed: {processed_articles}")
        print(f"  Last update: {last_update}")
    else:
        print("No checkpoint file found")

    print()

    # Count files
    fulltext_dir = Path("data/Full Text")
    metadata_dir = Path("data/Metadata")

    if fulltext_dir.exists():
        issue_folders = [d for d in fulltext_dir.iterdir() if d.is_dir()]
        total_fulltext = sum(len(list(d.glob("*.txt"))) for d in issue_folders)

        print(f"File System:")
        print(f"  Issue folders: {len(issue_folders)}")
        print(f"  Full text files: {total_fulltext}")

        # Show recent folders
        if issue_folders:
            recent = sorted(issue_folders, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            print(f"\n  Recent issues scraped:")
            for folder in recent:
                txt_count = len(list(folder.glob("*.txt")))
                print(f"    - {folder.name} ({txt_count} articles)")
    else:
        print("No Full Text directory found")

    # Check log for errors
    log_file = "data/scraper.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()

        errors = [l for l in lines if 'ERROR' in l or 'FAIL' in l]
        warnings = [l for l in lines if 'WARNING' in l]

        print(f"\nLog Summary:")
        print(f"  Total log lines: {len(lines)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")

        if errors:
            print(f"\n  Recent errors:")
            for error in errors[-3:]:
                print(f"    {error.strip()}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
