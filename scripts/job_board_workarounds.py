#!/usr/bin/env python3
"""
Workarounds for blocked job boards (AllJobs, TheMarker, Drushim, LinkedIn, Glassdoor).
Uses alternative methods to bypass anti-bot protection and JavaScript rendering.
"""

import requests
import json
import pathlib
from datetime import date
from bs4 import BeautifulSoup
from scripts.utils import create_session, job_id
import yaml
import time
import urllib.parse
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARDS_CONFIG = ROOT / "configs" / "boards.yaml"

def create_stealth_session():
    """Create a session that mimics a real browser to bypass anti-bot protection."""
    session = requests.Session()
    
    # Rotate user agents to look like real browsers
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ]
    
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })
    
    return session

def search_alljobs_workaround():
    """Workaround for AllJobs.co.il using mobile site and alternative endpoints."""
    jobs = []
    session = create_stealth_session()
    
    print("[ALLJOBS-WORKAROUND] Trying mobile site and alternative endpoints...")
    
    # Try different AllJobs endpoints
    endpoints = [
        "https://m.alljobs.co.il/",  # Mobile site
        "https://www.alljobs.co.il/mobile/",  # Mobile version
        "https://api.alljobs.co.il/jobs/",  # API endpoint
        "https://www.alljobs.co.il/jobs/search?q=DevOps+Director",  # Direct search
    ]
    
    search_terms = ["DevOps Director", "Head of DevOps", "VP DevOps", "Platform Director"]
    
    for endpoint in endpoints:
        try:
            print(f"[ALLJOBS-WORKAROUND] Trying endpoint: {endpoint}")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(2, 5))
            
            response = session.get(endpoint, timeout=15)
            
            if response.status_code == 200 and "job" in response.text.lower():
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job-related content
                job_elements = soup.find_all(['div', 'li', 'article'], 
                                           class_=lambda x: x and any(term in x.lower() for term in ['job', 'position', 'role']))
                
                for job_elem in job_elements[:3]:
                    title_elem = job_elem.find(['h1', 'h2', 'h3', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp', 'manager']):
                            job = {
                                "title": title,
                                "company": "AllJobs Listing",
                                "location": "Israel",
                                "url": endpoint,
                                "source": "alljobs_workaround",
                                "posted_at": date.today().isoformat(),
                                "jd": f"Leadership position: {title}",
                                "id": job_id({
                                    "title": title,
                                    "company": "alljobs",
                                    "location": "Israel",
                                    "url": endpoint
                                })
                            }
                            jobs.append(job)
                            print(f"[ALLJOBS-WORKAROUND] Found: {title}")
                
                if jobs:
                    break  # Found working endpoint
                    
        except Exception as e:
            print(f"[ALLJOBS-WORKAROUND] Error with {endpoint}: {e}")
            continue
    
    return jobs

def search_linkedin_workaround():
    """Workaround for LinkedIn using RSS feeds and alternative endpoints."""
    jobs = []
    session = create_stealth_session()
    
    print("[LINKEDIN-WORKAROUND] Using RSS feeds and alternative endpoints...")
    
    # LinkedIn RSS feeds (if available)
    linkedin_endpoints = [
        "https://www.linkedin.com/jobs/search/?keywords=DevOps%20Director&location=Israel",
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=DevOps%20Director&location=Israel",
        "https://linkedin.com/jobs/api/jobPostings?keywords=DevOps&location=Israel"
    ]
    
    for endpoint in linkedin_endpoints:
        try:
            print(f"[LINKEDIN-WORKAROUND] Trying: {endpoint}")
            
            # Add LinkedIn-specific headers
            session.headers.update({
                'Referer': 'https://www.linkedin.com/',
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            time.sleep(random.uniform(3, 7))  # Longer delays for LinkedIn
            
            response = session.get(endpoint, timeout=20)
            
            if response.status_code == 200:
                # Try to parse JSON response first
                try:
                    data = response.json()
                    if 'elements' in data or 'jobs' in data:
                        print(f"[LINKEDIN-WORKAROUND] Found JSON data structure")
                        # Parse job data from JSON
                        # Implementation would depend on actual API structure
                except:
                    # Parse HTML response
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    job_elements = soup.find_all(['div'], 
                                               class_=lambda x: x and 'job' in x.lower())
                    
                    for job_elem in job_elements[:3]:
                        title_elem = job_elem.find(['h3', 'h4', 'a'])
                        company_elem = job_elem.find(['h4', 'span'], 
                                                   class_=lambda x: x and 'company' in x.lower())
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            company = company_elem.get_text(strip=True) if company_elem else "LinkedIn Company"
                            
                            if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp']):
                                job = {
                                    "title": title,
                                    "company": company,
                                    "location": "Israel",
                                    "url": endpoint,
                                    "source": "linkedin_workaround",
                                    "posted_at": date.today().isoformat(),
                                    "jd": f"LinkedIn position: {title} at {company}",
                                    "id": job_id({
                                        "title": title,
                                        "company": company,
                                        "location": "Israel",
                                        "url": endpoint
                                    })
                                }
                                jobs.append(job)
                                print(f"[LINKEDIN-WORKAROUND] Found: {title} @ {company}")
                
        except Exception as e:
            print(f"[LINKEDIN-WORKAROUND] Error: {e}")
            continue
    
    return jobs

def search_glassdoor_workaround():
    """Workaround for Glassdoor using mobile site and API endpoints."""
    jobs = []
    session = create_stealth_session()
    
    print("[GLASSDOOR-WORKAROUND] Using mobile site and API endpoints...")
    
    glassdoor_endpoints = [
        "https://www.glassdoor.com/Job/israel-devops-director-jobs-SRCH_IL.0,6_IN119_KO7,21.htm",
        "https://www.glassdoor.com/api/employer/jobs/search?locId=119&jobType=devops+director",
        "https://m.glassdoor.com/Job/israel-jobs-SRCH_IL.0,6_IN119.htm?q=DevOps+Director"
    ]
    
    for endpoint in glassdoor_endpoints:
        try:
            print(f"[GLASSDOOR-WORKAROUND] Trying: {endpoint}")
            
            # Glassdoor-specific headers
            session.headers.update({
                'Referer': 'https://www.glassdoor.com/',
                'Accept': 'application/json, text/plain, */*'
            })
            
            time.sleep(random.uniform(2, 4))
            
            response = session.get(endpoint, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_elements = soup.find_all(['li', 'div'], 
                                           class_=lambda x: x and 'job' in x.lower())
                
                for job_elem in job_elements[:3]:
                    title_elem = job_elem.find(['a', 'h2', 'h3'])
                    company_elem = job_elem.find(['span'], 
                                               class_=lambda x: x and any(term in x.lower() for term in ['company', 'employer']))
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True) if company_elem else "Glassdoor Company"
                        
                        if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp']):
                            job = {
                                "title": title,
                                "company": company,
                                "location": "Israel",
                                "url": endpoint,
                                "source": "glassdoor_workaround",
                                "posted_at": date.today().isoformat(),
                                "jd": f"Glassdoor position: {title} at {company}",
                                "id": job_id({
                                    "title": title,
                                    "company": company,
                                    "location": "Israel",
                                    "url": endpoint
                                })
                            }
                            jobs.append(job)
                            print(f"[GLASSDOOR-WORKAROUND] Found: {title} @ {company}")
                
        except Exception as e:
            print(f"[GLASSDOOR-WORKAROUND] Error: {e}")
            continue
    
    return jobs

def search_themarker_workaround():
    """Workaround for TheMarker using alternative endpoints and mobile site."""
    jobs = []
    session = create_stealth_session()
    
    print("[THEMARKER-WORKAROUND] Trying alternative endpoints...")
    
    # Try different TheMarker endpoints
    endpoints = [
        "https://www.themarker.com/career/",
        "https://jobs.themarker.com/",
        "https://m.themarker.com/career/",
        "https://www.themarker.com/jobs/search?q=DevOps"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"[THEMARKER-WORKAROUND] Trying: {endpoint}")
            
            time.sleep(random.uniform(2, 4))
            
            response = session.get(endpoint, timeout=15)
            
            if response.status_code == 200 and len(response.text) > 1000:  # Has content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job-related content
                job_elements = soup.find_all(['div', 'article'], 
                                           class_=lambda x: x and any(term in x.lower() for term in ['job', 'career', 'position']))
                
                for job_elem in job_elements[:3]:
                    title_elem = job_elem.find(['h2', 'h3', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp', 'manager']):
                            job = {
                                "title": title,
                                "company": "TheMarker Listing",
                                "location": "Israel",
                                "url": endpoint,
                                "source": "themarker_workaround",
                                "posted_at": date.today().isoformat(),
                                "jd": f"Business leadership position: {title}",
                                "id": job_id({
                                    "title": title,
                                    "company": "themarker",
                                    "location": "Israel",
                                    "url": endpoint
                                })
                            }
                            jobs.append(job)
                            print(f"[THEMARKER-WORKAROUND] Found: {title}")
                
        except Exception as e:
            print(f"[THEMARKER-WORKAROUND] Error: {e}")
            continue
    
    return jobs

def main():
    """Run all job board workarounds."""
    print("🔧 Running Job Board Workarounds")
    print("=" * 50)
    
    all_jobs = []
    
    # Try each workaround
    alljobs_results = search_alljobs_workaround()
    all_jobs.extend(alljobs_results)
    
    themarker_results = search_themarker_workaround()
    all_jobs.extend(themarker_results)
    
    linkedin_results = search_linkedin_workaround()
    all_jobs.extend(linkedin_results)
    
    glassdoor_results = search_glassdoor_workaround()
    all_jobs.extend(glassdoor_results)
    
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
    
    print("=" * 50)
    print(f"✅ JOB BOARD WORKAROUNDS COMPLETE")
    print(f"📊 Results:")
    print(f"   • {len(alljobs_results)} from AllJobs workarounds")
    print(f"   • {len(themarker_results)} from TheMarker workarounds")
    print(f"   • {len(linkedin_results)} from LinkedIn workarounds")
    print(f"   • {len(glassdoor_results)} from Glassdoor workarounds")
    print(f"   • {len(unique_jobs)} total unique positions")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
