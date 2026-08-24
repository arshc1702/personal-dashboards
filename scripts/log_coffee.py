"""
Parses a coffee-log GitHub Issue (opened via .github/ISSUE_TEMPLATE/coffee-log.yml),
prepends the entry to data/coffee.json (newest first), and closes the issue.

Reads the issue payload from GITHUB_EVENT_PATH rather than a raw env var — issue
bodies can contain characters that break shell escaping.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

EVENT_PATH = os.environ["GITHUB_EVENT_PATH"]
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
DATA_PATH = "data/coffee.json"

with open(EVENT_PATH) as f:
    event = json.load(f)

issue = event["issue"]
body = issue["body"] or ""
number = issue["number"]


def field(label):
    pattern = rf"### {re.escape(label)}\s*\n+(.*?)(?=\n### |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    if not m:
        return ""
    value = m.group(1).strip()
    return "" if value == "_No response_" else value


rating_raw = field("Rating")
try:
    rating = int(rating_raw)
except ValueError:
    rating = None

entry = {
    "id": number,
    "date": datetime.now(timezone.utc).isoformat(),
    "bean": field("Bean / Roaster"),
    "origin": field("Origin"),
    "method": field("Brew Method"),
    "rating": rating,
    "notes": field("Notes"),
}

try:
    with open(DATA_PATH) as f:
        entries = json.load(f)
except FileNotFoundError:
    entries = []

entries.insert(0, entry)

with open(DATA_PATH, "w") as f:
    json.dump(entries, f, indent=2)

print("Logged coffee entry:", entry)

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/issues/{number}",
    method="PATCH",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "panel-bot",
    },
    data=json.dumps({"state": "closed"}).encode(),
)
urllib.request.urlopen(req, timeout=15)
