# GitPulse

GitPulse is a zero-input PM dashboard for GitHub repositories. Paste in any public repo and it turns recent commits, pull requests, and issues into a fast project status report with shipped work, work in progress, risks, team activity, and an overall health signal.

## Why it exists

Status updates are usually manual, delayed, and inconsistent. GitPulse pulls activity directly from GitHub and uses an LLM to generate a PM-style summary so you can understand project momentum without chasing people for updates.

## What it does

- Accepts a repo as `owner/repo` or a full GitHub URL
- Fetches recent commits, pull requests, and issues from the GitHub API
- Sends a trimmed activity snapshot to OpenAI for structured analysis
- Renders a dashboard with project health, an executive summary, shipped work, in-progress work, risks, team activity, and key decisions
- Caches analyses in memory during the current app session to speed up repeat demos

## Tech stack

- Python
- Flask
- GitHub REST API
- OpenAI API
- Jinja templates with a single-page dashboard UI

## How it works

1. The Flask app accepts a repository input from the dashboard form.
2. `app.py` parses the repo name and checks an in-memory cache.
3. `github_client.py` fetches the last 14 days of commits, pull requests, and issues.
4. `ai_analyzer.py` trims that data and asks the model for a strict JSON project report.
5. `templates/dashboard.html` renders the final PM summary.

## Project structure

```text
zero-input-pm/
├── app.py
├── ai_analyzer.py
├── github_client.py
├── templates/
│   └── dashboard.html
├── test_ai.py
├── test_github.py
└── guide.md
```

## Local setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install flask openai python-dotenv requests
```

### 3. Add environment variables

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the app

```bash
python app.py
```

Then open [http://localhost:5001](http://localhost:5001).

## Example input

```text
facebook/react
```

or

```text
https://github.com/facebook/react
```

## Output format

GitPulse asks the model to return a structured JSON report with fields like:

- `health`
- `health_reason`
- `executive_summary`
- `shipped`
- `in_progress`
- `risks`
- `team_activity`
- `key_decisions`

If the AI call fails, the app falls back to a simpler rule-based summary built from raw GitHub data.

## Current limitations

- The cache is in memory only and resets when the server restarts.
- The app currently analyzes a fixed 14-day window.
- Pull request review details are intentionally simplified for speed.
- The OpenAI model is currently set in code and not configurable from the UI.
- There is no persisted database, auth layer, or background job system yet.

## Good use cases

- Quick repo health checks before standup
- Demoing AI-assisted project management
- Summarizing open source repo activity
- Turning noisy GitHub activity into an executive-ready status snapshot

## Future improvements

- Configurable time ranges
- Better PR review and stale-work detection
- Saved report history
- Org-level multi-repo rollups
- Slack or email status digests
- Stronger fallback analytics without the LLM

## GitHub description

If you also want a short GitHub repo description, use:

> AI-powered zero-input PM dashboard that turns GitHub repo activity into instant project health, progress, and risk reports.
