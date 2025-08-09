import os, json, yaml, pathlib, datetime
from dotenv import load_dotenv
from scripts.utils import job_id, slug, now_iso, create_session, safe_get

load_dotenv()
ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / "configs" / "boards.yaml"))
OUT_RAW = ROOT / "data" / "raw" / f"{datetime.date.today().isoformat()}.json"
OUT_JL  = ROOT / "data" / "processed" / "jobs.jsonl"

def greenhouse_company_jobs(company: str, session):
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    r = safe_get(url, session)
    return r.json().get("jobs", [])

def lever_company_jobs(company: str, session):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    r = safe_get(url, session)
    return r.json()

def normalize_gh(j):
    return {
        "title": j.get("title",""),
        "company": j.get("absolute_url","").split("/")[3] if j.get("absolute_url") else "unknown",
        "location": (j.get("location") or {}).get("name",""),
        "url": j.get("absolute_url",""),
        "source": "greenhouse",
        "posted_at": j.get("updated_at") or j.get("absolute_url",""),
        "jd": "",  # could fetch detail page if needed
    }

def normalize_lever(j):
    return {
        "title": j.get("text",""),
        "company": j.get("categories",{}).get("team","") or j.get("company","unknown"),
        "location": (j.get("categories",{}) or {}).get("location",""),
        "url": j.get("hostedUrl",""),
        "source": "lever",
        "posted_at": j.get("createdAt"),
        "jd": j.get("descriptionPlain","") or j.get("description",""),
    }

def title_matches(title: str) -> bool:
    title_l = title.lower()
    for t in CFG.get("titles", []):
        if t.lower() in title_l:
            return True
    return False

def location_matches(loc: str) -> bool:
    return "israel" in (loc or "").lower() or "tel aviv" in (loc or "").lower() or "herzliya" in (loc or "").lower() or "kfar saba" in (loc or "").lower()

def main():
    session = create_session()
    records = []
    # Greenhouse
    for comp in CFG.get("sources",{}).get("greenhouse",{}).get("companies",[]):
        try:
            for j in greenhouse_company_jobs(comp, session):
                rec = normalize_gh(j)
                if title_matches(rec["title"]) and location_matches(rec["location"]):
                    records.append(rec)
        except Exception as e:
            print(f"[WARN] greenhouse {comp}: {e}")
    # Lever
    for comp in CFG.get("sources",{}).get("lever",{}).get("companies",[]):
        try:
            for j in lever_company_jobs(comp, session):
                rec = normalize_lever(j)
                if title_matches(rec["title"]) and location_matches(rec["location"]):
                    records.append(rec)
        except Exception as e:
            print(f"[WARN] lever {comp}: {e}")

    # Dedupe
    dedup = {}
    for r in records:
        k = r["title"].lower() + "|" + r["company"].lower() + "|" + (r["location"] or "").lower()
        dedup[k] = r
    records = list(dedup.values())

    OUT_RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    # Append to jobs.jsonl (idempotent-ish by URL)
    seen = set()
    if OUT_JL.exists():
        with open(OUT_JL, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                    seen.add(item.get("url",""))
                except:
                    pass
    with open(OUT_JL, "a", encoding="utf-8") as f:
        for r in records:
            if r["url"] in seen: 
                continue
            r["id"] = job_id(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[OK] Collected {len(records)} records. Saved to {OUT_RAW} and appended new to {OUT_JL}.")

if __name__ == "__main__":
    main()
