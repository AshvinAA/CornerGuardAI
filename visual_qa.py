import os
import csv
import json
import pygame
import cv2
import numpy as np
from pathlib import Path

# Import our vision engine
from player_detector import extract_players_from_frame

# --- SECTION 1: Configuration ---
CSV_FILE = Path("match_metadata.csv")
FRAMES_DIR = Path("data/extracted_frames")
JSON_DIR = Path("data/detections")
os.makedirs(JSON_DIR, exist_ok=True)

# Pygame Colors
COLOR_SAFE = (0, 255, 0)      # Green for grass-verified
COLOR_FLAGGED = (255, 165, 0) # Orange for borderline/off-pitch
COLOR_NEW = (0, 255, 255)     # Cyan for manually added boxes

# --- SECTION 2: The Pygame App ---
def run_qa_tool():
    pygame.init()
    
    # 1. Load the synced CSV
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    print(f"🚀 Starting QA Tool for {len(rows)} frames...")
    
    # Initialize Pygame window (will resize dynamically per image)
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Stage 2: Bounding Box QA (Space: Save & Next | Click: Delete | Drag: Add | Ctrl+Z: Undo)")
    
    for row in rows:
        image_name = row[0]
        image_path = FRAMES_DIR / image_name
        json_path = JSON_DIR / image_name.replace(".jpg", ".json")
        
        # Skip if we already QA'd this frame
        if json_path.exists():
            continue
            
        print(f"🔍 Processing: {image_name}")
        
        # 2. Run the Vision Engine (YOLO + Grass Filter)
        cv2_img, detections = extract_players_from_frame(image_path)
        
        # Convert OpenCV BGR image to Pygame RGB surface
        cv2_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        img_surface = pygame.surfarray.make_surface(np.swapaxes(cv2_rgb, 0, 1))
        
        # Resize window to exactly match the video frame
        img_w, img_h = img_surface.get_size()
        screen = pygame.display.set_mode((img_w, img_h))
        
        # 3. Interactive Loop State Variables
        drawing = False
        start_pos = (0, 0)
        current_pos = (0, 0)
        running_frame = True
        deleted_boxes = [] # Stack for Ctrl+Z
        
        while running_frame:
            screen.blit(img_surface, (0, 0))
            
            # Draw existing detections
            for i, det in enumerate(detections):
                x1, y1, x2, y2 = det["box"]
                color = COLOR_SAFE if det["status"] == "safe" else COLOR_FLAGGED
                if det["status"] == "manual": color = COLOR_NEW
                
                pygame.draw.rect(screen, color, (x1, y1, x2-x1, y2-y1), 2)
                # Draw the foot anchor point
                pygame.draw.circle(screen, color, det["foot_point"], 4)

            # Draw the box currently being dragged by the mouse
            if drawing:
                dx = current_pos[0] - start_pos[0]
                dy = current_pos[1] - start_pos[1]
                pygame.draw.rect(screen, COLOR_NEW, (start_pos[0], start_pos[1], dx, dy), 2)

            pygame.display.flip()
            
            # 4. Event Handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # SAVE & ADVANCE
                        save_detections(json_path, image_name, detections)
                        running_frame = False 
                        
                    # UNDO Logic
                    elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if deleted_boxes:
                            restored_box = deleted_boxes.pop() 
                            detections.append(restored_box)    
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left Click
                        mouse_x, mouse_y = event.pos
                        
                        # Check if clicking INSIDE an existing box to DELETE it
                        clicked_box = False
                        for det in detections:
                            x1, y1, x2, y2 = det["box"]
                            if x1 <= mouse_x <= x2 and y1 <= mouse_y <= y2:
                                deleted_boxes.append(det) # Save to memory before deleting
                                detections.remove(det)
                                clicked_box = True
                                break # Only delete one box per click
                        
                        # If we didn't click a box, start DRAWING a new one
                        if not clicked_box:
                            drawing = True
                            start_pos = event.pos
                            current_pos = event.pos
                            
                elif event.type == pygame.MOUSEMOTION:
                    if drawing:
                        current_pos = event.pos
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and drawing:
                        drawing = False
                        end_pos = event.pos
                        
                        # Math to handle dragging in any direction
                        x1 = min(start_pos[0], end_pos[0])
                        x2 = max(start_pos[0], end_pos[0])
                        y1 = min(start_pos[1], end_pos[1])
                        y2 = max(start_pos[1], end_pos[1])
                        
                        # Ignore accidental micro-clicks (must be a real box)
                        if x2 - x1 > 10 and y2 - y1 > 10:
                            foot_x = int((x1 + x2) / 2)
                            foot_y = y2
                            detections.append({
                                "box": [x1, y1, x2, y2],
                                "foot_point": [foot_x, foot_y],
                                "status": "manual"
                            })

    print("🎉 All frames QA'd! Stage 2 Complete.")
    pygame.quit()

def save_detections(json_path, image_name, detections):
    """Packages the validated data and saves to disk."""
    data = {
        "image": image_name,
        "total_players": len(detections),
        "players": detections
    }
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    run_qa_tool()