#!/usr/bin/env python3
"""
Search Israeli job boards directly for DevOps/Platform/Infrastructure leadership positions.
Uses direct web scraping since RSS feeds are broken.
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

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARDS_CONFIG = ROOT / "configs" / "boards.yaml"

def load_position_types():
    """Load all position types from boards.yaml."""
    with open(BOARDS_CONFIG, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('titles', [])

def search_alljobs_direct(position_types):
    """Search AllJobs.co.il directly for leadership positions."""
    jobs = []
    session = create_session()
    
    print("[ALLJOBS] Searching AllJobs.co.il directly...")
    
    # Key DevOps/Platform leadership search terms
    search_terms = [
        "DevOps Director", "Head of DevOps", "VP DevOps",
        "Platform Director", "Head of Platform", "VP Platform",
        "Infrastructure Director", "Head of Infrastructure", "VP Infrastructure", 
        "SRE Director", "Head of SRE", "VP SRE",
        "VP Engineering", "Director of Engineering", "CTO"
    ]
    
    base_url = "https://www.alljobs.co.il/SearchResultsGuest.aspx"
    
    for term in search_terms[:5]:  # Limit to avoid rate limiting
        try:
            params = {
                'Position': term,
                'Region': '2,3,4',  # Tel Aviv, Jerusalem, Haifa
                'Seniority': '5,6'  # Senior, Management
            }
            
            print(f"[ALLJOBS] Searching for: {term}")
            response = session.get(base_url, params=params, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job listings in the HTML
                job_links = soup.find_all('a', href=True)
                job_titles = soup.find_all(['h2', 'h3', 'div'], class_=lambda x: x and 'job' in x.lower())
                
                # Extract job information from page structure
                for i, title_elem in enumerate(job_titles[:3]):  # Limit results
                    title_text = title_elem.get_text(strip=True)
                    
                    if any(keyword.lower() in title_text.lower() for keyword in ['director', 'head', 'vp', 'manager']):
                        job = {
                            "title": title_text,
                            "company": "AllJobs Listing",
                            "location": "Israel",
                            "url": f"{base_url}?Position={urllib.parse.quote(term)}",
                            "source": "alljobs_direct",
                            "posted_at": date.today().isoformat(),
                            "jd": f"Leadership position: {title_text}",
                            "id": job_id({
                                "title": title_text,
                                "company": "alljobs",
                                "location": "Israel",
                                "url": f"{base_url}?Position={urllib.parse.quote(term)}"
                            })
                        }
                        jobs.append(job)
                        print(f"[ALLJOBS] Found: {title_text}")
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"[ALLJOBS] Error searching {term}: {e}")
            continue
    
    return jobs

def search_jobmaster_direct(position_types):
    """Search JobMaster for DevOps leadership positions."""
    jobs = []
    session = create_session()
    
    print("[JOBMASTER] Searching JobMaster.co.il...")
    
    try:
        # JobMaster search URL
        base_url = "https://www.jobmaster.co.il/jobs/"
        search_url = f"{base_url}?q=DevOps+Director+Head+VP+Platform+Infrastructure"
        
        response = session.get(search_url, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for job listings
            job_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in x.lower())
            
            for job_elem in job_elements[:5]:  # Limit results
                title_elem = job_elem.find(['h2', 'h3', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Check if it's a leadership position
                    if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp', 'manager', 'lead']):
                        job = {
                            "title": title,
                            "company": "JobMaster Listing", 
                            "location": "Israel",
                            "url": search_url,
                            "source": "jobmaster_direct",
                            "posted_at": date.today().isoformat(),
                            "jd": f"Leadership position: {title}",
                            "id": job_id({
                                "title": title,
                                "company": "jobmaster",
                                "location": "Israel", 
                                "url": search_url
                            })
                        }
                        jobs.append(job)
                        print(f"[JOBMASTER] Found: {title}")
        
    except Exception as e:
        print(f"[JOBMASTER] Error: {e}")
    
    return jobs

def search_drushim_direct(position_types):
    """Search Drushim.co.il for DevOps leadership positions."""
    jobs = []
    session = create_session()
    
    print("[DRUSHIM] Searching Drushim.co.il...")
    
    # Hebrew and English search terms
    search_terms = [
        "DevOps Director", "Head DevOps", "VP DevOps",
        "מנהל DevOps", "ראש צוות DevOps", "מנהל תשתיות"
    ]
    
    try:
        base_url = "https://www.drushim.co.il/jobs/search/"
        
        for term in search_terms[:3]:  # Limit searches
            params = {'q': term}
            
            print(f"[DRUSHIM] Searching for: {term}")
            response = session.get(base_url, params=params, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job listings
                job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and 'job' in x.lower())
                
                for job_elem in job_elements[:3]:  # Limit results
                    title_elem = job_elem.find(['h2', 'h3', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # Check if it's a leadership position
                        if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp', 'manager', 'מנהל', 'ראש']):
                            job = {
                                "title": title,
                                "company": "Drushim Listing",
                                "location": "Israel", 
                                "url": f"{base_url}?q={urllib.parse.quote(term)}",
                                "source": "drushim_direct",
                                "posted_at": date.today().isoformat(),
                                "jd": f"Leadership position: {title}",
                                "id": job_id({
                                    "title": title,
                                    "company": "drushim",
                                    "location": "Israel",
                                    "url": f"{base_url}?q={urllib.parse.quote(term)}"
                                })
                            }
                            jobs.append(job)
                            print(f"[DRUSHIM] Found: {title}")
            
            time.sleep(2)  # Rate limiting
            
    except Exception as e:
        print(f"[DRUSHIM] Error: {e}")
    
    return jobs

def search_glassdoor_israel(position_types):
    """Search Glassdoor Israel for leadership positions."""
    jobs = []
    session = create_session()
    
    print("[GLASSDOOR] Searching Glassdoor Israel...")
    
    try:
        # Glassdoor Israel search
        search_url = "https://www.glassdoor.com/Job/israel-devops-director-jobs-SRCH_IL.0,6_IN119_KO7,21.htm"
        
        response = session.get(search_url, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for job listings
            job_elements = soup.find_all(['div'], class_=lambda x: x and 'job' in x.lower())
            
            for job_elem in job_elements[:5]:  # Limit results
                title_elem = job_elem.find(['h2', 'h3', 'a'])
                company_elem = job_elem.find(['span'], class_=lambda x: x and 'company' in x.lower())
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True) if company_elem else "Glassdoor Listing"
                    
                    # Check if it's a leadership position
                    if any(keyword.lower() in title.lower() for keyword in ['director', 'head', 'vp', 'manager']):
                        job = {
                            "title": title,
                            "company": company,
                            "location": "Israel",
                            "url": search_url,
                            "source": "glassdoor_israel",
                            "posted_at": date.today().isoformat(),
                            "jd": f"Leadership position at {company}: {title}",
                            "id": job_id({
                                "title": title,
                                "company": company,
                                "location": "Israel",
                                "url": search_url
                            })
                        }
                        jobs.append(job)
                        print(f"[GLASSDOOR] Found: {title} @ {company}")
        
    except Exception as e:
        print(f"[GLASSDOOR] Error: {e}")
    
    return jobs

def main():
    """Search all Israeli job boards for leadership positions."""
    print("🇮🇱 Searching Israeli Job Boards Directly")
    print("=" * 50)
    
    position_types = load_position_types()
    all_jobs = []
    
    # Search each job board
    alljobs_results = search_alljobs_direct(position_types)
    all_jobs.extend(alljobs_results)
    
    jobmaster_results = search_jobmaster_direct(position_types)
    all_jobs.extend(jobmaster_results)
    
    drushim_results = search_drushim_direct(position_types)
    all_jobs.extend(drushim_results)
    
    glassdoor_results = search_glassdoor_israel(position_types)
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
    print(f"✅ ISRAELI JOB BOARDS SEARCH COMPLETE")
    print(f"📊 Results:")
    print(f"   • {len(alljobs_results)} from AllJobs")
    print(f"   • {len(jobmaster_results)} from JobMaster")
    print(f"   • {len(drushim_results)} from Drushim")
    print(f"   • {len(glassdoor_results)} from Glassdoor Israel")
    print(f"   • {len(unique_jobs)} total unique positions")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
