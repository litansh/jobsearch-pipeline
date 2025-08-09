import os, json, pathlib, numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

ROOT = pathlib.Path(__file__).resolve().parents[1]
load_dotenv()

def get_client():
    """Get OpenAI client, creating it lazily."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JOBS_JL = ROOT / "data" / "processed" / "jobs.jsonl"
PROFILE = (ROOT / "configs" / "profile.md").read_text(encoding="utf-8")
OUT_SCORES = ROOT / "outputs" / "scores.jsonl"

EMB_MODEL = "text-embedding-3-large"

def embed(text: str):
    text = text.replace("\n"," ")
    client = get_client()
    resp = client.embeddings.create(model=EMB_MODEL, input=[text])
    return np.array(resp.data[0].embedding, dtype=np.float32)

def cosine(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0: return 0.0
    return float(np.dot(a, b) / denom)

def main():
    profile_vec = embed(PROFILE)
    rows = []
    with open(JOBS_JL, "r", encoding="utf-8") as f:
        for line in f:
            try:
                j = json.loads(line)
            except:
                continue
            # Build JD text (title + jd if present)
            jd_text = f"{j.get('title','')}\n{j.get('jd','')}"
            vec = embed(jd_text)
            score = cosine(profile_vec, vec)
            why = []
            ttl = (j.get('title','') or '').lower()
            if 'head' in ttl or 'director' in ttl: why.append("senior leadership scope")
            if 'devops' in ttl or 'platform' in ttl or 'sre' in ttl: why.append("platform reliability focus")
            if 'kubernetes' in j.get('jd','').lower() or 'eks' in j.get('jd','').lower(): why.append("k8s scale")
            rows.append({
                "id": j.get("id"),
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "url": j.get("url"),
                "score": round(score, 4),
                "why_fit": ", ".join(why) or "strong profile alignment",
                "age": j.get("age", 1),
                "first_seen": j.get("first_seen", ""),
            })
    rows.sort(key=lambda r: r["score"], reverse=True)
    with open(OUT_SCORES, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[OK] Scored {len(rows)} roles. Top 5:")
    for r in rows[:5]:
        print(f"  - {r['title']} @ {r['company']} :: {r['score']}")

if __name__ == "__main__":
    main()
