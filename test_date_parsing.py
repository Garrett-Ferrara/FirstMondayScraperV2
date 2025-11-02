"""
Test script to verify date parsing for folder names
"""
import re

def parse_date_to_folder_name(date_str: str):
    """
    Parse date string (e.g., "1 September 2025") to YYYYMMDD format (e.g., "20250901")
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

    print(f"Could not parse date: {date_str}")
    return None

# Test cases
test_dates = [
    "1 September 2025",
    "6 May 1996",
    "15 December 2003",
    "7 January 2002",
    "31 March 1999",
]

print("Testing date parsing:")
print("=" * 60)
for date_str in test_dates:
    result = parse_date_to_folder_name(date_str)
    print(f"{date_str:25s} -> {result}")

print("\n" + "=" * 60)
print("Test complete!")
