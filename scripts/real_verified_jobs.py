"""
Add ONLY verified real DevOps leadership positions that actually exist.
Based on web search verification of actual job openings.
"""

import json
import pathlib
from datetime import date
from scripts.utils import job_id, create_session

ROOT = pathlib.Path(__file__).resolve().parents[1]

# VERIFIED real job openings (confirmed via web search)
VERIFIED_REAL_JOBS = [
    {
        "title": "Head of DevOps",
        "company": "Vicarius",
        "location": "Tel Aviv, Israel",
        "url": "https://vicarius.teamtailor.com/jobs/6110852-head-of-devops",
        "description": "Lead DevOps team, enhance tools and processes, manage infrastructure across dev and production. Hybrid role (2 days/week in office).",
        "requirements": "8+ years DevOps experience, 2+ years management, Python/Bash, AWS, Kubernetes, monitoring tools",
        "verified": "Confirmed via vicarius.teamtailor.com"
    },
    {
        "title": "Head of DevOps", 
        "company": "Transmit Security",
        "location": "Tel Aviv, Israel",
        "url": "https://wellfound.com/company/transmit-security/jobs",
        "description": "Lead DevOps group of ~20 engineers, define DevOps and production strategy, collaborate with development teams.",
        "requirements": "3+ years as Head of DevOps/Director, 2+ years managing managers/team leads, AWS/GCP, Kubernetes",
        "verified": "Confirmed via wellfound.com and thatstartupjob.com"
    }
]

# Major Israeli companies that should be checked (many missing from current search)
MAJOR_ISRAELI_COMPANIES = [
    # Major Israeli Tech Companies
    "monday.com", "wix", "outbrain", "gong", "cyberark", "checkmarx", 
    "riskified", "walkme", "fiverr", "ironSource", "nice", "verint",
    "amdocs", "varonis", "cellebrite", "sentinelone", "armis", 
    "orca-security", "aquasec", "twistlock", "guardicore", "claroty",
    "axonius", "bigid", "appdome", "lightcyber", "sysdig",
    
    # Fintech & Enterprise
    "payoneer", "pagaya", "riskified", "fundguard", "mesh-security",
    "silverfort", "vicarius", "transmit-security", "panorays",
    "cybersixgill", "cycode", "legit-security", "apiiro",
    
    # Global companies with major Israeli offices
    "nvidia", "microsoft", "google", "amazon", "meta", "apple",
    "intel", "qualcomm", "salesforce", "oracle", "sap", "vmware"
]

def add_verified_jobs():
    """Add only verified real job openings."""
    jobs = []
    
    print("[INFO] Adding VERIFIED real DevOps leadership positions...")
    
    for job_info in VERIFIED_REAL_JOBS:
        job = {
            "title": job_info["title"],
            "company": job_info["company"],
            "location": job_info["location"],
            "url": job_info["url"],
            "source": "verified_real",
            "posted_at": date.today().isoformat(),
            "jd": f"{job_info['description']} Requirements: {job_info['requirements']} (Verified: {job_info['verified']})",
            "id": job_id({
                "title": job_info["title"],
                "company": job_info["company"],
                "location": job_info["location"],
                "url": job_info["url"]
            })
        }
        jobs.append(job)
        print(f"[VERIFIED] {job_info['title']} @ {job_info['company']} - {job_info['url']}")
    
    return jobs

def search_more_real_positions():
    """Search for more real positions using comprehensive API coverage."""
    jobs = []
    session = create_session()
    
    print("[INFO] Searching for DevOps leadership positions across ALL major companies...")
    
    # ALL companies from boards.yaml + additional major Israeli companies
    greenhouse_companies = [
        # From boards.yaml
        "riskified", "jfrog", "taboola", "nice", "via", "mobility", 
        "payoneer", "pagaya", "snyk", "redis", "solarwinds", "elastic", 
        "mongodb", "datadog", "zscaler", "okta", "dropbox",
        
        # Additional major Israeli companies (many use Greenhouse)
        "monday", "wix", "outbrain", "gong", "cyberark", "checkmarx",
        "walkme", "fiverr", "ironsource", "verint", "amdocs", "varonis",
        "cellebrite", "sentinelone", "armis", "orca", "aqua", "guardicore",
        "claroty", "axonius", "bigid", "appdome", "sysdig", "fundguard",
        "silverfort", "vicarius", "transmit", "panorays", "cybersixgill",
        "cycode", "legit", "apiiro"
    ]
    
    # Also try Lever companies
    lever_companies = ["spotify"]
    
    # Keywords from boards.yaml
    devops_keywords = [
        "head of devops", "devops group lead", "director of devops", "devops director",
        "devops manager", "devops team lead", "vp devops", "chief devops",
        "head of platform", "platform director", "platform manager",
        "head of infrastructure", "infrastructure director", "infrastructure manager",
        "head of sre", "sre director", "sre manager", "engineering manager"
    ]
    
    israel_locations = ["israel", "tel aviv", "jerusalem", "haifa", "herzliya", "netanya", "ramat gan", "petach tikva"]
    
    print(f"[INFO] Searching {len(greenhouse_companies)} Greenhouse companies...")
    
    # Search Greenhouse companies
    for company in greenhouse_companies:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get("jobs", []):
                    title = job.get("title", "").lower()
                    location = job.get("location", {}).get("name", "")
                    
                    # Check if it's a DevOps leadership role
                    if any(keyword in title for keyword in devops_keywords):
                        # Check if it's in Israel
                        if any(loc in location.lower() for loc in israel_locations):
                            job_data = {
                                "title": job.get("title", ""),
                                "company": company,
                                "location": location,
                                "url": job.get("absolute_url", f"https://boards.greenhouse.io/{company}"),
                                "source": "greenhouse_api",
                                "posted_at": date.today().isoformat(),
                                "jd": job.get("content", "DevOps leadership role"),
                                "id": job_id({
                                    "title": job.get("title", ""),
                                    "company": company,
                                    "location": location,
                                    "url": job.get("absolute_url", "")
                                })
                            }
                            jobs.append(job_data)
                            print(f"[GREENHOUSE] {job.get('title', '')} @ {company} ({location})")
        except Exception as e:
            continue
    
    print(f"[INFO] Searching {len(lever_companies)} Lever companies...")
    
    # Search Lever companies
    for company in lever_companies:
        try:
            url = f"https://api.lever.co/v0/postings/{company}"
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                for job in data:
                    title = job.get("text", "").lower()
                    location = job.get("categories", {}).get("location", "")
                    
                    # Check if it's a DevOps leadership role in Israel
                    if any(keyword in title for keyword in devops_keywords):
                        if any(loc in location.lower() for loc in israel_locations):
                            job_data = {
                                "title": job.get("text", ""),
                                "company": company,
                                "location": location,
                                "url": job.get("hostedUrl", f"https://jobs.lever.co/{company}"),
                                "source": "lever_api",
                                "posted_at": date.today().isoformat(),
                                "jd": job.get("description", "DevOps leadership role"),
                                "id": job_id({
                                    "title": job.get("text", ""),
                                    "company": company,
                                    "location": location,
                                    "url": job.get("hostedUrl", "")
                                })
                            }
                            jobs.append(job_data)
                            print(f"[LEVER] {job.get('text', '')} @ {company} ({location})")
        except Exception as e:
            continue
    
    return jobs

def main():
    """Add all verified real DevOps leadership positions."""
    all_jobs = []
    
    print("[INFO] Finding ALL real DevOps leadership positions...")
    
    # Method 1: Add verified positions from web search
    verified_jobs = add_verified_jobs()
    all_jobs.extend(verified_jobs)
    
    # Method 2: Search more companies via APIs
    api_jobs = search_more_real_positions()
    all_jobs.extend(api_jobs)
    
    # Remove duplicates
    unique_jobs = []
    seen = set()
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}_{job['location'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
        else:
            print(f"[DEDUP] Skipping duplicate: {job['title']} @ {job['company']}")
    
    # Save results
    if unique_jobs:
        output_file = ROOT / "data" / "raw" / f"verified_real_{date.today().isoformat()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
        
        # Append to main jobs file
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in unique_jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        
        print(f"[SUCCESS] Found {len(unique_jobs)} VERIFIED real DevOps leadership roles")
        print(f"[INFO] Sources: {len(verified_jobs)} web-verified, {len(api_jobs)} API-verified")
    else:
        print("[INFO] No verified DevOps leadership roles found")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
