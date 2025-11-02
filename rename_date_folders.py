"""
Script to rename date-formatted folders (e.g., "1 April 2002") to YYYYMMDD format (e.g., "20020401")
in both Full Text and metadata directories.
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Month name to number mapping
MONTH_MAP = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08',
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

def parse_date_folder_name(folder_name):
    """
    Parse folder name like "1 April 2002" and return YYYYMMDD format.
    Returns None if the folder name doesn't match the expected pattern.
    """
    # Pattern: "D Month YYYY" or "DD Month YYYY"
    pattern = r'^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$'
    match = re.match(pattern, folder_name)

    if not match:
        return None

    day = match.group(1).zfill(2)  # Pad day with leading zero if needed
    month_name = match.group(2)
    year = match.group(3)

    # Get month number
    month = MONTH_MAP.get(month_name)
    if not month:
        print(f"Warning: Unrecognized month '{month_name}' in folder '{folder_name}'")
        return None

    return f"{year}{month}{day}"

def rename_folders_in_directory(base_path):
    """
    Rename all date-formatted folders in the given directory to YYYYMMDD format.
    """
    if not os.path.exists(base_path):
        print(f"Directory not found: {base_path}")
        return

    print(f"\nProcessing directory: {base_path}")
    print("-" * 80)

    # Get all items in the directory
    items = os.listdir(base_path)
    renamed_count = 0
    skipped_count = 0

    for item in items:
        item_path = os.path.join(base_path, item)

        # Only process directories
        if not os.path.isdir(item_path):
            continue

        # Try to parse the folder name
        new_name = parse_date_folder_name(item)

        if new_name:
            new_path = os.path.join(base_path, new_name)

            # Check if target already exists
            if os.path.exists(new_path):
                print(f"  SKIP: '{item}' -> '{new_name}' (target already exists)")
                skipped_count += 1
                continue

            # Rename the folder
            try:
                os.rename(item_path, new_path)
                print(f"  RENAMED: '{item}' -> '{new_name}'")
                renamed_count += 1
            except Exception as e:
                print(f"  ERROR renaming '{item}': {e}")
        else:
            # Not a date folder, skip silently
            skipped_count += 1

    print(f"\nSummary for {base_path}:")
    print(f"  Renamed: {renamed_count} folders")
    print(f"  Skipped: {skipped_count} folders")

def main():
    """Main function to rename folders in both directories."""
    # Define the base directories
    full_text_dir = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\Data\Full Text"
    metadata_dir = r"C:\Users\ferra\DevProjects\FirstMondayScraperV2\Data\metadata"

    print("=" * 80)
    print("FOLDER RENAMING SCRIPT")
    print("Converting date folders from 'D Month Year' to 'YYYYMMDD' format")
    print("=" * 80)

    # Rename folders in Full Text directory
    rename_folders_in_directory(full_text_dir)

    # Rename folders in metadata directory
    rename_folders_in_directory(metadata_dir)

    print("\n" + "=" * 80)
    print("RENAMING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
