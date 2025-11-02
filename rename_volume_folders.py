"""
Script to rename remaining volume-formatted folders to YYYYMMDD format
Based on the dates found in issue titles
"""

import os
import shutil
from pathlib import Path

# Manual mapping from analysis
FOLDER_MAPPINGS = {
    'v11_n5': '20060501',
    'v11_n6': '20060605',
    'v11_n7': '20060703',
    'v11_n8': '20060807',
    'v11_n9': '20060904',
    'v11_n10': '20061002',
    'v11_n11': '20061106',
    'v11_n12': '20061204',
    'v12_n1': '20070101',
    'v12_n2': '20070205',
    'v12_n3': '20070305',
    'v12_n4': '20070402',
    'v12_n5': '20070507',
    'v12_n6': '20070604',
    'v12_n7': '20070702',
    'vNone_nNone': '20050704',  # Special Issue #1: Music and the Internet
}

def rename_folders():
    """Rename volume-formatted folders to YYYYMMDD format"""

    base_dirs = [
        Path("Data/Full Text"),
        Path("Data/metadata")
    ]

    print("=" * 80)
    print("VOLUME FOLDER RENAMING SCRIPT")
    print("Converting v{volume}_n{issue} folders to YYYYMMDD format")
    print("=" * 80)

    for base_dir in base_dirs:
        print(f"\nProcessing directory: {base_dir}")
        print("-" * 80)

        renamed_count = 0

        for old_name, new_name in FOLDER_MAPPINGS.items():
            old_path = base_dir / old_name
            new_path = base_dir / new_name

            if old_path.exists():
                if new_path.exists():
                    print(f"  SKIP: '{old_name}' -> '{new_name}' (target exists)")
                    continue

                try:
                    os.rename(old_path, new_path)
                    print(f"  RENAMED: '{old_name}' -> '{new_name}'")
                    renamed_count += 1
                except Exception as e:
                    print(f"  ERROR: Could not rename '{old_name}': {e}")
            else:
                print(f"  NOT FOUND: '{old_name}'")

        print(f"\nSummary for {base_dir}:")
        print(f"  Renamed: {renamed_count} folders")

    print("\n" + "=" * 80)
    print("RENAMING COMPLETE")
    print("=" * 80)

def main():
    print("\nThis script will rename 16 volume-formatted folders to YYYYMMDD format.")
    print("\nMappings:")
    for old, new in sorted(FOLDER_MAPPINGS.items()):
        print(f"  {old:15s} -> {new}")

    response = input("\nProceed with renaming? (y/n): ").strip().lower()

    if response == 'y':
        rename_folders()
        print("\n✓ Folders renamed successfully!")
        print("\nYou can now re-run analyze_scraping_results.py to verify.")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
