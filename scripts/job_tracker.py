"""
Job tracking system with aging counter.
- Jobs start with age=1 on first appearance
- Age increments by 1 each day
- Jobs are removed after MAX_AGE days (default 14)
"""

import json
import pathlib
from datetime import date, datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOBS_JL = ROOT / "data" / "processed" / "jobs.jsonl"
TRACKED_JOBS = ROOT / "data" / "processed" / "job_tracker.json"

# Maximum age in days before jobs are removed (configurable via env)
MAX_AGE = int(os.getenv("JOB_MAX_AGE", "14"))

def load_tracked_jobs() -> Dict:
    """Load existing job tracking data."""
    if TRACKED_JOBS.exists():
        try:
            with open(TRACKED_JOBS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    return {
        "last_updated": date.today().isoformat(),
        "jobs": {}
    }

def save_tracked_jobs(data: Dict):
    """Save job tracking data."""
    with open(TRACKED_JOBS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_current_jobs() -> List[Dict]:
    """Load current jobs from jobs.jsonl."""
    jobs = []
    if JOBS_JL.exists():
        with open(JOBS_JL, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    job = json.loads(line.strip())
                    if job:  # Skip empty lines
                        jobs.append(job)
                except json.JSONDecodeError:
                    continue
    return jobs

def update_job_ages():
    """Update job ages and remove expired jobs."""
    tracked = load_tracked_jobs()
    current_jobs = load_current_jobs()
    today = date.today().isoformat()
    
    # Calculate days since last update
    last_updated = datetime.fromisoformat(tracked["last_updated"]).date()
    days_passed = (date.today() - last_updated).days
    
    if days_passed == 0:
        print("[INFO] Job ages already updated today")
        return
    
    print(f"[INFO] Updating job ages ({days_passed} days passed since last update)")
    
    # Create a set of current job IDs
    current_job_ids = {job["id"] for job in current_jobs if "id" in job}
    
    # Update existing job ages
    jobs_to_remove = []
    for job_id, job_data in tracked["jobs"].items():
        if job_id in current_job_ids:
            # Job still exists, increment age
            job_data["age"] += days_passed
            job_data["last_seen"] = today
            
            if job_data["age"] > MAX_AGE:
                jobs_to_remove.append(job_id)
                print(f"[REMOVE] Job {job_id} aged out (age: {job_data['age']} days)")
        else:
            # Job no longer exists in current jobs, mark for removal
            jobs_to_remove.append(job_id)
            print(f"[REMOVE] Job {job_id} no longer found in current jobs")
    
    # Remove expired/missing jobs
    for job_id in jobs_to_remove:
        del tracked["jobs"][job_id]
    
    # Add new jobs with age=1
    new_jobs_count = 0
    for job in current_jobs:
        job_id = job.get("id")
        if job_id and job_id not in tracked["jobs"]:
            tracked["jobs"][job_id] = {
                "age": 1,
                "first_seen": today,
                "last_seen": today,
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "url": job.get("url", "")
            }
            new_jobs_count += 1
            print(f"[NEW] Job {job_id}: {job.get('title', '')} @ {job.get('company', '')}")
    
    # Update timestamp
    tracked["last_updated"] = today
    
    # Save updated data
    save_tracked_jobs(tracked)
    
    print(f"[OK] Updated {len(tracked['jobs'])} jobs:")
    print(f"  - New jobs: {new_jobs_count}")
    print(f"  - Removed jobs: {len(jobs_to_remove)}")
    print(f"  - Active jobs: {len(tracked['jobs'])}")

def add_age_to_jobs():
    """Add age information to jobs in jobs.jsonl."""
    tracked = load_tracked_jobs()
    current_jobs = load_current_jobs()
    
    # Add age to each job
    updated_jobs = []
    for job in current_jobs:
        job_id = job.get("id")
        if job_id and job_id in tracked["jobs"]:
            job["age"] = tracked["jobs"][job_id]["age"]
            job["first_seen"] = tracked["jobs"][job_id]["first_seen"]
        else:
            job["age"] = 1
            job["first_seen"] = date.today().isoformat()
        
        updated_jobs.append(job)
    
    # Write updated jobs back to file
    with open(JOBS_JL, 'w', encoding='utf-8') as f:
        for job in updated_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"[OK] Added age information to {len(updated_jobs)} jobs")

def show_job_stats():
    """Show statistics about tracked jobs."""
    tracked = load_tracked_jobs()
    
    if not tracked["jobs"]:
        print("[INFO] No jobs being tracked")
        return
    
    # Group jobs by age
    age_groups = {}
    for job_data in tracked["jobs"].values():
        age = job_data["age"]
        if age not in age_groups:
            age_groups[age] = []
        age_groups[age].append(job_data)
    
    print(f"\n📊 JOB TRACKING STATISTICS (MAX_AGE: {MAX_AGE} days)")
    print("=" * 50)
    
    for age in sorted(age_groups.keys()):
        jobs = age_groups[age]
        print(f"Age {age} day{'s' if age != 1 else ''}: {len(jobs)} job{'s' if len(jobs) != 1 else ''}")
        for job in jobs[:3]:  # Show first 3 jobs
            print(f"  • {job['title']} @ {job['company']}")
        if len(jobs) > 3:
            print(f"  ... and {len(jobs) - 3} more")
    
    print(f"\nTotal active jobs: {len(tracked['jobs'])}")
    print(f"Last updated: {tracked['last_updated']}")

def clean_expired_jobs():
    """Remove jobs older than MAX_AGE from jobs.jsonl."""
    tracked = load_tracked_jobs()
    current_jobs = load_current_jobs()
    
    # Filter out expired jobs
    active_jobs = []
    removed_count = 0
    
    for job in current_jobs:
        job_id = job.get("id")
        if job_id and job_id in tracked["jobs"]:
            if tracked["jobs"][job_id]["age"] <= MAX_AGE:
                active_jobs.append(job)
            else:
                removed_count += 1
                print(f"[CLEAN] Removed expired job: {job.get('title', '')} @ {job.get('company', '')} (age: {tracked['jobs'][job_id]['age']})")
        else:
            # Job not tracked, keep it (will be added with age=1 next time)
            active_jobs.append(job)
    
    # Write cleaned jobs back
    with open(JOBS_JL, 'w', encoding='utf-8') as f:
        for job in active_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"[OK] Cleaned {removed_count} expired jobs. {len(active_jobs)} jobs remaining.")

def main():
    """Main job tracking function."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "stats":
            show_job_stats()
        elif command == "clean":
            clean_expired_jobs()
        elif command == "update":
            update_job_ages()
            add_age_to_jobs()
        else:
            print("Usage: python job_tracker.py [update|stats|clean]")
    else:
        # Default: update ages
        update_job_ages()
        add_age_to_jobs()

if __name__ == "__main__":
    main()
