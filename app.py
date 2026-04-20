from flask import Flask, render_template, request, jsonify
from github_client import fetch_repo_data
from ai_analyzer import analyze_repo
import time
 
app = Flask(__name__)
 
# Cache to avoid re-fetching during demo
cache = {}
 
 
@app.route("/")
def home():
    """Landing page with repo input."""
    return render_template("dashboard.html", analysis=None, repo=None)
 
 
# @app.route("/analyze", methods=["POST"])
# def analyze():
#     """Fetch and analyze a repo."""
#     repo_url = request.form.get("repo_url", "").strip()
 
#     # Parse the repo owner/name from various input formats
#     owner, name = parse_repo_input(repo_url)
 
#     if not owner or not name:
#         return render_template(
#             "dashboard.html",
#             analysis=None,
#             repo=None,
#             error="Invalid repo. Try format: owner/repo or a GitHub URL",
#         )
 
#     cache_key = f"{owner}/{name}"
 
#     # Check cache first
#     if cache_key in cache:
#         print(f"📦 Using cached data for {cache_key}")
#         analysis = cache[cache_key]["analysis"]
#         repo_data = cache[cache_key]["repo_data"]
#     else:
#         # Fetch and analyze
#         repo_data = fetch_repo_data(owner, name, days_back=14)
#         analysis = analyze_repo(repo_data)
#         cache[cache_key] = {"repo_data": repo_data, "analysis": analysis}
 
#     return render_template(
#         "dashboard.html",
#         analysis=analysis,
#         repo=f"{owner}/{name}",
#         stats=repo_data["summary_stats"],
#     )

@app.route("/analyze", methods=["POST"])
def analyze():
    """Fetch and analyze a repo."""
    repo_url = request.form.get("repo_url", "").strip()
 
    owner, name = parse_repo_input(repo_url)
 
    if not owner or not name:
        return render_template(
            "dashboard.html",
            analysis=None,
            repo=None,
            error="Invalid repo. Try format: owner/repo or a GitHub URL",
        )
 
    cache_key = f"{owner}/{name}"
 
    if cache_key in cache:
        print(f"📦 Using cached data for {cache_key}")
        analysis = cache[cache_key]["analysis"]
        repo_data = cache[cache_key]["repo_data"]
    else:
        start = time.time()
 
        repo_data = fetch_repo_data(owner, name, days_back=14)
        print(f"⏱️  GitHub fetch: {time.time() - start:.1f}s")
 
        ai_start = time.time()
        analysis = analyze_repo(repo_data)
        print(f"⏱️  AI analysis: {time.time() - ai_start:.1f}s")
        print(f"⏱️  Total: {time.time() - start:.1f}s")
 
        cache[cache_key] = {"repo_data": repo_data, "analysis": analysis}
 
    return render_template(
        "dashboard.html",
        analysis=analysis,
        repo=f"{owner}/{name}",
        stats=repo_data["summary_stats"],
    )
 
 
def parse_repo_input(input_str):
    """
    Accept various formats:
    - owner/repo
    - https://github.com/owner/repo
    - github.com/owner/repo
    """
    input_str = input_str.strip().rstrip("/")
 
    # Remove github.com prefix if present
    if "github.com" in input_str:
        parts = input_str.split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
 
    # Try owner/repo format
    parts = input_str.split("/")
    if len(parts) == 2:
        return parts[0], parts[1]
 
    return None, None
 
 
if __name__ == "__main__":
    print("🚀 Starting Zero-Input PM Dashboard...")
    print("   Open http://localhost:5001 in your browser")
    app.run(debug=True, port=5001)