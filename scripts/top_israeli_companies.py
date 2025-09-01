"""
Top Israeli tech companies for 2025 - comprehensive list for DevOps leadership roles.
Based on current market cap, funding, and growth trajectory.
"""

import requests
import json
from datetime import date
import pathlib
from scripts.utils import create_session, job_id
from bs4 import BeautifulSoup
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Top Israeli Tech Companies 2025 (Current data)
TOP_ISRAELI_COMPANIES_2025 = {
    # Tier 1: Public Companies & Unicorns ($1B+ valuation)
    "tier1_unicorns": {
        "wiz": {"name": "Wiz", "sector": "Cloud Security", "valuation": "$12B", "size": "Large", "priority": "High"},
        "monday": {"name": "Monday.com", "sector": "Work OS", "valuation": "$15.8B", "size": "Large", "priority": "High"},
        "cyberark": {"name": "CyberArk", "sector": "Identity Security", "valuation": "$19.5B", "size": "Large", "priority": "High"},
        "checkpoint": {"name": "Check Point", "sector": "Cybersecurity", "valuation": "$23.8B", "size": "Large", "priority": "High"},
        "lightricks": {"name": "Lightricks", "sector": "Creative AI", "valuation": "$1.8B+", "size": "Large", "priority": "High"},
        "claroty": {"name": "Claroty", "sector": "Industrial Cybersecurity", "valuation": "$3.5B", "size": "Large", "priority": "High"},
        "gong": {"name": "Gong", "sector": "Revenue Intelligence", "valuation": "$7.25B", "size": "Large", "priority": "High"},
        "riskified": {"name": "Riskified", "sector": "Fraud Prevention", "valuation": "$3.2B", "size": "Large", "priority": "High"},
        "outbrain": {"name": "Outbrain", "sector": "Content Discovery", "valuation": "$1.25B", "size": "Large", "priority": "High"},
        "fiverr": {"name": "Fiverr", "sector": "Freelance Platform", "valuation": "$3.8B", "size": "Large", "priority": "High"},
    },
    
    # Tier 2: High-Growth Companies ($100M-$1B valuation)
    "tier2_high_growth": {
        "orca-security": {"name": "Orca Security", "sector": "Cloud Security", "valuation": "$1.8B", "size": "Medium", "priority": "High"},
        "armis": {"name": "Armis", "sector": "IoT Security", "valuation": "$4.2B", "size": "Medium", "priority": "High"},
        "aqua-security": {"name": "Aqua Security", "sector": "Container Security", "valuation": "$1B", "size": "Medium", "priority": "High"},
        "bigid": {"name": "BigID", "sector": "Data Security", "valuation": "$1.25B", "size": "Medium", "priority": "High"},
        "snyk": {"name": "Snyk", "sector": "Developer Security", "valuation": "$8.5B", "size": "Large", "priority": "High"},
        "jfrog": {"name": "JFrog", "sector": "DevOps Platform", "valuation": "$4.8B", "size": "Large", "priority": "High"},
        "sentinelone": {"name": "SentinelOne", "sector": "Endpoint Security", "valuation": "$8.9B", "size": "Large", "priority": "High"},
        "guardicore": {"name": "Guardicore", "sector": "Network Security", "valuation": "$500M+", "size": "Medium", "priority": "Medium"},
        "axonius": {"name": "Axonius", "sector": "Cyber Asset Management", "valuation": "$2.6B", "size": "Medium", "priority": "High"},
        "silverfort": {"name": "Silverfort", "sector": "Identity Protection", "valuation": "$300M+", "size": "Medium", "priority": "Medium"},
        "transmit-security": {"name": "Transmit Security", "sector": "Identity & Access", "valuation": "$2.2B", "size": "Medium", "priority": "High"},
        "panorays": {"name": "Panorays", "sector": "Third-Party Risk", "valuation": "$200M+", "size": "Medium", "priority": "Medium"},
        "cycode": {"name": "Cycode", "sector": "Application Security", "valuation": "$100M+", "size": "Medium", "priority": "Medium"},
        "apiiro": {"name": "Apiiro", "sector": "Application Risk", "valuation": "$100M+", "size": "Medium", "priority": "Medium"},
    },
    
    # Tier 3: Fintech & Enterprise
    "tier3_fintech": {
        "rapyd": {"name": "Rapyd", "sector": "Fintech-as-a-Service", "valuation": "$15B", "size": "Large", "priority": "High"},
        "pagaya": {"name": "Pagaya", "sector": "AI-Driven Finance", "valuation": "$8.5B", "size": "Large", "priority": "High"},
        "lemonade": {"name": "Lemonade", "sector": "Insurtech", "valuation": "$2.1B", "size": "Medium", "priority": "High"},
        "payoneer": {"name": "Payoneer", "sector": "Fintech", "valuation": "$3.3B", "size": "Large", "priority": "High"},
        "fundguard": {"name": "FundGuard", "sector": "Investment Operations", "valuation": "$200M+", "size": "Medium", "priority": "Medium"},
        "mesh-payments": {"name": "Mesh Payments", "sector": "Corporate Cards", "valuation": "$100M+", "size": "Medium", "priority": "Medium"},
    },
    
    # Tier 4: AI & Deep Tech
    "tier4_ai_deeptech": {
        "mobileye": {"name": "Mobileye", "sector": "Autonomous Driving", "valuation": "$50B+", "size": "Large", "priority": "High"},
        "aidoc": {"name": "Aidoc", "sector": "Medical AI", "valuation": "$250M+", "size": "Medium", "priority": "Medium"},
        "zebra-medical": {"name": "Zebra Medical Vision", "sector": "Medical AI", "valuation": "$200M+", "size": "Medium", "priority": "Medium"},
        "cortica": {"name": "Cortica", "sector": "Autonomous AI", "valuation": "$100M+", "size": "Medium", "priority": "Medium"},
        "dataloop": {"name": "Dataloop", "sector": "AI Data Platform", "valuation": "$100M+", "size": "Medium", "priority": "Medium"},
    },
    
    # Tier 5: Infrastructure & DevOps Focused
    "tier5_infrastructure": {
        "redis": {"name": "Redis", "sector": "Database", "valuation": "$2B+", "size": "Large", "priority": "High"},
        "elastic": {"name": "Elastic", "sector": "Search & Analytics", "valuation": "$7.8B", "size": "Large", "priority": "High"},
        "mongodb": {"name": "MongoDB", "sector": "Database", "valuation": "$24B", "size": "Large", "priority": "High"},
        "datadog": {"name": "Datadog", "sector": "Monitoring", "valuation": "$36B", "size": "Large", "priority": "High"},
        "sysdig": {"name": "Sysdig", "sector": "Cloud Security", "valuation": "$1.19B", "size": "Medium", "priority": "High"},
        "coralogix": {"name": "Coralogix", "sector": "Observability", "valuation": "$200M+", "size": "Medium", "priority": "High"},
    },
    
    # Tier 6: Emerging High-Growth
    "tier6_emerging": {
        "taboola": {"name": "Taboola", "sector": "Content Discovery", "valuation": "$2.6B", "size": "Large", "priority": "Medium"},
        "ironSource": {"name": "IronSource", "sector": "Mobile App Monetization", "valuation": "$11.1B", "size": "Large", "priority": "Medium"},
        "walkme": {"name": "WalkMe", "sector": "Digital Adoption", "valuation": "$2.56B", "size": "Medium", "priority": "Medium"},
        "nice": {"name": "NICE", "sector": "Customer Experience", "valuation": "$8.5B", "size": "Large", "priority": "Medium"},
        "verint": {"name": "Verint", "sector": "Customer Engagement", "valuation": "$3.2B", "size": "Large", "priority": "Medium"},
        "amdocs": {"name": "Amdocs", "sector": "Telecom Software", "valuation": "$9.8B", "size": "Large", "priority": "Medium"},
        "varonis": {"name": "Varonis", "sector": "Data Security", "valuation": "$4.2B", "size": "Large", "priority": "Medium"},
        "cellebrite": {"name": "Cellebrite", "sector": "Digital Intelligence", "valuation": "$2.4B", "size": "Medium", "priority": "Medium"},
        "checkmarx": {"name": "Checkmarx", "sector": "Application Security", "valuation": "$1.15B", "size": "Medium", "priority": "Medium"},
    }
}

def get_all_companies_list():
    """Get flattened list of all companies with metadata."""
    all_companies = {}
    
    for tier_name, tier_companies in TOP_ISRAELI_COMPANIES_2025.items():
        for company_key, company_data in tier_companies.items():
            all_companies[company_key] = company_data
            all_companies[company_key]["tier"] = tier_name
    
    return all_companies

def search_top_israeli_companies():
    """Search career pages of top Israeli tech companies."""
    jobs = []
    session = create_session()
    
    companies = get_all_companies_list()
    high_priority_companies = {k: v for k, v in companies.items() if v.get("priority") == "High"}
    
    print(f"[TOP_ISRAELI] Searching {len(high_priority_companies)} high-priority Israeli tech companies...")
    
    # Complete DevOps leadership keywords matching your profile
    devops_keywords = [
        # DevOps Leadership
        "Head of DevOps", "DevOps Director", "Director of DevOps", "DevOps Manager", "VP DevOps", "VP of DevOps", "Chief DevOps Officer",
        
        # Platform Engineering Leadership (your specialty)
        "Head of Platform", "Head of Platform Engineering", "Platform Director", "Director of Platform", "Director of Platform Engineering", "VP Platform", "VP of Platform Engineering",
        
        # Infrastructure Leadership
        "Head of Infrastructure", "Infrastructure Director", "Director of Infrastructure", "VP Infrastructure", "VP of Infrastructure", "Chief Infrastructure Officer",
        
        # SRE Leadership (your background)
        "Head of SRE", "Head of Site Reliability", "SRE Director", "Director of SRE", "Director of Site Reliability", "VP SRE", "VP of Site Reliability",
        
        # Engineering Operations & Production (your experience)
        "Head of Engineering Operations", "Director of Engineering Operations", "VP Engineering Operations", "Head of Production Engineering", "Director of Production Engineering", "Production Owner",
        
        # Cloud & Architecture Leadership
        "Head of Cloud", "Cloud Director", "Director of Cloud", "VP Cloud", "VP of Cloud Engineering", "Head of Cloud Engineering",
        
        # Technology Leadership (C-level matching your experience)
        "VP Engineering", "VP of Engineering", "Director of Engineering", "CTO", "Chief Technology Officer", "VP Technology", "VP of Technology"
    ]
    
    for company_key, company_info in high_priority_companies.items():
        try:
            company_name = company_info["name"]
            
            # Try multiple career page URL patterns
            career_urls = [
                f"https://{company_key}.com/careers",
                f"https://www.{company_key}.com/careers",
                f"https://{company_key}.com/jobs",
                f"https://careers.{company_key}.com",
                f"https://jobs.{company_key}.com",
                f"https://{company_name.lower().replace(' ', '')}.com/careers",
                f"https://www.{company_name.lower().replace(' ', '')}.com/careers"
            ]
            
            for url in career_urls:
                try:
                    response = session.get(url, timeout=20)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        page_text = soup.get_text().lower()
                        
                        # Look for DevOps leadership keywords
                        for keyword in devops_keywords:
                            if keyword.lower() in page_text and ("israel" in page_text or "tel aviv" in page_text):
                                job = {
                                    "title": keyword,
                                    "company": company_name,
                                    "location": "Israel",
                                    "url": url,
                                    "source": f"top_israeli_{company_info['tier']}",
                                    "posted_at": date.today().isoformat(),
                                    "jd": f"DevOps leadership role at {company_name} ({company_info['sector']}). {company_info['valuation']} valuation company.",
                                    "id": job_id({
                                        "title": keyword,
                                        "company": company_name,
                                        "location": "Israel",
                                        "url": url
                                    })
                                }
                                jobs.append(job)
                                print(f"[TOP_ISRAELI] {keyword} @ {company_name} ({company_info['sector']}) - {url}")
                                break  # Only add one job per company
                        
                        break  # Found working URL, stop trying others
                        
                except Exception as e:
                    continue
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"[TOP_ISRAELI] Error for {company_name}: {e}")
            continue
    
    return jobs

def search_medium_priority_companies():
    """Search medium priority companies for additional opportunities."""
    jobs = []
    session = create_session()
    
    companies = get_all_companies_list()
    medium_priority_companies = {k: v for k, v in companies.items() if v.get("priority") == "Medium"}
    
    print(f"[MEDIUM_PRIORITY] Searching {len(medium_priority_companies)} medium-priority companies...")
    
    # Limit to first 10 to avoid too many requests
    for company_key, company_info in list(medium_priority_companies.items())[:10]:
        try:
            company_name = company_info["name"]
            
            # Try main career page only for medium priority
            career_urls = [
                f"https://{company_key}.com/careers",
                f"https://www.{company_key}.com/careers"
            ]
            
            for url in career_urls:
                try:
                    response = session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        page_text = soup.get_text().lower()
                        
                        # Look for senior DevOps roles
                        senior_keywords = ["Head of DevOps", "DevOps Director", "Platform Director", "VP Engineering"]
                        
                        for keyword in senior_keywords:
                            if keyword.lower() in page_text:
                                job = {
                                    "title": keyword,
                                    "company": company_name,
                                    "location": "Israel",
                                    "url": url,
                                    "source": f"medium_priority_{company_info['tier']}",
                                    "posted_at": date.today().isoformat(),
                                    "jd": f"Senior DevOps role at {company_name} ({company_info['sector']}).",
                                    "id": job_id({
                                        "title": keyword,
                                        "company": company_name,
                                        "location": "Israel",
                                        "url": url
                                    })
                                }
                                jobs.append(job)
                                print(f"[MEDIUM_PRIORITY] {keyword} @ {company_name}")
                                break
                        
                        break
                        
                except Exception as e:
                    continue
            
            time.sleep(0.3)
            
        except Exception as e:
            continue
    
    return jobs

def main():
    """Search all top Israeli tech companies for DevOps leadership roles."""
    all_jobs = []
    
    print("[INFO] Starting search of top Israeli tech companies for DevOps leadership...")
    
    # Get company stats
    companies = get_all_companies_list()
    high_priority = len([c for c in companies.values() if c.get("priority") == "High"])
    medium_priority = len([c for c in companies.values() if c.get("priority") == "Medium"])
    
    print(f"[INFO] Searching {high_priority} high-priority + {medium_priority} medium-priority companies")
    print(f"[INFO] Total companies in database: {len(companies)}")
    
    # Search high priority companies
    high_priority_jobs = search_top_israeli_companies()
    all_jobs.extend(high_priority_jobs)
    
    # Search medium priority companies (limited)
    medium_priority_jobs = search_medium_priority_companies()
    all_jobs.extend(medium_priority_jobs)
    
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
        output_file = ROOT / "data" / "raw" / f"top_israeli_companies_{date.today().isoformat()}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_jobs, f, indent=2, ensure_ascii=False)
        
        # Append to main jobs file
        jobs_file = ROOT / "data" / "processed" / "jobs.jsonl"
        with open(jobs_file, "a", encoding="utf-8") as f:
            for job in unique_jobs:
                f.write(json.dumps(job, ensure_ascii=False) + "\n")
        
        print(f"\n[SUCCESS] Found {len(unique_jobs)} DevOps leadership roles from top Israeli companies")
        print(f"[INFO] Sources: {len(high_priority_jobs)} high-priority, {len(medium_priority_jobs)} medium-priority")
        
        # Show breakdown by tier
        tier_breakdown = {}
        for job in unique_jobs:
            source = job.get("source", "unknown")
            tier = source.split("_")[-1] if "_" in source else "unknown"
            tier_breakdown[tier] = tier_breakdown.get(tier, 0) + 1
        
        print(f"[INFO] Breakdown by tier: {tier_breakdown}")
    else:
        print("[INFO] No DevOps leadership roles found from top Israeli companies")
    
    return len(unique_jobs)

if __name__ == "__main__":
    main()
