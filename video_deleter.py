import os
import csv
from pathlib import Path

# --- Configuration ---
SOCCERNET_DIR = "data/SoccerNet"
CSV_FILE = "match_metadata.csv"

def purge_source_videos():
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file '{CSV_FILE}' not found.")
        return

    # 1. Read completed matches from the CSV
    completed_matches = set()
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None) # Skip header
        for row in reader:
            if row and len(row) > 1:
                completed_matches.add(row[1]) # The 'Match' column

    print(f"🔍 Found {len(completed_matches)} unique matches fully processed in the CSV.")
    
    # 2. Scan the SoccerNet directory for massive .mkv files
    mkv_files = list(Path(SOCCERNET_DIR).rglob("*.mkv"))
    
    if not mkv_files:
        print("✅ No .mkv files found! Your drive is already clean.")
        return
        
    print(f"📂 Scanning {len(mkv_files)} raw video files...")
    
    deleted_count = 0
    freed_space_mb = 0
    
    # 3. Safely delete files that belong to completed matches
    for mkv_path in mkv_files:
        # Reconstruct the CSV match name format (spaces replaced by underscores)
        match_name = mkv_path.parent.name.replace(" ", "_")
        
        if match_name in completed_matches:
            try:
                # Calculate file size before deleting to track freed space
                file_size = os.path.getsize(mkv_path) / (1024 * 1024) 
                os.remove(mkv_path)
                deleted_count += 1
                freed_space_mb += file_size
                print(f"🗑️ Deleted: {mkv_path.name} from {match_name}")
            except Exception as e:
                print(f"⚠️ Could not delete {mkv_path}: {e}")

    print(f"\n🎉 Cleanup Complete!")
    print(f"🔥 Total massive videos purged: {deleted_count}")
    print(f"💾 Total space freed: {freed_space_mb / 1024:.2f} GB")

if __name__ == "__main__":
    purge_source_videos()