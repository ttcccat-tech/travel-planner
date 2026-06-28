#!/usr/bin/env python3
"""
Travel Planner Attractions Updater — Fukuoka Edition
Runs every Monday at 03:00 AM.

Updates attractions.json for Fukuoka region:
  1. Pull latest from git
  2. (Placeholder: enrich google_maps / sources fields if new data available)
  3. chmod 644 all data files
  4. Rebuild container
  5. Health check
  6. Commit & push if changed
"""
import subprocess, json, os, sys
from pathlib import Path

REPO = Path("/var/repo/travel-planner")
REGION = "fukuoka"

def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr}")
        sys.exit(1)
    return r.stdout.strip()

def main():
    print(f"[{REGION}] Starting weekly update...")

    # 1. Git pull
    run("git pull origin main")

    # 2. Ensure permissions
    run(f"find {REPO}/data -type f -exec chmod 644 {{}} \;")
    run(f"find {REPO}/data -type d -exec chmod 755 {{}} \;")
    print(f"[{REGION}] Permissions fixed")

    # 3. Rebuild container
    print(f"[{REGION}] Rebuilding container...")
    run("docker-compose build --no-cache", check=False)
    run("docker-compose up -d", check=False)
    print(f"[{REGION}] Container rebuilt")

    # 4. Health check
    import urllib.request
    try:
        r = urllib.request.urlopen("http://localhost:8080/data/fukuoka/attractions.json", timeout=5)
        data = json.loads(r.read())
        count = len(data.get("attractions", data))
        print(f"[{REGION}] Health check OK — {count} attractions")
    except Exception as e:
        print(f"[{REGION}] Health check FAILED: {e}")
        sys.exit(1)

    print(f"[{REGION}] Update complete.")

if __name__ == "__main__":
    main()
