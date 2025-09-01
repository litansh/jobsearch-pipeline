#!/usr/bin/env python3
"""
Test script for the enhanced Israeli job sources.
Run this locally to see if the new company lists are working.
"""

import sys
import pathlib
import os
from dotenv import load_dotenv

# Add the project root to Python path
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv()

def test_israeli_sources():
    """Test the Israeli job sources with enhanced company lists."""
    print("🇮🇱 Testing Enhanced Israeli Job Sources")
    print("=" * 50)
    
    try:
        # Test the Israeli job sources
        from scripts.israeli_job_sources import main as israeli_main
        print("\n[TEST] Running Israeli job sources...")
        israeli_jobs = israeli_main()
        print(f"✅ Israeli sources: {israeli_jobs} jobs found")
        
    except Exception as e:
        print(f"❌ Israeli sources failed: {e}")
        israeli_jobs = 0
    
    try:
        # Test running the digest to see what would be sent
        print("\n[TEST] Testing digest logic...")
        os.environ["PYTHONPATH"] = str(ROOT)
        from scripts.digest import main as digest_main
        digest_main()
        print("✅ Digest test completed")
        
    except Exception as e:
        print(f"❌ Digest test failed: {e}")
    
    print(f"\n🎯 Total jobs found: {israeli_jobs}")
    print("=" * 50)
    
    return israeli_jobs

if __name__ == "__main__":
    test_israeli_sources()
