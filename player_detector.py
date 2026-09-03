import os 
import cv2
import numpy as np 
from pathlib import Path
from ultralytics import YOLO

#I/O configuration
INPUT_DIR = Path("data/extracted_frames")
OUTPUT_DIR = Path("data/detections")
os.makedirs(OUTPUT_DIR, exist_ok=True)

#HSV color range for green lighting
LOWER_GREEN = np.array([35, 40, 40])  
UPPER_GREEN = np.array([85, 255, 255])


print("⏳ Loading YOLOv10x model...")
model = YOLO("yolov10x.pt")


#Coverting the image to HSV , isolates the green pitch and checks if the player's foot coordinates lands on a green pixel or na
def check_foot_on_grass(img , foot_x ,foot_y):

    #coverting the image to HSV color space 
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #creating a binary mask where pixels in our given green range only exists as white and everything else turns black
    grass_mask = cv2.inRange(hsv_img, LOWER_GREEN , UPPER_GREEN)

    # Ensuring the foot coordinate hasn't accidentally fallen outside the image boundaries
    height, width = grass_mask.shape
    foot_x = max(0, min(foot_x, width - 1))
    foot_y = max(0, min(foot_y, height - 1))


    #If the pixel value in the mask is greater than White , it is grass
    is_on_grass = grass_mask[foot_y, foot_x] > 0

    return is_on_grass

#Extraction engine for players/YOLO interface engine
def extract_players_from_frame(image_path):
    #extracts the image path
    img = cv2.imread(str(image_path))

    results = model.predict(
        source=img, 
        conf=0.25, 
        iou=0.65, 
        classes=[0], 
        verbose=False
    )

    detections = []

    #extracting the coordinates 
    for box in results[0].boxes :
        x1 , y1 , x2 ,y2 = map(int, box.xyxy[0].tolist())

        #points the bottom centre of a player
        foot_x = int((x1 + x2 )/2)
        foot_y = y2

        #Flag if these coordinates are on the grass or not 
        on_grass = check_foot_on_grass(img , foot_x , foot_y)

        #Soft-Flagging Logic 
        status  = "safe" if on_grass else "flagged"

        detections.append({
            "box": [x1, y1, x2, y2],
            "foot_point": [foot_x, foot_y],
            "status": status 
        })

    return img , detections
        
