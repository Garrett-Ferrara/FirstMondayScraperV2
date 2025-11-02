"""
Rebuild issue_info.json files for folders in vNone_nNone
based on the articles contained in each folder
"""

import json
import os
from pathlib import Path
from datetime import datetime

def extract_volume_issue_from_folder_name(folder_name):
    """Extract volume and issue from folder name like 20040704_vSE_n1"""
    parts = folder_name.split('_')

    volume = None
    issue = None

    for part in parts:
        if part.startswith('v'):
            volume = part[1:]  # Remove 'v' prefix
        elif part.startswith('n'):
            issue = part[1:]   # Remove 'n' prefix

    return volume, issue

def parse_date_from_yyyymmdd(date_str):
    """Convert YYYYMMDD to readable date like '4 July 2004'"""
    if not date_str or len(date_str) != 8:
        return None

    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    try:
        year = date_str[:4]
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        month_name = month_names[month - 1]
        return f"{day} {month_name} {year}"
    except:
        return None

def get_article_metadata(article_file):
    """Load article metadata from JSON file"""
    try:
        with open(article_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  Error reading {article_file.name}: {e}")
        return None

def rebuild_issue_info(folder_path):
    """Create issue_info.json based on folder contents"""

    folder_name = folder_path.name

    # Parse folder name for date and volume/issue
    date_prefix = folder_name.split('_')[0] if '_' in folder_name else folder_name
    volume, issue = extract_volume_issue_from_folder_name(folder_name)

    # Convert date to readable format
    date_readable = parse_date_from_yyyymmdd(date_prefix)

    # Get all article JSON files
    article_files = [f for f in folder_path.glob('*.json')
                     if f.name != 'issue_info.json']

    if not article_files:
        print(f"  WARNING: No articles found in {folder_name}")
        return None

    # Load first article to get some metadata
    first_article = get_article_metadata(article_files[0])

    if not first_article:
        return None

    # Try to determine title from articles
    # Special editions might have special titles
    title_parts = []
    if volume:
        title_parts.append(f"Volume {volume}")
    if issue:
        title_parts.append(f"Number {issue}")
    if date_readable:
        title_parts.append(f"— {date_readable}")

    title = ", ".join(title_parts) if title_parts else f"Special Edition — {date_readable or folder_name}"

    # Check if this is a special edition (has 'SE' in folder name)
    if 'SE' in folder_name or 'vSE' in folder_name:
        # Try to find special edition title from article titles
        special_title = None
        for article_file in article_files[:3]:  # Check first 3 articles
            article = get_article_metadata(article_file)
            if article and 'title' in article:
                article_title = article['title']
                if 'Special' in article_title or 'Introduction' in article_title:
                    # This might give us a clue about the special edition theme
                    pass

        # For special editions, mark them clearly
        if 'Music' in str(article_files[0]):
            title = f"Special Issue #1: Music and the Internet — {date_readable or folder_name}"

    # Build issue_info structure
    issue_info = {
        "issue_id": None,  # We don't have this from folder structure
        "title": title,
        "volume": volume,
        "issue_number": issue,
        "date": date_readable,
        "url": None,  # We don't have this
        "description": f"Reconstructed from {len(article_files)} articles",
        "article_count": len(article_files),
        "scraped_date": datetime.now().isoformat(),
        "reconstructed": True
    }

    return issue_info

def rebuild_all_issue_info():
    """Rebuild issue_info.json for all folders in vNone_nNone"""

    vnone_dir = Path("Data/articles/vNone_nNone")

    if not vnone_dir.exists():
        print(f"Error: {vnone_dir} does not exist!")
        return

    print("=" * 80)
    print("REBUILDING ISSUE_INFO.JSON FILES")
    print("Processing folders in vNone_nNone")
    print("=" * 80)

    # Get all subdirectories
    folders = [f for f in vnone_dir.iterdir() if f.is_dir()]

    print(f"\nFound {len(folders)} folders to process\n")

    success_count = 0
    error_count = 0

    for folder in sorted(folders):
        folder_name = folder.name
        print(f"Processing: {folder_name}")

        # Build issue_info
        issue_info = rebuild_issue_info(folder)

        if not issue_info:
            print(f"  ERROR: Could not build issue_info for {folder_name}")
            error_count += 1
            continue

        # Save issue_info.json
        issue_info_file = folder / "issue_info.json"

        try:
            with open(issue_info_file, 'w', encoding='utf-8') as f:
                json.dump(issue_info, f, indent=2, ensure_ascii=False)

            print(f"  CREATED: issue_info.json")
            print(f"    Title: {issue_info['title']}")
            print(f"    Articles: {issue_info['article_count']}")
            print(f"    Volume: {issue_info['volume']}, Issue: {issue_info['issue_number']}")
            success_count += 1
        except Exception as e:
            print(f"  ERROR: Could not save issue_info.json: {e}")
            error_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("REBUILD COMPLETE")
    print("=" * 80)
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {len(folders)}")
    print("=" * 80)

def main():
    print("\nThis script will rebuild issue_info.json files for folders in vNone_nNone")
    print("based on the articles contained in each folder.")

    response = input("\nProceed? (y/n): ").strip().lower()

    if response == 'y':
        rebuild_all_issue_info()
        print("\n[SUCCESS] Issue info files rebuilt!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
