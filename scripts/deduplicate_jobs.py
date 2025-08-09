"""
Deduplicate jobs from the main jobs.jsonl file.
Removes exact duplicates and filters out unwanted roles.
"""

import json
import pathlib
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Roles to exclude (no architects, tech leads, or team leads)
EXCLUDED_ROLES = [
    "architect", "tech lead", "technical lead", "team lead", "staff engineer", 
    "principal engineer", "senior engineer", "software engineer", "devops team lead"
]

# Required leadership keywords (excluding team lead and tech lead)
REQUIRED_LEADERSHIP = [
    "head", "director", "manager", "vp", "group lead"
]

def should_exclude_job(title):
    """Check if job should be excluded based on title."""
    title_lower = title.lower()
    
    # Exclude architect and tech lead roles
    for excluded in EXCLUDED_ROLES:
        if excluded in title_lower:
            return True
    
    # Must have leadership keyword
    has_leadership = any(keyword in title_lower for keyword in REQUIRED_LEADERSHIP)
    if not has_leadership:
        return True
        
    return False

def deduplicate_jobs():
    """Remove duplicates and filter unwanted roles from jobs.jsonl."""
    jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
    
    if not jobs_file.exists():
        print("[INFO] No jobs file found")
        return
    
    # Read all jobs
    jobs = []
    with open(jobs_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    job = json.loads(line.strip())
                    jobs.append(job)
                except json.JSONDecodeError:
                    continue
    
    print(f"[INFO] Read {len(jobs)} jobs from file")
    
    # Filter and deduplicate
    unique_jobs = []
    seen = set()
    excluded_count = 0
    duplicate_count = 0
    
    for job in jobs:
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")
        
        # Skip excluded roles
        if should_exclude_job(title):
            excluded_count += 1
            print(f"[EXCLUDE] {title} @ {company} (excluded role type)")
            continue
        
        # Create deduplication key
        key = f"{title.lower()}_{company.lower()}_{location.lower()}"
        
        if key in seen:
            duplicate_count += 1
            print(f"[DEDUP] {title} @ {company} ({location}) - duplicate")
            continue
        
        seen.add(key)
        unique_jobs.append(job)
    
    # Write deduplicated jobs back
    with open(jobs_file, "w", encoding="utf-8") as f:
        for job in unique_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + "\n")
    
    print(f"[OK] Deduplicated: {len(jobs)} -> {len(unique_jobs)} jobs")
    print(f"[INFO] Excluded {excluded_count} unwanted roles, {duplicate_count} duplicates")
    
    return len(unique_jobs)

if __name__ == "__main__":
    deduplicate_jobs()
