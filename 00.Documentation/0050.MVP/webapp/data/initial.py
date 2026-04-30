"""
PM008 MVP 初始資料 — 永祿三年・桶狹間前夕
"""

INITIAL_STATE = {
    "date": {"year": 1560, "month": 5},
    "player_faction": "oda",
    "turn": 1,
    "log": [],

    "factions": {
        "oda": {
            "id": "oda", "name": "織田家", "color": "#c0392b",
            "daimyo_id": "nobunaga",
            "gold": 500, "military_supply": 300,
        },
        "imagawa": {
            "id": "imagawa", "name": "今川家", "color": "#2980b9",
            "daimyo_id": "yoshimoto",
            "gold": 800, "military_supply": 600,
        },
    },

    "castles": [
        {"id": "castle_01", "name": "清洲城", "faction": "oda",   "level": 2, "garrison": 1000, "max_garrison": 1000, "province": "尾張國", "is_capital": True,  "x": 28, "y": 44, "districts": ["dist_01", "dist_02"]},
        {"id": "castle_02", "name": "小牧山城","faction": "oda",   "level": 1, "garrison": 500,  "max_garrison": 500,  "province": "尾張國", "is_capital": False, "x": 22, "y": 30, "districts": ["dist_03", "dist_04"]},
        {"id": "castle_03", "name": "岡崎城",  "faction": "imagawa","level": 3, "garrison": 1500, "max_garrison": 1500, "province": "三河國", "is_capital": True,  "x": 62, "y": 50, "districts": ["dist_05", "dist_06"]},
        {"id": "castle_04", "name": "吉田城",  "faction": "imagawa","level": 1, "garrison": 1000, "max_garrison": 500,  "province": "三河國", "is_capital": False, "x": 75, "y": 36, "districts": ["dist_07", "dist_08"]},
    ],

    "districts": [
        {"id": "dist_01", "name": "清洲西郡", "castle": "castle_01", "type": "商業郡",
         "facility_name": "市集", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 20, "retainer": "niwachoja",
         "adjacent": ["dist_02", "dist_05"]},

        {"id": "dist_02", "name": "那古野郡", "castle": "castle_01", "type": "軍事郡",
         "facility_name": "駐屯地", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 20, "retainer": "shibatakatsuie",
         "adjacent": ["dist_01", "dist_05"]},

        {"id": "dist_03", "name": "春日井郡", "castle": "castle_02", "type": "農業郡",
         "facility_name": "村落", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 20, "retainer": "kinoshita",
         "adjacent": ["dist_04"]},

        {"id": "dist_04", "name": "丹羽郡",   "castle": "castle_02", "type": "農業郡",
         "facility_name": "村落", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 20, "retainer": "maedatoshiie",
         "adjacent": ["dist_03"]},

        {"id": "dist_05", "name": "額田郡",   "castle": "castle_03", "type": "軍事郡",
         "facility_name": "駐屯地", "facility_level": 2, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 25, "retainer": "okabemotonobu",
         "adjacent": ["dist_01", "dist_02", "dist_06"]},

        {"id": "dist_06", "name": "碧海郡",   "castle": "castle_03", "type": "農業郡",
         "facility_name": "農村", "facility_level": 2, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 25, "retainer": None,
         "adjacent": ["dist_05", "dist_07"]},

        {"id": "dist_07", "name": "渥美郡",   "castle": "castle_04", "type": "農業郡",
         "facility_name": "村落", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 25, "retainer": None,
         "adjacent": ["dist_06", "dist_08"]},

        {"id": "dist_08", "name": "寶飯郡",   "castle": "castle_04", "type": "商業郡",
         "facility_name": "市集", "facility_level": 1, "facility_max": 3,
         "building": False, "building_turns": 0,
         "nengu_rate": 25, "retainer": None,
         "adjacent": ["dist_07"]},
    ],

    "retainers": [
        {"id": "nobunaga",       "name": "織田信長",  "faction": "oda",     "rank": "大名", "lineage": "一門",  "loyalty": 100, "loyalty_label": "—",      "forces": 5000, "location": "castle_01",
         "mil": 85, "str_": 82, "pol": 78, "cha": 96,
         "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"), "politics": ("B","為政清明"), "charisma": ("S","魅力無雙")}},

        {"id": "shibatakatsuie", "name": "柴田勝家",  "faction": "oda",     "rank": "宿老", "lineage": "譜代",  "loyalty": 80,  "loyalty_label": "忠心耿耿", "forces": 4000, "location": "dist_02",
         "mil": 92, "str_": 52, "pol": 55, "cha": 72,
         "eval": {"military": ("S","無敵猛將"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")}},

        {"id": "niwachoja",      "name": "丹羽長秀",  "faction": "oda",     "rank": "家老", "lineage": "譜代",  "loyalty": 78,  "loyalty_label": "忠心耿耿", "forces": 2000, "location": "dist_01",
         "mil": 75, "str_": 76, "pol": 84, "cha": 73,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("B","奇謀之將"), "politics": ("A","治國之能臣"), "charisma": ("B","人望漸隆")}},

        {"id": "kinoshita",      "name": "木下藤吉郎", "faction": "oda",    "rank": "家老", "lineage": "外樣",  "loyalty": 65,  "loyalty_label": "表面恭敬", "forces": 2000, "location": "dist_03",
         "mil": 58, "str_": 88, "pol": 86, "cha": 90,
         "eval": {"military": ("C","嶄露頭角"), "strategy": ("A","謀略過人"), "politics": ("A","治國之能臣"), "charisma": ("A","呼風喚雨")}},

        {"id": "maedatoshiie",   "name": "前田利家",  "faction": "oda",     "rank": "部將", "lineage": "譜代",  "loyalty": 82,  "loyalty_label": "忠心耿耿", "forces": 1000, "location": "dist_04",
         "mil": 77, "str_": 55, "pol": 58, "cha": 70,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")}},

        {"id": "yoshimoto",      "name": "今川義元",  "faction": "imagawa", "rank": "大名", "lineage": "一門",  "loyalty": 100, "loyalty_label": "—",      "forces": 5000, "location": "castle_03",
         "mil": 83, "str_": 84, "pol": 93, "cha": 85,
         "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"), "politics": ("S","天下文臣之宗"), "charisma": ("A","呼風喚雨")}},

        {"id": "matsudasira",    "name": "松平元康",  "faction": "imagawa", "rank": "家老", "lineage": "外樣",  "loyalty": 63,  "loyalty_label": "表面恭敬", "forces": 2000, "location": "dist_06",
         "mil": 82, "str_": 74, "pol": 76, "cha": 75,
         "eval": {"military": ("A","名將之風"), "strategy": ("B","奇謀之將"), "politics": ("B","為政清明"), "charisma": ("B","人望漸隆")}},

        {"id": "okabemotonobu",  "name": "岡部元信",  "faction": "imagawa", "rank": "家老", "lineage": "譜代",  "loyalty": 77,  "loyalty_label": "忠心耿耿", "forces": 2000, "location": "dist_05",
         "mil": 76, "str_": 54, "pol": 57, "cha": 60,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("C","巧舌如簧")}},
    ],
}

FACILITY_UPGRADE = {
    "農業郡": [
        {"level": 1, "name": "村落",  "cost": 0,   "turns": 0, "gold_out": 50,  "supply_out": 10},
        {"level": 2, "name": "農村",  "cost": 100, "turns": 1, "gold_out": 75,  "supply_out": 15},
        {"level": 3, "name": "農莊",  "cost": 300, "turns": 2, "gold_out": 110, "supply_out": 22},
    ],
    "商業郡": [
        {"level": 1, "name": "市集",  "cost": 0,   "turns": 0, "gold_out": 70,  "supply_out": 5},
        {"level": 2, "name": "商街",  "cost": 120, "turns": 1, "gold_out": 112, "supply_out": 8},
        {"level": 3, "name": "行會",  "cost": 360, "turns": 2, "gold_out": 175, "supply_out": 12},
    ],
    "軍事郡": [
        {"level": 1, "name": "駐屯地", "cost": 0,   "turns": 0, "supply_out": 40, "cap_bonus": 0},
        {"level": 2, "name": "兵營",   "cost": 150, "turns": 1, "supply_out": 60, "cap_bonus": 500},
        {"level": 3, "name": "軍陣營", "cost": 400, "turns": 2, "supply_out": 88, "cap_bonus": 1000},
    ],
}

LOYALTY_GRADES = [
    (91, 100, "臣服如山", "#f1c40f"),
    (71,  90, "忠心耿耿", "#27ae60"),
    (51,  70, "表面恭敬", "#3498db"),
    (31,  50, "意圖未明", "#e67e22"),
    (11,  30, "暗懷異志", "#e74c3c"),
    (0,   10, "潛在叛徒", "#8e44ad"),
]

def loyalty_label(val):
    for lo, hi, label, _ in LOYALTY_GRADES:
        if lo <= val <= hi:
            return label
    return "—"

def loyalty_color(val):
    for lo, hi, _, color in LOYALTY_GRADES:
        if lo <= val <= hi:
            return color
    return "#888"
