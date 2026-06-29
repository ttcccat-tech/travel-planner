#!/usr/bin/env python3
"""
enrich_details.py — 使用 Browser Use 批次補足 107 個景點的 details{}
每次處理完即寫入磁盤（斷點續傳）
"""
import json, time, re, os, sys, urllib.request, urllib.parse, subprocess
from pathlib import Path

REPO = Path("/var/repo/travel-planner")
ATTR_PATH = REPO / "data" / "osaka" / "attractions.json"
UA = "Mozilla/5.0"

def maps_url(name):
    q = urllib.parse.quote(f"{name} 大阪")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def yt_search_script(name):
    """用 hermes browser tool 搜 YouTube，返回 [{url,title}]"""
    q = urllib.parse.quote(f"{name} 大阪")
    return (
        f"https://www.youtube.com/results?search_query={q}"
    )

def blog_search_script(name):
    """部落格搜尋 URL"""
    q = urllib.parse.quote(f"{name} 大阪 遊記 部落格")
    return f"https://searxng.org/search?q={q}&format=json"

def do_blog_search(name):
    """用 searxng 找部落格文章"""
    q = urllib.parse.quote(f"{name} 大阪 遊記")
    for inst in ["https://searxng.org", "https://search.bus-hit.me"]:
        try:
            url = f"{inst}/search?q={q}&format=json&limit=8"
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                if r.status != 200:
                    continue
                data = json.loads(r.read().decode())
                results = []
                seen = set()
                skip = ["youtube.com","google.com","amazon.co.jp","jalan.net",
                        "rurubu.com","knt.co.jp","his-j.com","facebook.com",
                        "twitter.com","instagram.com","wikipedia.org"]
                for item in data.get("results", []):
                    link = item.get("url", "")
                    title = re.sub(r'<[^>]+>', '', item.get("title", ""))
                    if not link or link in seen or any(s in link for s in skip):
                        continue
                    seen.add(link)
                    results.append({"url": link, "title": title[:80]})
                    if len(results) >= 3:
                        break
                return results
        except Exception:
            continue
    return []

def load():
    return json.load(open(ATTR_PATH))

def save(data):
    with open(ATTR_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(ATTR_PATH, 0o644)

def main():
    data = load()
    attractions = data["attractions"]

    total = len(attractions)
    missing = [(i, a) for i, a in enumerate(attractions) if not a.get("details")]
    done = total - len(missing)
    print(f"總景點：{total}｜已有 details：{done}｜缺 details：{len(missing)}")

    # 每次處理的景點數（避免太久）
    BATCH = 107  # 全量跑

    for batch_start in range(0, len(missing), BATCH):
        batch = missing[batch_start:batch_start + BATCH]
        for pos, (idx, attr) in enumerate(batch):
            name = attr["name"]
            tag = f"[{idx+1}/{total}] {name}"
            print(f"\n{tag}")

            # ── 1. Google Maps ─────────────────────────
            gmap = maps_url(name)
            print(f"  Maps: OK")

            # ── 2. YouTube（需手動用 browser）──────────
            # YouTube URL 已就緒，等 browser tool 執行
            yt_url_str = yt_search_script(name)
            print(f"  YT: {yt_url_str}")

            # ── 3. 部落格（自動）──────────────────────
            print(f"  Blog 搜尋中...", end=" ", flush=True)
            blogs = do_blog_search(name)
            if blogs:
                for b in blogs:
                    print(f"\n    {b['title'][:60]}")
            else:
                print("⚠️ 無")
            time.sleep(0.6)

            # 寫入（YouTube 留空，等 browser 補）
            attractions[idx]["details"] = {
                "google_maps": gmap,
                "youtube": [],   # ← 待 browser 補
                "blog_article": blogs,
            }
            save(data)
            print(f"  ✅ 已寫入（{pos+1}/{len(batch)}）")

    print(f"\n完成 ✅  details 結構已就緒，請用 browser 補足 YouTube 欄位")
    save(data)

if __name__ == "__main__":
    main()
