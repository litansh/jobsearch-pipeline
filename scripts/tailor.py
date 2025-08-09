import os, json, pathlib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
ROOT = pathlib.Path(__file__).resolve().parents[1]

def get_client():
    """Get OpenAI client, creating it lazily."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCORES = ROOT / "outputs" / "scores.jsonl"
PROFILE = (ROOT / "configs" / "profile.md").read_text(encoding="utf-8")
COVER_TPL = (ROOT / "configs" / "prompts" / "cover_note.j2").read_text(encoding="utf-8")

def pick(job_id: str):
    with open(SCORES, "r", encoding="utf-8") as f:
        for line in f:
            j = json.loads(line)
            if j.get("id") == job_id:
                return j
    raise SystemExit("Job ID not found in outputs/scores.jsonl")

def gen_cover(job):
    prompt = f"""You are drafting a brief, high-signal cover note (120-150 words) for Litan Shabtai Shamir.
    Job title: {job.get('title')}
    Company: {job.get('company')}
    JD URL: {job.get('url')}
    Candidate profile:
    {PROFILE}
    Write 1 paragraph, crisp, metrics-forward, no fluff, focus on production ownership, live-event readiness, observability, GitOps, and leadership.
    """
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/tailor.py <JOB_ID>")
    job = pick(sys.argv[1])
    print(gen_cover(job))
