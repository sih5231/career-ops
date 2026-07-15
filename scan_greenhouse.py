"""
Career-Ops Greenhouse API Scanner — v2.0
Reads config from portals.yml (no hardcoding).
Applies title_filter + fit_scoring, outputs data/scan_results.json.

Usage: python3 scan_greenhouse.py
"""
import json
import re
import time
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

TODAY = date.today().isoformat()
ROOT = Path(__file__).parent
PORTALS_YML = ROOT / "portals.yml"
SCAN_RESULTS = ROOT / "data" / "scan_results.json"
SCAN_HISTORY = ROOT / "data" / "scan-history.tsv"
PIPELINE_MD = ROOT / "data" / "pipeline.md"
APPLICATIONS_MD = ROOT / "data" / "applications.md"

# ── Load portals.yml ─────────────────────────────────────────────────────────
with open(PORTALS_YML, encoding="utf-8") as f:
    config = yaml.safe_load(f)

POSITIVE = [k.lower() for k in config["title_filter"]["positive"]]
NEGATIVE = [k.lower() for k in config["title_filter"]["negative"]]
SENIORITY_BOOST = [k.lower() for k in config["title_filter"].get("seniority_boost", [])]
FIT_DIMENSIONS = config.get("fit_scoring", {}).get("dimensions", [])
TIER_THRESHOLDS = config.get("fit_scoring", {}).get(
    "tier_thresholds", {"tier1": 90, "tier2": 75, "tier3": 60}
)

# ── Already-seen URLs ────────────────────────────────────────────────────────
def load_seen_urls():
    seen = set()
    for path in [SCAN_HISTORY, PIPELINE_MD, APPLICATIONS_MD]:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                seen.update(re.findall(r'https?://[^\s\t|]+', line))
    return seen

# ── Title filter ─────────────────────────────────────────────────────────────
def passes_title_filter(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in POSITIVE) and not any(k in t for k in NEGATIVE)

# ── Fit scoring ──────────────────────────────────────────────────────────────
def compute_fit_score(title: str, jd_snippet: str = "") -> int:
    text = (title + " " + jd_snippet).lower()
    raw = 0
    for dim in FIT_DIMENSIONS:
        keywords = [k.lower() for k in dim.get("keywords", [])]
        if any(k in text for k in keywords):
            raw += dim["weight"]
    if any(k in title.lower() for k in SENIORITY_BOOST):
        raw = min(100, int(raw * 1.05))
    return raw

def get_tier(score: int) -> int:
    if score >= TIER_THRESHOLDS["tier1"]:
        return 1
    elif score >= TIER_THRESHOLDS["tier2"]:
        return 2
    elif score >= TIER_THRESHOLDS["tier3"]:
        return 3
    return 0

# ── Greenhouse API fetch ──────────────────────────────────────────────────────
def fetch_greenhouse(company_name: str, api_url: str, seen_urls: set) -> tuple:
    try:
        req = urllib.request.Request(
            api_url, headers={"User-Agent": "career-ops/2.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read())
        jobs_raw = data.get("jobs", [])
    except Exception as e:
        print(f"  ✗ {company_name}: {e}")
        return [], 0

    results = []
    for job in jobs_raw:
        title = job.get("title", "")
        url = job.get("absolute_url", "")
        if not title or not url:
            continue
        if url in seen_urls:
            continue
        if not passes_title_filter(title):
            continue
        score = compute_fit_score(title)
        tier = get_tier(score)
        if tier == 0:
            continue
        results.append({
            "company": company_name,
            "title": title,
            "url": url,
            "source": "greenhouse_api",
            "fit_score": score,
            "tier": tier,
            "date": TODAY,
        })
    return results, len(jobs_raw)

# ── Main ──────────────────────────────────────────────────────────────────────
seen_urls = load_seen_urls()

# Build company list from portals.yml (api: field only)
companies_with_api = [
    c for c in config.get("tracked_companies", [])
    if c.get("enabled", True) and c.get("api")
]

print(f"\n🔍 Greenhouse API Scan — {TODAY}")
print(f"   Config: {PORTALS_YML.name} | Companies: {len(companies_with_api)}")
print("=" * 55)

all_results = []
total_scanned = 0
total_filtered = 0

for company in companies_with_api:
    name = company["name"]
    api_url = company["api"]
    results, total = fetch_greenhouse(name, api_url, seen_urls)
    total_scanned += total
    total_filtered += len(results)
    all_results.extend(results)
    status = f"✅ {len(results)}/{total}" if results else f"   0/{total}"
    print(f"{status}  {name}")
    time.sleep(0.3)

# Sort by fit_score descending
all_results.sort(key=lambda x: x["fit_score"], reverse=True)

# ── Summary ───────────────────────────────────────────────────────────────────
tier1 = [j for j in all_results if j["tier"] == 1]
tier2 = [j for j in all_results if j["tier"] == 2]
tier3 = [j for j in all_results if j["tier"] == 3]

print(f"\n{'='*55}")
print(f"📊 Scanned: {total_scanned} | Matched (fit≥60): {total_filtered}")
print(f"   Tier 1 (≥{TIER_THRESHOLDS['tier1']}): {len(tier1)} | "
      f"Tier 2 (≥{TIER_THRESHOLDS['tier2']}): {len(tier2)} | "
      f"Tier 3 (≥{TIER_THRESHOLDS['tier3']}): {len(tier3)}")

if tier1:
    print(f"\n🔥 Tier 1 highlights:")
    for j in tier1[:5]:
        print(f"  [{j['fit_score']}] {j['company']} | {j['title']}")

# Save results
SCAN_RESULTS.parent.mkdir(exist_ok=True)
with open(SCAN_RESULTS, "w", encoding="utf-8") as f:
    json.dump({
        "date": TODAY,
        "total_scanned": total_scanned,
        "total_relevant": total_filtered,
        "results": all_results,
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved to {SCAN_RESULTS}")
