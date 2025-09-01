#!/usr/bin/env python3
"""
Run Israeli job sources integration.
This script can be called from the main pipeline to search Israeli-specific sources.
"""

import sys
import pathlib
import importlib.util

# Add the project root to Python path
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main():
    """Run the Israeli job sources script."""
    try:
        # Import and run the Israeli job sources
        from scripts.israeli_job_sources import main as israeli_main
        print("[INFO] Running Israeli job sources search...")
        result = israeli_main()
        print(f"[INFO] Israeli sources completed successfully - found {result} jobs")
        return result
    except ImportError as e:
        print(f"[WARN] Could not import israeli_job_sources: {e}")
        return 0
    except Exception as e:
        print(f"[ERROR] Israeli job sources failed: {e}")
        return 0

if __name__ == "__main__":
    main()
