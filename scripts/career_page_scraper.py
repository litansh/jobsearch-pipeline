#!/usr/bin/env python3
"""
Direct career page scraper for major Israeli companies.
Bypasses job board limitations by going directly to company career pages.
"""

import requests
import json
import pathlib
from datetime import date
from bs4 import BeautifulSoup
from scripts.utils import create_session, job_id
import yaml
import time
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARDS_CONFIG = ROOT / "configs" / "boards.yaml"
TOP_COMPANIES_CONFIG = ROOT / "configs" / "top_israeli_companies_2025.yaml"

def load_position_types():
    """Load all position types from boards.yaml."""
    with open(BOARDS_CONFIG, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('titles', [])

def create_stealth_session():
    """Create a session that mimics a real browser."""
    session = requests.Session()
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    return session

def search_company_careers(company_info, position_types):
    """Search a specific company's career page for all position types."""
    jobs = []
    session = create_stealth_session()
    
    company_name = company_info['name']
    company_description = company_info.get('description', company_name)
    
    # Try multiple career page patterns
    career_urls = [
        f"https://{company_name}.com/careers",
        f"https://www.{company_name}.com/careers", 
        f"https://careers.{company_name}.com",
        f"https://{company_name}.com/jobs",
        f"https://jobs.{company_name}.com",
        f"https://{company_name}.com/about/careers",
        f"https://www.{company_name}.com/company/careers"
    ]
    
    # Add specific career page if provided
    if 'career_page' in company_info:
        career_urls.insert(0, company_info['career_page'])
    
    print(f"[CAREER] Searching {company_name}...")
    
    for url in career_urls:
        try:
            time.sleep(random.uniform(1, 3))  # Random delay
            
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Look for leadership positions
                leadership_keywords = [
                    'director', 'head of', 'vp ', 'vice president', 'chief', 'manager',
                    'devops', 'platform', 'infrastructure', 'sre', 'engineering'
                ]
                
                # Check if this page has relevant job content
                has_jobs = any(keyword in page_text for keyword in ['job', 'position', 'role', 'career', 'opening'])
                has_leadership = any(keyword in page_text for keyword in leadership_keywords)
                has_israel = any(keyword in page_text for keyword in ['israel', 'tel aviv', 'jerusalem'])
                
                if has_jobs and has_leadership and has_israel:
                    # Look for specific job listings
                    job_elements = soup.find_all(['div', 'li', 'article', 'section'], 
                                               class_=lambda x: x and any(term in x.lower() for term in ['job', 'position', 'role', 'opening']))
                    
                    for job_elem in job_elements[:5]:  # Limit results
                        title_elem = job_elem.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if title_elem:
                            title_text = title_elem.get_text(strip=True)
                            
                            # Check if this matches our position types
                            for position in position_types:
                                if position.lower() in title_text.lower():
                                    job = {
                                        "title": title_text,
                                        "company": company_description,
                                        "location": "Israel",
                                        "url": url,
                                        "source": "career_page_direct",
                                        "posted_at": date.today().isoformat(),
                                        "jd": f"{position} role at {company_name}. {company_info.get('description', '')}",
                                        "id": job_id({
                                            "title": title_text,
                                            "company": company_name,
                                            "location": "Israel",
                                            "url": url
                                        })
                                    }
                                    jobs.append(job)
                                    print(f"[CAREER] Found: {title_text} @ {company_name}")
                                    break
                    
                    # If no specific job elements found, create a general listing
                    if not jobs and has_leadership:
                        # Find the most relevant position type mentioned
                        for position in position_types:
                            if position.lower() in page_text:
                                job = {
                                    "title": f"{position} (Career Page)",
                                    "company": company_description,
                                    "location": "Israel",
                                    "url": url,
                                    "source": "career_page_general",
                                    "posted_at": date.today().isoformat(),
                                    "jd": f"{position} opportunity at {company_name}. Visit career page for details.",
                                    "id": job_id({
                                        "title": position,
                                        "company": company_name,
                                        "location": "Israel",
                                        "url": url
                                    })
                                }
                                jobs.append(job)
                                print(f"[CAREER] Found opportunity: {position} @ {company_name}")
                                break
                
                if jobs:
                    break  # Found working career page
                    
        except Exception as e:
            continue
    
    return jobs

def search_major_israeli_companies():
    """Search career pages of major Israeli companies."""
    jobs = []
    
    # Major Israeli companies with known career pages
    companies = [
        {
            'name': 'monday',
            'description': 'Monday.com - Work OS Platform',
            'career_page': 'https://monday.com/careers'
        },
        {
            'name': 'wix',
            'description': 'Wix - Website Builder Platform',
            'career_page': 'https://www.wix.com/jobs'
        },
        {
            'name': 'outbrain',
            'description': 'Outbrain - Content Discovery',
            'career_page': 'https://www.outbrain.com/careers'
        },
        {
            'name': 'gong',
            'description': 'Gong - Revenue Intelligence',
            'career_page': 'https://www.gong.io/careers'
        },
        {
            'name': 'fiverr',
            'description': 'Fiverr - Freelance Marketplace',
            'career_page': 'https://careers.fiverr.com'
        },
        {
            'name': 'cyberark',
            'description': 'CyberArk - Privileged Access Management',
            'career_page': 'https://www.cyberark.com/careers'
        },
        {
            'name': 'checkmarx',
            'description': 'Checkmarx - Application Security',
            'career_page': 'https://www.checkmarx.com/careers'
        },
        {
            'name': 'walkme',
            'description': 'WalkMe - Digital Adoption Platform',
            'career_page': 'https://www.walkme.com/careers'
        },
        {
            'name': 'lightricks',
            'description': 'Lightricks - AI-Powered Creative Tools',
            'career_page': 'https://www.lightricks.com/careers'
        },
        {
            'name': 'nvidia-israel',
            'description': 'NVIDIA Israel - AI Chip Leader',
            'career_page': 'https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite'
        },
        {
            'name': 'google-israel',
            'description': 'Google Israel - Search and Cloud',
            'career_page': 'https://careers.google.com/locations/israel/'
        },
        {
            'name': 'microsoft-israel',
            'description': 'Microsoft Israel - Cloud and Software',
            'career_page': 'https://careers.microsoft.com/professionals/us/en/l-israel'
        }
    ]
    
    position_types = load_position_types()
    
    for company in companies:
        try:
            company_jobs = search_company_careers(company, position_types)
            jobs.extend(company_jobs)
            
            # Rate limiting
            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            print(f"[CAREER] Error searching {company['name']}: {e}")
            continue
    
    return jobs

def main():
    """Search career pages of major Israeli companies."""
    print("🏢 Searching Israeli Company Career Pages")
    print("=" * 60)
    
    all_jobs = search_major_israeli_companies()
    
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
    print(f"✅ CAREER PAGE SEARCH COMPLETE")
    print(f"📊 Found {len(unique_jobs)} unique positions from Israeli company career pages")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
