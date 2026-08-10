import csv
from pathlib import Path

LOG_FILE = Path("processed_log.txt")
CSV_FILE = Path("match_metadata.csv")

def rebuild_ledger():
    print("🛠️ Rebuilding corrupted ledger...")
    
    # 1. Get the matches we ACTUALLY fully extracted from the CSV
    extracted_matches = set()
    if CSV_FILE.exists():
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                if len(row) > 1:
                    extracted_matches.add(row[1]) # The Match column
                    
    print(f"🔍 Found {len(extracted_matches)} fully extracted matches in your CSV.")

    # 2. Read the current bloated ledger
    if not LOG_FILE.exists():
        print("❌ No processed_log.txt found.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        bloated_ledger = f.read().splitlines()

    # 3. Filter the ledger mathematically
    repaired_ledger = []
    for line in bloated_ledger:
        # Extract just the folder name (e.g., "2015-02-21 - 18-00 Chelsea 1 - 1 Burnley")
        folder_name = line.split("/")[-1]
        
        # Convert it to the underscore format used in your CSV
        csv_formatted_name = folder_name.replace(" ", "_")
        
        # If it is in the CSV, it's safe. If not, it was falsely logged and gets purged.
        if csv_formatted_name in extracted_matches:
            repaired_ledger.append(line)

    # 4. Save the repaired ledger
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for match in sorted(repaired_ledger):
            f.write(f"{match}\n")

    print(f"✅ Ledger repaired! Shrunk from {len(bloated_ledger)} down to the true {len(repaired_ledger)} matches.")
    print("🚀 You can now run batch_manager.py to safely re-download the lost videos.")

if __name__ == "__main__":
    rebuild_ledger()