#!/usr/bin/env python3
"""
link_attractions_to_stations.py
自動為 attractions.json 的每個景點對接最近車站（station_id）

邏輯：
1. 讀取 attractions.json 與 stations.json
2. 用 zone 名稱匹配（ attraction.zone == station.zone）
3. 若多個車站同 zone → 取半徑 800m 內最近的
4. 匹配成功 → 寫入 station_id + nearby_stations[]
5. 匹配失敗 → station_id: null（慢慢補）
"""

import json
import math
import os
import sys

# ---------- 工具函數 ----------
def haversine(lat1, lon1, lat2, lon2):
    """計算兩點直線距離（公尺）"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fuzzy_match(text, keyword, threshold=0.6):
    """簡單模糊比對：keyword 是否出現在 text 裡（包含關鍵字）"""
    text = text.lower().replace(" ", "").replace("・", "").replace("（", "").replace("）", "")
    keyword = keyword.lower().replace(" ", "").replace("・", "").replace("（", "").replace("）", "")
    return keyword in text or text in keyword


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  寫入：{path}")


# ---------- 匹配函數 ----------
def find_nearest_stations(attraction_zone, attraction_lat, attraction_lng, stations, radius_m=800):
    """為單一景點找最近車站，回傳 (best_station_id, all_nearby_ids)"""

    candidates = []

    for station in stations:
        if not station.get("active", True):
            continue
        if not station.get("lat") or not station.get("lng"):
            continue

        # zone 精確匹配
        zone_match = attraction_zone == station.get("zone", "")

        # 若有座標 → 計算距離
        if attraction_lat and attraction_lng:
            dist = haversine(attraction_lat, attraction_lng, station["lat"], station["lng"])
        else:
            dist = 999999  # 無座標就當很遠

        in_radius = dist <= radius_m

        score = 0
        if zone_match:
            score += 100
        if in_radius:
            score += 50
        score -= dist / 100  # 距離越近分數越高

        candidates.append({
            "station": station,
            "dist": dist,
            "score": score,
            "zone_match": zone_match,
            "in_radius": in_radius
        })

    # 依分數排序
    candidates.sort(key=lambda x: -x["score"])

    if not candidates:
        return None, []

    best = candidates[0]["station"]["id"]
    nearby = [c["station"]["id"] for c in candidates if c.get("in_radius") or c.get("zone_match")][:5]

    return best, nearby


def process_region(region):
    """處理單一地區"""
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", region)

    attractions_path = os.path.join(base_dir, "attractions.json")
    stations_path = os.path.join(base_dir, "stations.json")
    outlets_path = os.path.join(base_dir, "outlets.json")

    if not os.path.exists(stations_path):
        print(f"  ⚠️  {region}: stations.json 不存在，跳過")
        return

    attractions_data = load_json(attractions_path)
    stations_data = load_json(stations_path)

    # 支援 outlets.json（可選）
    outlets_data = {"outlets": []}
    if os.path.exists(outlets_path):
        outlets_data = load_json(outlets_path)

    stations = stations_data.get("stations", [])

    # 建立 station zone → id 索引
    zone_to_stations = {}
    for s in stations:
        z = s.get("zone", "")
        if z not in zone_to_stations:
            zone_to_stations[z] = []
        zone_to_stations[z].append(s)

    def link_item(item, item_type="attraction"):
        """為單一項目填 station_id"""
        zone = item.get("zone", "")
        lat = item.get("lat") or item.get("details", {}).get("lat")
        lng = item.get("lng") or item.get("details", {}).get("lng")

        best_id, nearby_ids = find_nearest_stations(zone, lat, lng, stations)

        # 嘗試用 name 模糊匹配
        if not best_id:
            for s in stations:
                if fuzzy_match(item.get("name", ""), s.get("name", "")):
                    best_id = s["id"]
                    nearby_ids = [best_id]
                    break

        old_sid = item.get("station_id")
        item["station_id"] = best_id
        item["nearby_stations"] = nearby_ids if nearby_ids else []

        # 清除 null 欄位
        if item["nearby_stations"] and None in item["nearby_stations"]:
            item["nearby_stations"] = [x for x in item["nearby_stations"] if x]

        changed = old_sid != best_id
        status = "✅" if best_id else "⚠️ "
        action = "link" if changed else "skip"
        return status, action, best_id

    # ---- 處理 attractions ----
    attrs = attractions_data.get("attractions", attractions_data.get("data", []))
    results = {"linked": 0, "skipped": 0, "unlinked": 0}

    for item in attrs:
        status, action, sid = link_item(item)
        if status == "✅":
            results["linked"] += 1
            print(f"  {status} {item['name']} → {sid}")
        elif status == "⚠️ ":
            results["unlinked"] += 1
            print(f"  {status} {item['name']} (無車站)")
        else:
            results["skipped"] += 1

    # ---- 處理 outlets ----
    for item in outlets_data.get("outlets", []):
        status, action, sid = link_item(item, "outlet")
        if status == "✅":
            print(f"  {status} [outlet] {item['name']} → {sid}")
        elif status == "⚠️ ":
            print(f"  {status} [outlet] {item['name']} (無車站)")

    # ---- 寫回 ----
    save_json(attractions_path, attractions_data)
    if outlets_data.get("outlets"):
        save_json(outlets_path, outlets_data)

    total = len(attrs)
    print(f"\n  📊 {region}: {results['linked']}/{total} 景點已對接車站，{results['unlinked']} 個未匹配")
    return results


def main():
    regions = ["osaka", "fukuoka", "tokyo", "kyushu"]
    all_results = {}

    for region in regions:
        print(f"\n{'='*50}")
        print(f"處理地區：{region.upper()}")
        print(f"{'='*50}")
        all_results[region] = process_region(region)

    # 總結
    print(f"\n{'='*50}")
    print("全部地區完成")
    print(f"{'='*50}")
    for region, res in all_results.items():
        if res:
            print(f"  {region}: {res['linked']} 已對接, {res['unlinked']} 未匹配")


if __name__ == "__main__":
    main()
