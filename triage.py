import os
import requests
import json

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

with open(os.environ["GITHUB_EVENT_PATH"]) as f:
    event = json.load(f)

issue = event["issue"]
title = issue["title"]
body = issue["body"] or ""
issue_number = issue["number"]
repo = event["repository"]["full_name"]

prompt = f"""
You are a GitHub issue classifier.

Classify into:
- bug
- feature
- question

Also assign priority: low, medium, high

Return ONLY JSON:
{{
 "label": "...",
 "priority": "..."
}}

Title: {title}
Body: {body}
"""

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    },
)

result = response.json()

content = result["choices"][0]["message"]["content"]

data = json.loads(content)

label = data["label"]
priority = data["priority"]

url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"

requests.post(
    url,
    headers={"Authorization": f"token {GITHUB_TOKEN}"},
    json={"labels": [label, f"priority:{priority}"]},
)