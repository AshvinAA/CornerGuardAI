import os
from pathlib import Path

SOCCERNET_DIR = "data/SoccerNet"
MIN_SIZE_BYTES = 600_000_000 

def count_videos():
    # Find all mkv files in the folder
    video_files = list(Path(SOCCERNET_DIR).rglob('*.mkv'))
    
    valid_videos = 0
    for video in video_files:
        if video.stat().st_size >= MIN_SIZE_BYTES:
            valid_videos += 1
            
    print(f"✅ Total videos downloaded: {valid_videos}")

if __name__ == "__main__":
    count_videos()