"""
Job state management for tracking user interactions with jobs.
Tracks: applied, ignored, sent_to_telegram to prevent duplicates.
"""

import json
import pathlib
from datetime import date, datetime
from typing import Dict, Set, List
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOB_STATE_FILE = ROOT / "data" / "processed" / "job_state.json"

class JobState:
    def __init__(self):
        self.data = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load job state data from file."""
        if JOB_STATE_FILE.exists():
            try:
                with open(JOB_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "applied": {},      # job_id -> {"date": "2024-01-01", "title": "...", "company": "..."}
            "ignored": {},      # job_id -> {"date": "2024-01-01", "reason": "not_relevant"}
            "sent_to_telegram": {},  # job_id -> {"date": "2024-01-01", "sent_count": 1}
            "last_updated": date.today().isoformat()
        }
    
    def save_state(self):
        """Save job state data to file."""
        self.data["last_updated"] = date.today().isoformat()
        JOB_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(JOB_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def mark_applied(self, job_id: str, job_title: str = "", job_company: str = ""):
        """Mark a job as applied to."""
        self.data["applied"][job_id] = {
            "date": date.today().isoformat(),
            "title": job_title,
            "company": job_company
        }
        self.save_state()
        print(f"[JOB_STATE] Marked as applied: {job_title} @ {job_company}")
    
    def mark_ignored(self, job_id: str, job_title: str = "", job_company: str = "", reason: str = "not_relevant"):
        """Mark a job as ignored/not relevant."""
        self.data["ignored"][job_id] = {
            "date": date.today().isoformat(),
            "title": job_title,
            "company": job_company,
            "reason": reason
        }
        self.save_state()
        print(f"[JOB_STATE] Marked as ignored: {job_title} @ {job_company} (reason: {reason})")
    
    def mark_sent_to_telegram(self, job_id: str):
        """Mark a job as sent to Telegram."""
        if job_id in self.data["sent_to_telegram"]:
            self.data["sent_to_telegram"][job_id]["sent_count"] += 1
        else:
            self.data["sent_to_telegram"][job_id] = {
                "date": date.today().isoformat(),
                "sent_count": 1
            }
        self.save_state()
    
    def is_applied(self, job_id: str) -> bool:
        """Check if job has been applied to."""
        return job_id in self.data["applied"]
    
    def is_ignored(self, job_id: str) -> bool:
        """Check if job has been ignored."""
        return job_id in self.data["ignored"]
    
    def was_sent_to_telegram(self, job_id: str) -> bool:
        """Check if job was already sent to Telegram."""
        return job_id in self.data["sent_to_telegram"]
    
    def get_unsent_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs to only include those not yet sent to Telegram and not applied/ignored."""
        unsent = []
        for job in jobs:
            job_id = job.get("id")
            if not job_id:
                continue
                
            # Skip if already applied or ignored
            if self.is_applied(job_id) or self.is_ignored(job_id):
                continue
                
            # Skip if already sent to Telegram
            if self.was_sent_to_telegram(job_id):
                continue
                
            unsent.append(job)
        
        return unsent
    
    def get_stats(self) -> Dict:
        """Get statistics about job states."""
        return {
            "applied": len(self.data["applied"]),
            "ignored": len(self.data["ignored"]),
            "sent_to_telegram": len(self.data["sent_to_telegram"]),
            "last_updated": self.data["last_updated"]
        }
    
    def cleanup_old_entries(self, days_to_keep: int = 30):
        """Remove old entries to keep the state file manageable."""
        cutoff_date = (datetime.now().date() - timedelta(days=days_to_keep)).isoformat()
        
        # Clean up old sent_to_telegram entries
        old_sent = [job_id for job_id, data in self.data["sent_to_telegram"].items() 
                   if data.get("date", "") < cutoff_date]
        for job_id in old_sent:
            del self.data["sent_to_telegram"][job_id]
        
        if old_sent:
            print(f"[JOB_STATE] Cleaned up {len(old_sent)} old telegram entries")
            self.save_state()

# Global instance
job_state = JobState()

def main():
    """CLI interface for job state management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python job_state.py [stats|applied <job_id>|ignored <job_id>|cleanup]")
        return
    
    command = sys.argv[1]
    
    if command == "stats":
        stats = job_state.get_stats()
        print(f"\n📊 JOB STATE STATISTICS")
        print("=" * 30)
        print(f"Applied to: {stats['applied']} jobs")
        print(f"Ignored: {stats['ignored']} jobs") 
        print(f"Sent to Telegram: {stats['sent_to_telegram']} jobs")
        print(f"Last updated: {stats['last_updated']}")
        
    elif command == "applied" and len(sys.argv) > 2:
        job_id = sys.argv[2]
        job_state.mark_applied(job_id)
        
    elif command == "ignored" and len(sys.argv) > 2:
        job_id = sys.argv[2]
        job_state.mark_ignored(job_id)
        
    elif command == "cleanup":
        job_state.cleanup_old_entries()
        print("Cleaned up old job state entries")
        
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()
