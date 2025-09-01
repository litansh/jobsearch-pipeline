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
    
    def remove_applied(self, job_id: str):
        """Remove a job from applied list (reverse accidental marking)."""
        if job_id in self.data["applied"]:
            job_info = self.data["applied"][job_id]
            del self.data["applied"][job_id]
            self.save_state()
            print(f"[JOB_STATE] Removed from applied: {job_info.get('title', '')} @ {job_info.get('company', '')}")
            return True
        else:
            print(f"[JOB_STATE] Job {job_id} not found in applied list")
            return False
    
    def remove_ignored(self, job_id: str):
        """Remove a job from ignored list (reverse accidental marking)."""
        if job_id in self.data["ignored"]:
            job_info = self.data["ignored"][job_id]
            del self.data["ignored"][job_id]
            self.save_state()
            print(f"[JOB_STATE] Removed from ignored: {job_info.get('title', '')} @ {job_info.get('company', '')}")
            return True
        else:
            print(f"[JOB_STATE] Job {job_id} not found in ignored list")
            return False
    
    def remove_sent_to_telegram(self, job_id: str):
        """Remove a job from sent_to_telegram list (allow it to be sent again)."""
        if job_id in self.data["sent_to_telegram"]:
            del self.data["sent_to_telegram"][job_id]
            self.save_state()
            print(f"[JOB_STATE] Removed from sent list: {job_id} (will appear in next digest)")
            return True
        else:
            print(f"[JOB_STATE] Job {job_id} not found in sent list")
            return False
    
    def list_applied_jobs(self):
        """List all applied jobs with their IDs."""
        if not self.data["applied"]:
            print("No applied jobs found")
            return
        
        print("\n📝 APPLIED JOBS:")
        print("=" * 50)
        for job_id, job_info in self.data["applied"].items():
            print(f"ID: {job_id[:12]}...")
            print(f"   {job_info.get('title', 'Unknown')} @ {job_info.get('company', 'Unknown')}")
            print(f"   Applied: {job_info.get('date', 'Unknown')}")
            print()
    
    def list_ignored_jobs(self):
        """List all ignored jobs with their IDs."""
        if not self.data["ignored"]:
            print("No ignored jobs found")
            return
        
        print("\n❌ IGNORED JOBS:")
        print("=" * 50)
        for job_id, job_info in self.data["ignored"].items():
            print(f"ID: {job_id[:12]}...")
            print(f"   {job_info.get('title', 'Unknown')} @ {job_info.get('company', 'Unknown')}")
            print(f"   Ignored: {job_info.get('date', 'Unknown')} (reason: {job_info.get('reason', 'Unknown')})")
            print()
    
    def search_job_by_title_company(self, title_part: str, company_part: str = ""):
        """Find job IDs by partial title and company match."""
        matches = []
        
        # Search in applied jobs
        for job_id, job_info in self.data["applied"].items():
            job_title = job_info.get('title', '').lower()
            job_company = job_info.get('company', '').lower()
            
            if (title_part.lower() in job_title and 
                (not company_part or company_part.lower() in job_company)):
                matches.append({
                    'id': job_id,
                    'title': job_info.get('title', ''),
                    'company': job_info.get('company', ''),
                    'status': 'applied',
                    'date': job_info.get('date', '')
                })
        
        # Search in ignored jobs
        for job_id, job_info in self.data["ignored"].items():
            job_title = job_info.get('title', '').lower()
            job_company = job_info.get('company', '').lower()
            
            if (title_part.lower() in job_title and 
                (not company_part or company_part.lower() in job_company)):
                matches.append({
                    'id': job_id,
                    'title': job_info.get('title', ''),
                    'company': job_info.get('company', ''),
                    'status': 'ignored',
                    'date': job_info.get('date', ''),
                    'reason': job_info.get('reason', '')
                })
        
        return matches

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
        print("Usage:")
        print("  python job_state.py stats                    # Show statistics")
        print("  python job_state.py list-applied             # List applied jobs")
        print("  python job_state.py list-ignored             # List ignored jobs")
        print("  python job_state.py search <title> [company] # Search jobs by title/company")
        print("  python job_state.py remove-applied <job_id>  # Remove from applied (reverse)")
        print("  python job_state.py remove-ignored <job_id>  # Remove from ignored (reverse)")
        print("  python job_state.py reset-sent <job_id>      # Allow job to be sent again")
        print("  python job_state.py cleanup                  # Clean up old entries")
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
        
    elif command == "list-applied":
        job_state.list_applied_jobs()
        
    elif command == "list-ignored":
        job_state.list_ignored_jobs()
        
    elif command == "search" and len(sys.argv) > 2:
        title_part = sys.argv[2]
        company_part = sys.argv[3] if len(sys.argv) > 3 else ""
        matches = job_state.search_job_by_title_company(title_part, company_part)
        
        if not matches:
            print(f"No jobs found matching '{title_part}' {f'at {company_part}' if company_part else ''}")
        else:
            print(f"\n🔍 SEARCH RESULTS for '{title_part}' {f'at {company_part}' if company_part else ''}:")
            print("=" * 60)
            for match in matches:
                print(f"ID: {match['id'][:12]}...")
                print(f"   {match['title']} @ {match['company']}")
                print(f"   Status: {match['status']} on {match['date']}")
                if match['status'] == 'ignored':
                    print(f"   Reason: {match.get('reason', 'Unknown')}")
                print()
        
    elif command == "remove-applied" and len(sys.argv) > 2:
        job_id = sys.argv[2]
        success = job_state.remove_applied(job_id)
        if success:
            print("✅ Job removed from applied list - it may appear in future digests")
        
    elif command == "remove-ignored" and len(sys.argv) > 2:
        job_id = sys.argv[2]
        success = job_state.remove_ignored(job_id)
        if success:
            print("✅ Job removed from ignored list - it may appear in future digests")
        
    elif command == "reset-sent" and len(sys.argv) > 2:
        job_id = sys.argv[2]
        success = job_state.remove_sent_to_telegram(job_id)
        if success:
            print("✅ Job removed from sent list - it will appear in next digest")
        
    elif command == "cleanup":
        job_state.cleanup_old_entries()
        print("Cleaned up old job state entries")
        
    else:
        print("Invalid command or missing parameters")

if __name__ == "__main__":
    main()
