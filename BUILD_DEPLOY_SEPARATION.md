# 🏗️ Build vs Deploy Pipeline Separation

## 📋 **Architecture Overview**

### **BUILD PHASE** 🏗️
**Purpose**: Setup, validation, and testing  
**When**: On code changes (push/PR)  
**Duration**: ~2-3 minutes  
**Workflow**: `.github/workflows/build-pipeline.yml`

### **DEPLOY PHASE** 🚀  
**Purpose**: Execute actual job search  
**When**: Daily cron OR Telegram `/search` command  
**Duration**: ~3-5 minutes  
**Workflow**: `.github/workflows/deploy-daily.yml` + `.github/workflows/deploy-telegram.yml`

---

## 🏗️ **BUILD PIPELINE** 

### **Triggers:**
- ✅ Push to main branch (scripts/configs changes)
- ✅ Pull requests  
- ✅ Manual workflow dispatch

### **Build Steps:**
1. **Environment Validation** - Check API keys, tokens
2. **Source Testing** - Test Greenhouse/Lever APIs
3. **Israeli Sources Test** - Test AllJobs, TheMarker, workarounds  
4. **Deduplication Test** - Verify filtering works
5. **Scoring Test** - Test AI scoring system
6. **Artifact Upload** - Save build validation report

### **Build Outputs:**
- ✅ `build_validation_report.json` - What sources work/fail
- ✅ Test job data - Sample results from each source
- ✅ Configuration validation - All configs are valid

---

## 🚀 **DEPLOY PIPELINES**

### **1. Daily Deploy** (Scheduled)
**Trigger**: Cron `30 5 * * *` (5:30 AM UTC daily)  
**Purpose**: Regular job discovery  
**Mode**: Full comprehensive search

### **2. Telegram Deploy** (On-Demand)
**Trigger**: Repository dispatch from Telegram `/search`  
**Purpose**: User-initiated job search  
**Modes**: 
- `full` - Complete search (default)
- `quick` - Greenhouse/Lever only  
- `clean` - Remove old jobs

### **Deploy Steps:**
1. **Setup** - Environment, git, state management
2. **Execute** - Run `deploy_pipeline.py` with specified mode
3. **Process** - Deduplicate, score, send digest
4. **Persist** - Commit results, create PR, auto-merge
5. **Notify** - Send completion status to Telegram

---

## 🔄 **Workflow Integration**

### **Telegram Commands → Deploy:**
```
/search → deploy-telegram.yml (full mode)
/crawl  → deploy-telegram.yml (quick mode)  
/clean  → deploy-telegram.yml (clean mode)
```

### **Daily Schedule → Deploy:**
```
Cron 5:30 AM → deploy-daily.yml (full mode)
```

### **Code Changes → Build:**
```
Push to main → build-pipeline.yml (validation only)
```

---

## 🎯 **Benefits of Separation**

### **✅ Build Phase Benefits:**
- **Fast feedback** on code changes (2-3 min vs 5+ min)
- **Source validation** before deployment
- **No job state changes** during testing
- **Parallel development** - build while deploy runs

### **✅ Deploy Phase Benefits:**  
- **Clean execution** - only job search logic
- **Optimized for results** - all sources, comprehensive
- **State management** - proper job state persistence
- **User notifications** - Telegram integration

### **✅ Overall Benefits:**
- **Faster development** - quick build feedback
- **Reliable deployment** - tested sources only
- **Better monitoring** - separate build/deploy logs
- **Cleaner workflows** - single responsibility

---

## 📊 **Expected Performance**

### **Build Pipeline:**
- ⏱️ **Duration**: 2-3 minutes
- 🔍 **Purpose**: Validate and test
- 📊 **Output**: Build validation report
- 🚫 **No job state changes**

### **Deploy Pipeline:**
- ⏱️ **Duration**: 3-5 minutes  
- 🔍 **Purpose**: Find and deliver jobs
- 📊 **Output**: Job digest to Telegram
- ✅ **Updates job state**

---

## 🚀 **Ready to Use**

The separation is complete! Now:

1. **Build pipeline** validates your enhancements
2. **Deploy pipeline** executes job search
3. **Telegram `/search`** triggers deploy only
4. **Daily cron** runs deploy automatically

**Clean separation achieved!** 🎯
