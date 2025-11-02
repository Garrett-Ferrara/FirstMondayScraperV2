"""
Rename article folders to include volume and issue numbers
Format: YYYYMMDD_vX_nY (e.g., 20251205_v1_n7)
"""

import json
import os
from pathlib import Path

def get_volume_issue_from_folder(folder_path):
    """Extract volume and issue from issue_info.json"""
    issue_info_file = folder_path / "issue_info.json"

    if not issue_info_file.exists():
        return None, None

    try:
        with open(issue_info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        volume = data.get('volume')
        issue = data.get('issue_number')

        return volume, issue
    except Exception as e:
        print(f"Error reading {issue_info_file}: {e}")
        return None, None

def rename_articles_folders():
    """Rename all article folders to include volume and issue"""

    articles_dir = Path("Data/articles")

    if not articles_dir.exists():
        print(f"Error: {articles_dir} does not exist!")
        return

    print("=" * 80)
    print("RENAMING ARTICLE FOLDERS TO INCLUDE VOLUME/ISSUE")
    print("Format: YYYYMMDD_vX_nY")
    print("=" * 80)

    # Get all folders
    folders = [f for f in articles_dir.iterdir() if f.is_dir()]

    print(f"\nFound {len(folders)} folders to process\n")

    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for folder in sorted(folders):
        folder_name = folder.name

        # Get volume and issue
        volume, issue = get_volume_issue_from_folder(folder)

        if volume is None or issue is None:
            print(f"SKIP: {folder_name} (no volume/issue info)")
            skipped_count += 1
            continue

        # Check if already renamed (has _v pattern)
        if '_v' in folder_name:
            print(f"SKIP: {folder_name} (already renamed)")
            skipped_count += 1
            continue

        # Create new name
        new_name = f"{folder_name}_v{volume}_n{issue}"
        new_path = articles_dir / new_name

        # Check if target exists
        if new_path.exists():
            print(f"SKIP: {folder_name} -> {new_name} (target exists)")
            skipped_count += 1
            continue

        # Rename
        try:
            folder.rename(new_path)
            print(f"RENAMED: {folder_name} -> {new_name}")
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
    print(f"Total: {len(folders)}")
    print("=" * 80)

def main():
    print("\nThis script will rename article folders to include volume and issue numbers.")
    print("\nExample transformations:")
    print("  19960506 -> 19960506_v1_n1")
    print("  20250901 -> 20250901_v30_n9")
    print("  v11_n5 -> v11_n5_v11_n5")

    response = input("\nProceed with renaming? (y/n): ").strip().lower()

    if response == 'y':
        rename_articles_folders()
        print("\n[SUCCESS] Folder renaming complete!")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
