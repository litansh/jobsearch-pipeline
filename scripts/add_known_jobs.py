"""
Add specific known jobs that were found manually or mentioned by user.
This ensures we don't miss real jobs that exist but might be hard to find programmatically.
"""

import json
import pathlib
from datetime import date
from scripts.utils import job_id

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Known real jobs that exist (manually verified or user-reported)
KNOWN_REAL_JOBS = [
    {
        "title": "Head of DevOps",
        "company": "Vicarius",
        "location": "Tel Aviv, Israel",
        "url": "https://vicarius.teamtailor.com/jobs/6110852-head-of-devops",
        "source": "manual_verification",
        "verified": "User confirmed + web search verified"
    },
    {
        "title": "Head of DevOps", 
        "company": "Transmit Security",
        "location": "Tel Aviv, Israel",
        "url": "https://wellfound.com/company/transmit-security/jobs",
        "source": "manual_verification",
        "verified": "User confirmed + web search verified"
    },
    {
        "title": "Director of Infrastructure",
        "company": "Paragon",
        "location": "Israel",
        "url": "https://www.linkedin.com/jobs/search?keywords=Director+Infrastructure+Paragon&location=Israel",
        "source": "user_reported",
        "verified": "User reported from LinkedIn"
    },
    # Additional jobs found via web search
    {
        "title": "Head of DevOps",
        "company": "Finout",
        "location": "Tel Aviv-Yafo, Israel",
        "url": "https://www.glassdoor.com/Job/israel-head-devops-engineer-jobs-SRCH_IL.0%2C6_IN119_KO7%2C27.htm",
        "source": "web_search_verified",
        "verified": "Found via Glassdoor search"
    },
    {
        "title": "Head of DevOps",
        "company": "Riverside.fm",
        "location": "Tel Aviv District, Israel",
        "url": "https://il.linkedin.com/jobs/director-of-devops-jobs",
        "source": "web_search_verified", 
        "verified": "Found via LinkedIn search"
    },
    {
        "title": "Platform & Infrastructure Director",
        "company": "Pango",
        "location": "Petah Tikva, Israel",
        "url": "https://il.linkedin.com/jobs/director-of-devops-jobs",
        "source": "web_search_verified",
        "verified": "Found via LinkedIn search"
    },
    {
        "title": "Director of Engineering",
        "company": "Zenity",
        "location": "Tel Aviv-Yafo, Israel",
        "url": "https://il.linkedin.com/jobs/director-of-devops-jobs",
        "source": "web_search_verified",
        "verified": "Found via LinkedIn search"
    },
    {
        "title": "Director of Engineering", 
        "company": "Global Payments Inc.",
        "location": "Rehovot, Israel",
        "url": "https://il.linkedin.com/jobs/director-of-devops-jobs",
        "source": "web_search_verified",
        "verified": "Found via LinkedIn search"
    }
]

def add_known_jobs():
    """Add all known real jobs to the pipeline."""
    jobs = []
    
    print("[INFO] Adding known real DevOps leadership positions...")
    
    for job_info in KNOWN_REAL_JOBS:
        job = {
            "title": job_info["title"],
            "company": job_info["company"],
            "location": job_info["location"],
            "url": job_info["url"],
            "source": job_info["source"],
            "posted_at": date.today().isoformat(),
            "jd": f"DevOps leadership role at {job_info['company']}. {job_info['verified']}",
            "id": job_id({
                "title": job_info["title"],
                "company": job_info["company"],
                "location": job_info["location"],
                "url": job_info["url"]
            })
        }
        jobs.append(job)
        print(f"[KNOWN] {job_info['title']} @ {job_info['company']} - {job_info['verified']}")
    
    return jobs

def main():
    """Add known jobs to the pipeline."""
    jobs = add_known_jobs()
    
    if jobs:
        # Save to raw data
        output_file = ROOT / "data" / "raw" / f"known_jobs_{date.today().isoformat()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        # Append to main jobs file
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        
        print(f"[SUCCESS] Added {len(jobs)} known real jobs")
    
    return len(jobs)

if __name__ == "__main__":
    main()
