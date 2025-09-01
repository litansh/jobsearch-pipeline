"""
Additional Israeli job sources for DevOps leadership positions.
Integrates AllJobs, Drushim, TheMarker, and other Israeli platforms.
"""

import requests
import json
from datetime import date
import pathlib
from scripts.utils import create_session, job_id
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote_plus, urljoin
import feedparser

ROOT = pathlib.Path(__file__).resolve().parents[1]

# DevOps leadership keywords in Hebrew and English
DEVOPS_KEYWORDS_HEBREW = [
    "מנהל DevOps", "ראש צוות DevOps", "מנהל תשתיות", "ראש תשתיות",
    "מנהל פלטפורמה", "ראש פלטפורמה", "מנהל SRE", "ראש SRE",
    "מנהל הנדסה", "VP הנדסה", "מנהל טכנולוגיות"
]

DEVOPS_KEYWORDS_ENGLISH = [
    # DevOps Leadership
    "Head of DevOps", "DevOps Director", "Director of DevOps", "DevOps Manager", "VP DevOps", "VP of DevOps", "Chief DevOps Officer",
    
    # Platform Engineering Leadership  
    "Head of Platform", "Head of Platform Engineering", "Platform Director", "Director of Platform", "Director of Platform Engineering", "VP Platform", "VP of Platform Engineering",
    
    # Infrastructure Leadership
    "Head of Infrastructure", "Infrastructure Director", "Director of Infrastructure", "VP Infrastructure", "VP of Infrastructure", "Chief Infrastructure Officer",
    
    # SRE Leadership
    "Head of SRE", "Head of Site Reliability", "SRE Director", "Director of SRE", "Director of Site Reliability", "VP SRE", "VP of Site Reliability",
    
    # Engineering Operations & Production
    "Head of Engineering Operations", "Director of Engineering Operations", "VP Engineering Operations", "Head of Production Engineering", "Director of Production Engineering", "Production Owner",
    
    # Cloud & Architecture Leadership
    "Head of Cloud", "Cloud Director", "Director of Cloud", "VP Cloud", "VP of Cloud Engineering", "Head of Cloud Engineering", "Solutions Architect Director", "Principal Solutions Architect",
    
    # Technology Leadership
    "VP Engineering", "VP of Engineering", "Director of Engineering", "CTO", "Chief Technology Officer", "VP Technology", "VP of Technology",
    
    # Security Engineering Leadership
    "Head of Security Engineering", "Director of Security Engineering", "VP Security Engineering", "CISO", "Chief Information Security Officer"
]

def search_alljobs():
    """Search AllJobs.co.il for DevOps leadership positions."""
    jobs = []
    session = create_session()
    
    print("[ALLJOBS] Searching AllJobs.co.il for DevOps leadership roles...")
    
    try:
        # AllJobs search URL for tech positions in central Israel
        search_params = {
            "q": "DevOps Director OR Head of DevOps OR Platform Director",
            "l": "Tel Aviv,Jerusalem,Herzliya,Petach Tikva,Ramat Gan"
        }
        
        # Try RSS feed first
        rss_url = "https://www.alljobs.co.il/rss/jobs.aspx?region=2,3,4&category=2"
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                title = entry.title
                if any(keyword.lower() in title.lower() for keyword in DEVOPS_KEYWORDS_ENGLISH):
                    job = {
                        "title": title,
                        "company": "Unknown",  # Extract from description if available
                        "location": "Israel",
                        "url": entry.link,
                        "source": "alljobs",
                        "posted_at": date.today().isoformat(),
                        "jd": entry.summary if hasattr(entry, 'summary') else "",
                        "id": job_id({
                            "title": title,
                            "company": "AllJobs",
                            "location": "Israel",
                            "url": entry.link
                        })
                    }
                    jobs.append(job)
                    print(f"[ALLJOBS] {title}")
        except Exception as e:
            print(f"[ALLJOBS] RSS feed error: {e}")
            
        # Fallback to web scraping if RSS fails
        if not jobs:
            search_url = "https://www.alljobs.co.il/SearchResultsGuest.aspx"
            for keyword in DEVOPS_KEYWORDS_ENGLISH[:3]:  # Limit searches
                try:
                    params = {
                        "Position": keyword,
                        "Region": "2,3,4",  # Central Israel
                        "Seniority": "5,6"  # Senior, Management
                    }
                    
                    response = session.get(search_url, params=params, timeout=20)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # Parse job listings (implementation depends on page structure)
                        # This would need detailed scraping logic
                        
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"[ALLJOBS] Search error for {keyword}: {e}")
                    continue
                    
    except Exception as e:
        print(f"[ALLJOBS] General error: {e}")
    
    return jobs

def search_themarker_rss():
    """Search TheMarker careers RSS feed."""
    jobs = []
    
    print("[THEMARKER] Searching TheMarker careers RSS...")
    
    try:
        rss_url = "https://www.themarker.com/career/rss/"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:30]:  # Check recent entries
            title = entry.title
            description = entry.summary if hasattr(entry, 'summary') else ""
            
            # Check for DevOps leadership keywords
            text_to_check = f"{title} {description}".lower()
            
            if any(keyword.lower() in text_to_check for keyword in DEVOPS_KEYWORDS_ENGLISH):
                # Extract company name from title or description
                company = "Unknown"
                for word in title.split():
                    if len(word) > 3 and word.istitle():
                        company = word
                        break
                
                job = {
                    "title": title,
                    "company": company,
                    "location": "Israel",
                    "url": entry.link,
                    "source": "themarker",
                    "posted_at": entry.published if hasattr(entry, 'published') else date.today().isoformat(),
                    "jd": description,
                    "id": job_id({
                        "title": title,
                        "company": company,
                        "location": "Israel",
                        "url": entry.link
                    })
                }
                jobs.append(job)
                print(f"[THEMARKER] {title} @ {company}")
                
    except Exception as e:
        print(f"[THEMARKER] Error: {e}")
    
    return jobs

def search_comeet_companies():
    """Search Comeet API for Israeli companies."""
    jobs = []
    session = create_session()
    
    # Israeli companies using Comeet
    comeet_companies = [
        "monday", "wix", "outbrain", "gong", "cyberark", "checkmarx",
        "riskified", "walkme", "fiverr", "ironSource", "nice"
    ]
    
    print(f"[COMEET] Searching {len(comeet_companies)} companies using Comeet ATS...")
    
    for company in comeet_companies:
        try:
            # Comeet API endpoint
            url = f"https://{company}.comeet.co/careers-api/2.0/company/positions"
            
            response = session.get(url, timeout=20)
            if response.status_code == 200:
                positions = response.json()
                
                for position in positions:
                    title = position.get("name", "")
                    location = position.get("location", {}).get("name", "")
                    
                    # Filter for DevOps leadership and Israel location
                    if (any(keyword.lower() in title.lower() for keyword in DEVOPS_KEYWORDS_ENGLISH) and
                        ("israel" in location.lower() or "tel aviv" in location.lower() or 
                         "jerusalem" in location.lower() or "herzliya" in location.lower())):
                        
                        job = {
                            "title": title,
                            "company": company.title(),
                            "location": location,
                            "url": f"https://{company}.comeet.co/careers/{position.get('uid', '')}",
                            "source": "comeet",
                            "posted_at": position.get("time_updated", date.today().isoformat()),
                            "jd": position.get("details", ""),
                            "id": job_id({
                                "title": title,
                                "company": company,
                                "location": location,
                                "url": f"https://{company}.comeet.co/careers/{position.get('uid', '')}"
                            })
                        }
                        jobs.append(job)
                        print(f"[COMEET] {title} @ {company.title()} ({location})")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"[COMEET] Error for {company}: {e}")
            continue
    
    return jobs

def search_smartrecruiters_companies():
    """Search SmartRecruiters API for Israeli companies."""
    jobs = []
    session = create_session()
    
    # Israeli companies using SmartRecruiters
    smartrecruiters_companies = [
        "wix", "outbrain", "monday", "gong", "cyberark"
    ]
    
    print(f"[SMARTRECRUITERS] Searching {len(smartrecruiters_companies)} companies...")
    
    for company in smartrecruiters_companies:
        try:
            # SmartRecruiters public API
            url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
            params = {
                "limit": 50,
                "offset": 0,
                "country": "il"  # Israel
            }
            
            response = session.get(url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                postings = data.get("content", [])
                
                for posting in postings:
                    title = posting.get("name", "")
                    location = posting.get("location", {})
                    city = location.get("city", "")
                    country = location.get("country", "")
                    
                    # Filter for DevOps leadership in Israel
                    if (any(keyword.lower() in title.lower() for keyword in DEVOPS_KEYWORDS_ENGLISH) and
                        country.lower() == "israel"):
                        
                        job = {
                            "title": title,
                            "company": posting.get("company", {}).get("name", company.title()),
                            "location": f"{city}, Israel" if city else "Israel",
                            "url": f"https://jobs.smartrecruiters.com/{posting.get('id', '')}",
                            "source": "smartrecruiters",
                            "posted_at": posting.get("releasedDate", date.today().isoformat()),
                            "jd": posting.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text", ""),
                            "id": job_id({
                                "title": title,
                                "company": company,
                                "location": city,
                                "url": posting.get('id', '')
                            })
                        }
                        jobs.append(job)
                        print(f"[SMARTRECRUITERS] {title} @ {company.title()} ({city})")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"[SMARTRECRUITERS] Error for {company}: {e}")
            continue
    
    return jobs

def search_vc_portfolio_companies():
    """Search VC portfolio companies for DevOps leadership roles."""
    jobs = []
    
    print("[VC_PORTFOLIO] Searching VC portfolio companies...")
    
    # Major Israeli VC portfolio companies
    vc_portfolios = {
        "bessemer": ["monday", "wix", "fiverr", "lightricks"],
        "insight": ["armis", "orca-security", "snyk"],
        "viola": ["ironSource", "outbrain", "riskified"],
        "83north": ["gong", "lemonade", "fundguard"]
    }
    
    session = create_session()
    
    for vc_name, companies in vc_portfolios.items():
        for company in companies:
            try:
                # Try common career page patterns
                career_urls = [
                    f"https://{company}.com/careers",
                    f"https://www.{company}.com/careers",
                    f"https://careers.{company}.com",
                    f"https://{company}.com/jobs"
                ]
                
                for url in career_urls:
                    try:
                        response = session.get(url, timeout=15)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            page_text = soup.get_text().lower()
                            
                            # Look for DevOps leadership keywords
                            for keyword in DEVOPS_KEYWORDS_ENGLISH:
                                if keyword.lower() in page_text:
                                    job = {
                                        "title": keyword,
                                        "company": company.title(),
                                        "location": "Israel",
                                        "url": url,
                                        "source": f"vc_portfolio_{vc_name}",
                                        "posted_at": date.today().isoformat(),
                                        "jd": f"DevOps leadership role at {company.title()}. Portfolio company of {vc_name.title()} Ventures.",
                                        "id": job_id({
                                            "title": keyword,
                                            "company": company,
                                            "location": "Israel",
                                            "url": url
                                        })
                                    }
                                    jobs.append(job)
                                    print(f"[VC_PORTFOLIO] {keyword} @ {company.title()} ({vc_name})")
                                    break  # Only one job per company
                            
                            break  # Found working URL
                            
                    except Exception as e:
                        continue
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"[VC_PORTFOLIO] Error for {company}: {e}")
                continue
    
    return jobs

def search_executive_search_firms():
    """Monitor executive search firms for DevOps leadership roles."""
    jobs = []
    
    print("[EXECUTIVE_SEARCH] Checking executive search firms...")
    
    # Known Israeli tech executive search firms
    search_firms = [
        {
            "name": "Ethos Human Capital",
            "url": "https://www.ethos-hr.com/jobs",
            "focus": "Israeli tech executives"
        },
        {
            "name": "Talentiv",
            "url": "https://talentiv.com/jobs",
            "focus": "Tech recruitment specialists"
        }
    ]
    
    session = create_session()
    
    for firm in search_firms:
        try:
            response = session.get(firm["url"], timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Look for DevOps leadership positions
                for keyword in DEVOPS_KEYWORDS_ENGLISH:
                    if keyword.lower() in page_text and "israel" in page_text:
                        job = {
                            "title": keyword,
                            "company": firm["name"],
                            "location": "Israel",
                            "url": firm["url"],
                            "source": "executive_search",
                            "posted_at": date.today().isoformat(),
                            "jd": f"Executive search opportunity: {keyword} role in Israeli tech. {firm['focus']}",
                            "id": job_id({
                                "title": keyword,
                                "company": firm["name"],
                                "location": "Israel",
                                "url": firm["url"]
                            })
                        }
                        jobs.append(job)
                        print(f"[EXECUTIVE_SEARCH] {keyword} via {firm['name']}")
                        break
            
            time.sleep(1)  # Respectful rate limiting
            
        except Exception as e:
            print(f"[EXECUTIVE_SEARCH] Error for {firm['name']}: {e}")
            continue
    
    return jobs

def search_drushim():
    """Search Drushim.co.il for tech leadership roles."""
    jobs = []
    
    print("[DRUSHIM] Searching Drushim.co.il...")
    
    try:
        # Drushim often has RSS feeds or API endpoints
        # This would need Hebrew language support and specific implementation
        # For now, create a placeholder that could be expanded
        
        session = create_session()
        search_url = "https://www.drushim.co.il/jobs/search/"
        
        # Search for English DevOps terms
        for keyword in ["DevOps Director", "Head of DevOps", "Platform Director"]:
            try:
                params = {
                    "q": keyword,
                    "city": "תל אביב,ירושלים,הרצליה"  # Hebrew city names
                }
                
                response = session.get(search_url, params=params, timeout=15)
                if response.status_code == 200:
                    # Would need specific parsing logic for Drushim's HTML structure
                    print(f"[DRUSHIM] Searched for {keyword} - implementation needed")
                
                time.sleep(1)
                
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"[DRUSHIM] Error: {e}")
    
    return jobs

def main():
    """Search all additional Israeli job sources."""
    all_jobs = []
    
    print("[INFO] Starting search of additional Israeli job sources...")
    
    # Search all sources
    alljobs_results = search_alljobs()
    all_jobs.extend(alljobs_results)
    
    themarker_results = search_themarker_rss()
    all_jobs.extend(themarker_results)
    
    comeet_results = search_comeet_companies()
    all_jobs.extend(comeet_results)
    
    smartrecruiters_results = search_smartrecruiters_companies()
    all_jobs.extend(smartrecruiters_results)
    
    vc_results = search_vc_portfolio_companies()
    all_jobs.extend(vc_results)
    
    executive_results = search_executive_search_firms()
    all_jobs.extend(executive_results)
    
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
        output_file = ROOT / "data" / "raw" / f"israeli_sources_{date.today().isoformat()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
        
        # Append to main jobs file
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in unique_jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        
        print(f"\n[SUCCESS] Found {len(unique_jobs)} DevOps leadership roles from additional Israeli sources")
        print(f"[INFO] Sources: {len(alljobs_results)} AllJobs, {len(themarker_results)} TheMarker, {len(comeet_results)} Comeet, {len(smartrecruiters_results)} SmartRecruiters, {len(vc_results)} VC Portfolio, {len(executive_results)} Executive Search")
    else:
        print("[INFO] No additional DevOps leadership roles found from Israeli sources")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
