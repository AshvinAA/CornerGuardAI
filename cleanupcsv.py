import os
import csv

# --- Configuration ---
CLIPS_DIR = "data/corner_clips"
CSV_FILE = "match_metadata.csv"

def clean_csv():
    if not os.path.exists(CLIPS_DIR):
        print(f"❌ Folder '{CLIPS_DIR}' not found.")
        return
        
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file '{CSV_FILE}' not found.")
        return

    # 1. Look inside corner_clips and grab all the .mp4 filenames
    clip_files = [f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4")]
    
    if not clip_files:
        print("✅ No .mp4 files found in corner_clips. Your CSV is safe.")
        return

    # 2. Convert the .mp4 names to .jpg names to match the CSV records
    target_images = set(f.replace(".mp4", ".jpg") for f in clip_files)
    print(f"🔍 Found {len(target_images)} crashed clips to wipe from the CSV memory.")

    # 3. Read the current CSV
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        rows = list(reader)

    original_count = len(rows)

    # 4. Filter the CSV (Keep the row ONLY IF its Image_Name is NOT in our target list)
    kept_rows = [row for row in rows if row and row[0] not in target_images]
    removed_count = original_count - len(kept_rows)

    # 5. Overwrite the CSV with the cleaned data
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(kept_rows)

    print(f"🗑️ Purged {removed_count} corrupted rows from the CSV.")
    print("✅ You can now safely delete all .mp4 files in data/corner_clips and run clip_extractor.py again.")

if __name__ == "__main__":
    clean_csv()
