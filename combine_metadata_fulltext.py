"""
Combine metadata JSON files with full text into unified JSON files
Creates a new 'combined' directory with one JSON file per article
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

def load_metadata(metadata_file: Path) -> Optional[Dict]:
    """Load metadata JSON file"""
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata {metadata_file}: {e}")
        return None

def load_fulltext(fulltext_file: Path) -> Optional[str]:
    """Load full text file"""
    try:
        with open(fulltext_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading full text {fulltext_file}: {e}")
        return None

def combine_article_data(metadata: Dict, full_text: str) -> Dict:
    """Combine metadata and full text into single structure"""
    combined = metadata.copy()
    combined['full_text'] = full_text

    # Add word count if not present
    if 'word_count' not in combined:
        combined['word_count'] = len(full_text.split()) if full_text else 0

    return combined

def process_all_articles():
    """Process all articles and combine metadata with full text"""

    metadata_dir = Path("Data/metadata")
    fulltext_dir = Path("Data/Full Text")
    output_dir = Path("Data/articles")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("COMBINING METADATA AND FULL TEXT")
    print("=" * 80)

    # Statistics
    total_processed = 0
    total_success = 0
    total_metadata_only = 0
    total_fulltext_only = 0
    total_failed = 0

    # Track issues processed
    issues_processed = []

    # Get all issue folders from metadata
    issue_folders = [f for f in os.listdir(metadata_dir)
                    if os.path.isdir(metadata_dir / f)]

    print(f"\nFound {len(issue_folders)} issue folders to process\n")

    for i, issue_folder in enumerate(sorted(issue_folders), 1):
        metadata_issue_dir = metadata_dir / issue_folder
        fulltext_issue_dir = fulltext_dir / issue_folder

        # Create corresponding output directory
        output_issue_dir = output_dir / issue_folder
        output_issue_dir.mkdir(exist_ok=True)

        # Get all metadata JSON files (excluding issue_info.json)
        metadata_files = [f for f in metadata_issue_dir.glob("*.json")
                         if f.name != "issue_info.json"]

        if not metadata_files:
            continue

        print(f"[{i}/{len(issue_folders)}] Processing {issue_folder} ({len(metadata_files)} articles)")

        issue_success = 0
        issue_metadata_only = 0
        issue_fulltext_only = 0

        for metadata_file in metadata_files:
            total_processed += 1

            # Determine corresponding full text file
            # Metadata: article_id_title.json -> Full text: article_id_title.txt
            base_name = metadata_file.stem
            fulltext_file = fulltext_issue_dir / f"{base_name}.txt"

            # Load metadata
            metadata = load_metadata(metadata_file)
            if not metadata:
                total_failed += 1
                continue

            # Load full text if available
            full_text = ""
            if fulltext_file.exists():
                full_text = load_fulltext(fulltext_file)
                if full_text is None:
                    full_text = ""

            # Combine data
            if full_text:
                combined = combine_article_data(metadata, full_text)
                issue_success += 1
                total_success += 1
            else:
                # Metadata only
                combined = metadata.copy()
                combined['full_text'] = ""
                combined['word_count'] = 0
                issue_metadata_only += 1
                total_metadata_only += 1

            # Save combined JSON
            output_file = output_issue_dir / f"{base_name}.json"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(combined, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"  ERROR saving {output_file}: {e}")
                total_failed += 1
                continue

        # Copy issue_info.json if it exists
        issue_info = metadata_issue_dir / "issue_info.json"
        if issue_info.exists():
            try:
                import shutil
                shutil.copy2(issue_info, output_issue_dir / "issue_info.json")
            except Exception as e:
                print(f"  WARNING: Could not copy issue_info.json: {e}")

        status = f"  [OK] {issue_success} combined"
        if issue_metadata_only > 0:
            status += f", {issue_metadata_only} metadata only"
        print(status)

        issues_processed.append(issue_folder)

    # Final summary
    print("\n" + "=" * 80)
    print("COMBINATION COMPLETE")
    print("=" * 80)
    print(f"\nStatistics:")
    print(f"  Total articles processed: {total_processed}")
    print(f"  Successfully combined: {total_success}")
    print(f"  Metadata only (no full text): {total_metadata_only}")
    print(f"  Failed: {total_failed}")
    print(f"\nSuccess rate: {total_success/total_processed*100:.1f}%")
    print(f"\nOutput directory: {output_dir}")
    print(f"Issues processed: {len(issues_processed)}")
    print("=" * 80)

def main():
    print("\nThis script will combine metadata and full text into unified JSON files.")
    print("\nStructure of combined files:")
    print("  - All metadata fields (title, authors, abstract, etc.)")
    print("  - full_text field with complete article text")
    print("  - word_count field")
    print("\nOutput location: Data/articles/[issue-folder]/")

    response = input("\nProceed? (y/n): ").strip().lower()

    if response == 'y':
        process_all_articles()
        print("\n[SUCCESS] Combined JSON files created successfully!")
        print("\nYou can now access all article data in a single JSON file per article.")
    else:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
