#!/usr/bin/env python3
"""
每週車站美食寫入任務
Week 37 (奇數週) — 只搜大站
"""

import sqlite3, json, re
from datetime import datetime

DB_PATH = "/var/repo/travel-planner/backend/travel.db"

# ============================================================
# Collected search results (URLs by station)
# Format: {station_id: {"name": "...", "zone": "...", "region": "...", "urls": [(url, query), ...]}}
# ============================================================

STATION_DATA = {
    # SEOUL
    "seoul_001": {
        "name": "首爾站", "zone": "龍山", "region": "seoul",
        "urls": [
            "https://creatrip.com/zh-TW/blog/963",
            "https://tw.trip.com/travel-guide/destination/seoul-station-2035755",
            "https://alinalife.tw/seoul-food",
            "https://creatrip.com/zh-HK/blog/11377",
            "https://www.kkday.com/zh-hk/blog/101575/seoul-station-food",
            "https://nnyy.tw/seoul-tasty-food",
            "https://mimigo.tw/seoul-goodeats",
            "https://www.bring-you.info/zh-tw/seoul-must-eat",
            "https://helena.tw/bibimbap-house-seoul-station",
            "https://beri.tw/seoul-food-list",
            "https://gototravel.tw/seoul-station",
            "https://orange.udn.com/orange/story/123282/8338180",
            "https://feitravel.tw/p-5071018929",
            "https://creatrip.com/zh-HK/blog/14761",
            "https://creatrip.com/zh-TW/blog/3759",
            "https://tournews.tw/seoul-food-guide-2026",
            "https://www.funliday.com/posts/2022-seoul-top15-must-eat-restaurant",
            "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026",
            "https://creatrip.com/en/blog/11538",
            "https://www.funliday.com/posts/gyeongbukgung_cafe",
            "https://alinalife.tw/cafe-column",
            "https://we4-travel.com/gongdeog-coffee-shop",
            "https://lilytogo.com/seoul-tribe-cafe",
            "https://listentolu.com/2025/04/fritz-coffee",
            "https://www.bring-you.info/zh-hans/yeonnam-dong",
            "https://tchinese.seoul.go.kr",
            "https://world.nol.com/en/content/pois/6957b2d8-5459-4646-af6c-bed542f8b7f2",
        ]
    },
    "seoul_004": {
        "name": "弘大入口站", "zone": "麻浦", "region": "seoul",
        "urls": [
            "https://www.bring-you.info/zh-hans/hongdae-cuisine",
            "https://feitravel.tw/p-5070812994",
            "https://feitravel.tw/p-5071461447",
            "https://feitravel.tw/hongdae-best-food-guide",
            "https://tisshuang.com/blog/post/hongdaefoods",
            "https://alinalife.tw/jopoktopokki",
            "https://alinalife.tw/seoul-food",
            "https://www.funliday.com/posts/hongdae-food-recommendations",
            "https://lilianyolo.wordpress.com/2025/11/21/hongdae-8-9-exit-map-food",
            "https://feitravel.tw/p-5070251291",
            "https://feitravel.tw/p-5071667313",
            "https://hikorealife.com/首爾弘大入口-在地韓國好味-保承會館血腸-水煮豬肉湯飯專門店",
            "https://tw.trip.com/guide/destination/弘大.html",
            "https://www.kkday.com/zh-hk/blog/98493/hongdae-routine",
            "https://www.klook.com/zh-TW/blog/hongdae-foods-recommend",
            "https://windko.tw/hongdae-kimchi",
            "https://alinalife.tw/ninggyocho/",
            "https://big5chinese.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=52515",
            "https://hikorealife.com/首爾-弘大入口-喉嚨目구멍-跟著善宰吃烤三層肉",
            "https://feitravel.tw/p-5071461447",
            "https://feitravel.tw/p-5066371463",
            "https://alinalife.tw/hongdaefood/",
            "https://creatrip.com/zh-TW/blog/2351",
            "https://creatrip.com/zh-TW/blog/14628",
            "https://omofood.com/coffee-libre",
            "https://creatrip.com/zh-TW/blog/2657",
            "https://korea.ggogo.com/tour/metro/hongik.html",
            "https://www.funliday.com/posts/hongdae_cafe",
            "https://hikorealife.com/首爾孔德-韓國喝咖啡吃甜點不踩雷的-A-Twosome-place",
            "https://lilytogo.com/sinleedoga",
            "https://creatrip.com/zh-TW/blog/4770",
            "https://nellydyu.tw/blog/post/sinidoga",
        ]
    },
    "seoul_002": {
        "name": "龍山站", "zone": "龍山", "region": "seoul",
        "urls": [
            "https://gowentgone.net/2025/02/12/seouldtravelyongsan-district-tour",
            "https://simpleball.pixnet.net/blog/posts/14222680626",
            "https://popbee.com/lifestyle/seoul-yongsan-ipark-mall-shopping-2026",
            "https://alinalife.tw/seoul-food",
            "https://tw.trip.com/moments/destination-yongsan-gu-2016420",
            "https://tw.trip.com/moments/detail/yongsan-gu-2016420-146236554",
            "https://www.catchtable.net/discovery/zh-TW/%E9%A6%96%E7%88%BE%E9%BE%8D%E5%B1%B1%E5%8D%80%E9%9F%93%E5%9C%8B%E7%89%A9%E8%B6%85%E6%89%80%E5%80%BC%E9%A4%90%E5%BB%B3%E6%8E%A8%E8%96%A6.html",
            "https://www.catchtable.net/discovery/zh-TW/%E9%A6%96%E7%88%BE%E9%BE%8D%E5%B1%B1%E5%8D%80%E9%9F%93%E5%9C%8B%E9%AB%98CP%E5%80%BC%E9%A4%90%E5%BB%B3%E6%8E%A8%E8%96%A6.html",
            "https://hk.trip.com/moments/theme/destination-yongsan-gu-2016420-restaurant-993134",
            "https://creatrip.com/zh-TW/blog/4419",
            "https://www.tripadvisor.com.hk/Restaurants-g294197-zfn15565978-Seoul.html",
            "https://www.tripadvisor.com.hk/Restaurants-g294197-zfn7778658-Seoul.html",
            "https://orange.udn.com/orange/story/123282/8338180",
            "https://windko.tw/yongsan-gamjatang",
            "https://zh.wikipedia.org/wiki/%E9%BE%8D%E5%B1%B1%E7%AB%99_(%E9%A6%96%E7%88%BE%E7%89%B9%E5%88%A5%E5%B8%82)",
            "https://sim88.com.tw/blogs/travel-internet-tips/seoul-food-guide-2026",
            "https://creatrip.com/en/blog/963",
            "https://creatrip.com/zh-TW/blog/13993",
            "https://judyer.com/slporksoup",
            "https://tsukiito05.pixnet.net/blog/posts/9576581376",
            "https://hk.trip.com/moments/theme/poi-i-park-mall-18555550-restaurant-993134",
            "https://creatrip.com/zh-TW/blog/13993",
            "https://zh.wikipedia.org/zh-hans/%E9%BE%8D%E5%B1%B1%E7%AB%99_(%E9%A6%96%E7%88%BE%E7%89%B9%E5%88%A5%E5%B8%82)",
            "https://www.catchtable.net/discovery/zh-TW/%E9%A6%96%E7%88%BE%E9%BE%8D%E5%B1%B1%E5%8D%80%E9%9F%93%E5%9C%8B%E9%AB%98cp%E5%80%BC%E9%A4%90%E5%BB%B3%E6%8E%A8%E8%96%A6.html",
        ]
    },
    "seoul_009": {
        "name": "合井站", "zone": "麻浦", "region": "seoul",
        "urls": [
            "https://shannysnote.com/tag/%E5%90%88%E4%BA%95%E7%AB%99%E7%BE%8E%E9%A3%9F",
            "https://creatrip.com/zh-TW/tips/subway-guide/2653/recommended-places-nearby-Hapjeong-station",
            "https://creatrip.com/zh-TW/blog/4346",
            "https://feitravel.tw/p-5067425633",
            "https://imagefromrita.com/okdongsik",
            "https://suger25.pixnet.net/blog/posts/9577455808",
            "https://alinalife.tw/42760823-hapjeong-home-plus",
            "https://hk.trip.com/moments/detail/seoul-234-121419705",
            "https://www.paine0602.com/hapjeong-bbq-gusamda",
            "https://adriannelife.com/blog/donsadon",
            "https://missbusan.com/doremi",
            "https://world.nol.com/zh-CN/content/pois/b36742bd-6886-4164-b6e0-e5849d7e119e",
            "https://guide.michelin.com/us/en/seoul-capital-area/kr-seoul/restaurant/okdongsik",
            "https://www.okdongsik.net/",
            "https://lilytogo.com/post-44597992/",
            "https://creatrip.com/zh-TW/blog/14924",
            "https://beri.tw/seoul-food-list",
            "https://ginatw.com/jeju-pork-bbq-donsadon-gd",
            "https://www.threads.com/@klocal_tw/post/DXgWI2uD8i_",
        ]
    },
    "seoul_010": {
        "name": "堂山站", "zone": "麻浦", "region": "seoul",
        "urls": [
            "https://creatrip.com/zh-TW/tips/subway-guide/2920/recommended-places-nearby-Dangsan-station",
        ]
    },

    # BUSAN
    "busan_001": {
        "name": "釜山站", "zone": "中央區", "region": "busan",
        "urls": [
            "https://www.funliday.com/posts/busan-food",
            "https://cc2kitchen.com/busanfoodie",
            "https://tournews.tw/2026/08/05/busan-food-guide-2026",
            "https://helena.tw/hanam-hagfish-busan",
            "https://helena.tw/puradak-choryang",
            "https://www.visitbusan.net/index.do?lang_cd=cnb&menuCd=DOM_000000602002001000&uc_seq=2396",
            "https://helena.tw/busan-yeongju-hwaejjip",
            "https://qhk.rfl.mybluehost.me/korea-busan-spots-food-tw",
            "https://www.funliday.com/posts/busan_dwaeji_gukbap",
            "https://helena.tw/post-39346069",
            "https://benjamintrips.tw/read-11091",
            "https://helena.tw/no9hanwoo",
            "https://smallchin.com/13981",
            "https://helena.tw/lee-jae-mo-pizza-busan-stn",
            "https://tw.trip.com/moments/theme/destination-ktx-busan-station-2040144-restaurant-993134",
            "https://helena.tw/busan-ktx-delicious",
            "https://feitravel.tw/p-5071576662",
            "https://lilytogo.com/busan-anmok",
            "https://traveltokoreanow.com/busan-coffee-map",
            "https://helena.tw/tobuk-bakery-cafe",
            "https://windko.tw/fm-coffee",
            "https://www.funliday.com/posts/momos-cafe",
            "https://banbi.tw/p-ark-cafe",
        ]
    },
    "busan_002": {
        "name": "草梁站", "zone": "中央區", "region": "busan",
        "urls": [
            "https://feitravel.tw/p-5071408296",
            "https://traveltokoreanow.com/grass-beam",
            "https://misoway.com/miryang-choryang",
            "https://pattersonwang.blogspot.com/2026/05/blog-post.html",
            "https://helena.tw/busan-ktx-delicious",
            "https://tw.trip.com/moments/theme/destination-ktx-busan-station-2040144-restaurant-993134",
            "https://helena.tw/puradak-choryang",
            "https://feitravel.tw/p-5071207146",
            "https://helena.tw/choryang-eel",
            "https://creatrip.com/zh-CN/blog/999",
            "https://traveltokoreanow.com/busan-coffee-map",
            "https://www.visitbusan.net/zht/index.do?lang_cd=cnb&menuCd=DOM_000000602002001000&uc_seq=513",
        ]
    },
    "busan_009": {
        "name": "金堂站", "zone": "江西區", "region": "busan",
        "urls": [
            "https://helena.tw/busan-ktx-delicious",
            "https://creatrip.com/zh-CN/blog/999",
            "https://www.funliday.com/posts/busan-food",
            "https://cc2kitchen.com/busanfoodie",
            "https://tournews.tw/busan-food-guide-2026",
            "https://wenthetravelbegins.com/busan-foodie-guide",
            "https://whatime.space/busan-food",
            "https://feitravel.tw/p-5071504899",
            "https://www.funliday.com/posts/busan_jeonpo_cafe",
            "https://windko.tw/fm-coffee",
            "https://traveltokoreanow.com/busan-coffee-map",
            "https://www.funliday.com/posts/momos-cafe",
            "https://ajtravel.tw/20240326",
        ]
    },
    "busan_010": {
        "name": "冷井站", "zone": "江西區", "region": "busan",
        "urls": [
            "https://www.visitbusan.net/index.do?menuCd=DOM_000000201002000000",
            "https://www.visitbusan.net/index.do?lang_cd=cnb&menuCd=DOM_000000602002001000&uc_seq=2396",
            "https://visitbusan.net/en/index.do?lang_cd=cnb&menuCd=DOM_000000602003001000&uc_seq=389",
            "https://www.visitbusan.net/index.do?menuCd=DOM_000000301002000000",
            "https://visitbusan.net/index.do?menuCd=DOM_000000302013000000",
            "https://news.sbs.co.kr/english/article.do?news_id=N1008650971",
            "https://stay.enko.kr/blog/must-try-food-busan",
            "https://stay.enko.kr/blog/en/must-try-food-in-busan-2025-guide-to-the-citys-best-bites",
            "https://wherebest.com/en/busan-food-guide",
            "https://www.tourlogy.com/en/busan-street-food",
            "https://www.catchtable.net/discovery/top-korean-fried-chicken%E1%84%8E%E1%85%B5%E1%84%8F%E1%85%B5%E1%86%AB-restaurants-in-busan.html",
            "https://smilevivi.com/sasang-sot",
            "https://www.funliday.com/posts/busan_dwaeji_gukbap",
            "https://creatrip.com/en/blog/11092",
            "https://creatrip.com/en/blog/798",
            "https://creatrip.com/en/blog/12711",
            "https://helena.tw/kkotgedang_haeundae",
            "https://helena.tw/busan-geukttong-dwaejigukppap",
            "https://helena.tw/busan-ktx-delicious",
            "https://whatime.space/busan-food",
            "https://missbusan.com/good",
            "https://www.busan.go.kr/bige/food/view?bbsNo=10&dataNo=72652&srchCl=Food",
        ]
    },
    "busan_006": {
        "name": "溫泉場站", "zone": "江西區", "region": "busan",
        "urls": [
            "https://big5chinese.visitkorea.or.kr/svc/contents/contentsView.do?vcontsId=194272",
            "https://windko.tw/fm-coffee",
            "https://www.funliday.com/posts/busan_jeonpo_cafe",
            "https://bigmouthblog.tw/blog/post/lasoop",
            "https://helena.tw/tobuk-bakery-cafe",
            "https://www.funliday.com/posts/blue-bottle-busan",
        ]
    },

    # FUKUOKA
    "fukuoka_001": {
        "name": "博多站", "zone": "博多", "region": "fukuoka",
        "urls": [
            "https://omakaseje.com/zh-tw/articles/ub230860",
            "https://feitravel.tw/p-5071059600",
            "https://tisshuang.com/blog/post/hakatafoods",
            "https://bobbytravel.tw/fukuoka-foods",
            "https://marukoblog.tw/2018-10-18.html",
            "https://www.5c5g.net/post/%E7%A6%8F%E5%B2%A1%E7%BE%8E%E9%A3%9F%E6%8E%A8%E4%BB%8B",
            "https://tasting-japan.com/archives/4975",
            "https://www.gltjp.com/zh-hant/article/item/21214",
            "https://www.facebook.com/JapanDIY/posts/-%E7%A6%8F%E5%86%88%E5%A4%A9%E7%A5%9E2026%E5%BF%85%E5%90%83top12-%E5%8E%BB%E7%A6%8F%E5%86%88%E8%87%AA%E7%94%B1%E8%A1%8C%E9%99%A2%E9%99%A4%E4%BA%86%E5%8D%9A%E5%A4%9A%E7%AB%99%E5%A4%A9%E7%A5%9E%E4%B9%9F%E6%98%AF%E9%9D%9E%E5%B8%B8%E9%80%B2%E5%90%88%E5%AE%89%E6%8E%92%E7%BE%8E%E9%A3%9F%E7%9A%84%E4%B8%80%E7%AB%99%E8%BF%99%E9%87%8C%E4%B8%8D%E5%8F%AA%E6%9C%89%E7%99%BE%E8%B4%A7%E5%9C%B0%E4%B8%8B%E8%A1%97%E5%92%8C%E8%8D%AF%E5%A6%86%E5%BA%97%E5%91%A8%E8%BE%B9%E4%B9%9F%E8%81%9A%E9%9B%86%E4%BA%86%E5%BE%88%E5%A4%9A%E7%A6%8F%E5%86%88%E5%90%8D%E7%89%A9%E6%8E%92%E9%98%9F%E5%90%8D%E5%BA%97%E5%92%8C%E9%AB%98%E4%BA%BA%E6%B0%94%E9%A4%90%E5%8E%85%E9%80%9B/",
            "https://catheadtravel.com/fukuoka-food-recommendations",
            "https://peikie.com/hakataizakayakeisuke",
            "https://marukoblog.tw/fukuka-udon.html",
            "https://www.travelerluxe.com/article/desc/200003484",
            "https://www.crossroadfukuoka.jp/tw/inbound-shop/15386",
            "https://www.hk01.com/%E6%97%85%E9%81%8A/60267030/%E5%8D%9A%E5%A4%9A%E7%BE%8E%E9%A3%9F7%E5%A4%A7%E6%8E%A8%E4%BB%8B-%E5%A3%BD%E5%8F%B8%E6%94%BE%E9%A1%8C-%E9%9B%9E%E8%82%89%E9%8D%8C-%E5%A3%BD%E5%96%9C%E7%87%92-1%E9%96%93%E6%8E%92%E9%9A%8A%E6%8B%89%E9%BA%B5%E5%BA%97%E5%BF%85%E5%90%83",
            "https://kyushu.letsgojp.com/archives/608908",
            "https://japantravel.navitime.com/zh-tw/area/jp/guide/NTJnews0612-zh-tw",
            "https://marukoblog.tw/rice-breakfast.html",
            "https://marukoblog.tw/mentaiko-rice.html",
            "https://vialife.tw/21487",
            "https://www.bring-you.info/zh-tw/jr-hakata-station",
            "https://www.gltjp.com/zh-hant/article/item/21052",
            "https://kyushu.letsgojp.com/archives/603822",
            "https://www.jrkyushu.co.jp/chinese/guide/station/station_hakata.html",
            "https://gogojp.tw/tag/%E5%8D%9A%E5%A4%9A%E4%B8%80%E7%95%AA%E8%A1%97",
            "https://cn.savorjapan.com/contents/discover-oishii-japan/12-izakaya-in-fukuoka-and-hakata-with-the-best-seafood",
            "https://kaikk.tw/owst",
            "https://tasting-japan.com/archives/5892",
            "https://kyushu.letsgojp.com/archives/663526",
            "https://gogojp.tw/seafood-owst-3rd",
            "https://fukuokainsider.com/article/fukuoka_matcha",
            "https://tw.fukuoka-leapup.jp/gourmet/202311.19894",
            "https://boo2k.com/fukuoka-best-restaurants",
            "https://gofukuoka.jp/zh-tw/spots/detail/27174",
            "https://gofukuoka.jp/zh-tw/articles/detail/d15d1a18-f250-439e-943e-bfe27987dc1c",
            "https://global.hankyu-hanshin-dept.co.jp/zh-CHT/store/hakata/recommend/12667466_3372.html",
            "https://fukuokainsider.com/article/hakatastation-21",
            "https://fukuokainsider.com/article/fukcoffee",
        ]
    },
    "fukuoka_003": {
        "name": "中洲川端站", "zone": "中洲", "region": "fukuoka",
        "urls": [
            "https://carlming.net/57901",
            "https://carlming.net/51314",
            "https://carlming.net/51404",
            "https://carlming.net/53438",
            "https://carlming.net/52605",
            "https://carlming.net/53276",
            "https://carlming.net/53392",
            "https://kyushu.letsgojp.com/archives/603822",
            "https://www.crossroadfukuoka.jp/cn/spot/12306",
            "https://www.japan.travel/hk/spot/2171",
            "https://tabelog.com/tw/fukuoka/A4001/A400102/R6992/rstLst",
            "https://tabelog.com/tw/fukuoka/A4001/A400102/40000122",
            "https://tabelog.com/cn/fukuoka/A4001/A400102/40056464",
            "https://fukuokainsider.com/article/fukuoka_matcha",
            "https://fukuokainsider.com/article/fukcoffee",
            "https://gofukuoka.jp/zh-tw/articles/detail/d15d1a18-f250-439e-943e-bfe27987dc1c",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-recommended-restaurants-where-you-can-try-specialties-of-fukuoka",
            "https://marukoblog.tw/food-way.html",
            "https://omakaseje.com/zh-tw/restaurants/rk473222",
            "https://www.hotpepper.jp/SA91/Y705/G001",
            "https://www.royalparkhotels.co.jp/zh-CHT/canvas/fukuokanakasu/index.html",
        ]
    },
    "fukuoka_004": {
        "name": "天神站", "zone": "天神", "region": "fukuoka",
        "urls": [
            "https://tasting-japan.com/archives/5554",
            "https://marukoblog.tw/2018-10-18.html",
            "https://tw.fukuoka-leapup.jp/gourmet/202312.21535",
            "https://bobbytravel.tw/fukuoka-foods",
            "https://kyushu.letsgojp.com/archives/603822",
            "https://gogojp.tw/tenji-yumyum",
            "https://www.funliday.com/posts/fukuoka-tenjinchikagai",
            "https://minako.tw/fukuoka-must-eat",
            "https://catheadtravel.com/fukuoka-food-recommendations",
            "https://marukoblog.tw/los-fukuoka.html",
            "https://www.bring-you.info/zh-tw/menya-kanetora",
            "https://boo2k.com/tenjin-map",
            "https://cn.savorjapan.com/contents/discover-oishii-japan/15-izakaya-to-visit-in-tenjin-fukuoka",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-izakaya-to-visit-in-tenjin-fukuoka",
            "https://peikie.com/notime-mixology-bar",
            "https://tasting-japan.com/archives/5892",
            "https://www.crossroadfukuoka.jp/tw/inbound-shop/15379",
            "https://itainan.com.tw/bottle-coffee-fukuoka",
            "https://marukoblog.tw/cheese-toast.html",
            "https://fukuokainsider.com/article/fukuoka_matcha",
            "https://yukigo.tw/blue-bottle-fukuoka",
            "https://www.lotofjapan.com/pages/fukuokaimdonut",
            "https://marukoblog.tw/los-fukuoka.html",
        ]
    },
    "fukuoka_005": {
        "name": "天神南站", "zone": "天神", "region": "fukuoka",
        "urls": [
            "https://tasting-japan.com/archives/5554",
            "https://marukoblog.tw/2018-10-18.html",
            "https://tw.fukuoka-leapup.jp/gourmet/202312.21535",
            "https://bobbytravel.tw/fukuoka-foods",
            "https://kyushu.letsgojp.com/archives/603822",
            "https://gogojp.tw/tenji-yumyum",
            "https://www.funliday.com/posts/fukuoka-tenjinchikagai",
            "https://minako.tw/fukuoka-must-eat",
            "https://catheadtravel.com/fukuoka-food-recommendations",
            "https://marukoblog.tw/los-fukuoka.html",
            "https://www.bring-you.info/zh-tw/menya-kanetora",
            "https://boo2k.com/tenjin-map",
            "https://cn.savorjapan.com/contents/discover-oishii-japan/15-izakaya-to-visit-in-tenjin-fukuoka",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-izakaya-to-visit-in-tenjin-fukuoka",
            "https://peikie.com/notime-mixology-bar",
            "https://tasting-japan.com/archives/5892",
            "https://www.crossroadfukuoka.jp/tw/inbound-shop/15379",
            "https://itainan.com.tw/bottle-coffee-fukuoka",
            "https://marukoblog.tw/cheese-toast.html",
            "https://fukuokainsider.com/article/fukuoka_matcha",
            "https://yukigo.tw/blue-bottle-fukuoka",
            "https://www.lotofjapan.com/pages/fukuokaimdonut",
        ]
    },
    "fukuoka_007": {
        "name": "渡邊通站", "zone": "渡邊通", "region": "fukuoka",
        "urls": [
            # Limited results — broader Fukuoka food guides
            "https://tw.fukuoka-leapup.jp/gourmet/202312.21535",
            "https://marukoblog.tw/2018-10-18.html",
            "https://fukuokainsider.com/article/fukuoka_matcha",
            "https://kyushu.letsgojp.com/archives/603822",
            "https://tasting-japan.com/archives/5554",
        ]
    },

    # OSAKA
    "osaka_station_001": {
        "name": "大阪站", "zone": "梅田", "region": "osaka",
        "urls": [
            "https://ethanadventures.tw/blogs/1029438",
            "https://feitravel.tw/p-5070449105",
            "https://mimigo.tw/osaka-foods",
            "https://www.funliday.com/posts/osaka-best-food-20",
            "https://www.funliday.com/posts/osaka-okonomiyaki-top12",
            "https://marukojp.com/article/osaka-food",
            "https://marukojp.com/article/Okonomiyaki",
            "https://curly.com.tw/osaka-food",
            "https://osaka.letsgojp.com/archives/585002",
            "https://osaka.letsgojp.com/archives/616411",
            "https://osaka.letsgojp.com/archives/749007",
            "https://osaka.letsgojp.com/archives/854373",
            "https://osaka.letsgojp.com/archives/895075",
            "https://supertaste.tvbs.com.tw/asia/351039",
            "https://tw.japan-travel-note.com/posts/418",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-14-recommended-restaurants-and-izakayas-around-osaka-umeda-station-japanese-cuisine-edition",
            "https://www.kkday.com/zh-hk/blog/112579/osaka-izakaya",
            "https://www.kkday.com/zh-hk/blog/115078/umeda-area-izakaya",
            "https://matcha-jp.com/tw/12080",
            "https://matcha-jp.com/tw/527",
            "https://www.gltjp.com/zh-hant/article/item/20937",
            "https://tabiiro.travel/article/18072901",
            "https://www.japan.travel/hk/destinations/kansai/osaka/shin-osaka-station-and-umeda",
            "https://www.japan.travel/tw/spot/2206",
            "https://omakaseje.com/zh-tw/articles/tj194635",
            "https://omakaseje.com/zh-tw/articles/gd547318",
            "https://zh-tw.hoshinoresorts.com/guide/area/kinki/osaka/osaka-osaka/shinosaka-omiyage",
            "https://metronine.osaka/tw/article_tour/20200306-coffee-shop",
            "https://tw.news.yahoo.com/%E6%97%A5%E6%9C%AC%E7%A5%A8%E9%81%B8%E6%9C%80%E6%96%B0%E6%8E%A8%E8%96%A6%E5%A4%A7%E9%98%AA%E5%BF%85%E5%90%83%E7%94%9C%E9%BB%9E%E5%92%96%E5%95%A1%E5%BB%B38%E9%81%B8-020012421.html",
            "https://finduheart.com/lapause",
            "https://venuslin.tw/le-cafe-v",
            "https://minako.tw/kissa_sancho",
            "https://bobbytravel.tw/osaka-food",
            "https://gowithmarkhazyl.com/osaka-food-guide",
            "https://www.bring-you.info/zh-tw/osaka-cuisine",
        ]
    },
    "osaka_station_002": {
        "name": "新大阪", "zone": "新大阪", "region": "osaka",
        "urls": [
            "https://omakaseje.com/zh-cn/articles/tj194635",
            "https://www.walkerplus.com/article/1145235",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/must-visit-restaurants-in-osaka-expo-2025",
            "https://mimigo.tw/osaka-foods",
            "https://www.gov-online.go.jp/hlj/en/july_2025/july_2025-02.html",
            "https://kaikk.tw/osaka-cuisine",
            "https://marukojp.com/article/osaka-food",
            "https://zh-tw.hoshinoresorts.com/guide/area/kinki/shinsekai-meiten",
            "https://marukojp.com/article/Shinsaibashi-Eats",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-15-restaurants-around-shin-osaka-station",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/perfect-for-post-work-relaxation-or-dining-on-a-business-trip-top-13-gourmet-destinations",
            "https://zh-tw.hoshinoresorts.com/guide/area/kinki/osaka/osaka-osaka/shinosaka-omiyage",
            "https://curly.com.tw/osaka-food",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-14-recommended-restaurants-and-izakayas-around-osaka-umeda-station-japanese-cuisine-edition",
            "https://matcha-jp.com/tw/12080",
            "https://www.tsunagujapan.com/zh-hant/7-delicious-and-convenient-izakaya-open-in-the-morning-in-osaka",
            "https://metronine.osaka/tw/article_tour/bar-hopping-uratennoji",
            "https://www.nap-camp.com/mag/57249",
            "https://aura.tw/nonkiya",
            "https://carlming.net/55529",
            "https://finduheart.com/lapause",
            "https://tw.wamazing.com/media/article/a-1691",
            "https://kaikk.tw/gokan-osaka",
            "https://tw.news.yahoo.com/%E6%97%A5%E6%9C%AC%E7%A5%A8%E9%81%B8%E6%9C%80%E6%96%B0%E6%8E%A8%E8%96%A6%E5%A4%A7%E9%98%AA%E5%BF%85%E5%90%83%E7%94%9C%E9%BB%9E%E5%92%96%E5%95%A1%E5%BB%B38%E9%81%B8",
        ]
    },
    "osaka_station_003": {
        "name": "天王寺", "zone": "天王寺", "region": "osaka",
        "urls": [
            "https://japannook.com/zh/articles/tennoji-restaurant-food-walk-guide",
            "https://jacid.pixnet.net/blog/posts/859060913226112439",
            "https://www.j-culturearc.com/tentoji-food-osaka",
            "https://tw.trip.com/moments/theme/destination-tennoji-2032155-restaurant-993134",
            "https://osaka.letsgojp.cn/archives/700553",
            "https://omakaseje.com/zh-tw/articles/yr265967",
            "https://tabelog.com/osaka/A2701/A270203/rank",
            "https://utravel.com.hk/news/detail/20012287/%E5%A4%A7%E9%98%AA%E5%A3%BD%E5%96%9C%E7%87%922024-8%E9%96%93%E5%A4%A7%E9%98%AA%E5%A3%BD%E5%96%9C%E7%87%92%E6%8E%A8%E4%BB%8B-%E8%BF%99%E9%9B%A3%E6%B3%A2-%E5%BF%83%E9%BD%8B%E6%A9%8B-%E5%A4%A9%E7%8E%8B%E5%AF%BA-%E4%BA%BA%E5%9D%87-400%E6%9C%89%E6%89%BE",
            "https://matcha-jp.com/tw/7979",
            "https://osaka.letsgojp.com/archives/700553",
            "https://www.bring-you.info/zh-tw/tennoji",
            "https://www.japan.travel/hk/destinations/kansai/osaka/tennoji",
            "https://metronine.osaka/tw/article_tour/bar-hopping-uratennoji",
            "https://www.kkday.com/zh-tw/blog/8780/asia-japan-osakasabenoharukas",
            "https://metronine.osaka/tw/spot-details?spot_id=10008381105",
            "https://boo2k.com/osaka-must-eat",
            "https://jamesdiscover.tw/blog/322170",
            "https://tabelog.com/tw/osaka/A2701/A270203/R6532/rstLst",
            "https://hk.trip.com/moments/theme/destination-tennoji-ward-2016474-restaurant-993134",
            "https://hk.trip.com/moments/destination-tennoji-2032155",
            "https://goodxssss.com/osaka-food-guide-tenma-best-izakaya",
            "https://30min.jp/gourmet/station/2823/%E5%96%AB%E7%85%99%E5%B8%AD%E3%81%82%E3%82%8A",
            "https://www.favy.jp/topics/30755",
            "https://www.japan-travel.cn/destinations/kansai/osaka/tennoji",
            "https://tw.wamazing.com/media/article/a-287",
            "https://jinggotrip.com/tag/ufu/",
            "https://gwan.tw/gelivery-gift",
            "https://journey.tw/harbs-namba-parks",
            "https://japannook.com/en/articles/tennoji-first-timer-guide",
            "https://osaka-info.jp/experience/ko/osaka/spot/286",
            "https://www.gltjp.com/en/directory/item/17152",
        ]
    },
    "osaka_station_004": {
        "name": "難波", "zone": "難波", "region": "osaka",
        "urls": [
            "https://marukojp.com/article/osaka-food",
            "https://omakaseje.com/zh-tw/articles/ac314547",
            "https://osaka.letsgojp.com/archives/895075",
            "https://www.bubu-jp.com/archives/47490",
            "https://mimigo.tw/osaka-foods",
            "https://jamesdiscover.tw/blog/321096",
            "https://www.funliday.com/posts/2023-osaka-namba-food",
            "https://osaka.letsgojp.com/archives/585002",
            "https://www.gltjp.com/zh-hant/article/item/20295",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/must-visit-restaurants-in-osaka-expo-2025",
            "https://www.threads.com/%40mani_tokyo_go/post/DVV7w-aj8y3/%E5%A4%A7%E9%98%AA%E5%BF%85%E5%90%83Top%E7%BE%8E%E9%A3%9F-%E6%9C%AC%E5%9C%B0%E4%BA%BA%E6%9C%80%E6%84%9B7%E5%AE%B6%E9%9A%B1%E8%97%8F%E7%89%88%E6%8E%A8%E8%96%A6%E6%A0%B9%E6%93%9Agoogle%E6%9C%80%E6%96%B0%E9%AB%98%E8%A9%95%E5%83%B9%E7%B2%BE%E9%81%B8%E5%9C%A8%E5%9C%B0%E4%BA%BA%E6%84%9B%E5%8E%BB%E7%9A%847%E5%AE%B6%E5%BA%97",
            "https://gototravel.tw/naniwa-menjiro",
            "https://www.hk01.com/%E6%97%85%E9%81%8A/60287801/%E5%A4%A7%E9%98%AA%E9%9B%A3%E6%B3%A2%E7%BE%8E%E9%A3%9F9%E5%A4%A7%E6%8E%A8%E8%96%A6",
            "https://livejapan.com/zh-tw/in-kansai/in-pref-osaka/in-namba_dotonbori_shinsaibashi/article-a2000327",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-11-lunches-at-osakas-food-paradise-namba",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/izakayas-in-namba-to-visit-after-enjoying-expo-2025-osaka-kansai",
            "https://www.bubu-jp.com/archives/47490",
            "https://www.klook.com/zh-HK/fnb/city-acategory/29-50-473-osaka-namba-izakaya",
            "https://tabelog.com/tw/osaka/A2701/A270202/R3388/rstLst/izakaya",
            "https://japan-food.guide/zh-TW/articles/nambas-Izakaya-paradise-5-izakaya-havens-to-explore-in-namba",
            "https://cc2kitchen.com/narutoya",
            "https://gurunavi.com/zh-hant/keex600/rst",
            "https://journey.tw/teppanyarou-uranamba",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/osaka-best-dessert-sweets-cafe-shops-top5",
            "https://tw.wamazing.com/media/article/a-1691",
            "https://metronine.osaka/tw/article_tour/20200306-coffee-shop",
            "https://tasting-japan.com/archives/4812",
            "https://gototravel.tw/osaka-rikuro-cheese-cake",
            "https://venuslin.tw/le-cafe-v",
            "https://elsa819.com/osaka-breakfast",
            "https://tenjo.tw/sakimoto-bakerycafe",
            "https://mimigo.tw/namba",
            "https://gototravel.tw/osaka-namba-food",
            "https://tasting-japan.com/archives/4862",
        ]
    },

    # TOKYO
    "tokyo_001": {
        "name": "東京站", "zone": "丸之內", "region": "tokyo",
        "urls": [
            "https://www.tokyoeki-1bangai.co.jp/feature/detail?cd=000007",
            "https://www.iza.ne.jp/article/20250429-7MLOH6PCHVCYVJ75YG57WBFL2E",
            "https://www.tokyoeki-1bangai.co.jp/feature/detail?cd=000036",
            "https://tabiiro.jp/gourmet/article/tokyostation-gourmet",
            "https://goodxssss.com/tokyo-station-transit-restaurants",
            "https://otonano-shumatsu.com/articles/447576",
            "https://amonblog.com/blog/category/japantravel/japan-tokyo/page/2",
            "https://livejapan.com/zh-tw/in-tokyo/in-pref-tokyo/in-tokyo_train_station/article-a0005431",
            "https://omakaseje.com/zh-tw/articles/ry720406",
            "https://tokyo.letsgojp.com/archives/72363",
            "https://tokyo.letsgojp.com/archives/601864",
            "https://isabellalife.tw/articles-657039",
            "https://www.kkday.com/zh-hk/blog/115960/%E6%9D%B1%E4%BA%AC%E8%BB%8A%E7%AB%99%E6%94%BB%E7%95%A5",
            "https://www.japan.travel/hk/spot/1710",
            "https://japanzerolag.com/?p=19130",
            "https://hk.trip.com/blog/tokyo-food-recommendation",
            "https://alinalife.tw/tokyo-food",
            "https://www.bring-you.info/zh-tw/tokyoeki-1bangai",
            "https://kyoko.tw/zojirushisyokudo",
            "https://goodxssss.com/zh-cn/tokyo-station-food-guide-best-restaurants-cn",
            "https://www.wowlavie.com/article/260026989",
            "https://www.gotokyo.org/tc/destinations/central-tokyo/tokyo-station-and-marunouchi/index.html",
            "https://matcha-jp.com/tw/26370",
            "https://goodxssss.com/autoreserve-top-6-tokyo-izakaya-experience",
            "https://djbcard.com/tokyofood",
            "https://www.hk01.com/%E6%97%85%E9%81%8A/60271179/%E6%9D%B1%E4%BA%AC%E5%B1%85%E9%85%92%E5%B1%8B8%E5%A4%A7%E6%8E%A8%E4%BB%8B-265%E9%A3%9F7%E9%81%93%E8%8F%9C-%E8%B6%85%E7%94%9C%E5%88%BA%E8%BA%AB-%E4%B8%B2%E7%87%92-%E6%9D%B1%E9%9C%B2%E8%9B%8B%E9%BB%9E%E6%8B%8C%E9%A3%AF",
            "https://goodxssss.com/best-izakayas-tokyo-shimbashi",
            "https://www.timeout.com/tokyo/restaurants/10-best-restaurants-inside-tokyo-station",
            "https://soranews24.com/2025/01/15/traveling-with-taste-try-one-of-tokyo-stations-top-ten-ranked-ekiben",
            "https://omakaseje.com/articles/ry720406",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/10-recommended-restaurants-near-tokyo-station",
            "https://blog.hamibook.com.tw/%E7%BE%8E%E9%A3%9F%E6%97%85%E9%81%8A/%E6%9D%B1%E4%BA%AC%E5%BF%85%E8%A8%AA%EF%BC%81%E5%93%81%E5%9A%90%E7%BE%8E%E5%91%B3%E7%94%9C%E9%BB%9E%E8%88%87%E6%A5%B5%E8%87%B4%E5%92%96%E5%95%A1%E7%9A%84%E7%B2%BE%E5%93%81%E5%92%96%E5%95%A1%E9%A4%A8?p=266472",
            "https://livejapan.com/en/in-tokyo/in-pref-tokyo/in-tokyo_train_station/spot-lj0054459",
            "https://tw.wamazing.com/media/article/a-2702",
            "https://wow-japan.com/food-tokyo-instagram-coffee-pick-ups",
            "https://alinalife.tw/onibuscoffee-tokyo",
            "https://www.uniopen.com/news/content/68f1eaacf8cb70500d25cb32",
        ]
    },
    "tokyo_002": {
        "name": "新宿站", "zone": "新宿", "region": "tokyo",
        "urls": [
            "https://gofunit.com/%E6%96%B0%E5%AE%BF%E7%BE%8E%E9%A3%9F",
            "https://travo.guide/japan/tokyo/best-restaurants-in-shinjuku",
            "https://missi.com.tw/shinjuku-food-guide",
            "https://travel-ink-trip.blogspot.com/2026/08/shinjuku-food-guide.html",
            "https://omakaseje.com/zh-tw/articles/jn829594",
            "https://tokyo.letsgojp.com/archives/601864",
            "https://marukoblog.tw/tokyo-restaurants.html",
            "https://www.threads.com/%40fattsai/post/Da5WN0DiYzC/2026-...",
            "https://matcha-jp.com/tw/3746",
            "https://tasting-japan.com/archives/5508",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-10-izakaya-in-shinjuku-recommended-by-locals",
            "https://www.tsunagujapan.com/zh-hant/10-unique-izakaya-experience-in-shinjuku",
            "https://matcha-jp.com/tw/6309",
            "https://today.line.me/tw/v3/article/X2MpEw",
            "https://www.gltjp.com/zh-hant/directory/item/11194",
            "https://gototravel.tw/shinjuku-omoide-yokocho",
            "https://matcha-jp.com/tw/7075",
            "https://www.gltjp.com/zh-hant/article/item/20067",
            "https://hk.trip.com/moments/poi-all-seasons-coffee-139430397",
            "https://gogojp.tw/tokyo-cafe-aaliya",
            "https://tokyo.letsgojp.com/archives/582120",
            "https://orange-dog.com/cafeaaliya",
            "https://alinalife.tw/depot-tokyo",
            "https://shinblog.com.tw/hoshinocoffee",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/a-unique-ninja-wagyu-beef-restaurant-5-minutes-from-shinjuku-station",
            "https://feitravel.tw/p-5071574022",
            "https://japan-food.guide/zh-TW/articles/the-best-yakiniku-in-shinjuku-5-recommendations",
            "https://japan-food.guide/zh-TW/articles/A-Complete-Guide-to-Enjoying-the-Charm-and-Highlights-of-Autumn-Leaves-at-Shinjuku-Gyoen-in-Tokyo",
            "https://allabout-japan.com/zh-tw/article/5956",
            "https://hk.wamazing.com/media/article/a-1574",
            "https://locally.matcha-jp.com/tw/24499",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-must-try-lunches-in-shinjuku-under-1000-jpy",
            "https://blog.hamibook.com.tw/...",
        ]
    },
    "tokyo_003": {
        "name": "澀谷站", "zone": "澀谷", "region": "tokyo",
        "urls": [
            "https://www.esquirehk.com/lifestyle/shibuya-best-choice-restaurants-tokyo-tabelog-high-score",
            "https://travo.guide/japan/tokyo/best-restaurants-in-shibuya",
            "https://tw.trip.com/blog/%E6%BE%80%E8%B0%B7%E7%BE%8E%E9%A3%9F",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/shibuya-best-dinner-20-popular-local-restaurants",
            "https://tokyo.letsgojp.com/archives/601864",
            "https://tokyo.letsgojp.com/archives/491357",
            "https://imreadygo.com/220695",
            "https://omakaseje.com/zh-tw/articles/en949725",
            "https://tabelog.com/tw/tokyo/A1303/A130301/rank",
            "https://www.gltjp.com/zh-hant/article/item/20511",
            "https://minako.tw/shibuya-travel",
            "https://omakaseje.com/zh-tw/articles/as545806",
            "https://www.bring-you.info/zh-tw/shibuya",
            "https://pipichocho.com/kiwamiya-shibuya",
            "https://tw.wamazing.com/media/article/a-3530",
            "https://www.japan.travel/tw/spot/2109",
            "https://japanzerolag.com/?p=23984",
            "https://zh-yue.wikipedia.org/wiki/%E6%BE%80%E8%B0%B7%E7%AB%99",
            "https://multi.andtrip.jp/LUC2AITRIP/cdata/luc2aitrip_2587_jazhb.html",
            "https://www.gotokyo.org/tc/destinations/western-tokyo/shibuya/index.html",
            "https://www.kkday.com/zh-hk/blog/115144/shibuya-izakaya",
            "https://tw.savorjapan.com/0006027337",
            "https://tw.savorjapan.com/0031538792",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/10-recommended-restaurants-around-shibuya-station-now-trending-as-an-entertainment-hot-spot",
            "https://matcha-jp.com/tw/3073",
            "https://blog.hamibook.com.tw/%E7%BE%8E%E9%A3%9F%E6%97%85%E9%81%8A/%E6%9D%B1%E4%BA%AC%E5%BF%85%E8%A8%AA%EF%BC%81%E5%93%81%E5%9A%90%E7%BE%8E%E5%91%B3%E7%94%9C%E9%BB%9E%E8%88%87%E6%A5%B5%E8%87%B4%E5%92%96%E5%95%A1%E7%9A%84%E7%B2%BE%E5%93%81%E5%92%96%E5%95%A1%E9%A4%A8",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/top-15-cafes-in-harajuku-and-shibuya-serving-delicious-desserts",
            "https://wow-japan.com/food-tokyo-shibuya-must-eat",
            "https://bobowin.blog/bluebottle-shibuya",
            "https://alinalife.tw/ruru-shibuya",
            "https://shinblog.com.tw/kenyanshibuya",
            "https://www.byfood.com/zh-tw/blog/breakfast-in-shibuya-p-515",
            "https://matcha-jp.com/tw/23684",
            "https://www.hk01.com/%E6%97%85%E9%81%8A/1036281/%E6%BE%80%E8%B0%B7%E7%BE%8E%E9%A3%9F11%E9%96%932025-%E7%89%9B%E6%89%92%E8%93%8B%E9%A3%AF-%E6%B5%B7%E9%AE%AE%E4%B8%BC-%E8%9B%8B%E5%8C%85%E9%A3%AF-%E7%87%92%E8%82%89-%E6%B0%B4%E6%9E%9C%E5%8D%83%E5%B1%A4%E8%9B%8B%E7%B3%95",
        ]
    },
    "tokyo_004": {
        "name": "池袋站", "zone": "池袋", "region": "tokyo",
        "urls": [
            "https://www.klook.com/zh-HK/blog/ikebukuro-food",
            "https://livejapan.com/zh-tw/in-tokyo/in-pref-tokyo/in-ikebukuro/article-a0005432",
            "https://travo.guide/japan/tokyo/best-restaurants-in-ikebukuro",
            "https://omakaseje.com/zh-tw/articles/hz709000",
            "https://tokyo.letsgojp.com/archives/679888",
            "https://www.gltjp.com/zh-hant/article/item/20300",
            "https://matcha-jp.com/tw/3547",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-restaurants-in-ikebukuro-recommended-by-japanese-top-chefs",
            "https://www.funliday.com/posts/tokyo-ikebukuro-1day-trip",
            "https://www.gotokyo.org/tc/destinations/northern-tokyo/ikebukuro/index.html",
            "https://lunaexplorer.tw/chapter/1067",
            "https://missi.com.tw/ikebukurofood-guide",
            "https://www.japaholic.com/tw/article/detail/522679",
            "https://maxfoodfun.com/ichiran-ikebukuro-station",
            "https://maxfoodfun.com/yayoiken-ikebukuro",
            "https://hk.trip.com/guide/destination/%E6%B1%A0%E8%A2%8B%E6%99%AF%E9%BB%9E.html",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/14-great-places-to-satisfy-your-lunch-cravings-for-less-than-1000-jpy-in-ikebukuro",
            "https://digjapan.travel/zh_tw/blog/id%3D11358",
            "https://bearlovefood.com/blog/post/izumo-ikebukuro",
            "https://tw.wamazing.com/media/article/a-2124",
            "https://japanzerolag.com/?p=17823",
            "https://gurunavi.com/zh-hant/gh73200/mp/rst",
            "https://cn.savorjapan.com/contents/discover-oishii-japan/14-must-visit-izakaya-in-ikebukuro-tokyo",
            "https://japanzerolag.com/?p=29185",
            "https://www.gotokyo.org/cn/story/guide/pub-grub-decoded-a-guide-to-japanese-izakaya/index.html",
            "https://livejapan.com/ja/in-tokyo/in-pref-tokyo/in-ikebukuro/article-a0001239",
            "https://tw.wamazing.com/media/article/a-2702",
            "https://blog.hamibook.com.tw/%E7%BE%8E%E9%A3%9F%E6%97%85%E9%81%8A/%E6%9D%B1%E4%BA%AC%E5%BF%85%E8%A8%AA%EF%BC%81%E5%93%81%E5%9A%90%E7%BE%8E%E5%91%B3%E7%94%9C%E9%BB%9E%E8%88%87%E6%A5%B5%E8%87%B4%E5%92%96%E5%95%A1%E7%9A%84%E7%B2%BE%E5%93%81%E5%92%96%E5%95%A1%E9%A4%A8?p=266472",
            "https://matcha-jp.com/tw/21804",
            "https://tokyo.letsgojp.com/archives/582120",
            "https://japanzerolag.com/?p=16713",
            "https://matcha-jp.com/tw/9598",
            "https://livejapan.com/zh-cn/in-tokyo/in-pref-tokyo/in-ikebukuro/article-a0003600",
            "https://livejapan.com/zh-tw/in-tokyo/in-pref-tokyo/in-akihabara/article-a0000048",
            "https://alinalife.tw/onibuscoffee-tokyo",
        ]
    },
    "tokyo_005": {
        "name": "上野站", "zone": "上野", "region": "tokyo",
        "urls": [
            "https://www.esquirehk.com/lifestyle/tokyo-ueno-best-restaurants-recommandation",
            "https://travo.guide/japan/tokyo/best-restaurants-in-ueno",
            "https://goodxssss.com/ueno-ameyoko-food-guide-top-15-sushi-seafood-restaurants",
            "https://www.bring-you.info/zh-tw/ueno-restaurants",
            "https://tokyo.letsgojp.com/archives/558755",
            "https://matcha-jp.com/tw/21960",
            "https://gototravel.tw/tokyo-ueno-food",
            "https://www.klook.com/zh-TW/blog/ueno-food-recommend",
            "https://omakaseje.com/zh-tw/articles/iu662555",
            "https://upssmile.com/204313/yamabe-okachimachi-uenotaito-tokyo",
            "https://tasting-japan.com/archives/2497",
            "https://tyaward.com.tw/%E7%BE%8E%E9%A3%9F/%E4%B8%8A%E9%87%8E%E8%BB%8A%E7%AB%99%E7%BE%8E%E9%A3%9F",
            "https://momoblog.tw/rokurinsha-ueno",
            "https://today.line.me/tw/v3/article/mw1BQz",
            "https://bobbytravel.tw/ameya-yokocho",
            "https://gototravel.tw/ueno-rokurinsha",
            "https://www.bring-you.info/zh-tw/ueno",
            "https://boo2k.com/tag/%E4%B8%8A%E9%87%8E%E8%BB%8A%E7%AB%99%E9%99%84%E8%BF%91%E7%BE%8E%E9%A3%9F",
            "https://isabellalife.tw/articles-1028011",
            "https://hk.wamazing.com/media/article/a-559",
            "https://gogojp.tw/toriichizu-ueno",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-izakaya-in-ueno-recommended-by-locals-for-visitors",
            "https://www.bring-you.info/zh-tw/yakitori-bunraku",
            "https://baygolee.com/ueno-monraku",
            "https://gototravel.tw/ueno-kushiyaki",
            "https://tabelog.com/tw/tokyo/A1311/A131101/R1164/rstLst/izakaya",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/15-best-izakaya-in-ueno-for-a-glass-of-delicious-sake-on-your-way-home-from-a-busy-day-sightseeing",
            "https://kouinjp.com/coffee-ojo",
            "https://pengu777.com/coffee-oujyou",
            "https://hk.wamazing.com/media/article/a-3645",
            "https://alinalife.tw/coffee-ojo",
            "https://tokyo.letsgojp.com/archives/582120",
            "https://tw.wamazing.com/media/article/a-2702",
            "https://www.wowlavie.com/article/260026989",
            "https://alinalife.tw/depot-tokyo",
            "https://alinalife.tw/onibuscoffee-tokyo",
        ]
    },

    # OKINAWA
    "okinawa_station_001": {
        "name": "那霸機場", "zone": "那霸", "region": "okinawa",
        "urls": [
            "https://todolist-japan.com/zh/naha-food-guide",
            "https://okinawa.letsgojp.com/archives/23438",
            "https://tw.gogo-tour.com/info/naha-airport-restaurants",
            "https://www.lotofjapan.com/pages/nahaairport",
            "https://tw.trip.com/guide/info/%E9%82%A3%E9%9C%B8%E6%A9%9F%E5%A0%B4.html",
            "https://boo2k.com/naha-airport",
            "https://bobbytravel.tw/naha-airport",
            "https://ajunfun.tw/naha-airport",
            "https://mimigo.tw/okinawa_trips",
            "https://okinawa.letsgojp.com/archives/23951",
            "https://momoblog.tw/jefburger",
            "https://www.whbydcc.com/%E9%82%A3%E9%9C%B8%E6%A9%9F%E5%A0%B4%E5%90%83%E4%BB%80%E9%BA%BC",
            "https://okinawa.letsgojp.cn/archives/23438",
            "https://matcha-jp.com/tw/18664",
            "https://visitokinawajapan.com/zh-hant/travel-inspiration/must-try-okinawa-street-foods",
            "https://alinalife.tw/porktamago",
            "https://tasting-japan.com/archives/4071",
            "https://lailai-web.com/airport",
            "https://nicklee.tw/2736/naha-airport-dutyfree-lounge",
            "https://ajunfun.tw/okinawafoodtop",
            "https://slowlifeinokinawa.com/",
            "https://we4-travel.com/naha-lucky-maximum",
            "https://japanzerolag.com/?p=7235",
            "https://www.tylinnetravel.tw/naha-airport-lounge_hana/",
            "https://gogojp.tw/new-naha-airport",
            "https://djbcard.com/nahaairport",
            "https://uptogo.com.tw/%E7%BE%8E%E9%A3%9F/%E6%97%A5%E5%BC%8F%E6%96%99%E7%90%86/%E9%82%A3%E9%9C%B8%E6%A9%9F%E5%A0%B4%E6%9C%89%E4%BB%80%E9%BA%BC%E5%95%BD%E5%90%83%E7%9A%84%E5%9C%A8%E5%B9%BE%E6%A8%93%EF%BC%9F",
            "https://uptogo.com.tw/%E7%BE%8E%E9%A3%9F/%E9%82%A3%E9%9C%B8%E6%A9%9F%E5%A0%B4%E5%90%83%E7%9A%84%E5%9C%A8%E5%B9%BE%E6%A8%93%EF%BC%9F",
            "https://uptogo.com.tw/%E7%BE%8E%E9%A3%9F/%E6%97%A5%E5%BC%8F%E6%96%99%E7%90%86/%E6%B2%96%E7%B9%A9%E4%B8%8B%E9%A3%9F%E6%A9%9F%E5%90%83%E4%BB%80%E9%BA%BC%EF%BC%9F",
            "https://shin.tw/jp-okinawa-food",
            "https://tc.tabirai.net/sightseeing/article/naha-airport-food",
            "https://aiwahu.tw/oki071203",
            "https://adontrip.com/blog/71638",
            "https://hk.trip.com/moments/theme/poi-naha-international-airport-13100473-restaurant-993134",
            "https://www.tsunagujapan.com/zh-hant/seven-okinawa-sweets",
            "https://fullfenblog.tw/okinawan-food",
            "https://slowlifeinokinawa.com/okicafe-midnightsweets",
            "https://slowlifeinokinawa.com/okicafe-rokkanshuri",
        ]
    },
    "okinawa_station_002": {
        "name": "赤崗", "zone": "那霸", "region": "okinawa",
        "urls": [
            "https://note.com/tabi_to_yado/n/n41e72ca5c2c5",
            "https://japanzerolag.com/?p=7235",
            "https://marukoblog.tw/okinawa-good.html",
            "https://shin.tw/jp-okinawa-food",
            "https://www.klook.com/zh-TW/blog/okinawa-food",
            "https://travelcontentsapp.com/guide/okinawa/b544",
            "https://minako.tw/okinawa-food",
            "https://www.funliday.com/posts/2026-okinawa-travel-food",
            "https://dorapig.com/sun-naha/",
            "https://okajapan.com/category/okinawa-food-guide",
            "https://slowlifeinokinawa.com/okicafe-rokkanshuri",
            "https://tingandkao.com/okinawa-cerrado-coffee",
            "https://travel.nantou.gov.tw/article/%E4%BE%86%E5%8D%81%E6%8A%95%EF%BC%8C%E6%80%8E%E8%83%BD%E9%8C%AF%E9%81%8E%E9%90%B5%E9%81%93%E5%91%A8%E9%82%8B%EF%BC%8C%E7%B2%BE%E9%81%B8%E9%9B%86%E9%9B%86%E3%80%81%E6%B0%B4%E9%87%8C%E5%9C%A8%E5%9C%B0",
        ]
    },
    "okinawa_station_005": {
        "name": "旭橋", "zone": "那霸", "region": "okinawa",
        "urls": [
            "https://okidokey.jp/portal/blog?lang=zh",
            "https://roundtripjp.com/2025/07/09/food-17",
            "https://itravelblog.net/kokusai-dori",
            "https://www.kkday.com/zh-tw/blog/45834/asia-japan-okinawa-must-eat-restaurants",
            "https://yipupupu.pixnet.net/blog/posts/16129570280",
            "https://www.chictrip.com.tw/blog/country/japan/2026_okinawa_travel",
            "https://japanzerolag.com/?p=7235",
            "https://tingandkao.com/mikado-shokudo",
            "https://www.funliday.com/posts/2026-okinawa-travel-food",
            "https://niniyeh.com/okinawan-food",
            "https://hellokids.tw/posts/2oo/can",
            "https://karenchang1981.pixnet.net/blog/posts/10127989656",
            "https://tw.savorjapan.com/search?prefecture_codes=47&restaurant_class_codes=2",
            "https://travelcontentsapp.com/guide/okinawa/b544",
            "https://okinawa.letsgojp.com/archives/16942",
            "https://hk.wamazing.com/media/article/a-3645",
            "https://treeman.tw/%E3%80%90%E6%B2%96%E7%B8%84%E7%B8%A3%E8%B1%8A%E8%A6%8B%E5%9F%8E%E5%B8%82%E3%80%91%E5%B9%B8%E7%A6%8F%E9%AC%86%E9%A4%85%EF%BD%9C%E6%B2%96%E7%B9%A9%E7%80%A8%E9%95%B7%E5%B3%B6%E5%BF%85%E5%90%83%E6%8E%92",
            "https://furikake.okinawa/gourmet/makebake",
            "https://baygolee.com/kurukuma",
            "https://marukoblog.tw/okinawa-good.html",
            "https://lailai-web.com/gourmet",
            "https://momoblog.tw/marutama",
        ]
    },
    "okinawa_station_008": {
        "name": "縣廳前", "zone": "那霸", "region": "okinawa",
        "urls": [
            "https://ethanadventures.tw/blogs/1028524",
            "https://okinawa.letsgojp.com/archives/657147",
            "https://www.wendyjourney.com/okinawa-food",
            "https://lailai-web.com/gourmet",
            "https://marukoblog.tw/okinawa-good.html",
            "https://ajunfun.tw/kokusai-dori",
            "https://autoreserve.com/zh-tw/jp/okinawa/kennchoumae-2-station/okinawa-cuisine",
            "https://wu1234321.pixnet.net/blog/posts/14222937186",
            "https://dorapig.com/furusato-okinawa",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/-okinawa-don-t-know-where-to-go-locals-are-in-love-with-these-selected-10-restaurants",
            "https://www.kkday.com/zh-tw/blog/45834/asia-japan-okinawa-must-eat-restaurants",
            "https://okinawa.letsgojp.com/archives/782803",
            "https://www.lotofjapan.com/pages/okinawanahaizakaya",
            "https://okinawa.letsgojp.com/archives/615882",
            "https://gogoout.com/blog/okinawa-food",
            "https://eisei86.pixnet.net/blog/posts/15203266643",
        ]
    },
    "okinawa_station_009": {
        "name": "牧志", "zone": "那霸", "region": "okinawa",
        "urls": [
            "https://marukoblog.tw/okinawa-good.html",
            "https://luka-life.com/oka-makishi-market",
            "https://www.wendyjourney.com/makishi-public-market",
            "https://jamesdiscover.tw/blog/8582",
            "https://wu840531wu890515.pixnet.net/blog/posts/9577806588",
            "https://boo2k.com/okinawa-dining-guide",
            "https://okinawa.letsgojp.com/archives/23951",
            "https://journey.tw/makishi-public-market",
            "https://yusuke.com.tw/blog/post/makishi-public-market",
            "https://www.lotofjapan.com/pages/okinawafood-1",
            "https://www.chictrip.com.tw/blog/country/japan/2026_okinawa_travel",
            "https://tw.savorjapan.com/contents/discover-oishii-japan/-okinawa-don-t-know-where-to-go-locals-are-in-love-with-these-selected-10-restaurants",
            "https://tabelog.com/tw/okinawa/A4701/A470101/R10744/rstLst",
            "https://okajapan.com/naha-makishi-public-market",
            "https://marukoblog.tw/ayumi.html",
            "https://japanzerolag.com/?p=7235",
            "https://jamesdiscover.tw/blog/17983",
            "https://luka-life.com/oka-makishi-market",
            "https://uptogo.com.tw/%E7%BE%8E%E9%A3%9F/%E7%89%A7%E5%BF%97%E5%85%AC%E8%A8D%E5%B8%82%E5%A0%B4%E5%90%83%E4%BB%80%E9%BA%BC%EF%BC%9F",
            "https://www.lotofjapan.com/pages/okinawanahaizakaya",
            "https://furikake.okinawa/shopping/ishigakijima-rayu",
            "https://www.threads.com/%40goodxssss/post/DVdZIEqkTvD/%E9%82%A3%E9%9C%B8top20%E5%AE%B6-%E5%B1%85%E9%85%92%E5%B1%8B-%E7%9C%8B%E9%80%99%E9%82%8Ahttpsgoodxsssscombest-izakaya-naha-kokusai-dori-okinawa?hl=zh-tw",
            "https://mustbuyjapan.com/meishi/renqidianpu/48208",
            "https://okinawa.letsgojp.com/archives/16942",
            "https://furikake.okinawa/gourmet/makebake",
            "https://treeman.tw/%E3%80%90%E6%B2%96%E7%B8%84%E7%B8%A3%E8%B1%8A%E8%A6%8B%E5%9F%8E%E5%B8%82%E3%80%91%E5%B9%B8%E7%A6%8F%E9%AC%86%E9%A4%85%EF%BD%9C%E6%B2%96%E7%B9%A9%E7%80%A8%E9%95%B7%E5%B3%B6%E5%BF%85%E5%90%83%E6%8E%92",
            "https://baygolee.com/kurukuma",
            "https://tingandkao.com/banta-cafe",
            "https://travel.yam.com/article/136698",
        ]
    },
}


def generate_id(url, region_code):
    """Generate a short unique ID from URL."""
    # Take domain + first path segment
    clean = re.sub(r'[^a-zA-Z0-9]', '', url.split('//')[1] if '//' in url else url)[:12]
    return f"{region_code}_{clean[:8]}"


def guess_sub_category(url, query):
    """Guess sub_category from URL or query."""
    q = (url + ' ' + query).lower()
    if any(k in q for k in ['咖啡', 'cafe', 'coffee', '甜點', 'dessert', '下午茶', '蛋糕']):
        return '咖啡甜點'
    elif any(k in q for k in ['居酒屋', 'izakaya', '小吃', 'snack', ' street']):
        return '小吃'
    elif any(k in q for k in ['燒肉', 'yakiniku', '烤肉', 'bbq']):
        return '燒肉'
    elif any(k in q for k in ['拉麵', 'ramen', '麵', 'noodle']):
        return '拉麵'
    elif any(k in q for k in ['壽司', 'sushi', '生魚']):
        return '壽司'
    elif any(k in q for k in ['大阪燒', 'okonomiyaki', ' 章魚燒']):
        return '大阪燒'
    return '小吃'


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get existing URLs
    cur.execute("SELECT sources FROM meals WHERE sources IS NOT NULL")
    existing_urls = set()
    for (sources,) in cur.fetchall():
        if sources:
            try:
                for u in json.loads(sources):
                    if isinstance(u, str) and u.startswith('http'):
                        existing_urls.add(u)
            except:
                pass

    total_new = 0
    station_counts = {}

    for station_id, data in STATION_DATA.items():
        region = data['region']
        station_name = data['name']
        zone = data['zone']
        urls = data['urls']

        station_new = 0
        for url in urls:
            if url in existing_urls:
                continue

            url_id = generate_id(url, region)
            sub_cat = guess_sub_category(url, '')
            details = json.dumps({'blog_article': url}, ensure_ascii=False)
            sources = json.dumps([url], ensure_ascii=False)

            try:
                cur.execute("""
                    INSERT OR IGNORE INTO meals (
                        id, region_code, station_id, name,
                        category, sub_category, zone,
                        sources, details, created_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    url_id,
                    region,
                    station_id,
                    f"{station_name} 周邊美食",
                    'meal',
                    sub_cat,
                    zone,
                    sources,
                    details,
                    datetime.now().isoformat(),
                ))
                if cur.rowcount > 0:
                    existing_urls.add(url)  # prevent duplicates within same run
                    station_new += 1
                    total_new += 1
            except Exception as e:
                print(f"  [WARN] Insert error for {url}: {e}")

        if station_new > 0:
            station_counts[station_id] = {'name': station_name, 'new': station_new}

    conn.commit()
    conn.close()

    print(f"Week 37 車站美食更新完成")
    print(f"本週新增 {total_new} 筆美食（來自 {len(station_counts)} 個車站）")
    for sid, info in sorted(station_counts.items(), key=lambda x: x[1]['new'], reverse=True):
        print(f"  {sid} {info['name']}: +{info['new']}")

if __name__ == '__main__':
    main()
