import sys, csv, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "connections.csv"

HELP = "Usage: python scripts/network.py <company_domain_or_name>\nPlace your LinkedIn connections export as data/connections.csv"

def norm(s): return (s or "").strip().lower()

def main():
    if len(sys.argv) < 2:
        print(HELP); raise SystemExit(1)
    needle = norm(sys.argv[1])
    if not CSV.exists():
        print("Missing data/connections.csv (export from LinkedIn)."); raise SystemExit(2)
    matches = []
    with open(CSV, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            company = norm(row.get("Company","") or row.get("Position",""))
            name = row.get("First Name","") + " " + row.get("Last Name","")
            if needle in company or re.search(needle.replace(".", r"\."), company or ""):
                matches.append((name, row.get("Email Address","") or "", row.get("Company","") or row.get("Position","")))
    if not matches:
        print("No likely connectors found.")
        return
    print(f"Potential connectors for '{needle}':")
    for i,(n,e,c) in enumerate(matches,1):
        print(f"{i:>2}. {n} — {c} {f'({e})' if e else ''}")
    print("\nSuggested intro DM:")
    print("Hi <Name>, hope you’re well! I’m exploring leadership roles at <Company>. Given our connection, would you feel comfortable introducing me to the hiring manager or eng leadership? Happy to send a short blurb. Thanks! — Litan")

if __name__ == "__main__":
    main()
