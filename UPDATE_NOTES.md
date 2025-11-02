# Folder Naming Update - YYYYMMDD Format

## Summary
Updated the First Monday scraper to use numerical YYYYMMDD date format for folder organization instead of "D Month Year" text format.

## Changes Made

### 1. Renamed Existing Folders (Completed)
- **Script**: `rename_date_folders.py`
- **Action**: Renamed all existing date-formatted folders in both `Data/Full Text/` and `Data/metadata/` directories
- **Format Change**: `"1 September 2025"` → `"20250901"`
- **Results**:
  - Full Text: 336 folders renamed
  - metadata: 336 folders renamed
  - 17 folders skipped (non-date formats like `v11_n10`, special edition names, etc.)

### 2. Updated Scraper Code (scraper_by_issue.py)

#### Added Method: `parse_date_to_folder_name()`
- **Location**: Lines 75-104
- **Purpose**: Convert text dates (e.g., "1 September 2025") to YYYYMMDD format (e.g., "20250901")
- **Features**:
  - Handles both single and double-digit days
  - Zero-pads single-digit days (e.g., "1" → "01")
  - Supports all month names
  - Returns None if parsing fails, allowing fallback to v{volume}_n{issue} format

#### Modified Method: `save_issue_data()`
- **Location**: Lines 380-476
- **Changes**:
  - Now calls `parse_date_to_folder_name()` to convert dates
  - Falls back to `v{volume}_n{issue}` format for unparseable dates
  - Creates folders in YYYYMMDD format for all new scrapes
  - Fixed metadata directory name to use lowercase "metadata" consistently

### 3. Updated Documentation (scrape_all.py)
- Updated output message to reflect new YYYYMMDD format
- Changed from `[issue-date]` to `[YYYYMMDD]` in documentation

## Benefits of YYYYMMDD Format

1. **Chronological Sorting**: Folders sort naturally in chronological order
2. **Programmatic Processing**: Easier to parse and filter by date range
3. **Consistency**: Eliminates ambiguity in date representation
4. **Cross-Platform**: Works reliably across all operating systems
5. **Standards Compliance**: Follows ISO 8601 date format standard

## Folder Examples

### Before:
```
1 September 2025/
6 May 1996/
15 December 2003/
```

### After:
```
19960506/
20031215/
20250901/
```

## Backward Compatibility

Existing folders have been renamed, so:
- All old data is preserved
- No data loss occurred
- Folder structure remains the same (just renamed)
- Non-date folders (like `v11_n10`) remain unchanged

## Future Scraping

When running the scraper again:
- All new issues will automatically use YYYYMMDD format
- The scraper will create folders like:
  - `data/Full Text/20250901/`
  - `data/metadata/20250901/`
- Special cases or unparseable dates will fall back to `v{volume}_n{issue}` format

## Files Modified

1. `scraper_by_issue.py` - Main scraper logic updated
2. `scrape_all.py` - Documentation updated
3. `rename_date_folders.py` - One-time migration script (created)
4. `test_date_parsing.py` - Test script for date parsing (created)

## Testing

Run `test_date_parsing.py` to verify the date parsing function:
```bash
python test_date_parsing.py
```

Expected output shows proper conversion of various date formats to YYYYMMDD.

---
**Date Updated**: October 20, 2025
**Author**: FirstMonday Scraper Project
