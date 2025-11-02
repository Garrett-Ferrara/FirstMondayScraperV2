"""
Rename volume-formatted folders (v##_n##) to YYYYMMDD_vX_nY format
based on the date information in issue_info.json
Excludes vNone_nNone folder
"""

import json
import os
import re
from pathlib import Path

def parse_date_to_yyyymmdd(date_str):
    """
    Parse date string (e.g., "1 May 2006") to YYYYMMDD format
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

    return None

def get_folder_info(folder_path):
    """Extract date, volume, and issue from issue_info.json"""
    issue_info_file = folder_path / "issue_info.json"

    if not issue_info_file.exists():
        return None, None, None

    try:
        with open(issue_info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        date_str = data.get('date')
        volume = data.get('volume')
        issue = data.get('issue_number')

        return date_str, volume, issue
    except Exception as e:
        print(f"Error reading {issue_info_file}: {e}")
        return None, None, None

def rename_volume_folders():
    """Rename volume-formatted folders to date format"""

    articles_dir = Path("Data/articles")

    if not articles_dir.exists():
        print(f"Error: {articles_dir} does not exist!")
        return

    print("=" * 80)
    print("RENAMING VOLUME-FORMATTED FOLDERS TO DATE FORMAT")
    print("Format: v##_n## -> YYYYMMDD_vX_nY")
    print("=" * 80)

    # Get all folders that start with 'v' and match pattern v##_n##
    folders = [f for f in articles_dir.iterdir()
               if f.is_dir() and f.name.startswith('v')
               and '_n' in f.name]

    # Filter out vNone_nNone
    folders = [f for f in folders if f.name != 'vNone_nNone']

    print(f"\nFound {len(folders)} volume-formatted folders to process")
    print("(Excluding vNone_nNone)\n")

    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for folder in sorted(folders):
        folder_name = folder.name

        # Get date, volume, and issue from metadata
        date_str, volume, issue = get_folder_info(folder)

        if not date_str:
            print(f"SKIP: {folder_name} (no date in metadata)")
            skipped_count += 1
            continue

        # Parse date to YYYYMMDD
        date_formatted = parse_date_to_yyyymmdd(date_str)

        if not date_formatted:
            print(f"SKIP: {folder_name} (could not parse date: '{date_str}')")
            skipped_count += 1
            continue

        # Create new name
        new_name = f"{date_formatted}_v{volume}_n{issue}"
        new_path = articles_dir / new_name

        # Check if target exists
        if new_path.exists():
            print(f"SKIP: {folder_name} -> {new_name} (target exists)")
            skipped_count += 1
            continue

        # Rename
        try:
            folder.rename(new_path)
            print(f"RENAMED: {folder_name:20s} -> {new_name} (date: {date_str})")
            renamed_count += 1
        except Exception as e:
            print(f"ERROR: Could not rename {folder_name}: {e}")
            error_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("RENAMING COMPLETE")
    print("=" * 80)
    print(f"Renamed: {renamed_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Total processed: {len(folders)}")
    print("=" * 80)

def main():
    print("\nThis script will rename volume-formatted folders (v##_n##) to date format.")
    print("\nExample transformations:")
    print("  v11_n5 -> 20060501_v11_n5 (based on date in metadata)")
    print("  v12_n3 -> 20070305_v12_n3")
    print("\nExcluded:")
    print("  vNone_nNone (will not be renamed)")

    response = input("\nProceed with renaming? (y/n): ").strip().lower()

    if response == 'y':
        rename_volume_folders()
        print("\n[SUCCESS] Folder renaming complete!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
