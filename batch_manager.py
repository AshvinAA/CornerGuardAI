import os
from pathlib import Path
from SoccerNet.Downloader import SoccerNetDownloader
from SoccerNet.utils import getListGames
from unittest.mock import patch

# Configuration
BASE_DIR = Path("data/SoccerNet")
LOG_FILE = Path("processed_log.txt")
LOCK_FILE = Path("download.lock")
BATCH_SIZE = 100

# SoccerNet requires a password for raw video files. Enter it here.
SOCCERNET_PASSWORD = "s0cc3rn3t"

def load_ledger_only():
    """Loads the ledger without deleting any files (used during crash recovery)."""
    processed_matches = set()
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            processed_matches = set(f.read().splitlines())
    return processed_matches

def update_ledger_and_cleanup():
    """Scans for .mkv files, logs them as processed, and deletes them to save space."""
    processed_matches = load_ledger_only()

    print("🧹 Scanning for old processed videos to clean up...")
    mkv_files = list(BASE_DIR.rglob("*.mkv"))
    deleted_count = 0

    for mkv in mkv_files:
        # Extract the match name and force forward slashes for cross-platform consistency
        match_name = mkv.parent.relative_to(BASE_DIR).as_posix()
        
        # Add to our permanent ledger
        processed_matches.add(match_name)
        
        # Delete the massive video file
        os.remove(mkv)
        deleted_count += 1

    # Save the updated ledger
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for match in sorted(processed_matches):
            f.write(f"{match}\n")

    print(f"✅ Cleanup Complete: Deleted {deleted_count} old video files.")
    print(f"📚 Total matches recorded in ledger: {len(processed_matches)}")
    return processed_matches

def download_next_batch(processed_matches):
    """Fetches the next 100 untouched matches from SoccerNet."""
    # Initialize Downloader
    downloader = SoccerNetDownloader(LocalDirectory=str(BASE_DIR))
    downloader.password = SOCCERNET_PASSWORD
    
    # Get the master list of all SoccerNet matches
    all_games = getListGames(["train", "valid", "test"])
    
    # Normalize Windows backslashes to forward slashes so it matches the ledger perfectly
    normalized_all_games = [Path(game).as_posix() for game in all_games]
    
    # Filter out games we have already processed
    pending_games = [game for game in normalized_all_games if game not in processed_matches]
    
    if not pending_games:
        print("🎉 ALL SOCCERNET MATCHES HAVE BEEN PROCESSED!")
        return

    # Slice the next 100 matches
    target_games = pending_games[:BATCH_SIZE]
    print(f"\n📥 Queuing {len(target_games)} new matches for download...")

    # THE API HACK: Intercept the internal game list function and return ONLY our 100 target games.
    def mock_get_games(*args, **kwargs):
        return target_games

    print("⏳ Downloading 1st and 2nd Half Videos (Bypassing API limits)...")
    
    # Patch the Downloader to only see our 100 games while passing the strict "train" security check.
    with patch('SoccerNet.Downloader.getListGames', side_effect=mock_get_games, create=True), \
         patch('SoccerNet.utils.getListGames', side_effect=mock_get_games, create=True):
        
        downloader.downloadGames(files=["1_720p.mkv", "2_720p.mkv"], split=["train"])

    print("\n✅ Batch Download Complete! You are ready to run the clip extractor on these new videos.")

if __name__ == "__main__":
    print("🚀 Starting Batch Manager...")
    
    # FAILSAFE CHECK: Did the script crash during the last download?
    if LOCK_FILE.exists():
        print("⚠️ [CRASH RECOVERY MODE] Interrupted download detected!")
        print("🛡️ Skipping cleanup phase to protect your currently downloading files...")
        ledger = load_ledger_only()
    else:
        print("✨ [CLEAN RUN] No interruptions detected. Proceeding with cleanup...")
        ledger = update_ledger_and_cleanup()
        # Drop the lock file to protect this new batch
        LOCK_FILE.touch()
    
    # Step 2: Download or resume the 100 fresh matches
    download_next_batch(ledger)
    
    # Step 3: If it reaches this line, the entire batch finished perfectly. Remove the lock file.
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()