#!/usr/bin/env python3
"""
DEPLOY PHASE: Execute the actual job search pipeline.
This runs on cron schedule or when triggered by Telegram /search command.
"""

import os
import sys
import pathlib
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PipelineDeployer:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "started_at": self.start_time.isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "total_jobs_found": 0,
            "jobs_sent_to_telegram": 0
        }
    
    def run_step(self, step_name: str, script_path: str, description: str):
        """Run a single pipeline step and track results."""
        print(f"\n🔄 {step_name}")
        print(f"   {description}")
        print("   " + "-" * 40)
        
        try:
            # Set Python path and run script
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT)
            
            result = subprocess.run([
                sys.executable, script_path
            ], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   ✅ {step_name} completed successfully")
                self.results["steps_completed"].append({
                    "name": step_name,
                    "script": script_path,
                    "output": result.stdout[-200:] if result.stdout else ""  # Last 200 chars
                })
                return True
            else:
                print(f"   ❌ {step_name} failed (exit code: {result.returncode})")
                print(f"   Error: {result.stderr[-200:] if result.stderr else 'No error output'}")
                self.results["steps_failed"].append({
                    "name": step_name,
                    "script": script_path,
                    "error": result.stderr[-200:] if result.stderr else "Unknown error"
                })
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {step_name} timed out (5 minutes)")
            self.results["steps_failed"].append({
                "name": step_name,
                "script": script_path,
                "error": "Timeout after 5 minutes"
            })
            return False
        except Exception as e:
            print(f"   ❌ {step_name} error: {e}")
            self.results["steps_failed"].append({
                "name": step_name,
                "script": script_path,
                "error": str(e)
            })
            return False
    
    def deploy_full_pipeline(self):
        """Run the complete job search pipeline."""
        print("🚀 DEPLOY PHASE: Full Job Search Pipeline")
        print("=" * 60)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Search Greenhouse/Lever APIs
        self.run_step(
            "API Search",
            "scripts/crawl.py", 
            "Search Greenhouse and Lever job board APIs"
        )
        
        # Step 2: Search comprehensive sources
        self.run_step(
            "Comprehensive Search",
            "scripts/real_job_finder.py",
            "Search additional verified job sources"
        )
        
        # Step 3: Add known real jobs
        self.run_step(
            "Known Jobs",
            "scripts/add_known_jobs.py",
            "Add manually verified real positions"
        )
        
        # Step 4: Search verified positions
        self.run_step(
            "Verified Positions",
            "scripts/real_verified_jobs.py",
            "Search verified real job positions"
        )
        
        # Step 5: Search Israeli sources
        self.run_step(
            "Israeli Sources",
            "scripts/israeli_job_sources.py",
            "Search Israeli job boards and company sources"
        )
        
        # Step 6: Run job board workarounds
        self.run_step(
            "Workaround Sources",
            "scripts/job_board_workarounds.py",
            "Use workarounds for blocked job boards"
        )
        
        # Step 7: Search career pages
        self.run_step(
            "Career Pages",
            "scripts/career_page_scraper.py",
            "Search company career pages directly"
        )
        
        # Step 8: Deduplicate
        self.run_step(
            "Deduplication",
            "scripts/deduplicate_jobs.py",
            "Remove duplicates and filter unwanted roles"
        )
        
        # Step 9: Update job ages
        self.run_step(
            "Job Tracking",
            "scripts/job_tracker.py",
            "Update job age information"
        )
        
        # Step 10: Score jobs
        self.run_step(
            "Job Scoring",
            "scripts/score.py",
            "Score jobs against user profile using AI"
        )
        
        # Step 11: Send digest
        digest_success = self.run_step(
            "Send Digest",
            "scripts/digest.py",
            "Send job digest to Telegram with interactive buttons"
        )
        
        return self.generate_deploy_report()
    
    def deploy_quick_pipeline(self):
        """Run a quick job search (Greenhouse/Lever only)."""
        print("⚡ DEPLOY PHASE: Quick Job Search")
        print("=" * 60)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Quick pipeline - just essential steps
        self.run_step("API Search", "scripts/crawl.py", "Quick Greenhouse/Lever search")
        self.run_step("Deduplication", "scripts/deduplicate_jobs.py", "Clean up results")
        self.run_step("Job Scoring", "scripts/score.py", "Score jobs")
        self.run_step("Send Digest", "scripts/digest.py", "Send to Telegram")
        
        return self.generate_deploy_report()
    
    def generate_deploy_report(self):
        """Generate deployment report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.results["completed_at"] = end_time.isoformat()
        self.results["duration_seconds"] = duration.total_seconds()
        
        print("\n📊 DEPLOYMENT REPORT")
        print("=" * 60)
        print(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        print(f"✅ Steps completed: {len(self.results['steps_completed'])}")
        print(f"❌ Steps failed: {len(self.results['steps_failed'])}")
        
        if self.results["steps_failed"]:
            print("\n❌ Failed Steps:")
            for step in self.results["steps_failed"]:
                print(f"   • {step['name']}: {step['error'][:100]}...")
        
        # Save deployment report
        report_file = ROOT / "deployment_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        success = len(self.results["steps_failed"]) == 0
        print(f"\n🎯 Deployment Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"📁 Report saved to: {report_file}")
        
        return success

def main():
    """Main deployment entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy job search pipeline")
    parser.add_argument("--mode", choices=["full", "quick"], default="full",
                       help="Pipeline mode: full (all sources) or quick (APIs only)")
    
    args = parser.parse_args()
    
    deployer = PipelineDeployer()
    
    if args.mode == "full":
        success = deployer.deploy_full_pipeline()
    else:
        success = deployer.deploy_quick_pipeline()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
