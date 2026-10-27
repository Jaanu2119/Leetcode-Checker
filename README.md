# Leetcode-Checker

Checks once a day whether a LeetCode user solved the daily problem. If not, sends one reminder email.

Runs free on GitHub Actions (`.github/workflows/daily-check.yml`, daily at 18:17 UTC). Python standard library only.

## Setup
1. Gmail: turn on 2-Step Verification, create an App Password at https://myaccount.google.com/apppasswords
2. Repo → Settings → Secrets and variables → Actions → add:
   - `LEETCODE_USERNAME` – account to check
   - `SMTP_USER` – Gmail address
   - `SMTP_PASSWORD` – 16-char App Password
   - `TO_EMAIL` – reminder recipient
3. Actions tab → "LeetCode daily check" → Run workflow (test).

Note: scheduled workflows in public repos are disabled after 60 days without repo activity; re-enable from the Actions tab.
