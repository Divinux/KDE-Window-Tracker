import re
import sys
import os
from datetime import datetime, timezone

INPUT_FILE = os.path.expanduser("~/.window_activity.jsonl")
BACKUP_FILE = os.path.expanduser("~/.window_activity.jsonl.bu")
TEMP_FILE = os.path.expanduser("~/.window_activity.jsonl.tmp")

timestamp_pattern = re.compile(
    r'("timestamp"\s*:\s*)"([^"]+)"'
)

entry_pattern = re.compile(
    r'\{\s*"timestamp"\s*:\s*([^,]+),\s*'
    r'"class"\s*:\s*("(?:\\.|[^"\\])*"),\s*'
    r'"title"\s*:\s*("(?:\\.|[^"\\])*")\s*\}'
)

if os.path.exists(BACKUP_FILE):
    sys.exit(f"Error: Backup already exists: {BACKUP_FILE}")

if not os.path.isfile(INPUT_FILE):
    sys.exit(f"Error: Input file not found: {INPUT_FILE}")

os.rename(INPUT_FILE, BACKUP_FILE)

try:
    with open(BACKUP_FILE, "r", encoding="utf-8", newline="") as infile, \
         open(TEMP_FILE, "w", encoding="utf-8", newline="") as outfile:

        for line_number, line in enumerate(infile, start=1):

            # Convert the timestamp to Unix time.
            def convert_timestamp(match):
                try:
                    timestamp = datetime.fromisoformat(match.group(2))

                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)

                    return f"{match.group(1)}{timestamp.timestamp()}"

                except ValueError as e:
                    print(
                        f"Invalid timestamp on line {line_number}: {e}",
                        file=sys.stderr
                    )
                    return match.group(0)

            line = timestamp_pattern.sub(
                convert_timestamp, line, count=1
            )

            # Remove field names and use square brackets.
            match = entry_pattern.search(line)

            if match:
                timestamp, window_class, title = match.groups()
                line = (
                    f"[{timestamp.strip()},{window_class},{title}]"
                    + line[match.end():]
                )
            else:
                print(
                    f"Unmatched line {line_number}",
                    file=sys.stderr
                )

            outfile.write(line)

    os.replace(TEMP_FILE, INPUT_FILE)

except Exception:
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
    raise

print(f"Backup saved to: {BACKUP_FILE}")
print(f"Converted log written to: {INPUT_FILE}")
