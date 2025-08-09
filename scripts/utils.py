import os, hashlib, re, time
import requests
from typing import Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def getenv(name: str, default: str = "") -> str:
    v = os.getenv(name, default)
    if v is None:
        return ""
    return v

def slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def job_id(record: Dict) -> str:
    base = f"{record.get('title','')}|{record.get('company','')}|{record.get('location','')}|{record.get('url','')}"
    return hashlib.sha256(base.encode('utf-8')).hexdigest()[:20]

def now_iso():
    import datetime as dt
    return dt.datetime.now().isoformat(timespec='seconds')

def create_session() -> requests.Session:
    """Create a requests session with timeout and retry logic (exponential backoff)."""
    session = requests.Session()
    
    # Configure retry strategy with exponential backoff
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,  # Will be 1, 2, 4 seconds
        raise_on_status=False
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default timeout (20 seconds as per project rules)
    session.timeout = 20
    
    return session

def safe_get(url: str, session: Optional[requests.Session] = None, **kwargs) -> requests.Response:
    """Make a GET request with proper error handling and timeout."""
    if session is None:
        session = create_session()
    
    try:
        response = session.get(url, timeout=20, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Request failed for {url}: {e}")
        raise
