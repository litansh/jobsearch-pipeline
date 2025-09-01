# GitHub Actions Update Instructions

To fix the issue where GitHub Actions shows the same jobs daily, you need to update the workflow to persist job state between runs.

## 🔧 **Required Changes to `.github/workflows/daily.yml`**

Add these steps to your workflow to enable job state persistence:

### **After "Create data directories" step, add:**

```yaml
- name: Setup git for state persistence
  run: |
    export PYTHONPATH=$GITHUB_WORKSPACE
    python scripts/github_actions_helper.py setup-git

- name: Pull existing job state
  run: |
    export PYTHONPATH=$GITHUB_WORKSPACE  
    python scripts/github_actions_helper.py pull

- name: Initialize state files
  run: |
    export PYTHONPATH=$GITHUB_WORKSPACE
    python scripts/github_actions_helper.py init
```

### **At the very end, after "Push to Notion" step, add:**

```yaml
- name: Show job state summary
  run: |
    export PYTHONPATH=$GITHUB_WORKSPACE
    python scripts/github_actions_helper.py summary

- name: Push updated job state
  run: |
    export PYTHONPATH=$GITHUB_WORKSPACE
    python scripts/github_actions_helper.py push
```

## 🎯 **What This Fixes:**

1. **No more duplicate jobs daily** - Job state persists between workflow runs
2. **Applied/ignored jobs remembered** - Your button clicks are saved permanently
3. **Better job discovery** - Only truly new jobs are sent to Telegram
4. **Automatic state management** - The workflow handles all persistence automatically

## 📋 **Complete Updated Workflow:**

```yaml
name: Daily Job Search

on:
  schedule:
    - cron: '30 5 * * *'  # Daily at 05:30 UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  job-search:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Set up environment
      run: |
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "TELEGRAM_BOT_TOKEN=${{ secrets.TELEGRAM_BOT_TOKEN }}" >> $GITHUB_ENV
        echo "TELEGRAM_CHAT_ID=${{ secrets.TELEGRAM_CHAT_ID }}" >> $GITHUB_ENV
        echo "NOTION_API_KEY=${{ secrets.NOTION_API_KEY }}" >> $GITHUB_ENV
        echo "NOTION_DB_ID=${{ secrets.NOTION_DB_ID }}" >> $GITHUB_ENV
        echo "SCORE_THRESHOLD=0.50" >> $GITHUB_ENV
        echo "DIGEST_MAX=10" >> $GITHUB_ENV
        echo "JOB_MAX_AGE=14" >> $GITHUB_ENV
        
    - name: Create data directories
      run: |
        mkdir -p data/raw data/processed outputs

    # NEW: State persistence setup
    - name: Setup git for state persistence
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/github_actions_helper.py setup-git

    - name: Pull existing job state
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE  
        python scripts/github_actions_helper.py pull

    - name: Initialize state files
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/github_actions_helper.py init
    # END NEW
        
    - name: Crawl jobs
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/crawl.py
        
    - name: Track job ages
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/job_tracker.py update
        
    - name: Score jobs
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/score.py
        
    - name: Send digest
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/digest.py
        
    - name: Push to Notion (if configured)
      if: env.NOTION_API_KEY != ''
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/notion_writer.py

    # NEW: State persistence save
    - name: Show job state summary
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/github_actions_helper.py summary

    - name: Push updated job state
      run: |
        export PYTHONPATH=$GITHUB_WORKSPACE
        python scripts/github_actions_helper.py push
    # END NEW
```

## 🔐 **Required Permissions:**

Make sure your GitHub Actions has write permissions:

1. Go to your repository → **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**

## 🧪 **Testing:**

After updating the workflow:

1. **Manual trigger**: Go to Actions tab → Daily Job Search → Run workflow
2. **Check logs**: Look for "Job State Summary" in the workflow logs
3. **Verify persistence**: Run workflow again - should show fewer/different jobs

## 📊 **Benefits:**

- ✅ **No duplicate jobs** - Only new jobs sent daily
- ✅ **Button memory** - Applied/ignored choices persist
- ✅ **Better discovery** - More varied job results over time
- ✅ **Automatic management** - No manual intervention needed

The workflow will now automatically commit job state changes back to your repository, ensuring continuity between runs!
