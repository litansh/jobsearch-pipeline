#!/usr/bin/env python3
"""
Comprehensive Israeli company search for ALL DevOps/Platform/Infrastructure leadership positions.
Searches all top 50+ Israeli companies for all position types from boards.yaml.
"""

import os
import json
import yaml
import pathlib
from datetime import date
from dotenv import load_dotenv
from scripts.utils import create_session, job_id

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARDS_CONFIG = ROOT / "configs" / "boards.yaml"
TOP_COMPANIES_CONFIG = ROOT / "configs" / "top_israeli_companies_2025.yaml"

def load_position_types():
    """Load all position types from boards.yaml."""
    with open(BOARDS_CONFIG, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('titles', [])

def load_top_companies():
    """Load all top Israeli companies from the comprehensive list."""
    with open(TOP_COMPANIES_CONFIG, 'r') as f:
        config = yaml.safe_load(f)
    
    all_companies = []
    
    # Add startups
    for startup in config.get('top_startups_2025', []):
        all_companies.append(startup)
    
    # Add best companies
    for company in config.get('best_companies_2025', []):
        all_companies.append(company)
    
    return all_companies

def search_company_career_page(company_info, position_types):
    """Search a company's career page for all position types."""
    jobs = []
    session = create_session()
    
    company_name = company_info.get('name', '')
    career_page = company_info.get('career_page')
    
    if not career_page:
        # Try common career page patterns
        career_urls = [
            f"https://{company_name}.com/careers",
            f"https://www.{company_name}.com/careers", 
            f"https://careers.{company_name}.com",
            f"https://{company_name}.com/jobs",
            f"https://jobs.{company_name}.com"
        ]
    else:
        career_urls = [career_page]
    
    for url in career_urls:
        try:
            print(f"[CAREER] Searching {company_name} at {url}")
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                page_text = response.text.lower()
                
                # Search for each position type
                for position in position_types:
                    position_lower = position.lower()
                    
                    # Look for exact position matches
                    if position_lower in page_text and 'israel' in page_text:
                        job = {
                            "title": position,
                            "company": company_info.get('description', company_name),
                            "location": "Israel", 
                            "url": url,
                            "source": "career_page",
                            "posted_at": date.today().isoformat(),
                            "jd": f"{position} role at {company_name}. {company_info.get('description', '')}",
                            "id": job_id({
                                "title": position,
                                "company": company_name,
                                "location": "Israel",
                                "url": url
                            })
                        }
                        jobs.append(job)
                        print(f"[FOUND] {position} @ {company_name}")
                        break  # Only one job per company to avoid duplicates
                
                break  # Found working URL
                
        except Exception as e:
            continue
    
    return jobs

def search_greenhouse_companies(companies, position_types):
    """Search Greenhouse companies for all position types."""
    jobs = []
    session = create_session()
    
    greenhouse_companies = [c for c in companies if c.get('greenhouse')]
    print(f"[GREENHOUSE] Searching {len(greenhouse_companies)} companies...")
    
    for company in greenhouse_companies:
        company_name = company.get('name', '')
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs"
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                greenhouse_jobs = response.json().get("jobs", [])
                
                for job in greenhouse_jobs:
                    title = job.get("title", "")
                    location = job.get("location", {}).get("name", "")
                    
                    # Check if this matches any of our position types
                    for position in position_types:
                        if position.lower() in title.lower():
                            # Check if location is Israel
                            if any(loc in location.lower() for loc in ["israel", "tel aviv", "jerusalem", "herzliya"]):
                                job_data = {
                                    "title": title,
                                    "company": company.get('description', company_name),
                                    "location": location,
                                    "url": job.get("absolute_url", ""),
                                    "source": "greenhouse",
                                    "posted_at": date.today().isoformat(),
                                    "jd": job.get("content", ""),
                                    "id": job_id({
                                        "title": title,
                                        "company": company_name,
                                        "location": location,
                                        "url": job.get("absolute_url", "")
                                    })
                                }
                                jobs.append(job_data)
                                print(f"[GREENHOUSE] {title} @ {company_name} ({location})")
                                break
        except Exception as e:
            print(f"[WARN] greenhouse {company_name}: {e}")
            continue
    
    return jobs

def search_lever_companies(companies, position_types):
    """Search Lever companies for all position types."""
    jobs = []
    session = create_session()
    
    lever_companies = [c for c in companies if c.get('lever')]
    print(f"[LEVER] Searching {len(lever_companies)} companies...")
    
    for company in lever_companies:
        company_name = company.get('name', '')
        try:
            url = f"https://api.lever.co/v0/postings/{company_name}?mode=json"
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                lever_jobs = response.json()
                
                for job in lever_jobs:
                    title = job.get("text", "")
                    location = job.get("categories", {}).get("location", "")
                    
                    # Check if this matches any of our position types
                    for position in position_types:
                        if position.lower() in title.lower():
                            # Check if location is Israel
                            if any(loc in location.lower() for loc in ["israel", "tel aviv", "jerusalem", "herzliya"]):
                                job_data = {
                                    "title": title,
                                    "company": company.get('description', company_name),
                                    "location": location,
                                    "url": job.get("hostedUrl", ""),
                                    "source": "lever",
                                    "posted_at": date.today().isoformat(),
                                    "jd": job.get("description", ""),
                                    "id": job_id({
                                        "title": title,
                                        "company": company_name,
                                        "location": location,
                                        "url": job.get("hostedUrl", "")
                                    })
                                }
                                jobs.append(job_data)
                                print(f"[LEVER] {title} @ {company_name} ({location})")
                                break
        except Exception as e:
            print(f"[WARN] lever {company_name}: {e}")
            continue
    
    return jobs

def main():
    """Run comprehensive search across all Israeli companies for all position types."""
    print("🇮🇱 Starting Comprehensive Israeli Company Search")
    print("=" * 60)
    
    # Load configuration
    position_types = load_position_types()
    companies = load_top_companies()
    
    print(f"📋 Position types to search: {len(position_types)}")
    print(f"🏢 Companies to search: {len(companies)}")
    print()
    
    all_jobs = []
    
    # Search Greenhouse companies
    greenhouse_jobs = search_greenhouse_companies(companies, position_types)
    all_jobs.extend(greenhouse_jobs)
    
    # Search Lever companies  
    lever_jobs = search_lever_companies(companies, position_types)
    all_jobs.extend(lever_jobs)
    
    # Search career pages for companies without API access
    career_page_jobs = []
    non_api_companies = [c for c in companies if not c.get('greenhouse') and not c.get('lever')]
    print(f"[CAREER_PAGES] Searching {len(non_api_companies)} companies without API access...")
    
    for company in non_api_companies[:10]:  # Limit to avoid timeouts
        career_jobs = search_company_career_page(company, position_types)
        career_page_jobs.extend(career_jobs)
        all_jobs.extend(career_jobs)
    
    # Remove duplicates
    unique_jobs = []
    seen = set()
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Save results
    if unique_jobs:
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        jobs_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in unique_jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
    
    print("=" * 60)
    print(f"✅ COMPREHENSIVE SEARCH COMPLETE")
    print(f"📊 Results:")
    print(f"   • {len(greenhouse_jobs)} from Greenhouse APIs")
    print(f"   • {len(lever_jobs)} from Lever APIs") 
    print(f"   • {len(career_page_jobs)} from career pages")
    print(f"   • {len(unique_jobs)} total unique positions")
    print(f"📁 Saved to: {jobs_file}")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
