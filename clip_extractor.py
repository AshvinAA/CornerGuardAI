import json
import subprocess
import os
import csv
from pathlib import Path

SOCCERNET_DIR = "data/SoccerNet"
CLIPS_DIR = "data/corner_clips" 
OUTPUT_DIR = "data/extracted_frames" 
CSV_FILE = "match_metadata.csv"

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return (int(parts[0]) * 60) + int(parts[1])
    elif len(parts) == 3:
        return (int(parts[0]) * 3600) + (int(parts[1]) * 60) + int(parts[2])
    return 0

def extract_clips():
    print("🔍 Scanning matches and extracting 17-second mini-clips...")
    
    json_files = list(Path(SOCCERNET_DIR).rglob('Labels-v2.json'))
    csv_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not csv_exists:
            writer.writerow(["Image_Name", "Match", "Half", "Outcome_Label", "Corner_Side", "Attacking_Color", "Defending_Color", "GK_Color"])

        for json_path in json_files:
            match_folder = json_path.parent
            match_name = match_folder.name.replace(" ", "_") 
            
            with open(json_path, 'r') as file:
                data = json.load(file)
            
            events = data.get("annotations", [])
            corner_count = 0
            
            for i, event in enumerate(events):
                if event.get("label") == "Corner":
                    corner_count += 1
                    
                    half_str, time_str = event.get("gameTime").split(" - ")
                    corner_seconds = time_to_seconds(time_str)
                    
                    outcome_label = 0 
                    
                    for future_event in events[i+1:]:
                        fut_half_str, fut_time_str = future_event.get("gameTime").split(" - ")
                        
                        if fut_half_str != half_str:
                            break
                            
                        time_difference = time_to_seconds(fut_time_str) - corner_seconds
                        
                        if 0 <= time_difference <= 8:
                            if future_event.get("label") in ["Goal", "Shots on target", "Shots off target"]:
                                outcome_label = 1
                                break
                        elif time_difference > 8:
                            break

                    video_path = match_folder / f"{half_str}_720p.mkv"
                    
                    if not video_path.exists():
                        continue 
                        
                    # CHANGED: T-minus 15 seconds to start the clip
                    start_time = max(0, corner_seconds - 15)
                    
                    clip_filename = f"{match_name}_corner_{corner_count}.mp4"
                    image_filename = f"{match_name}_corner_{corner_count}.jpg"
                    
                    clip_output_path = os.path.join(CLIPS_DIR, clip_filename)
                    
                    if not os.path.exists(clip_output_path):
                        # CHANGED: -t 17 limits the video strictly to 17 seconds. Added -y flag.
                        command = [
                            "ffmpeg", "-y", "-nostdin", "-ss", str(start_time), "-i", str(video_path),
                            "-t", "17", "-c:v", "libx264", "-preset", "ultrafast", clip_output_path
                        ]
                        print(f"🎬 Extracting Clip: {clip_filename} | Auto-Label: {outcome_label}")
                        
                        try:
                            # Added a 20-second timeout failsafe
                            subprocess.run(
                                command, 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.STDOUT, 
                                stdin=subprocess.DEVNULL, 
                                timeout=20
                            )
                            # If successful, log it to the CSV
                            writer.writerow([image_filename, match_name, half_str, outcome_label, "", "", "", ""])
                            
                        except subprocess.TimeoutExpired:
                            # If FFmpeg freezes, Python kills it, warns you, and skips to the next clip
                            print(f"⚠️ CORRUPTED VIDEO DETECTED: {clip_filename} caused a freeze. Skipping...")
                            if os.path.exists(clip_output_path):
                                os.remove(clip_output_path) # Clean up the broken ghost file
                            continue # Move to the next corner
                    
    print("\n✅ 17-Second Clip Extraction and Auto-Labeling Complete!")

if __name__ == "__main__":
    extract_clips()