# Tactical Soccer Vision Pipeline (SoccerNet)

An end-to-end computer vision and data engineering pipeline designed to extract, clean, and process tactical soccer footage (specifically corner kicks) from the SoccerNet dataset. The system transforms raw, chaotic broadcast video into a standardized, mathematically rigorous 2D coordinate plane for downstream tactical modeling (e.g., XGBoost).

##  Project Overview
Broadcast soccer footage suffers from extreme variance in camera angles, zoom levels, lighting conditions, and player occlusion. This pipeline solves these issues through deterministic spatial mapping, dynamic color signal scanning, and self-gating statistical filters. It ensures that the tactical geometry of a penalty box scrum is captured accurately without algorithmic hallucination.

##  Architecture & Pipeline

### Stage 1: Metadata Ingestion & Data Mining
* Parses raw SoccerNet `Labels-v2.json` files to isolate specific chronological events (Corner Kicks).
* Extracts event metadata (home/away possession, match timestamps) to anchor the visual data in absolute ground truth.

### Stage 2: Player Detection & Data Cleaning
* **Detection Engine (`player_detector.py`):** Utilizes **YOLOv10x** (Extra Large) for high-recall player detection in dense scrums. Employs relaxed NMS thresholds (IoU=0.65) to preserve distinct bounding boxes in tight marking situations.
* **Custom Annotation GUI (`data_cleaner.py`):** A custom Pygame-based scrubbing engine built to instantly load, visualize, and drop corrupted frames or falsely classified clips at 60fps without manual spreadsheet data entry.

### Stage 2.5: Context Synchronization
* **Dynamic Kit Patcher (`metadata_patcher.py`):** Automatically maps changing HSV kit colors (Home, Away, Goalkeeper) to specific corner events based on parsed match possession data.
* **Rapid-Fire Tagger (`corner_tagger.py`):** A Pygame interface for lightning-fast manual tagging of `Corner_Side` (Left/Right) to set up the canonical coordinate mapping.

### Stage 3: Canonical Mapping & Team Classification (Architecture Locked)
* **Canonical Spatial Mapping:** Maps raw YOLO pixel coordinates to a normalized `[0, 1]` grid. Applies a Dual-Axis Flip (conditional Y-axis and X-axis inversion) to ensure rotational invariance—forcing every corner kick to originate mathematically from `(1, 1)`.
* **Occlusion-Aware Pixel Scanning:** Mitigates pixel contamination from overlapping bounding boxes by restricting HSV color extraction to strictly non-intersecting sub-regions. Scans boxes in overlapping horizontal bands to hunt for the strongest jersey signal, bypassing traditional fixed-crop assumptions.
* **Automated Kicker Exclusion (MAD Filter):** Dynamically isolates and excludes the corner-taker from the tactical geometry using a Median Absolute Deviation (MAD) threshold. This self-scaling statistical filter prevents the outlier kicker from masking true penalty box density.
* **Anchor/Fringe Splitting:** Prevents cascading uncertainty by computing the scrum's structural centroid using only high-confidence detections ("Anchors"), while gracefully degrading highly occluded players ("Fringe") into an Unclassified subset.

##  Tech Stack
* **Computer Vision:** OpenCV, Ultralytics YOLOv10
* **Data Processing:** Pandas, NumPy
* **Custom Tooling/GUI:** Pygame
* **Data Source:** SoccerNet Dataset

##  Current Status
**Status: Development Paused**
The project successfully completed extraction, detection, and metadata synchronization (Stages 1–2.5). The theoretical architecture for Stage 3 (Canonical Mapping) is fully designed and stress-tested against severe edge cases (dual goalkeepers, pixel contamination, statistical masking). Development is temporarily paused to conduct a deeper theoretical study of image processing fundamentals (linear algebra, optics, and signal processing) before executing the final mathematical mapping layer.
