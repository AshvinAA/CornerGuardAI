import csv
from pathlib import Path

CSV_FILE = Path("match_metadata.csv")
FRAMES_DIR = Path("data/extracted_frames")

def sync_csv_with_frames():
    if not CSV_FILE.exists():
        print(f"❌ Error: {CSV_FILE} not found.")
        return
    
    if not FRAMES_DIR.exists():
        print(f"❌ Error: {FRAMES_DIR} directory not found.")
        return

    # 1. Index all real image filenames physically on disk
    existing_images = {p.name for p in FRAMES_DIR.glob("*.jpg")}
    print(f"📸 Found {len(existing_images)} verified .jpg frames in {FRAMES_DIR}")

    # 2. Read the full CSV
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    initial_row_count = len(rows)
    print(f"📄 Read {initial_row_count} total rows from {CSV_FILE}")

    # 3. Filter rows strictly where Image_Name exists on disk
    valid_rows = []
    seen_images = set()

    for row in rows:
        if not row:
            continue
        image_name = row[0]
        # Keep if file exists and avoid duplicate entries
        if image_name in existing_images and image_name not in seen_images:
            valid_rows.append(row)
            seen_images.add(image_name)

    # 4. Overwrite CSV with the cleaned, synchronized dataset
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(valid_rows)

    removed_count = initial_row_count - len(valid_rows)
    print(f"🧹 Purged {removed_count} ghost/bad rows.")
    print(f"✅ Synced! CSV now contains exactly {len(valid_rows)} matching rows.")

if __name__ == "__main__":
    sync_csv_with_frames()