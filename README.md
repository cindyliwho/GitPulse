# 🚀 GitPulse — AI-Powered PM Dashboard for GitHub Repos

Paste any public GitHub repo and instantly get a PM-style project status report — no manual updates, no chasing people for standups. GitPulse fetches real-time repo activity and uses an LLM to generate structured insights about project health, shipped work, risks, and team contributions.

🎥 **[Watch the Demo →] **

![GitPulse Dashboard Screenshot](screenshot.png)

---

## The Problem

Status updates are manual, delayed, and inconsistent. Engineering managers and PMs spend hours piecing together what shipped, what's blocked, and who's doing what — usually by digging through GitHub or Slack.

## The Solution

GitPulse automates this entirely. Paste in `facebook/react` or any public repo URL, and in seconds you get:

- 🟢🟡🔴 **Project Health Signal** — instant red/yellow/green assessment with reasoning
- 📋 **Executive Summary** — 2-3 sentence overview of project momentum
- ✅ **Shipped Work** — merged PRs grouped by feature/workstream
- 🔨 **In Progress** — open PRs with on-track / needs-attention / blocked status
- 🚨 **Risks & Blockers** — stale PRs, review bottlenecks, idle work flagged automatically
- 👥 **Team Activity** — per-person breakdown of commits, PRs, and focus areas
- 📌 **Key Decisions** — notable changes surfaced from PR descriptions

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **Data Fetching** | GitHub REST API |
| **AI Analysis** | OpenAI GPT-3.5 Turbo |
| **Frontend** | Jinja2 templates, HTML/CSS |
| **Config** | python-dotenv for API key management |

---

## Key Engineering Decisions

### 1. Structured JSON Output from LLM
Instead of free-text responses, the LLM is constrained to return a strict JSON schema using OpenAI's `response_format={"type": "json_object"}`. This makes the output directly renderable in the dashboard without parsing.

### 2. Data Trimming Before LLM Call
Raw GitHub API responses are large. `prepare_data_for_llm()` trims commits to 30, PRs to 20, and issues to 15 — keeping only the fields that matter for PM analysis. This reduces token usage and keeps responses fast.

### 3. Graceful Fallback
If the OpenAI call fails (rate limit, timeout, etc.), `generate_fallback_analysis()` kicks in with a rule-based summary built from raw GitHub data — so the dashboard never shows an empty state.

### 4. In-Memory Caching
Repeat queries for the same repo hit a cache instead of re-fetching from GitHub and re-calling OpenAI. This speeds up demos and saves API costs.

### 5. Speed Optimization
PR review details (individual review fetching) were intentionally removed to keep GitHub API calls fast. The analyzer infers review status from PR metadata instead.
