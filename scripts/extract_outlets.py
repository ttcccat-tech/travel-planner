#!/usr/bin/env python3
"""
extract_outlets.py
從 attractions.json 分離出 outlets，寫入獨立的 outlets.json
"""

import json
import os

REGIONS = ["osaka", "fukuoka", "tokyo", "kyushu"]

for region in REGIONS:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", region)
    attr_path = os.path.join(base, "attractions.json")
    outlet_path = os.path.join(base, "outlets.json")

    with open(attr_path, encoding="utf-8") as f:
        data = json.load(f)

    attrs = data.get("attractions", data.get("data", []))

    outlets = []
    remaining = []

    for item in attrs:
        if item.get("category") == "outlet" or item.get("sub_category") == "outlet":
            outlet_entry = {
                "id": item.get("id", f"outlet_{region}_{len(outlets)+1:03d}"),
                "name": item["name"],
                "name_en": item.get("name_en"),
                "zone": item.get("zone", ""),
                "station_id": item.get("station_id"),
                "nearby_stations": item.get("nearby_stations", []),
                "details": item.get("details", {}),
                "tags": item.get("tags", []),
                "sources": item.get("sources", []),
                "priority": item.get("priority", 1)
            }
            # details 裡常見的 outlet 欄位
            if "fee" not in outlet_entry["details"]:
                outlet_entry["details"]["fee"] = "免費"
            if "stay_time" not in outlet_entry["details"]:
                outlet_entry["details"]["stay_time"] = "2-3小時"
            outlets.append(outlet_entry)
        else:
            remaining.append(item)

    # 寫入 outlets.json
    with open(outlet_path, "w", encoding="utf-8") as f:
        json.dump({"region": region, "outlets": outlets}, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {region}: {len(outlets)} 間 outlets → {outlet_path}")

    # 更新 attractions.json（移除 outlets）
    data["attractions"] = remaining
    with open(attr_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {region}: attractions.json 更新（移除 {len(outlets)} 間 outlets）")

print("\n完成！outlets 已從 attractions 分離。")
