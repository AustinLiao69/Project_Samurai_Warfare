GAME_STATE = {
    "date": {"year": 1560, "month": 5},
    "player_faction": "oda",
    "factions": {
        "oda": {
            "id": "oda",
            "name": "織田家",
            "name_kana": "おだけ",
            "daimyo_id": "nobunaga",
            "gold": 500,
            "military_supply": 300,
            "color": "#c0392b",
        },
        "imagawa": {
            "id": "imagawa",
            "name": "今川家",
            "name_kana": "いまがわけ",
            "daimyo_id": "yoshimoto",
            "gold": 800,
            "military_supply": 600,
            "color": "#2980b9",
        },
    },
    "castles": [
        {
            "id": "castle_01", "name": "清洲城", "faction": "oda",
            "level": 2, "garrison": 1000, "max_garrison": 1000,
            "province": "尾張國", "is_capital": True,
            "x": 28, "y": 42,
            "districts": ["dist_01", "dist_02"],
        },
        {
            "id": "castle_02", "name": "小牧山城", "faction": "oda",
            "level": 1, "garrison": 500, "max_garrison": 500,
            "province": "尾張國", "is_capital": False,
            "x": 22, "y": 32,
            "districts": ["dist_03", "dist_04"],
        },
        {
            "id": "castle_03", "name": "岡崎城", "faction": "imagawa",
            "level": 3, "garrison": 1500, "max_garrison": 1500,
            "province": "三河國", "is_capital": True,
            "x": 62, "y": 50,
            "districts": ["dist_05", "dist_06"],
        },
        {
            "id": "castle_04", "name": "吉田城", "faction": "imagawa",
            "level": 1, "garrison": 1000, "max_garrison": 500,
            "province": "三河國", "is_capital": False,
            "x": 75, "y": 38,
            "districts": ["dist_07", "dist_08"],
        },
    ],
    "districts": [
        {"id": "dist_01", "name": "清洲西郡", "castle": "castle_01", "type": "商業郡", "facility": "市集", "facility_level": 1, "nengu_rate": 20, "retainer": "niwachoja"},
        {"id": "dist_02", "name": "那古野郡", "castle": "castle_01", "type": "軍事郡", "facility": "駐屯地", "facility_level": 1, "nengu_rate": 20, "retainer": "shibatakatsuie"},
        {"id": "dist_03", "name": "春日井郡", "castle": "castle_02", "type": "農業郡", "facility": "村落", "facility_level": 1, "nengu_rate": 20, "retainer": "kinoshita"},
        {"id": "dist_04", "name": "丹羽郡",   "castle": "castle_02", "type": "農業郡", "facility": "村落", "facility_level": 1, "nengu_rate": 20, "retainer": "maedatoshiie"},
        {"id": "dist_05", "name": "額田郡",   "castle": "castle_03", "type": "軍事郡", "facility": "駐屯地", "facility_level": 2, "nengu_rate": 25, "retainer": "okabemotonobu"},
        {"id": "dist_06", "name": "碧海郡",   "castle": "castle_03", "type": "農業郡", "facility": "農村", "facility_level": 2, "nengu_rate": 25, "retainer": None},
        {"id": "dist_07", "name": "渥美郡",   "castle": "castle_04", "type": "農業郡", "facility": "村落", "facility_level": 1, "nengu_rate": 25, "retainer": None},
        {"id": "dist_08", "name": "寶飯郡",   "castle": "castle_04", "type": "商業郡", "facility": "市集", "facility_level": 1, "nengu_rate": 25, "retainer": None},
    ],
    "retainers": [
        {
            "id": "nobunaga", "name": "織田信長", "faction": "oda",
            "rank": "大名", "lineage": "一門",
            "loyalty_label": "—", "loyalty_value": 100,
            "forces": 5000,
            "location": "castle_01",
            "eval": {"military": ("A", "名將之風"), "strategy": ("A", "謀略過人"), "politics": ("B", "為政清明"), "charisma": ("S", "魅力無雙")},
        },
        {
            "id": "shibatakatsuie", "name": "柴田勝家", "faction": "oda",
            "rank": "宿老", "lineage": "譜代",
            "loyalty_label": "忠心耿耿", "loyalty_value": 80,
            "forces": 4000,
            "location": "dist_02",
            "eval": {"military": ("S", "無敵猛將"), "strategy": ("C", "聰明機智"), "politics": ("C", "能幹之材"), "charisma": ("B", "人望漸隆")},
        },
        {
            "id": "niwachoja", "name": "丹羽長秀", "faction": "oda",
            "rank": "家老", "lineage": "譜代",
            "loyalty_label": "忠心耿耿", "loyalty_value": 78,
            "forces": 2000,
            "location": "dist_01",
            "eval": {"military": ("B", "頗有勇名"), "strategy": ("B", "奇謀之將"), "politics": ("A", "治國之能臣"), "charisma": ("B", "人望漸隆")},
        },
        {
            "id": "kinoshita", "name": "木下藤吉郎", "faction": "oda",
            "rank": "家老", "lineage": "外樣",
            "loyalty_label": "表面恭敬", "loyalty_value": 65,
            "forces": 2000,
            "location": "dist_03",
            "eval": {"military": ("C", "嶄露頭角"), "strategy": ("A", "謀略過人"), "politics": ("A", "治國之能臣"), "charisma": ("A", "呼風喚雨")},
        },
        {
            "id": "maedatoshiie", "name": "前田利家", "faction": "oda",
            "rank": "部將", "lineage": "譜代",
            "loyalty_label": "忠心耿耿", "loyalty_value": 82,
            "forces": 1000,
            "location": "dist_04",
            "eval": {"military": ("B", "頗有勇名"), "strategy": ("C", "聰明機智"), "politics": ("C", "能幹之材"), "charisma": ("B", "人望漸隆")},
        },
        {
            "id": "yoshimoto", "name": "今川義元", "faction": "imagawa",
            "rank": "大名", "lineage": "一門",
            "loyalty_label": "—", "loyalty_value": 100,
            "forces": 5000,
            "location": "castle_03",
            "eval": {"military": ("A", "名將之風"), "strategy": ("A", "謀略過人"), "politics": ("S", "天下文臣之宗"), "charisma": ("A", "呼風喚雨")},
        },
        {
            "id": "matsudasira", "name": "松平元康", "faction": "imagawa",
            "rank": "家老", "lineage": "外樣",
            "loyalty_label": "表面恭敬", "loyalty_value": 63,
            "forces": 2000,
            "location": "dist_06",
            "eval": {"military": ("A", "名將之風"), "strategy": ("B", "奇謀之將"), "politics": ("B", "為政清明"), "charisma": ("B", "人望漸隆")},
        },
        {
            "id": "okabemotonobu", "name": "岡部元信", "faction": "imagawa",
            "rank": "家老", "lineage": "譜代",
            "loyalty_label": "忠心耿耿", "loyalty_value": 77,
            "forces": 2000,
            "location": "dist_05",
            "eval": {"military": ("B", "頗有勇名"), "strategy": ("C", "聰明機智"), "politics": ("C", "能幹之材"), "charisma": ("C", "巧舌如簧")},
        },
    ],
}

LOYALTY_GRADES = {
    "臣服如山": (91, 100, "#f1c40f"),
    "忠心耿耿": (71, 90, "#27ae60"),
    "表面恭敬": (51, 70, "#3498db"),
    "意圖未明": (31, 50, "#e67e22"),
    "暗懷異志": (11, 30, "#e74c3c"),
    "潛在叛徒": (0, 10, "#8e44ad"),
}

POLITICS_MENU = [
    {"id": 1, "name": "家臣管理", "icon": "👤", "sub": ["任命官職", "晉升武將", "知行分配", "家臣廢黜"]},
    {"id": 2, "name": "領地治理", "icon": "🏯", "sub": ["設施升級", "年貢調整", "開墾農田", "郡城巡視"]},
    {"id": 3, "name": "軍事行動", "icon": "⚔️",  "sub": ["徵集農兵", "出兵攻打", "調防部隊", "返還農民"]},
    {"id": 4, "name": "外交談判", "icon": "📜", "sub": ["結盟談判", "宣戰通告", "和議談判", "送質子"]},
    {"id": 5, "name": "情報活動", "icon": "🥷", "sub": ["派遣忍者", "收集情報", "召回忍者", "設置防諜"]},
    {"id": 6, "name": "評定會議", "icon": "🏛️", "sub": ["召開評議", "頒布法令", "繼承宣告", "分封領地"]},
    {"id": 7, "name": "儀式典禮", "icon": "🎌", "sub": ["舉行慶典", "祭祀神明", "茶道接待"]},
    {"id": 8, "name": "戰後處置", "icon": "🗡️",  "sub": ["領地處置", "收編武將", "封賞功臣"]},
    {"id": 9, "name": "結束回合", "icon": "⏭️", "sub": []},
]

def get_faction_total_forces(faction_id):
    return sum(r["forces"] for r in GAME_STATE["retainers"] if r["faction"] == faction_id)

def get_loyalty_color(value):
    if value >= 91: return "#f1c40f"
    if value >= 71: return "#27ae60"
    if value >= 51: return "#3498db"
    if value >= 31: return "#e67e22"
    if value >= 11: return "#e74c3c"
    return "#8e44ad"
