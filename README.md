<!-- ======================================================================
     BANNER — place your banner image at docs/assets/banner.png and
     uncomment the block below. 

<p align="center">
  <img src="docs/assets/banner.png" alt="Tactical Soccer Vision Pipeline" width="720" />
</p>
====================================================================== -->

# Tactical Soccer Vision Pipeline

> **Standardizing the physical space of soccer.**
> An end-to-end computer vision and data engineering pipeline that transforms chaotic broadcast footage into deterministic tactical geometry.

![Status](https://img.shields.io/badge/status-R%26D%20Paused-orange)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![YOLO](https://img.shields.io/badge/YOLOv10x-Ultralytics-00FFFF)

---

## The problem it solves

If you feed raw broadcast soccer footage into a downstream machine learning model (like XGBoost) for tactical analysis, the model will fail. Broadcast video is inherently chaotic: camera angles flip depending on the half, zoom levels change wildly, stadium lighting shifts, and players in the penalty box heavily occlude one another. 

**This pipeline enforces mathematical order on visual chaos.** It extracts raw frames from the SoccerNet dataset, detects players using a heavy-weight YOLO architecture, dynamically handles heavy occlusion without hallucinating kit colors, and mathematically maps every single corner kick to an identical `[0, 1]` coordinate plane. It does not guess; it relies on self-gating statistical filters and explicit metadata anchors.

## Screenshots & demo

### Custom Pygame Annotation Tooling
A custom-built, 60fps Pygame interface designed for lightning-fast manual QA. Scrub through clips, drop corrupted frames, and lock in canonical sides without ever touching a spreadsheet.

<p align="center">
  <!-- Placeholder for your pygame GUI screenshots -->
  <img src="docs/screenshots/pygame-gui.png" alt="Pygame Rapid-Fire Annotator" width="60%" />
</p>

### Dynamic Occlusion Handling
YOLOv10x identifying players in a dense penalty box scrum. Instead of static pixel cropping, the pipeline dynamically scans horizontal bands to hunt for the strongest jersey signal.

<p align="center">
  <!-- Placeholder for YOLO bounding box output -->
  <img src="docs/screenshots/dense-scrum-detection.png" alt="Dense scrum bounding boxes with confidence margins" width="60%" />
</p>

---

## The Canonical Architecture

The core engineering achievement of this pipeline is **Stage 3**. It takes raw YOLO bounding boxes and transforms them into perfectly standardized tactical geometry.

- **Dual-Axis Canonical Mapping** — Coordinates are normalized to a resolution-independent `[0, 1]` grid. The Y-axis is conditionally inverted so the goal line is always at $Y=0$. The X-axis is inverted based on metadata so every single corner mathematically originates from exactly $X=1, Y=1$. The downstream model only ever learns one spatial orientation.
- **Dynamic Pixel Scanning** — Fixed spatial assumptions (e.g., "the top 30% of a box is the jersey") fail on occluded players. This pipeline slices the non-overlapping sub-regions of bounding boxes into 5 horizontal bands, computes HSV Euclidean distances to ground-truth kit colors, and locks onto the band with the highest confidence margin.
- **Overlap-Scrubbing** — To maximize recall, the YOLO NMS threshold is relaxed (`iou=0.65`). To prevent the resulting bounding box overlap from causing classification bleed, the pipeline calculates cross-box IoU and strictly extracts pixels only from non-intersecting regions.
- **Statistical Self-Gating (Kicker Exclusion)** — The corner-taker must be excluded from penalty box density calculations. The pipeline calculates a high-confidence "Anchor" centroid, generates a dynamic spatial floor using the 25th percentile of origin distances, and sets an isolation threshold using the **Median Absolute Deviation (MAD)**. If the camera doesn't show the corner flag, the self-scaling statistics gracefully do nothing.

## The Data Contract (Methodology)

The design rule underneath everything: **The computer vision layer is not allowed to inject false confidence into the tactical data.**

- **Ground Truth Ingestion:** Kit colors and attacking directions are not guessed by an unsupervised clustering algorithm. They are cross-referenced directly from `match_metadata.csv` using chronological JSON event mapping (`metadata_patcher.py`).
- **Class 3 (Kicker) Exclusion:** The corner taker is explicitly flagged and removed from all downstream geometric calculations (Convex Hull, Attacker-to-Defender Ratio).
- **Class 4 (Unclassified) Degradation:** If a bounding box fails the confidence margin threshold, or if its non-overlapping pixel region is too thin, it is safely degraded to Class 4. **We intentionally trade a slight loss in recall to definitively prevent the catastrophic failure of injecting falsely classified positional data.**

## Tech stack

OpenCV + Ultralytics YOLOv10x + Pygame (Python 3.10+). Data manipulation relies on Pandas and NumPy. Designed for extraction and analysis from the SoccerNet dataset.

## Getting started

**Prerequisites:** Python 3.10+, Git. 

```bash
# 1. Clone
git clone [https://github.com/AshvinAA/Tactical-Soccer-Vision.git](https://github.com/AshvinAA/Tactical-Soccer-Vision.git)
cd Tactical-Soccer-Vision

# 2. Backend — create env, install
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Setup Directory Structure
mkdir -p data/extracted_frames data/detections data/SoccerNet
