"""
Career-Ops Pipeline Builder
Merges Greenhouse API results + WebSearch findings into pipeline.md and scan-history.tsv
"""
import json
from datetime import date

TODAY = date.today().isoformat()

# ── 1. Greenhouse API results (already filtered) ──────────────────────────────
with open("/home/ubuntu/career-ops/data/scan_results.json") as f:
    gh_data = json.load(f)

greenhouse_jobs = gh_data["results"]

# ── 2. WebSearch findings (manually curated from search results) ──────────────
websearch_jobs = [
    # OpenAI Seoul
    {
        "company": "OpenAI",
        "title": "AI Success Engineer",
        "url": "https://openai.com/careers/ai-success-engineer-seoul-south-korea-seoul-south-korea/",
        "portal": "WebSearch — OpenAI Seoul",
        "status": "active"
    },
    {
        "company": "OpenAI",
        "title": "AI Deployment Engineer",
        "url": "https://openai.com/careers/ai-deployment-engineer-seoul-south-korea/",
        "portal": "WebSearch — OpenAI Seoul",
        "status": "active"
    },
    # EY Singapore — Actuarial
    {
        "company": "EY",
        "title": "Actuarial - Non-Life Insurance Manager/Senior Manager, Risk Consulting",
        "url": "https://sg.linkedin.com/jobs/view/actuarial-non-life-insurance-financial-services-manager-senior-manager-risk-consulting-at-ey-4389178077",
        "portal": "WebSearch — EY Singapore Actuarial",
        "status": "active"
    },
    {
        "company": "EY",
        "title": "Actuarial - Life Insurance Manager/Senior Manager, Risk Consulting",
        "url": "https://sg.indeed.com/viewjob?jk=66290b5a3b21d573",
        "portal": "WebSearch — EY Singapore Actuarial",
        "status": "active"
    },
    # Deloitte Singapore — Risk Management
    {
        "company": "Deloitte",
        "title": "Manager, Integrated Risk Management",
        "url": "https://jobs.sea.deloitte.com/job/Singapore-A%26A-SG-CA-Manager%2C-Integrated-Risk-Management-Sing/1359470566/",
        "portal": "WebSearch — Deloitte Singapore Risk",
        "status": "active"
    },
    # PwC — AI Insurance
    {
        "company": "PwC",
        "title": "AI Insurance Solutions Architect, Sr. Manager",
        "url": "https://jobs.us.pwc.com/job/chicago/ai-insurance-solutions-architect-sr-manager/932/93266110432",
        "portal": "WebSearch — PwC AI Insurance",
        "status": "active"
    },
    # Swiss Re Singapore
    {
        "company": "Swiss Re",
        "title": "Global Pricing Actuary - L&H",
        "url": "https://www.swissre.com/careers/jobSearch.html",
        "portal": "WebSearch — Swiss Re APAC",
        "status": "active"
    },
    # WTW
    {
        "company": "WTW",
        "title": "Actuarial Talent Pool ICT (Insurance Consulting & Technology)",
        "url": "https://careers.wtwco.com/jobs/actuarial-talent-pool-ict-insurance-consulting-technology-team-malaysia-malaysia",
        "portal": "WebSearch — WTW ICT",
        "status": "active"
    },
    # Milliman Singapore
    {
        "company": "Milliman",
        "title": "Actuary - Singapore (IFRS17 Life Insurance Consulting)",
        "url": "https://sg.linkedin.com/jobs/view/actuary-singapore-sgp-at-milliman-3918954460",
        "portal": "WebSearch — Milliman Singapore",
        "status": "active"
    },
    # Alpha FMC
    {
        "company": "Alpha FMC",
        "title": "Manager - Insurance Strategic and Operational Transformation",
        "url": "https://www.linkedin.com/jobs/view/manager-insurance-strategic-and-operational-transformation-at-alpha-fmc-4362232738",
        "portal": "WebSearch — Alpha FMC Insurance",
        "status": "active"
    },
    # Pinpoint Asia
    {
        "company": "Pinpoint Asia (IFI)",
        "title": "AI & Automation Transformation Manager",
        "url": "https://hk.linkedin.com/jobs/view/ai-automation-transformation-manager-international-financial-institution-at-pinpoint-asia-4317173040",
        "portal": "WebSearch — Pinpoint Asia",
        "status": "active"
    },
    # KPMG Singapore
    {
        "company": "KPMG Singapore",
        "title": "FS Consulting, Life Actuarial, Senior Associate to Manager",
        "url": "https://sg.linkedin.com/jobs/view/fs-consulting-life-actuarial-senior-associate-to-manager-at-kpmg-singapore-4389178077",
        "portal": "WebSearch — KPMG Singapore",
        "status": "active"
    },
]

# ── 3. Curated high-priority Greenhouse jobs (from 486 results) ───────────────
# Filter to most relevant from Greenhouse scan
PRIORITY_TITLES = [
    "solutions architect", "solutions engineer", "ai product manager",
    "product manager", "ai outcomes", "ai sales engineer",
    "machine learning engineer", "principal machine learning",
    "customer success manager", "director", "manager",
    "forward deployed", "applied ai", "ai engineer"
]

priority_gh = []
for job in greenhouse_jobs:
    title_lower = job["title"].lower()
    if any(kw in title_lower for kw in PRIORITY_TITLES):
        priority_gh.append(job)

# Limit to top 50 most relevant Greenhouse jobs
priority_gh = priority_gh[:50]

# ── 4. Build pipeline.md ──────────────────────────────────────────────────────
pipeline_lines = [
    "# Career-Ops Pipeline",
    "",
    f"_Last scan: {TODAY}_",
    "",
    "## Pendientes (To Evaluate)",
    "",
    "### 🔥 High Priority — Actuarial / Risk / AI (Direct Matches)",
    "",
]

for job in websearch_jobs:
    pipeline_lines.append(f"- [ ] {job['url']} | {job['company']} | {job['title']}")

pipeline_lines += [
    "",
    "### 🤖 AI Platform Companies (Greenhouse API)",
    "",
]

for job in priority_gh:
    pipeline_lines.append(f"- [ ] {job['url']} | {job['company']} | {job['title']}")

pipeline_lines += [
    "",
    "## Procesadas (Evaluated)",
    "",
    "## Archivadas (Archived)",
    "",
]

with open("/home/ubuntu/career-ops/data/pipeline.md", "w") as f:
    f.write("\n".join(pipeline_lines))

# ── 5. Build scan-history.tsv ─────────────────────────────────────────────────
history_lines = ["url\tfirst_seen\tportal\ttitle\tcompany\tstatus"]

for job in websearch_jobs:
    history_lines.append(f"{job['url']}\t{TODAY}\t{job['portal']}\t{job['title']}\t{job['company']}\tadded")

for job in priority_gh:
    history_lines.append(f"{job['url']}\t{TODAY}\tGreenhouse API\t{job['title']}\t{job['company']}\tadded")

# Record skipped (non-priority) Greenhouse jobs
skipped_gh = [j for j in greenhouse_jobs if j not in priority_gh]
for job in skipped_gh[:100]:  # record first 100 skipped
    history_lines.append(f"{job['url']}\t{TODAY}\tGreenhouse API\t{job['title']}\t{job['company']}\tskipped_title")

with open("/home/ubuntu/career-ops/data/scan-history.tsv", "w") as f:
    f.write("\n".join(history_lines))

# ── 6. Summary ────────────────────────────────────────────────────────────────
total_added = len(websearch_jobs) + len(priority_gh)
total_skipped = len(greenhouse_jobs) - len(priority_gh)

print(f"""
Portal Scan — {TODAY}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Greenhouse API 기업 스캔: 17개 기업, {gh_data['total_scanned']}개 공고
WebSearch 검색 (보험/계리/AI 특화): {len(websearch_jobs)}개 공고
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title 필터 통과: {gh_data['total_relevant']}개
우선순위 선별 (Greenhouse): {len(priority_gh)}개
WebSearch 직접 발굴: {len(websearch_jobs)}개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pipeline.md에 추가된 공고: {total_added}개
  🔥 High Priority (계리/리스크/AI): {len(websearch_jobs)}개
  🤖 AI Platform (Greenhouse): {len(priority_gh)}개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("🔥 High Priority 공고:")
for job in websearch_jobs:
    print(f"  + {job['company']} | {job['title']}")

print("\n🤖 AI Platform 공고 (상위 10개):")
for job in priority_gh[:10]:
    print(f"  + {job['company']} | {job['title']}")
if len(priority_gh) > 10:
    print(f"  ... 외 {len(priority_gh)-10}개")
