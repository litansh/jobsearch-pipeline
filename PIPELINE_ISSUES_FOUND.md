# 🚨 Major Pipeline Issues Found

## ❌ **Root Cause: Enhanced Sources NOT Running**

The daily pipeline is **MISSING** the Israeli job sources entirely:

### **What's Actually Running:**
```yaml
- python scripts/crawl.py                 # Only basic Greenhouse/Lever
- python scripts/real_job_finder.py       # Limited sources  
- python scripts/add_known_jobs.py        # Manual jobs only
- python scripts/real_verified_jobs.py    # Small verified set
```

### **What's MISSING:**
```yaml
- python scripts/israeli_job_sources.py   # 🚨 NOT RUNNING!
```

This means **NONE** of these enhanced sources are working:
- ❌ AllJobs.co.il 
- ❌ TheMarker RSS
- ❌ Comeet API (Monday, Wix, Outbrain, etc.)
- ❌ SmartRecruiters API
- ❌ Enhanced Israeli company search

## 🔍 **Specific Issues Found:**

### **1. Wrong Company Slugs (404 Errors)**
These companies return 404 in Greenhouse/Lever:
- astrix-security ❌
- lakefs ❌  
- qodo ❌
- zenity ❌
- armis ❌
- lemonade ❌
- vicarius ❌
- nvidia-israel ❌
- check-point ❌
- cyberark ❌

### **2. Network Issues**
- Comeet API endpoints failing with DNS errors
- monday.comeet.co, wix.comeet.co not resolving

### **3. Score Threshold**
- Set to 0.50 (might be too high)
- Could be filtering out good Director positions

## 📊 **Current Results:**
- Only **16 records** found (vs expected 50+)
- Missing LinkedIn Director positions you mentioned
- Pipeline runs too fast (not searching enhanced sources)

## 🔧 **Fixes Needed:**

1. **Add Israeli sources to daily workflow**
2. **Fix company slugs** (research correct identifiers)  
3. **Fix Comeet API endpoints**
4. **Lower score threshold** to 0.40
5. **Test each source individually**

This explains why you're not seeing new positions! 🎯
