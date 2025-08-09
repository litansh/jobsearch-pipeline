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

def best_job():
    # return the top-scoring job as default
    rows = []
    with open(SCORES, "r", encoding="utf-8") as f:
        for line in f:
            try: rows.append(json.loads(line))
            except: pass
    rows.sort(key=lambda r: r.get("score",0), reverse=True)
    return rows[0] if rows else None

def generate_questions(job):
    prompt = f"""Create 10 senior DevOps/Platform leadership interview questions tailored to this role.
    Role: {job.get('title') if job else 'Head/Director of DevOps (General)'}
    Company: {job.get('company') if job else 'Unknown'}
    Candidate highlights:
    {PROFILE}
    Focus: production ownership, live-event readiness, observability, security alignment, databases, CI/CD, scaling strategy, team leadership, and exec communications.
    Return numbered questions only.
    """
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()

def score_answer(question, answer):
    rubric = "Score 1-10; consider clarity, metrics, STAR structure, relevance to reliability/cost/scale, and leadership signal."
    prompt = f"""Question: {question}
    Candidate answer:
    {answer}
    {rubric}
    Return a JSON with keys: score (int), strengths (bullets), improvements (bullets), tighter_version (<=120 words)."""
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

if __name__ == "__main__":
    import sys
    job = best_job()
    qs = generate_questions(job)
    print(qs)
    print("\nPaste one answer below and press Ctrl+D (Linux/macOS) or Ctrl+Z (Windows) when done:\n")
    try:
        ans = sys.stdin.read()
    except KeyboardInterrupt:
        raise SystemExit()
    if ans.strip():
        q1 = qs.splitlines()[0]
        print("\nFeedback:")
        print(score_answer(q1, ans.strip()))
    else:
        print("No answer provided. Exiting.")
