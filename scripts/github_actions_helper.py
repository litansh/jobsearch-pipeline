"""
GitHub Actions helper script to handle job state persistence.
This script manages downloading and uploading job state between workflow runs.
"""

import os
import json
import pathlib
import subprocess
from datetime import datetime
from scripts.job_state import job_state

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE_FILES = [
    "data/processed/job_state.json",
    "data/processed/job_tracker.json",
    "data/processed/jobs.jsonl"
]

def setup_git_config():
    """Configure git for automated commits."""
    try:
        subprocess.run(["git", "config", "user.name", "Job Search Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@jobsearch-pipeline.local"], check=True)
        print("[GIT] Configured git user for automated commits")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Failed to configure git: {e}")

def pull_state_from_repo():
    """Pull latest state files from repository."""
    try:
        # Pull latest changes to get any state updates
        result = subprocess.run(["git", "pull", "origin", "main"], 
                              capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("[GIT] Successfully pulled latest state from repository")
        else:
            print(f"[WARN] Git pull failed: {result.stderr}")
            
        # Ensure data directories exist
        for state_file in STATE_FILES:
            file_path = ROOT / state_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to pull state from repo: {e}")
        return False

def push_state_to_repo():
    """Push updated state files back to repository."""
    try:
        # Check if there are any changes to commit
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            print("[GIT] No state changes to commit")
            return True
            
        # Add state files
        state_files_to_add = []
        for state_file in STATE_FILES:
            file_path = ROOT / state_file
            if file_path.exists():
                state_files_to_add.append(state_file)
        
        if state_files_to_add:
            subprocess.run(["git", "add"] + state_files_to_add, check=True)
            
            # Create commit message with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
            commit_msg = f"Update job state - {timestamp}\n\n"
            commit_msg += "- Updated job state tracking\n"
            commit_msg += "- Updated job tracker data\n" 
            commit_msg += "- Updated jobs database\n"
            commit_msg += "\n[automated commit by job search pipeline]"
            
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print(f"[GIT] Successfully pushed state changes: {len(state_files_to_add)} files")
            return True
        else:
            print("[GIT] No state files to commit")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to push state to repo: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error pushing state: {e}")
        return False

def initialize_state_files():
    """Initialize state files if they don't exist."""
    try:
        # Initialize job state
        if not (ROOT / "data/processed/job_state.json").exists():
            job_state.save_state()
            print("[INIT] Created initial job_state.json")
            
        # Initialize jobs.jsonl if it doesn't exist
        jobs_file = ROOT / "data/processed/jobs.jsonl"
        if not jobs_file.exists():
            jobs_file.touch()
            print("[INIT] Created initial jobs.jsonl")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize state files: {e}")
        return False

def show_state_summary():
    """Show summary of current job state."""
    try:
        stats = job_state.get_stats()
        print("\n📊 JOB STATE SUMMARY")
        print("=" * 30)
        print(f"Applied jobs: {stats['applied']}")
        print(f"Ignored jobs: {stats['ignored']}")
        print(f"Sent to Telegram: {stats['sent_to_telegram']}")
        print(f"Last updated: {stats['last_updated']}")
        
        # Show jobs.jsonl stats
        jobs_file = ROOT / "data/processed/jobs.jsonl"
        if jobs_file.exists():
            with open(jobs_file, 'r') as f:
                job_count = sum(1 for line in f if line.strip())
            print(f"Total jobs in database: {job_count}")
        else:
            print("Total jobs in database: 0")
            
    except Exception as e:
        print(f"[ERROR] Failed to show state summary: {e}")

def main():
    """Main function for GitHub Actions integration."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python github_actions_helper.py [pull|push|init|summary|setup-git]")
        return 1
    
    command = sys.argv[1]
    
    if command == "setup-git":
        setup_git_config()
        
    elif command == "pull":
        success = pull_state_from_repo()
        return 0 if success else 1
        
    elif command == "push":
        success = push_state_to_repo()
        return 0 if success else 1
        
    elif command == "init":
        success = initialize_state_files()
        return 0 if success else 1
        
    elif command == "summary":
        show_state_summary()
        
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
