#!/usr/bin/env python3
"""
Travel Planner Attractions Updater
Weekly update: 周一福岡 → 周二大阪 → 周三東京 → 周四九州

Enriches each attraction with:
  1. blog_article  ← already in sources[], just copy over
  2. google_maps   ← web search for each attraction name + "Google Maps"
  3. youtube        ← web search for each attraction name + "YouTube"
"""
import subprocess, json, os, sys, re, time, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
REPO        = Path("/var/repo/travel-planner")
REGION      = os.environ.get("REGION", "fukuoka")   # set via cron env
PORT        = 8080
GITHUB_REPO = "https://github.com/ttcccat-tech/travel-planner.git"
# ─────────────────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}][{REGION}] {msg}", flush=True)

def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if check and r.returncode != 0:
        log(f"FAIL: {cmd}  →  {r.stderr[:200]}")
        sys.exit(1)
    return r.stdout.strip()

def search_google_maps(query):
    """Return a google_maps embed URL for a place."""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/maps/search/?api=1&query={encoded}"
        # Validate URL is reachable
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return url
    except Exception:
        pass
    return None

def search_youtube(query):
    """Return a YouTube search URL for a place."""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return url
    except Exception:
        pass
    return None

def build_attraction_url(name, search_fn, base_url_template):
    """Generic search helper: try name first, then name + city/region."""
    candidates = [
        f"{name} {REGION.capitalize()}",
        name,
    ]
    for q in candidates:
        result = search_fn(q)
        if result:
            return result
        time.sleep(0.5)   # be polite to servers
    return None

def load_attractions(region):
    path = REPO / "data" / region / "attractions.json"
    with open(path) as f:
        return json.load(f), path

def save_attractions(data, path):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Ensure permissions
    os.chmod(path, 0o644)

def enrich(data):
    """
    Enrich all attractions in data['attractions']:
      - blog_article ← copy from sources[0] if available
      - google_maps  ← web search
      - youtube      ← web search
    Returns (enriched_count, total_count).
    """
    attrs = data.get("attractions", data)
    enriched = 0
    total = len(attrs)

    for a in attrs:
        details = a.setdefault("details", {})
        sources = a.get("sources", [])

        changed = False

        # 1. blog_article from sources
        if not details.get("blog_article") and sources:
            details["blog_article"] = sources[0]
            changed = True

        # 2. google_maps
        if not details.get("google_maps"):
            name = a.get("name", "")
            url = build_attraction_url(name, search_google_maps,
                                       "https://www.google.com/maps/search/?api=1&query={q}")
            if url:
                details["google_maps"] = url
                changed = True
                log(f"  + google_maps: {name}")
            time.sleep(0.3)

        # 3. youtube
        if not details.get("youtube"):
            name = a.get("name", "")
            url = build_attraction_url(name, search_youtube,
                                       "https://www.youtube.com/results?search_query={q}")
            if url:
                details["youtube"] = url
                changed = True
                log(f"  + youtube: {name}")
            time.sleep(0.3)

        if changed:
            enriched += 1

    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    return enriched, total

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    log(f"=== Starting {REGION} weekly update ===")

    # 1. Git pull latest
    log("Pulling latest from git...")
    run("git pull origin main", check=False)

    # 2. Load attractions
    data, path = load_attractions(REGION)
    attrs = data.get("attractions", data)
    log(f"Loaded {len(attrs)} attractions")

    # 3. Enrich
    enriched, total = enrich(data)
    log(f"Enriched {enriched}/{total} attractions")

    # 4. Save
    save_attractions(data, path)
    log(f"Saved to {path}")

    # 5. Fix permissions
    run(f"find {REPO}/data -type f -exec chmod 644 {{}} \;")
    run(f"find {REPO}/data -type d -exec chmod 755 {{}} \;")
    log("Permissions fixed")

    # 6. Rebuild container
    log("Rebuilding container (no cache)...")
    run("docker-compose build --no-cache", check=False)
    run("docker-compose up -d", check=False)
    log("Container rebuilt")

    # 7. Health check
    try:
        url = f"http://localhost:{PORT}/data/{REGION}/attractions.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                log(f"Health check OK → {url}")
            else:
                log(f"Health check WARN: status {resp.status}")
    except Exception as e:
        log(f"Health check FAIL: {e}")
        sys.exit(1)

    # 8. Git commit & push if changed
    log("Checking for changes to commit...")
    diff = run("git diff --stat", check=False)
    if diff and diff.strip():
        log(f"Changes detected:\n{diff}")
        run("git add -A")
        date_str = datetime.now().strftime("%Y-%m-%d")
        run(f'git commit -m "chore: weekly {REGION} enrichment {date_str}"')
        run("git push origin main", check=False)
        log("Pushed to GitHub")
    else:
        log("No changes — nothing to commit")

    log(f"=== {REGION} update complete ===")

if __name__ == "__main__":
    main()
