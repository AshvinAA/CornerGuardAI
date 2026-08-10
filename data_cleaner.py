import pygame
import cv2
import os
import csv
import sys

# --- Configurations ---
CLIPS_DIR = "data/corner_clips"
OUTPUT_DIR = "data/extracted_frames"
CSV_FILE = "match_metadata.csv"

# Colors for Pygame UI
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)

def remove_csv_row(target_image_name):
    """Reads the CSV, filters out the trashed clip, and safely rewrites it."""
    if not os.path.exists(CSV_FILE):
        return

    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        rows = list(reader)

    # Keep rows where the Image_Name does NOT match the target
    kept_rows = [row for row in rows if row[0] != target_image_name]

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(kept_rows)
    print(f"🗑️  Removed {target_image_name} from {CSV_FILE}")

def load_video_frames(video_path):
    """Loads all frames of the 7-second clip into RAM for instant scrubbing."""
    cap = cv2.VideoCapture(video_path)
    cv2_frames = []   # Original BGR frames for saving the final .jpg
    pygame_surfs = [] # RGB Pygame surfaces for display

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2_frames.append(frame)
        
        # Convert BGR to RGB for Pygame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to Pygame surface (transpose needed because Pygame uses x,y instead of row,col)
        surf = pygame.image.frombuffer(frame_rgb.flatten(), (frame_rgb.shape[1], frame_rgb.shape[0]), 'RGB')
        pygame_surfs.append(surf)

    cap.release()
    return cv2_frames, pygame_surfs

def main():
    pygame.init()
    
    # Setup Pygame display (720p resolution matches the SoccerNet standard)
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Tactical Frame Annotator")
    font = pygame.font.SysFont("consolas", 20, bold=True)

    # Get list of remaining clips
    clips = [f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4")]
    
    if not clips:
        print("🎉 No clips found! The folder is completely empty.")
        pygame.quit()
        sys.exit()

    print(f"🔍 Found {len(clips)} clips to process.")

    # Process each clip one by one
    for clip_name in clips:
        clip_path = os.path.join(CLIPS_DIR, clip_name)
        target_image_name = clip_name.replace(".mp4", ".jpg")
        
        print(f"\nLoading: {clip_name}...")
        cv2_frames, pygame_surfs = load_video_frames(clip_path)
        
        if not cv2_frames:
            print(f"⚠️ Corrupted or empty video: {clip_name}. Trashing...")
            remove_csv_row(target_image_name)
            os.remove(clip_path)
            continue

        total_frames = len(cv2_frames)
        frame_index = 0
        processing_clip = True

        while processing_clip:
            # 1. Handle UI drawing
            screen.fill(BLACK)
            screen.blit(pygame_surfs[frame_index], (0, 0))

            # Draw overlay banner
            pygame.draw.rect(screen, BLACK, (0, 0, 1280, 40))
            
            text_info = font.render(f"Clip: {clip_name} | Frame: {frame_index + 1}/{total_frames}", True, WHITE)
            text_controls = font.render("[ENTER]: Save Frame | [X]: Trash Clip | [ESC]: Quit", True, GREEN)
            
            screen.blit(text_info, (10, 10))
            screen.blit(text_controls, (700, 10))
            
            pygame.display.flip()

            # 2. Handle Inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    shift_held = mods & pygame.KMOD_SHIFT
                    skip_amount = 10 if shift_held else 1

                    # Scrubbing Left/Right
                    if event.key == pygame.K_RIGHT:
                        frame_index = min(total_frames - 1, frame_index + skip_amount)
                    elif event.key == pygame.K_LEFT:
                        frame_index = max(0, frame_index - skip_amount)

                    # TRASH CLIP (Requirement 1 & 2)
                    elif event.key == pygame.K_x:
                        remove_csv_row(target_image_name)
                        os.remove(clip_path)
                        print(f"❌ Dumped clip: {clip_name}")
                        processing_clip = False # Breaks inner loop, moves to next video
                    
                    # SAVE FRAME (Requirement 2)
                    elif event.key == pygame.K_RETURN:
                        output_img_path = os.path.join(OUTPUT_DIR, target_image_name)
                        # Save using cv2 to perfectly preserve the original video quality
                        cv2.imwrite(output_img_path, cv2_frames[frame_index])
                        os.remove(clip_path)
                        print(f"✅ Saved Golden Frame: {target_image_name}")
                        processing_clip = False # Breaks inner loop, moves to next video
                    
                    # SAFETY QUIT
                    elif event.key == pygame.K_ESCAPE:
                        print("🛑 Safely exiting. Progress saved.")
                        pygame.quit()
                        sys.exit()

    print("\n🏆 All clips processed! The folder is empty.")
    pygame.quit()

if __name__ == "__main__":
    main()