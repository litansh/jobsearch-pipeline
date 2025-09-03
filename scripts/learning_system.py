#!/usr/bin/env python3
"""
Intelligent learning system that analyzes user feedback patterns.
Learns from Applied vs Ignored jobs to improve future scoring.
"""

import json
import pathlib
from datetime import date
from collections import defaultdict
import re
from scripts.job_state import job_state
from scripts.utils import create_session
import openai
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEARNING_DATA = ROOT / "data" / "processed" / "learning_patterns.json"

class JobLearningSystem:
    def __init__(self):
        self.patterns = self.load_learning_patterns()
        
    def load_learning_patterns(self):
        """Load existing learning patterns."""
        if LEARNING_DATA.exists():
            try:
                with open(LEARNING_DATA, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "preferred_keywords": [],      # Keywords from applied jobs
            "avoided_keywords": [],       # Keywords from ignored jobs  
            "preferred_companies": [],    # Companies you apply to
            "avoided_companies": [],      # Companies you ignore
            "preferred_roles": [],        # Role types you prefer
            "avoided_roles": [],          # Role types you avoid
            "last_updated": date.today().isoformat()
        }
    
    def save_learning_patterns(self):
        """Save learning patterns."""
        self.patterns["last_updated"] = date.today().isoformat()
        LEARNING_DATA.parent.mkdir(parents=True, exist_ok=True)
        with open(LEARNING_DATA, 'w') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def analyze_feedback_patterns(self):
        """Analyze user feedback to extract learning patterns."""
        print("🧠 Analyzing User Feedback Patterns")
        print("=" * 50)
        
        # Get applied and ignored jobs
        applied_jobs = job_state.data.get("applied", {})
        ignored_jobs = job_state.data.get("ignored", {})
        
        print(f"📊 Analyzing {len(applied_jobs)} applied + {len(ignored_jobs)} ignored jobs")
        
        # Extract keywords from applied jobs (positive signals)
        applied_keywords = []
        applied_companies = []
        applied_roles = []
        
        for job_id, job_info in applied_jobs.items():
            title = job_info.get("title", "").lower()
            company = job_info.get("company", "").lower()
            
            # Extract role types
            if "devops" in title:
                applied_roles.append("devops")
            if "infrastructure" in title:
                applied_roles.append("infrastructure") 
            if "platform" in title:
                applied_roles.append("platform")
            if "sre" in title or "reliability" in title:
                applied_roles.append("sre")
            if "director" in title:
                applied_roles.append("director")
            if "head" in title:
                applied_roles.append("head")
            if "vp" in title:
                applied_roles.append("vp")
                
            # Extract keywords
            keywords = re.findall(r'\b\w+\b', title)
            applied_keywords.extend([k for k in keywords if len(k) > 3])
            
            applied_companies.append(company)
        
        # Extract keywords from ignored jobs (negative signals)
        ignored_keywords = []
        ignored_companies = []
        ignored_roles = []
        
        for job_id, job_info in ignored_jobs.items():
            title = job_info.get("title", "").lower()
            company = job_info.get("company", "").lower()
            
            # Extract role types you avoid
            if "product" in title:
                ignored_roles.append("product")
            if "marketing" in title:
                ignored_roles.append("marketing")
            if "sales" in title:
                ignored_roles.append("sales")
            if "architect" in title:
                ignored_roles.append("architect")
            if "tech lead" in title or "team lead" in title:
                ignored_roles.append("tech_lead")
                
            # Extract negative keywords
            keywords = re.findall(r'\b\w+\b', title)
            ignored_keywords.extend([k for k in keywords if len(k) > 3])
            
            ignored_companies.append(company)
        
        # Count frequencies
        from collections import Counter
        
        preferred_keywords = [k for k, count in Counter(applied_keywords).most_common(10)]
        avoided_keywords = [k for k, count in Counter(ignored_keywords).most_common(10)]
        preferred_companies = [k for k, count in Counter(applied_companies).most_common(10)]
        avoided_companies = [k for k, count in Counter(ignored_companies).most_common(5)]
        preferred_roles = [k for k, count in Counter(applied_roles).most_common(10)]
        avoided_roles = [k for k, count in Counter(ignored_roles).most_common(10)]
        
        # Update patterns
        self.patterns.update({
            "preferred_keywords": preferred_keywords,
            "avoided_keywords": avoided_keywords,
            "preferred_companies": preferred_companies, 
            "avoided_companies": avoided_companies,
            "preferred_roles": preferred_roles,
            "avoided_roles": avoided_roles
        })
        
        # Print insights
        print("\n✅ LEARNED PREFERENCES:")
        print(f"Preferred roles: {', '.join(preferred_roles[:5])}")
        print(f"Avoided roles: {', '.join(avoided_roles[:5])}")
        print(f"Preferred keywords: {', '.join(preferred_keywords[:5])}")
        print(f"Avoided keywords: {', '.join(avoided_keywords[:5])}")
        
        self.save_learning_patterns()
        return True
    
    def calculate_preference_score(self, job_title: str, job_company: str):
        """Calculate preference score based on learned patterns."""
        title_lower = job_title.lower()
        company_lower = job_company.lower()
        
        score_adjustment = 0.0
        
        # Positive signals (boost score)
        for keyword in self.patterns.get("preferred_keywords", []):
            if keyword in title_lower:
                score_adjustment += 0.1
        
        for role in self.patterns.get("preferred_roles", []):
            if role in title_lower:
                score_adjustment += 0.15
        
        for company in self.patterns.get("preferred_companies", []):
            if company in company_lower:
                score_adjustment += 0.1
        
        # Negative signals (reduce score)
        for keyword in self.patterns.get("avoided_keywords", []):
            if keyword in title_lower:
                score_adjustment -= 0.2
        
        for role in self.patterns.get("avoided_roles", []):
            if role in title_lower:
                score_adjustment -= 0.3
        
        for company in self.patterns.get("avoided_companies", []):
            if company in company_lower:
                score_adjustment -= 0.2
        
        return max(-0.5, min(0.5, score_adjustment))  # Cap between -0.5 and +0.5
    
    def generate_learning_insights(self):
        """Generate AI insights about user preferences."""
        if not os.getenv("OPENAI_API_KEY"):
            return "OpenAI API key not available for insights generation."
        
        try:
            client = openai.OpenAI()
            
            prompt = f"""Based on this job feedback data, provide insights about the user's preferences:

APPLIED TO (Positive signals):
{json.dumps(list(job_state.data.get('applied', {}).values())[:5], indent=2)}

IGNORED (Negative signals):  
{json.dumps(list(job_state.data.get('ignored', {}).values())[:5], indent=2)}

LEARNED PATTERNS:
{json.dumps(self.patterns, indent=2)}

Provide 3-5 specific insights about what this user prefers in DevOps leadership roles, and what they avoid. Focus on role types, company characteristics, and specific keywords."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating insights: {e}"

def main():
    """Analyze user feedback and generate learning insights."""
    learning_system = JobLearningSystem()
    
    # Analyze patterns
    learning_system.analyze_feedback_patterns()
    
    # Generate AI insights
    print("\n🤖 AI-Generated Insights:")
    print("=" * 50)
    insights = learning_system.generate_learning_insights()
    print(insights)
    
    print(f"\n📁 Learning patterns saved to: {LEARNING_DATA}")
    
    return True

if __name__ == "__main__":
    main()
