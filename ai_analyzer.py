import os
import json
from dotenv import load_dotenv
from openai import OpenAI
 
load_dotenv()
 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
# SYSTEM_PROMPT = """You are an expert PM assistant that analyzes GitHub repository 
# activity and produces clear, actionable project status reports.
 
# You will receive raw GitHub data (commits, pull requests, issues) for a time period.
 
# Your job:
# 1. Group related activities into workstreams/features
# 2. Identify what SHIPPED (merged PRs), what's IN PROGRESS (open PRs), what's BLOCKED
# 3. Flag risks: stale PRs (open > 3 days with no review), idle contributors, 
#    review bottlenecks, unresolved review comments
# 4. Summarize each person's contributions
# 5. Give an overall project health assessment
 
# Rules:
# - Be SPECIFIC. Use real names, PR numbers, actual details from the data.
# - DON'T hallucinate or make up information not in the data.
# - Keep it concise and scannable.
# - Flag actionable risks with suggested next steps.
 
# Respond in this exact JSON format:
# {
#     "health": "green|yellow|red",
#     "health_reason": "One sentence explaining the health status",
#     "executive_summary": "2-3 sentence high-level summary of the project",
#     "shipped": [
#         {
#             "title": "What was shipped",
#             "pr_number": 123,
#             "author": "username",
#             "detail": "Brief description of what this does"
#         }
#     ],
#     "in_progress": [
#         {
#             "title": "What's being worked on",
#             "pr_number": 123,
#             "author": "username",
#             "detail": "Brief status",
#             "status": "on_track|needs_attention|blocked"
#         }
#     ],
#     "risks": [
#         {
#             "type": "stale_pr|blocked|no_activity|review_bottleneck|scope_concern",
#             "title": "Short risk title",
#             "description": "What's the issue",
#             "suggested_action": "What should be done"
#         }
#     ],
#     "team_activity": [
#         {
#             "person": "username",
#             "commits": 5,
#             "prs_opened": 1,
#             "prs_merged": 1,
#             "summary": "Brief description of what they focused on"
#         }
#     ],
#     "key_decisions": [
#         "Any notable decisions or changes visible from PR descriptions/comments"
#     ]
# }"""

SYSTEM_PROMPT = """Analyze GitHub activity and produce a project status report as JSON.

Be specific. Use real names and PR numbers. Don't hallucinate.

JSON format:
{
    "health": "green|yellow|red",
    "health_reason": "one sentence",
    "executive_summary": "2-3 sentences",
    "shipped": [{"title": "", "pr_number": 0, "author": "", "detail": ""}],
    "in_progress": [{"title": "", "pr_number": 0, "author": "", "detail": "", "status": "on_track|needs_attention|blocked"}],
    "risks": [{"type": "", "title": "", "description": "", "suggested_action": ""}],
    "team_activity": [{"person": "", "commits": 0, "prs_opened": 0, "prs_merged": 0, "summary": ""}],
    "key_decisions": [""]
}"""
 
 
def analyze_repo(repo_data):
    """
    Takes raw GitHub repo data and returns AI-generated analysis.
    """
    print("🤖 Analyzing repository activity...")
 
    # Prepare the data for the LLM (trim to stay within token limits)
    trimmed_data = prepare_data_for_llm(repo_data)
 
    try:
        response = client.chat.completions.create(
            #model="gpt-4o-mini",  # Good balance of quality and speed/cost
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Repo: {repo_data['repo']}\nPeriod: {repo_data['period']}\n\n{json.dumps(trimmed_data)}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower = more consistent/factual
        )
 
        result = json.loads(response.choices[0].message.content)
        print("✅ Analysis complete!")
        return result
 
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return generate_fallback_analysis(repo_data)
 
 
def prepare_data_for_llm(repo_data):
    """Trim data to minimum needed for good analysis."""
    return {
        "summary_stats": repo_data["summary_stats"],
        "commits": [
            {
                "author": c["author_github"],
                "message": c["message"][:80],
                "date": c["date"][:10],  # Just the date, not full timestamp
            }
            for c in repo_data["commits"][:30]
        ],
        "pull_requests": [
            {
                "number": pr["number"],
                "title": pr["title"],
                "author": pr["author"],
                "state": pr["state"],
                "merged": pr["merged"],
                "created_at": pr["created_at"][:10],
                "labels": pr["labels"],
                "comments": pr["comments"],
            }
            for pr in repo_data["pull_requests"][:20]
        ],
        "issues": [
            {
                "number": i["number"],
                "title": i["title"],
                "state": i["state"],
                "labels": i["labels"],
                "assignee": i["assignee"],
            }
            for i in repo_data["issues"][:15]
        ],
    }
 
 
def generate_fallback_analysis(repo_data):
    """
    If the AI call fails, generate a basic analysis from raw data.
    """
    merged_prs = [pr for pr in repo_data["pull_requests"] if pr["merged"]]
    open_prs = [pr for pr in repo_data["pull_requests"] if pr["state"] == "open"]
 
    return {
        "health": "yellow",
        "health_reason": "AI analysis unavailable — showing raw data summary",
        "executive_summary": f"Found {len(repo_data['commits'])} commits, {len(merged_prs)} merged PRs, and {len(open_prs)} open PRs.",
        "shipped": [
            {
                "title": pr["title"],
                "pr_number": pr["number"],
                "author": pr["author"],
                "detail": "Merged",
            }
            for pr in merged_prs[:10]
        ],
        "in_progress": [
            {
                "title": pr["title"],
                "pr_number": pr["number"],
                "author": pr["author"],
                "detail": f"{pr['comments']} comments",
                "status": "needs_attention",
            }
            for pr in open_prs[:10]
        ],
        "risks": [],
        "team_activity": [],
        "key_decisions": [],
    }
 
 
# ---- Test it! ----
if __name__ == "__main__":
    from github_client import fetch_repo_data
 
    # Fetch data
    data = fetch_repo_data("facebook", "react", days_back=7)
 
    # Analyze it
    analysis = analyze_repo(data)
 
    # Pretty print the result
    print("\n" + "=" * 60)
    print("📊 PROJECT STATUS REPORT")
    print("=" * 60)
 
    health_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    print(f"\nHealth: {health_emoji.get(analysis['health'], '⚪')} {analysis['health'].upper()}")
    print(f"Reason: {analysis['health_reason']}")
    print(f"\n📋 Summary: {analysis['executive_summary']}")
 
    print(f"\n✅ SHIPPED ({len(analysis['shipped'])} items):")
    for item in analysis["shipped"]:
        print(f"   • #{item['pr_number']} {item['title']} — {item['author']}")
 
    print(f"\n🔨 IN PROGRESS ({len(analysis['in_progress'])} items):")
    for item in analysis["in_progress"]:
        status_emoji = {"on_track": "🟢", "needs_attention": "🟡", "blocked": "🔴"}
        print(f"   {status_emoji.get(item['status'], '⚪')} #{item['pr_number']} {item['title']} — {item['author']}")
 
    print(f"\n🚨 RISKS ({len(analysis['risks'])} items):")
    for risk in analysis["risks"]:
        print(f"   ⚠️  {risk['title']}")
        print(f"      {risk['description']}")
        print(f"      → {risk['suggested_action']}")
 
    print(f"\n👥 TEAM:")
    for person in analysis["team_activity"]:
        print(f"   {person['person']}: {person['commits']} commits — {person['summary']}")