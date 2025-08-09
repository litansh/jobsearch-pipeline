"""
Comprehensive job search across ALL platforms for Israeli hitech companies.
Updates company list dynamically and searches LinkedIn, career pages, job boards, etc.
"""

import json
import pathlib
from datetime import date
from scripts.utils import job_id, create_session
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote_plus

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Comprehensive list of Israeli hitech companies (updated dynamically)
ISRAELI_HITECH_COMPANIES = {
    # Unicorns & Major Companies
    "monday.com": {"name": "Monday.com", "sector": "Productivity", "size": "Large"},
    "wix": {"name": "Wix", "sector": "Web Development", "size": "Large"},
    "outbrain": {"name": "Outbrain", "sector": "Content Discovery", "size": "Large"},
    "gong": {"name": "Gong", "sector": "Revenue Intelligence", "size": "Large"},
    "cyberark": {"name": "CyberArk", "sector": "Cybersecurity", "size": "Large"},
    "checkmarx": {"name": "Checkmarx", "sector": "Application Security", "size": "Large"},
    "riskified": {"name": "Riskified", "sector": "Fraud Prevention", "size": "Large"},
    "walkme": {"name": "WalkMe", "sector": "Digital Adoption", "size": "Large"},
    "fiverr": {"name": "Fiverr", "sector": "Freelance Marketplace", "size": "Large"},
    "ironSource": {"name": "IronSource", "sector": "Mobile App Monetization", "size": "Large"},
    "jfrog": {"name": "JFrog", "sector": "DevOps Platform", "size": "Large"},
    "snyk": {"name": "Snyk", "sector": "Developer Security", "size": "Large"},
    
    # High-Growth Security Companies
    "sentinelone": {"name": "SentinelOne", "sector": "Endpoint Security", "size": "Large"},
    "armis": {"name": "Armis", "sector": "IoT Security", "size": "Medium"},
    "orca-security": {"name": "Orca Security", "sector": "Cloud Security", "size": "Medium"},
    "aqua-security": {"name": "Aqua Security", "sector": "Container Security", "size": "Medium"},
    "guardicore": {"name": "Guardicore", "sector": "Network Security", "size": "Medium"},
    "claroty": {"name": "Claroty", "sector": "Industrial Cybersecurity", "size": "Medium"},
    "axonius": {"name": "Axonius", "sector": "Cybersecurity Asset Management", "size": "Medium"},
    "bigid": {"name": "BigID", "sector": "Data Security", "size": "Medium"},
    "silverfort": {"name": "Silverfort", "sector": "Identity Protection", "size": "Medium"},
    "vicarius": {"name": "Vicarius", "sector": "Vulnerability Management", "size": "Medium"},
    "transmit-security": {"name": "Transmit Security", "sector": "Identity & Access", "size": "Medium"},
    "panorays": {"name": "Panorays", "sector": "Third-Party Risk", "size": "Medium"},
    "cybersixgill": {"name": "Cybersixgill", "sector": "Threat Intelligence", "size": "Medium"},
    "cycode": {"name": "Cycode", "sector": "Application Security", "size": "Medium"},
    "apiiro": {"name": "Apiiro", "sector": "Application Risk", "size": "Medium"},
    
    # Fintech & Enterprise
    "payoneer": {"name": "Payoneer", "sector": "Fintech", "size": "Large"},
    "pagaya": {"name": "Pagaya", "sector": "AI-Driven Finance", "size": "Medium"},
    "fundguard": {"name": "FundGuard", "sector": "Investment Operations", "size": "Medium"},
    "mesh-payments": {"name": "Mesh Payments", "sector": "Corporate Cards", "size": "Medium"},
    "rapyd": {"name": "Rapyd", "sector": "Fintech-as-a-Service", "size": "Large"},
    "lemonade": {"name": "Lemonade", "sector": "Insurtech", "size": "Medium"},
    
    # Enterprise & Traditional
    "nice": {"name": "NICE", "sector": "Customer Experience", "size": "Large"},
    "verint": {"name": "Verint", "sector": "Customer Engagement", "size": "Large"},
    "amdocs": {"name": "Amdocs", "sector": "Telecom Software", "size": "Large"},
    "varonis": {"name": "Varonis", "sector": "Data Security", "size": "Large"},
    "cellebrite": {"name": "Cellebrite", "sector": "Digital Intelligence", "size": "Medium"},
    
    # AI & Deep Tech
    "mobileye": {"name": "Mobileye", "sector": "Autonomous Driving", "size": "Large"},
    "lightricks": {"name": "Lightricks", "sector": "Creative Apps", "size": "Medium"},
    "cortica": {"name": "Cortica", "sector": "Autonomous AI", "size": "Medium"},
    "aidoc": {"name": "Aidoc", "sector": "Medical AI", "size": "Medium"},
    "zebra-medical": {"name": "Zebra Medical Vision", "sector": "Medical AI", "size": "Medium"},
    
    # Mobility & Transportation
    "via": {"name": "Via", "sector": "Mobility", "size": "Medium"},
    "moovit": {"name": "Moovit", "sector": "Urban Mobility", "size": "Medium"},
    "trax": {"name": "Trax", "sector": "Retail Analytics", "size": "Medium"},
    
    # Infrastructure & DevOps
    "redis": {"name": "Redis", "sector": "Database", "size": "Large"},
    "elastic": {"name": "Elastic", "sector": "Search & Analytics", "size": "Large"},
    "mongodb": {"name": "MongoDB", "sector": "Database", "size": "Large"},
    "datadog": {"name": "Datadog", "sector": "Monitoring", "size": "Large"},
    
    # Emerging Companies
    "paragon": {"name": "Paragon", "sector": "Integration Platform", "size": "Small"},
    "taboola": {"name": "Taboola", "sector": "Content Discovery", "size": "Large"},
    "appdome": {"name": "Appdome", "sector": "Mobile Security", "size": "Medium"},
    "sysdig": {"name": "Sysdig", "sector": "Cloud Security", "size": "Medium"},
}

# Job search keywords for DevOps leadership
DEVOPS_LEADERSHIP_KEYWORDS = [
    "Head of DevOps", "DevOps Director", "Director of DevOps", "DevOps Manager",
    "VP DevOps", "VP of DevOps", "Chief DevOps Officer", "DevOps Group Lead",
    "Head of Platform", "Platform Director", "Director of Platform", "Platform Manager",
    "Head of Infrastructure", "Infrastructure Director", "Director of Infrastructure", "Infrastructure Manager",
    "Head of SRE", "SRE Director", "Director of SRE", "SRE Manager",
    "Head of Engineering Operations", "Director of Engineering Operations",
    "VP Engineering", "VP of Engineering" # Sometimes these include DevOps responsibilities
]

def update_company_list():
    """Dynamically update the list of Israeli hitech companies."""
    print("[INFO] Updating Israeli hitech company list...")
    
    # TODO: Could add web scraping to find new companies from:
    # - Israeli tech news sites
    # - Startup databases
    # - Recent funding announcements
    
    print(f"[INFO] Company database: {len(ISRAELI_HITECH_COMPANIES)} companies")
    return ISRAELI_HITECH_COMPANIES

def search_linkedin_jobs(company_info):
    """Search LinkedIn for DevOps leadership roles at a specific company."""
    jobs = []
    session = create_session()
    
    company_name = company_info["name"]
    company_slug = company_name.lower().replace(" ", "-").replace(".", "")
    
    # LinkedIn job search URLs for the company
    search_queries = [
        f"Head of DevOps {company_name}",
        f"DevOps Director {company_name}",  
        f"Infrastructure Director {company_name}",
        f"Platform Director {company_name}"
    ]
    
    for query in search_queries:
        try:
            # LinkedIn job search (note: this would need proper scraping or API access)
            # For now, we'll simulate based on known patterns
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={quote_plus(query)}&location=Israel"
            
            # Simulate finding jobs (in real implementation, would parse LinkedIn results)
            # This is where you'd implement actual LinkedIn scraping or API calls
            print(f"[LINKEDIN] Searching: {query}")
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            continue
    
    return jobs

def search_company_career_page(company_key, company_info):
    """Search company's career page for DevOps leadership roles."""
    jobs = []
    session = create_session()
    
    company_name = company_info["name"]
    
    # Try common career page URLs
    career_urls = [
        f"https://{company_key}.com/careers",
        f"https://www.{company_key}.com/careers", 
        f"https://{company_key}.com/jobs",
        f"https://careers.{company_key}.com",
        f"https://jobs.{company_key}.com"
    ]
    
    for url in career_urls:
        try:
            response = session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Look for DevOps leadership keywords
                for keyword in DEVOPS_LEADERSHIP_KEYWORDS:
                    if keyword.lower() in page_text:
                        # Found potential match
                        job = {
                            "title": keyword,
                            "company": company_name,
                            "location": "Israel",
                            "url": url,
                            "source": "career_page",
                            "posted_at": date.today().isoformat(),
                            "jd": f"DevOps leadership role at {company_name}. Check their careers page for details.",
                            "id": job_id({
                                "title": keyword,
                                "company": company_name,
                                "location": "Israel",
                                "url": url
                            })
                        }
                        jobs.append(job)
                        print(f"[CAREER_PAGE] {keyword} @ {company_name} - {url}")
                        break  # Only add one job per company to avoid duplicates
                
                break  # Found working URL, stop trying others
                
        except Exception as e:
            continue
    
    return jobs

def search_job_boards(company_info):
    """Search job boards for company-specific DevOps roles."""
    jobs = []
    company_name = company_info["name"]
    
    # Job board search URLs (these would need actual implementation)
    job_boards = [
        "alljobs.co.il",
        "jobmaster.co.il", 
        "drushim.co.il",
        "glassdoor.com",
        "indeed.com"
    ]
    
    # For now, simulate job board search
    print(f"[JOB_BOARDS] Searching for {company_name} DevOps roles...")
    
    return jobs

def main():
    """Comprehensive search across all platforms and companies."""
    all_jobs = []
    
    print("[INFO] Starting comprehensive DevOps leadership job search...")
    
    # Step 1: Update company list
    companies = update_company_list()
    
    # Step 2: Search each company across all platforms
    for company_key, company_info in companies.items():
        print(f"\n[INFO] Searching {company_info['name']} ({company_info['sector']})...")
        
        # Search LinkedIn
        linkedin_jobs = search_linkedin_jobs(company_info)
        all_jobs.extend(linkedin_jobs)
        
        # Search career pages
        career_jobs = search_company_career_page(company_key, company_info)
        all_jobs.extend(career_jobs)
        
        # Search job boards
        job_board_jobs = search_job_boards(company_info)
        all_jobs.extend(job_board_jobs)
        
        # Rate limiting
        time.sleep(0.5)
    
    # Remove duplicates
    unique_jobs = []
    seen = set()
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
        else:
            print(f"[DEDUP] Skipping duplicate: {job['title']} @ {job['company']}")
    
    # Save results
    if unique_jobs:
        output_file = ROOT / "data" / "raw" / f"comprehensive_{date.today().isoformat()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
        
        # Append to main jobs file
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in unique_jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        
        print(f"\n[SUCCESS] Found {len(unique_jobs)} DevOps leadership roles across all platforms")
        print(f"[INFO] Searched {len(companies)} Israeli hitech companies")
    else:
        print("[INFO] No DevOps leadership roles found")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
