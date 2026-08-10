import csv

CSV_FILE = "match_metadata.csv"

def clean_duplicates():
    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

    # We will track which Image_Names we have already seen
    seen_images = set()
    cleaned_data = []

    for row in data:
        image_name = row[0]
        # If we haven't seen this image name before, add it to our clean list
        if image_name not in seen_images:
            seen_images.add(image_name)
            cleaned_data.append(row)

    # Overwrite the CSV with only the unique rows
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_data)

    print(f"✅ Cleaned! Reduced from {len(data)} rows to {len(cleaned_data)} unique rows.")

if __name__ == "__main__":
    clean_duplicates()