from SoccerNet.Downloader import SoccerNetDownloader
import os

# --- THE MONKEY PATCH (Fixes the Google Analytics Crash) ---
import google_measurement_protocol.report
def dummy_report(*args, **kwargs):
    pass # Do absolutely nothing
# Overwrite their tracking function with our empty one
google_measurement_protocol.report.report = dummy_report
# -----------------------------------------------------------

# 1. Set up the download folder
DOWNLOAD_DIR = "data/SoccerNet"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 2. Authenticate
mySoccerNetDownloader = SoccerNetDownloader(LocalDirectory=DOWNLOAD_DIR)
mySoccerNetDownloader.password = "s0cc3rn3t"

print("✅ Authenticated successfully. Tracker bypassed.")

# 3. DOWNLOAD THE LABELS (JSON Files)
print("📥 Downloading Match Labels...")
mySoccerNetDownloader.downloadGames(files=["Labels-v2.json"], split=["train", "valid", "test"])

# 4. DOWNLOAD THE VIDEOS
print("📥 Downloading Match Videos...")
print("⚠️ IMPORTANT: Press Ctrl + C in your terminal to stop the script once the first match is downloaded!")
mySoccerNetDownloader.downloadGames(files=["1_720p.mkv", "2_720p.mkv"], split=["train"])

print("🎉 Download Complete!")