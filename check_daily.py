"""Check if a LeetCode user solved today's daily problem; email a reminder if not.

Uses only the Python standard library. Config comes from environment variables:
  LEETCODE_USERNAME, SMTP_USER, SMTP_PASSWORD, TO_EMAIL
Optional: SMTP_HOST (default smtp.gmail.com), SMTP_PORT (default 465)
"""
import json
import os
import smtplib
import sys
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage

GRAPHQL_URL = "https://leetcode.com/graphql"


def graphql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def get_daily():
    q = "query { activeDailyCodingChallengeQuestion { date link question { title titleSlug } } }"
    return graphql(q)["activeDailyCodingChallengeQuestion"]


def solved_today(username, slug, daily_date):
    q = """query($u: String!, $l: Int!) {
      recentAcSubmissionList(username: $u, limit: $l) { titleSlug timestamp }
    }"""
    subs = graphql(q, {"u": username, "l": 20})["recentAcSubmissionList"] or []
    # Daily problem resets at 00:00 UTC; only count accepted submissions made on that UTC date.
    day_start = datetime.strptime(daily_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    return any(s["titleSlug"] == slug and int(s["timestamp"]) >= day_start for s in subs)


def send_email(subject, text):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]
    msg.set_content(text)
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    with smtplib.SMTP_SSL(host, port) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        s.send_message(msg)


def main():
    username = os.environ["LEETCODE_USERNAME"]
    daily = get_daily()
    title = daily["question"]["title"]
    slug = daily["question"]["titleSlug"]
    link = "https://leetcode.com" + daily["link"]

    if solved_today(username, slug, daily["date"]):
        print(f"{username} already solved today's daily: {title}. No email sent.")
        return

    send_email(
        f"LeetCode reminder: daily problem not solved ({daily['date']})",
        f"Hi,\n\n{username} has not solved today's LeetCode daily problem yet.\n\n"
        f"Problem: {title}\nLink: {link}\n\nThe daily problem resets at 00:00 UTC.\n",
    )
    print(f"{username} has not solved {title}. Reminder email sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
