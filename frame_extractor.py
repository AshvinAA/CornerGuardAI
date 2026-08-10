import json
import subprocess
import os
import csv
from pathlib import Path

#destination defined
SOCCERNET_DIR = "data/SoccerNet"
OUTPUT_DIR = "data/extracted_frames"
CSV_FILE = "match_metadata.csv"

#defining where the images would be saved 
os.makedirs(OUTPUT_DIR, exist_ok=True)

def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return (int(parts[0]) * 60) + int(parts[1])
    elif len(parts) == 3:
        return (int(parts[0]) * 3600) + (int(parts[1]) * 60) + int(parts[2])
    return 0

def extract_frames():
    print("🔍 Scanning matches and extracting frames...")

    #making a list of all the json files 
    json_files = list(Path(SOCCERNET_DIR).rglob('Labels-v2.json'))
    csv_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)

        #creating the csv and the columns inside if the csv does not exist
        if not csv_exists:
            writer.writerow(["Image_Name", "Match", "Half", "Outcome_Label", "Corner_Side", "Attacking_Color", "Defending_Color", "GK_Color"])


        for json_path in json_files:
            #summoning the folder where this json exists
            match_folder = json_path.parent
            
            match_name = match_folder.name.replace(" ", "_") 

            #gets the json file
            with open(json_path, 'r') as file:
                data = json.load(file)

            #extracts the events that happened as a list
            events = data.get("annotations", [])
            corner_count = 0

            ## Finding the Corner and Auto-Labeling
            for i, event in enumerate(events):
                if event.get("label") == "Corner":
                    corner_count += 1
                    
                    half_str, time_str = event.get("gameTime").split(" - ")
                    corner_seconds = time_to_seconds(time_str)
                    
                    outcome_label = 0 
                    
                    for future_event in events[i+1:]:
                        fut_half_str, fut_time_str = future_event.get("gameTime").split(" - ")

                        #if the shot is being taken in the second half --> its not derived from the corner
                        if fut_half_str != half_str:
                            break

                        #The time difference between the corner and a probable shot being taken
                        time_difference = time_to_seconds(fut_time_str) - corner_seconds

                        #If its within 8 seconds --> means this was a succesful corner
                        if 0 <= time_difference <= 8:
                            if future_event.get("label") in ["Goal", "Shots on target", "Shots off target"]:
                                outcome_label = 1
                                break
                        elif time_difference > 8:
                            break

                    
                    video_path = match_folder / f"{half_str}_720p.mkv"
                    
                    # Checking if the file exists or not
                    if not video_path.exists():
                        continue 

                    #making sure that the time we are aiming is 1.5 seconds before the kick is taken
                    extraction_time = max(0, corner_seconds - 1.5)

                    #setting the output destination and settings 
                    image_filename = f"{match_name}_corner_{corner_count}.jpg"
                    output_path = os.path.join(OUTPUT_DIR, image_filename)

                    #Flag for duplication if the script runs again
                    if not os.path.exists(output_path):
                        command = [
                            "ffmpeg", "-ss", str(extraction_time), "-i", str(video_path),
                            "-vframes", "1", "-q:v", "2", output_path
                        ]
                        print(f"📸 Extracting: {image_filename} | Auto-Label: {outcome_label}")
                        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                        
                        writer.writerow([image_filename, match_name, half_str, outcome_label, "", "", "", ""])
                    
    print("\n✅ Extraction and Auto-Labeling Complete!")

if __name__ == "__main__":
    extract_frames()