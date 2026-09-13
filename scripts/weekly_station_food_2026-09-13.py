#!/usr/bin/env python3
"""
每週車站美食掃描任務 — 2026-09-13
對 6 地區精選車站搜尋美食店家，寫入 SQLite meals 表。
"""

import sqlite3
import json
import uuid
import sys
import os
from datetime import datetime

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

# ============================================================
# 大站候選美食（每站最多取 3 筆，避免重複）
#格式：(名稱, URL, sub_category, zone, description, ticket)
# ============================================================

SEOUL_STATIONS = ["seoul_001", "seoul_004", "seoul_016", "seoul_029", "seoul_012"]

MEALS_CANDIDATES = {
    "seoul_001": [
        ("厚肉", "https://www.kkday.com/zh-hk/blog/101575/seoul-station-food", "烤肉",
         "首爾站", "超人氣五花肉專門店，厚切鮮嫩多汁，專人代烤", "₩14,000~"),
        ("兔子停 奶油咖喱烏冬", "https://www.kkday.com/zh-hk/blog/101575/seoul-station-food", "餐廳",
         "首爾站", "弘大超人氣餐廳，奶油咖喱烏冬超邪惡，附中文菜單", "₩10,000~₩20,000"),
        ("龍山元祖馬鈴薯排骨湯", "https://www.kkday.com/zh-hk/blog/101575/seoul-station-food", "湯飯",
         "龍山", "24小時營業，經營二十多年，辣味馬鈴薯排骨湯最受歡迎", "₩8,000~₩40,000"),
    ],
    "seoul_004": [
        ("辣炒年糕商會", "https://nnyy.tw/seoul-tasty-food", "小吃",
         "弘大", "布帳馬車風格，橘醬雞肉辣炒年糕必點，CP值超高", "₩8,000~"),
        ("連陞烤肉", "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026", "烤肉",
         "弘大", "在地人推薦隱藏版烤肉名店，Google評分4.6", "₩14,000"),
        ("弘大帳篷小吃攤", "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026", "小吃",
         "弘大", "最道地韓國深夜美食體驗，海鮮煎餅配真露", "₩15,000"),
    ],
    "seoul_016": [
        ("明洞餃子", "https://nnyy.tw/seoul-tasty-food", "小吃",
         "明洞", "近60年歷史，米芝蓮推薦，刀削麵+餃子必點", "₩10,000~"),
        ("神仙雪濃湯", "https://nnyy.tw/seoul-tasty-food", "湯飯",
         "明洞", "24小時營業，牛骨熬十幾小時，清爽回甘", "₩12,000"),
        ("荒謬的生肉", "https://nnyy.tw/seoul-tasty-food", "烤肉",
         "明洞", "豬五花吃到飽，₩400台幣CP值極高", "₩400台幣/人"),
    ],
    "seoul_029": [
        ("陳玉華奶奶元祖一隻雞", "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026", "湯飯",
         "東大門", "蒜味雞湯超濃郁，軟嫩入味，營業至凌晨1點", "₩25,000/鍋"),
        ("橋村炸雞", "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026", "小吃",
         "東大門", "蜂蜜醬油炸雞經典，營業到凌晨", "₩20,000"),
        ("順美家幸福醬蟹", "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026", "海鮮",
         "東大門", "醬油蟹專門店，無腥味鮮甜，拌飯最對味", "₩15,000~"),
    ],
    "seoul_012": [
        ("滿足五香豬腳", "https://tchinese.seoul.go.kr", "小吃",
         "市廳", "2025百大首爾美食，豬腳香 Q 彈不油膩", "₩20,000~"),
        ("儒林麵館", "https://tchinese.seoul.go.kr", "麵類",
         "市廳", "2025百大首爾美食，蕎麥麵傳統老店", "₩10,000~"),
        ("光化門湯飯", "https://tchinese.seoul.go.kr", "湯飯",
         "光化門", "2025百大首爾美食，豬肉湯飯", "₩10,000~"),
    ],

    # BUSAN
    "busan_001": [
        ("安木豬肉湯飯", "https://lilytogo.com/busan-anmok", "湯飯",
         "釜山站", "2025米其林推薦，豬骨熬24小時以上，自助點餐機", "₩10,000~"),
        ("李在模披薩 釜山站店", "https://ginatw.com/leejaemo-pizza-busan", "餐廳",
         "釜山站", "釜山站7號出口出來就到，起司牽絲超邪惡", "₩10,000~"),
        ("大海鮑魚粥 釜山站店", "https://helena.tw/badamaru-busan-station", "海鮮",
         "草梁站", "現蒸大顆鮑魚，當天處理活鮑魚熬製濃稠粥", "₩13,000"),
    ],
    "busan_005": [
        ("味贊王鹽烤肉", "https://alinalife.tw/busan-food", "烤肉",
         "西面站", "釜山必吃鹽烤豬五花肉，桌邊代烤服務", "₩20,000~"),
        ("百年鐵鍋炸雞", "https://alinalife.tw/busan-food", "小吃",
         "西面站", "傳統市場炸全雞，外酥內嫩", "₩15,000~"),
        ("EGG DROP 釜山西面店", "https://alinalife.tw/busan-food", "小吃",
         "西面站", "超人氣早餐三明治，蛋香濃份量多", "₩5,000~"),
    ],
    "busan_003": [
        ("水營本家豬肉湯飯", "https://www.styletc.com/article/410576", "湯飯",
         "南浦洞", "24小時營業，豬肉湯飯經典老店", "₩10,000"),
        ("BIFF廣場黑糖餅", "https://alinalife.tw/busan-food", "小吃",
         "南浦洞", "釜山必吃傳統小吃，堅果黑糖餅", "₩2,000"),
        ("李在模披薩 本店", "https://ginatw.com/leejaemo-pizza-busan", "餐廳",
         "南浦洞", "在地30年人氣披薩，起司超多", "₩10,000~"),
    ],
    "busan_008": [
        ("海雲台五福豬肉湯飯", "https://cc2kitchen.com/busanfoodie", "湯飯",
         "海雲台", "24小時營業，豬頸肉湯飯份量足", "₩13,000"),
        ("密陽血腸豬肉湯飯", "https://cc2kitchen.com/busanfoodie", "湯飯",
         "海雲台", "2026更新，SJ始源也來吃過的知名老店", "₩10,000~"),
        ("Centum City 食堂3選", "https://cc2kitchen.com/busanfoodie", "餐廳",
         "Centum City", "新興美食廣場，多樣化選擇", "₩10,000~"),
    ],
    "busan_010": [
        ("彥陽家燒肉", "https://cc2kitchen.com/busanfoodie", "烤肉",
         "金蓮山站", "米其林推薦，韓牛代烤服務，玄彬也造訪", "₩30,000~"),
        ("廣安里 All Sunday Bagel", "https://cc2kitchen.com/busanfoodie", "咖啡",
         "廣安里", "超人氣貝果專門店，早8點就排隊", "₩3,000~"),
        ("廣安里83獬豬燒肉", "https://cc2kitchen.com/busanfoodie", "烤肉",
         "廣安里", "肉質好價格公道，服務優", "₩25,000~"),
    ],

    # FUKUOKA
    "fukuoka_001": [
        ("博多魚河岸 壽司", "https://peikie.com/uougashi", "壽司",
         "博多站", "博多站B1出站1分鐘，60種以上壽司現做", "₩1,000~/貫"),
        ("博多一味屋 牛腸鍋", "https://tasting-japan.com/archives/6212", "火鍋",
         "中洲川端站", "職人牛雜鍋，膠原蛋白滿滿", "₩3,000~"),
        ("笑門 居酒屋", "https://kyushu.letsgojp.com/archives/663526", "居酒屋",
         "博多站", "離車站30秒，明太子、活烏賊、牛腸鍋", "₩2,000~"),
    ],
    "fukuoka_003": [
        ("一幸舍 拉麵", "https://tw.wamazing.com/media/article/a-3407", "拉麵",
         "祇園站", "博多豚骨拉麵代表，等地旅客大排長龍", "₩800~"),
        ("JR博多城 美食", "https://tw.wamazing.com/media/article/a-3407", "餐廳",
         "博多站", "與博多站直結，AMU PLAZA博多美食街", "₩1,000~"),
        ("DEITOSANNEX 小幸拉麵", "https://tw.wamazing.com/media/article/a-3407", "拉麵",
         "筑紫口", "2024年新開幕，拉麵、長崎強棒麵", "₩800~"),
    ],

    # OSAKA
    "osaka_001": [
        ("北極星蛋包飯", "https://marukojp.com/article/osaka-food", "餐廳",
         "心齋橋", "關西蛋包飯創始店，滑嫩蛋皮與番茄炒飯經典", "₩1,500~"),
        ("甲賀流章魚燒", "https://marukojp.com/article/osaka-food", "小吃",
         "心齋橋", "米其林必比登推薦，外酥內軟", "₩500~₩700"),
        ("PABLO 半熟起司蛋糕", "https://marukojp.com/article/osaka-food", "甜點",
         "心齋橋", "大阪發跡人氣甜點，爆漿起司蛋糕", "₩300~₩1,000"),
    ],
    "osaka_004": [
        ("達摩串炸", "https://bobbytravel.tw/osaka-food", "小吃",
         "道頓堀", "大阪百年靈魂美食，炸物配秘傳醬汁", "₩500~"),
        ("蟹道樂", "https://bobbytravel.tw/osaka-food", "海鮮",
         "道頓堀", "大阪螃蟹料理代表，松葉蟹鮮甜", "₩5,000~"),
        ("一蘭拉麵", "https://bobbytravel.tw/osaka-food", "拉麵",
         "道頓堀", "個人獨立座位，浓厚豚骨湯頭", "₩1,000~"),
    ],
    "osaka_007": [
        ("味乃家御好燒", "https://bobbytravel.tw/osaka-food", "大阪燒",
         "難波", "1965年創業，連米其林都推薦", "₩2,000~₩4,000"),
        ("自由軒咖哩飯", "https://bobbytravel.tw/osaka-food", "咖哩",
         "難波", "百年歷史，獨創拌飯式咖哩+生蛋", "₩1,000~"),
        ("串之坊", "https://bobbytravel.tw/osaka-food", "小吃",
         "難波", "大阪串炸代表之一，現炸外酥脆", "₩500~"),
    ],

    # TOKYO
    "tokyo_001": [
        ("六厘舎沾麵", "https://goodxssss.com/zh-cn/tokyo-station-food-guide-best-restaurants-cn", "拉麵",
         "東京站", "東京車站一番街，浓厚豚骨魚介湯頭", "₩1,000~"),
        ("斑鳩拉麵", "https://goodxssss.com/zh-cn/tokyo-station-food-guide-best-restaurants-cn", "拉麵",
         "東京站", "東京車站一番街，豚骨魚介名店", "₩1,000~"),
        ("極味や", "https://goodxssss.com/zh-cn/tokyo-station-food-guide-best-restaurants-cn", "烤肉",
         "東京站", "職人代烤，可近距離欣賞技巧", "₩2,000~"),
    ],
    "tokyo_003": [
        ("六歌仙燒肉", "https://djbcard.com/tokyofood", "烤肉",
         "新宿", "和牛燒肉吃到飽，Tripadvisor新宿第一名", "₩6,000~"),
        ("牛舌の檸檬", "https://djbcard.com/tokyofood", "燒肉",
         "新宿", "極厚切牛舌專門，厚實彈牙", "₩3,000~"),
        ("豚珍館炸豬排", "https://djbcard.com/tokyofood", "小吃",
         "新宿", "厚實份量大，口感軟嫩不乾柴", "₩1,000~"),
    ],
    "tokyo_005": [
        ("入鹿拉麵 Iruca Tokyo", "https://djbcard.com/tokyofood", "拉麵",
         "六本木", "米其林必比登，牛肝菌醬油拉麵", "₩1,500~"),
        ("阿夫利柚子鹽拉麵", "https://djbcard.com/tokyofood", "拉麵",
         "新宿/原宿", "淡麗系拉麵代表，柚子清香", "₩1,000~"),
        ("叙叙苑", "https://djbcard.com/tokyofood", "烤肉",
         "晴空塔/銀座", "高空景觀燒肉，和牛高级", "₩5,000~"),
    ],

    # OKINAWA
    "okinawa_001": [
        ("豬肉蛋飯糰 那霸機場店", "https://adontrip.com/blog/71638", "小吃",
         "那霸機場", "沖繩必吃，現做飯糰，炸蝦口味超人氣", "¥600"),
        ("A&W 那霸機場店", "https://ajunfun.tw/naha-airport", "小吃",
         "那霸機場", "日本唯一沖繩限定，Root Beer+捲捲薯條", "¥500~"),
        ("BLUE SEAL 冰淇淋", "https://ajunfun.tw/naha-airport", "甜點",
         "那霸機場", "紅芋、鹽金楚糕為限定口味", "¥300~"),
    ],
    "okinawa_003": [
        ("泊港漁市場 丼すしまぐろ屋", "https://furikake.okinawa/okinawa-spot/naha-city", "海鮮",
         "泊港", "每日鮪魚50公噸，現撈直送，新鮮無冷凍", "¥1,500~"),
        ("oHacorté 水果塔", "https://furikake.okinawa/southern-area/ryubo-food-hall", "甜點",
         "縣廳前站", "職人手作水果塔，塔皮3~4次烘烤", "¥600~"),
        ("RYUBO FOOD HALL", "https://furikake.okinawa/southern-area/ryubo-food-hall", "餐廳",
         "縣廳前站", "2025新開幕，7間餐廳，350席美食廣場", "¥1,000~"),
    ],
    "okinawa_005": [
        ("A&W 牧港店", "https://furikake.okinawa/okinawa-spot/naha-city", "小吃",
         "沖繩市", "在地人激推，A&W人氣排行榜", "¥500~"),
        ("JEF 苦瓜漢堡", "https://furikake.okinawa/okinawa-spot/naha-city", "小吃",
         "平和通", "沖繩在地速食，苦瓜入漢堡", "¥400~"),
        ("甘味處萬丸咖啡", "https://furikake.okinawa/gourmet/mannmaru", "咖啡",
         "縣廳前站", "點飲料送早餐，7點就客滿的人氣咖啡廳", "¥380~"),
    ],
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_existing_urls(conn):
    """取得資料庫中所有已存在的 sources URL"""
    cur = conn.execute("SELECT sources FROM meals WHERE sources IS NOT NULL")
    existing = set()
    for (row,) in cur.fetchall():
        if row:
            try:
                urls = json.loads(row)
                existing.update(urls)
            except Exception:
                pass
    return existing


def get_region_code(station_id):
    return station_id.split("_")[0]


def build_id(name, region_code, station_id):
    """產生稳定的 meal ID"""
    base = f"{region_code}_{station_id}_{name}"
    return base[:64].replace(" ", "_").replace("/", "_")


def insert_meals(conn, existing_urls):
    """寫入候選餐廳到 meals 表"""
    inserted = 0
    skipped = 0
    region_counts = {}

    for station_id, candidates in MEALS_CANDIDATES.items():
        region = get_region_code(station_id)

        for (name, url, sub_cat, zone, desc, ticket) in candidates:
            # URL 去重
            if url in existing_urls:
                skipped += 1
                continue

            meal_id = build_id(name, region, station_id)
            details = json.dumps({"blog_article": url})
            sources = json.dumps([url])

            try:
                conn.execute("""
                    INSERT OR IGNORE INTO meals
                      (id, region_code, station_id, name, category, sub_category,
                       zone, description, ticket, sources, details)
                    VALUES (?, ?, ?, ?, 'meal', ?, ?, ?, ?, ?, ?)
                """, (meal_id, region, station_id, name, sub_cat, zone,
                       desc, ticket, sources, details))
                if conn.total_changes > 0:
                    inserted += 1
                    region_counts[region] = region_counts.get(region, 0) + 1
                    existing_urls.add(url)
                else:
                    skipped += 1
            except Exception as e:
                print(f"  [WARN] 寫入失敗 {name}: {e}", file=sys.stderr)
                skipped += 1

    return inserted, skipped, region_counts


def main():
    print("============================================================")
    print("Weekly Station Food Scan — 2026-09-13")
    print("============================================================")

    conn = get_connection()

    # 先確認 stations 表
    cur = conn.execute("SELECT COUNT(*) FROM stations")
    print(f"Stations in DB: {cur.fetchone()[0]}")

    # 現有 URL
    existing_urls = get_existing_urls(conn)
    print(f"Existing URLs in DB: {len(existing_urls)}")

    # 逐站插入
    print()
    all_region_counts = {}

    for station_id in sorted(MEALS_CANDIDATES.keys()):
        region = get_region_code(station_id)
        candidates = MEALS_CANDIDATES[station_id]

        print(f"[{station_id.upper()}] Candidates: {len(candidates)}")

        for (name, url, sub_cat, zone, desc, ticket) in candidates:
            if url in existing_urls:
                print(f"  - {name}: already exists, skipping")
            else:
                print(f"  + {name}: will be inserted")

    print()
    print("### 大站寫入 ###")

    inserted, skipped, region_counts = insert_meals(conn, existing_urls)

    conn.commit()
    conn.close()

    print()
    print(f"✅ Inserted: {inserted} | Skipped (duplicate): {skipped}")
    print()
    print("地區明細:")
    for region in sorted(region_counts.keys()):
        print(f"  {region}: +{region_counts[region]}")

    total = inserted
    return total


if __name__ == "__main__":
    total = main()
    print()
    print("============================================================")
    if total > 0:
        print(f"🎉 本週新增 {total} 筆美食")
    else:
        print("✅ 無新增（所有 URL 已存在）")
    print("============================================================")
