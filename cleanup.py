import os
from pathlib import Path

# The folder where your matches are saving
SOCCERNET_DIR = "data/SoccerNet"

# Updated Safety Threshold: 750 Megabytes (750,000,000 bytes)
MIN_SIZE_BYTES = 600_000_000 

def clean_broken_downloads():
    print("🧹 Scanning for video files smaller than 750 MB...")
    
    # Find every .mkv file in the entire SoccerNet folder
    video_files = list(Path(SOCCERNET_DIR).rglob('*.mkv'))
    deleted_count = 0
    
    for video in video_files:
        # Get the actual file size in bytes
        file_size = video.stat().st_size
        
        # If it is smaller than our 750MB threshold, it is corrupted or incomplete
        if file_size < MIN_SIZE_BYTES:
            mb_size = file_size / 1_000_000 # Convert to readable Megabytes
            print(f"🗑️ Deleting incomplete file ({mb_size:.1f} MB): {video.parent.name}/{video.name}")
            
            # Delete the file physically from the hard drive
            os.remove(video)
            deleted_count += 1
            
    if deleted_count == 0:
        print("\n✅ All existing files are over 650 MB. Your dataset is clean!")
    else:
        print(f"\n✅ Cleanup Complete! Vacuumed {deleted_count} broken files.")
        print("🚀 You can now run 'python download_soccernet.py' to redownload them cleanly.")

if __name__ == "__main__":
    clean_broken_downloads()