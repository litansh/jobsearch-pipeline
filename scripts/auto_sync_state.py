"""
Auto-sync job state to GitHub when local changes are detected.
This runs alongside the Telegram bot to automatically push job state changes.
"""

import time
import os
import json
import hashlib
from pathlib import Path
from scripts.github_actions_helper import push_state_to_repo, setup_git_config
from scripts.job_state import job_state

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "data" / "processed" / "job_state.json"

def get_file_hash(file_path):
    """Get MD5 hash of file for change detection."""
    if not file_path.exists():
        return None
    
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def auto_sync_loop():
    """Monitor job state file and auto-sync to GitHub when changes detected."""
    print("[AUTO_SYNC] Starting job state monitoring...")
    print("[AUTO_SYNC] Will auto-sync to GitHub when Telegram button changes are detected")
    
    setup_git_config()
    last_hash = get_file_hash(STATE_FILE)
    
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            
            current_hash = get_file_hash(STATE_FILE)
            
            if current_hash and current_hash != last_hash:
                print(f"[AUTO_SYNC] Job state file changed, syncing to GitHub...")
                
                # Show what changed
                stats = job_state.get_stats()
                print(f"[AUTO_SYNC] Current state: {stats['applied']} applied, {stats['ignored']} ignored")
                
                # Push to GitHub
                success = push_state_to_repo()
                
                if success:
                    print("[AUTO_SYNC] ✅ Successfully synced job state to GitHub")
                    print("[AUTO_SYNC] Remote GitHub Actions will now respect your button clicks")
                else:
                    print("[AUTO_SYNC] ❌ Failed to sync job state to GitHub")
                
                last_hash = current_hash
            
        except KeyboardInterrupt:
            print("\n[AUTO_SYNC] Stopping auto-sync...")
            break
        except Exception as e:
            print(f"[AUTO_SYNC] Error: {e}")
            time.sleep(60)  # Wait longer on error

def main():
    """CLI interface for auto-sync."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        auto_sync_loop()
    else:
        print("Usage: python auto_sync_state.py start")
        print("This will monitor job state changes and auto-sync to GitHub")

if __name__ == "__main__":
    main()
