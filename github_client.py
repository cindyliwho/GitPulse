import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
 
load_dotenv()
 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
BASE_URL = "https://api.github.com"
 
 
def fetch_repo_data(repo_owner, repo_name, days_back=14):
    """
    Fetches commits, PRs, and issues from a GitHub repo.
    Returns a clean dictionary with everything we need.
    """
    repo = f"{repo_owner}/{repo_name}"
    since_date = (datetime.now() - timedelta(days=days_back)).isoformat() + "Z"
 
    print(f"📡 Fetching data from {repo} (last {days_back} days)...")
 
    # Fetch everything
    commits = fetch_commits(repo, since_date)
    pull_requests = fetch_pull_requests(repo, since_date)
    issues = fetch_issues(repo, since_date)
 
    repo_data = {
        "repo": repo,
        "period": f"Last {days_back} days",
        "fetched_at": datetime.now().isoformat(),
        "summary_stats": {
            "total_commits": len(commits),
            "total_prs": len(pull_requests),
            "total_issues": len(issues),
        },
        "commits": commits,
        "pull_requests": pull_requests,
        "issues": issues,
    }
 
    print(f"✅ Fetched: {len(commits)} commits, {len(pull_requests)} PRs, {len(issues)} issues")
    return repo_data
 
 
def fetch_commits(repo, since_date):
    """Fetch recent commits."""
    url = f"{BASE_URL}/repos/{repo}/commits"
    params = {
        "since": since_date,
        "per_page": 100,
    }
 
    response = requests.get(url, headers=HEADERS, params=params)
 
    if response.status_code != 200:
        print(f"❌ Error fetching commits: {response.status_code}")
        return []
 
    commits = []
    for c in response.json():
        commits.append({
            "sha": c["sha"][:7],
            "author": c["commit"]["author"]["name"],
            "author_github": c["author"]["login"] if c["author"] else "unknown",
            "message": c["commit"]["message"].split("\n")[0],  # First line only
            "date": c["commit"]["author"]["date"],
        })
 
    return commits
 
 
def fetch_pull_requests(repo, since_date):
    """Fetch recent pull requests - FAST version (no individual review fetching)."""
    url = f"{BASE_URL}/repos/{repo}/pulls"
    all_prs = []
 
    # Fetch open PRs
    params = {"state": "open", "per_page": 15, "sort": "updated"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        all_prs.extend(response.json())
 
    # Fetch recently closed/merged PRs
    params = {"state": "closed", "per_page": 15, "sort": "updated"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        for pr in response.json():
            if pr["closed_at"] and pr["closed_at"] >= since_date:
                all_prs.append(pr)
 
    # Clean up — NO individual review fetching
    pull_requests = []
    for pr in all_prs:
        pull_requests.append({
            "number": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "state": pr["state"],
            "merged": pr.get("merged_at") is not None,
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "closed_at": pr["closed_at"],
            "body": (pr["body"] or "")[:300],
            "labels": [l["name"] for l in pr["labels"]],
            "reviewers": [r["login"] for r in pr["requested_reviewers"]],
            "review_count": 0,
            "review_states": [],
            "comments": pr.get("comments", 0),
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
        })
 
    return pull_requests
 
 
 
def fetch_issues(repo, since_date):
    """Fetch recent issues (not PRs)."""
    url = f"{BASE_URL}/repos/{repo}/issues"
    params = {
        "since": since_date,
        "per_page": 50,
        "state": "all",
        "sort": "updated",
    }
 
    response = requests.get(url, headers=HEADERS, params=params)
 
    if response.status_code != 200:
        print(f"❌ Error fetching issues: {response.status_code}")
        return []
 
    issues = []
    for i in response.json():
        # Skip pull requests (GitHub API returns them as issues too)
        if "pull_request" in i:
            continue
 
        issues.append({
            "number": i["number"],
            "title": i["title"],
            "author": i["user"]["login"],
            "state": i["state"],
            "created_at": i["created_at"],
            "updated_at": i["updated_at"],
            "labels": [l["name"] for l in i["labels"]],
            "assignee": i["assignee"]["login"] if i["assignee"] else None,
            "comments": i["comments"],
            "body": (i["body"] or "")[:300],
        })
 
    return issues
 
 
# ---- Test it! ----
if __name__ == "__main__":
    # Test with React repo (or change to any repo)
    data = fetch_repo_data("facebook", "react", days_back=7)
 
    print(f"\n📊 Summary for {data['repo']}:")
    print(f"   Commits: {data['summary_stats']['total_commits']}")
    print(f"   PRs: {data['summary_stats']['total_prs']}")
    print(f"   Issues: {data['summary_stats']['total_issues']}")
 
    print(f"\n📝 Recent commits:")
    for c in data["commits"][:5]:
        print(f"   {c['author']}: {c['message'][:60]}")
 
    print(f"\n🔀 Recent PRs:")
    for pr in data["pull_requests"][:5]:
        status = "✅ merged" if pr["merged"] else f"📂 {pr['state']}"
        print(f"   #{pr['number']} {pr['title'][:50]} ({status})")