#!/usr/bin/env python3
"""
BUILD PHASE: Pipeline setup, configuration validation, and source testing.
This runs during development/setup to ensure all sources are working.
"""

import os
import json
import pathlib
import yaml
from datetime import date
from dotenv import load_dotenv
from scripts.utils import create_session

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARDS_CONFIG = ROOT / "configs" / "boards.yaml"

class PipelineBuildValidator:
    def __init__(self):
        self.session = create_session()
        self.validation_results = {
            "greenhouse_companies": [],
            "lever_companies": [],
            "israeli_sources": [],
            "career_pages": [],
            "environment": {},
            "build_status": "pending"
        }
    
    def validate_environment(self):
        """Validate all required environment variables."""
        print("🔧 Validating Environment Configuration")
        print("=" * 50)
        
        required_vars = {
            "OPENAI_API_KEY": "OpenAI API for job scoring",
            "TELEGRAM_BOT_TOKEN": "Telegram bot for notifications", 
            "TELEGRAM_CHAT_ID": "Telegram chat for job digest",
            "GITHUB_TOKEN": "GitHub for state management"
        }
        
        env_status = {}
        all_good = True
        
        for var, description in required_vars.items():
            value = os.getenv(var, "")
            if value:
                env_status[var] = "✅ SET"
                print(f"✅ {var}: {description}")
            else:
                env_status[var] = "❌ MISSING"
                print(f"❌ {var}: {description} - MISSING")
                all_good = False
        
        self.validation_results["environment"] = env_status
        return all_good
    
    def validate_greenhouse_companies(self):
        """Test which Greenhouse companies actually work."""
        print("\n🌱 Validating Greenhouse Companies")
        print("=" * 50)
        
        with open(BOARDS_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        
        companies = config.get('sources', {}).get('greenhouse', {}).get('companies', [])
        working_companies = []
        broken_companies = []
        
        for company in companies[:10]:  # Test first 10 to avoid rate limiting
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    jobs = response.json().get("jobs", [])
                    working_companies.append({
                        "company": company,
                        "status": "✅ WORKING",
                        "job_count": len(jobs)
                    })
                    print(f"✅ {company}: {len(jobs)} jobs")
                else:
                    broken_companies.append({
                        "company": company,
                        "status": f"❌ {response.status_code}",
                        "job_count": 0
                    })
                    print(f"❌ {company}: {response.status_code}")
                    
            except Exception as e:
                broken_companies.append({
                    "company": company,
                    "status": f"❌ ERROR",
                    "error": str(e),
                    "job_count": 0
                })
                print(f"❌ {company}: {str(e)[:50]}...")
        
        self.validation_results["greenhouse_companies"] = {
            "working": working_companies,
            "broken": broken_companies,
            "total_tested": len(companies[:10])
        }
        
        return len(working_companies) > 0
    
    def validate_lever_companies(self):
        """Test which Lever companies actually work."""
        print("\n🎚️ Validating Lever Companies")
        print("=" * 50)
        
        with open(BOARDS_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        
        companies = config.get('sources', {}).get('lever', {}).get('companies', [])
        working_companies = []
        broken_companies = []
        
        for company in companies:
            try:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    jobs = response.json()
                    working_companies.append({
                        "company": company,
                        "status": "✅ WORKING",
                        "job_count": len(jobs) if isinstance(jobs, list) else 0
                    })
                    print(f"✅ {company}: {len(jobs) if isinstance(jobs, list) else 0} jobs")
                else:
                    broken_companies.append({
                        "company": company,
                        "status": f"❌ {response.status_code}",
                        "job_count": 0
                    })
                    print(f"❌ {company}: {response.status_code}")
                    
            except Exception as e:
                broken_companies.append({
                    "company": company,
                    "status": f"❌ ERROR", 
                    "error": str(e),
                    "job_count": 0
                })
                print(f"❌ {company}: {str(e)[:50]}...")
        
        self.validation_results["lever_companies"] = {
            "working": working_companies,
            "broken": broken_companies,
            "total_tested": len(companies)
        }
        
        return len(working_companies) > 0
    
    def validate_israeli_sources(self):
        """Test Israeli job sources availability."""
        print("\n🇮🇱 Validating Israeli Sources")
        print("=" * 50)
        
        sources = [
            {
                "name": "AllJobs RSS",
                "url": "https://www.alljobs.co.il/rss/jobs.aspx?region=2,3,4&category=2",
                "type": "rss"
            },
            {
                "name": "TheMarker RSS", 
                "url": "https://www.themarker.com/career/rss/",
                "type": "rss"
            },
            {
                "name": "LinkedIn Israel",
                "url": "https://www.linkedin.com/jobs/search/?keywords=DevOps&location=Israel",
                "type": "web"
            },
            {
                "name": "Glassdoor Israel",
                "url": "https://www.glassdoor.com/Job/israel-jobs-SRCH_IL.0,6_IN119.htm",
                "type": "web"
            }
        ]
        
        source_results = []
        
        for source in sources:
            try:
                response = self.session.get(source["url"], timeout=10)
                
                if response.status_code == 200 and len(response.text) > 1000:
                    source_results.append({
                        "name": source["name"],
                        "status": "✅ ACCESSIBLE",
                        "response_size": len(response.text)
                    })
                    print(f"✅ {source['name']}: Accessible ({len(response.text)} chars)")
                else:
                    source_results.append({
                        "name": source["name"],
                        "status": f"❌ {response.status_code}",
                        "response_size": len(response.text) if response.text else 0
                    })
                    print(f"❌ {source['name']}: {response.status_code}")
                    
            except Exception as e:
                source_results.append({
                    "name": source["name"],
                    "status": "❌ ERROR",
                    "error": str(e)
                })
                print(f"❌ {source['name']}: {str(e)[:50]}...")
        
        self.validation_results["israeli_sources"] = source_results
        return len([s for s in source_results if "✅" in s["status"]]) > 0
    
    def generate_build_report(self):
        """Generate a comprehensive build validation report."""
        print("\n📊 Build Validation Report")
        print("=" * 60)
        
        # Environment status
        env_good = all("✅" in status for status in self.validation_results["environment"].values())
        print(f"Environment: {'✅ PASS' if env_good else '❌ FAIL'}")
        
        # Greenhouse status
        gh_working = len(self.validation_results["greenhouse_companies"]["working"])
        gh_broken = len(self.validation_results["greenhouse_companies"]["broken"])
        print(f"Greenhouse: ✅ {gh_working} working, ❌ {gh_broken} broken")
        
        # Lever status
        lever_working = len(self.validation_results["lever_companies"]["working"])
        lever_broken = len(self.validation_results["lever_companies"]["broken"])
        print(f"Lever: ✅ {lever_working} working, ❌ {lever_broken} broken")
        
        # Israeli sources status
        israeli_accessible = len([s for s in self.validation_results["israeli_sources"] if "✅" in s["status"]])
        israeli_broken = len([s for s in self.validation_results["israeli_sources"] if "❌" in s["status"]])
        print(f"Israeli Sources: ✅ {israeli_accessible} accessible, ❌ {israeli_broken} broken")
        
        # Overall status
        overall_good = env_good and gh_working > 0
        self.validation_results["build_status"] = "✅ PASS" if overall_good else "❌ FAIL"
        
        print("=" * 60)
        print(f"🎯 Overall Build Status: {self.validation_results['build_status']}")
        
        # Save validation report
        report_file = ROOT / "build_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Report saved to: {report_file}")
        
        return overall_good

def main():
    """Run complete pipeline build validation."""
    print("🏗️ PIPELINE BUILD PHASE")
    print("=" * 60)
    print(f"Build Date: {date.today().isoformat()}")
    print("=" * 60)
    
    validator = PipelineBuildValidator()
    
    # Run all validations
    env_ok = validator.validate_environment()
    greenhouse_ok = validator.validate_greenhouse_companies()
    lever_ok = validator.validate_lever_companies()
    israeli_ok = validator.validate_israeli_sources()
    
    # Generate final report
    build_success = validator.generate_build_report()
    
    if build_success:
        print("\n🚀 BUILD PHASE COMPLETE - Ready for deployment!")
        return 0
    else:
        print("\n❌ BUILD PHASE FAILED - Fix issues before deployment!")
        return 1

if __name__ == "__main__":
    exit(main())
