"""
PM008 MVP 初始資料 — 永祿三年・桶狹間前夕
"""

# ── 評定議題池（Feedback 4：多主題）──────────────────────────
COUNCIL_TOPICS = [
    {
        "id": "ct_01",
        "title": "是否向今川家發動奇襲？",
        "desc": "今川義元率軍二萬五千沿東海道西進，清洲守備不足三千。各家老意見分歧，主公需作最終裁決。",
        "stances": {
            "shibatakatsuie": ("主戰派", "我軍雖寡，奇兵可以克敵。不戰而退，士氣必潰！", ["strike"]),
            "niwachoja":      ("主戰派", "桶狹間地勢崎嶇，若伏兵得當，可一擊制勝。",      ["strike"]),
            "kinoshita":      ("中立",   "請容我先探明敵情，再定攻守之策。",               []),
            "maedatoshiie":   ("謹慎",   "末將謹遵主公之命，但兵力確實懸殊。",             ["defend"]),
        },
        "choices": [
            {"id": "strike", "label": "⚔ 裁決：出兵奇襲", "desc": "以少擊多，奇取今川"},
            {"id": "defend", "label": "🏯 裁決：固守清洲", "desc": "堅守城池，以逸待勞"},
            {"id": "delay",  "label": "⏳ 延議：再觀一月", "desc": "靜觀其變，蒐集情報"},
        ],
    },
    {
        "id": "ct_02",
        "title": "今川義元遣使要求獻城",
        "desc": "今川使者到訪，要求織田家獻出小牧山城以示歸順。此辱難忍，但若拒絕恐激化衝突。",
        "stances": {
            "shibatakatsuie": ("強硬派", "獻城之事，有損主公威名！應即刻驅逐使者！",     ["reject"]),
            "niwachoja":      ("外交派", "可先虛與委蛇，爭取時間整備兵力。",             ["negotiate"]),
            "kinoshita":      ("外交派", "以談拖時，暗中備戰，方為上策。",               ["negotiate"]),
            "maedatoshiie":   ("中立",   "末將一切聽從主公裁量。",                       []),
        },
        "choices": [
            {"id": "reject",     "label": "✕ 拒絕：驅逐使者",   "desc": "強硬宣示不服從"},
            {"id": "negotiate",  "label": "📜 談判：虛與委蛇",   "desc": "以外交爭取時間"},
            {"id": "comply",     "label": "🤝 屈服：暫時妥協",   "desc": "保存實力，伺機再起"},
        ],
    },
    {
        "id": "ct_03",
        "title": "稻荷山城守備兵力不足",
        "desc": "探子來報，小牧山城（別名稻荷山城）守備僅五百人，若敵軍繞路奇攻，恐難堅守。需調兵補防。",
        "stances": {
            "shibatakatsuie": ("主張補防", "小牧山城是北方屏障，一旦失守清洲門戶大開！",  ["reinforce"]),
            "niwachoja":      ("中立",     "補防固然重要，但兵力分散亦有風險。",          []),
            "kinoshita":      ("反對調兵", "此時調兵恐減弱清洲主力，不如加強清洲本城防禦。", ["hold"]),
            "maedatoshiie":   ("主張補防", "末將可率千人前往支援！",                      ["reinforce"]),
        },
        "choices": [
            {"id": "reinforce", "label": "🪖 調兵：增援小牧山城", "desc": "從清洲調兵 500 人"},
            {"id": "hold",      "label": "🏯 堅守：集中清洲防禦", "desc": "暫不分兵，固守本城"},
            {"id": "recruit",   "label": "🌾 徵兵：就地補充",     "desc": "命令當地徵集農兵"},
        ],
    },
    {
        "id": "ct_04",
        "title": "商人提議開通新貿易路線",
        "desc": "尾張豪商伊藤屋提議，從清洲通往熱田港開設新商路，每月可增收約 50 金，但需前期投資 200 金。",
        "stances": {
            "shibatakatsuie": ("反對",   "亂世之際，金錢當用於備兵，商路之事等太平再議！", ["reject"]),
            "niwachoja":      ("支持",   "此乃長遠之計，商路可持續挹注軍費。",            ["approve"]),
            "kinoshita":      ("支持",   "主公，財源廣進方能持久作戰，臣以為應批准。",    ["approve"]),
            "maedatoshiie":   ("中立",   "末將不懂商業之事，一切聽主公定奪。",            []),
        },
        "choices": [
            {"id": "approve", "label": "✓ 批准：投資商路（-200金）", "desc": "每月 +50 金，3 月後回本"},
            {"id": "reject",  "label": "✕ 拒絕：暫不投資",           "desc": "保留金錢備戰"},
            {"id": "delay",   "label": "⏳ 延議：再議一月",           "desc": "等待更好時機"},
        ],
    },
    {
        "id": "ct_05",
        "title": "熱田神宮請求修繕資助",
        "desc": "熱田神宮神官來訪，稱宮殿年久失修，請求織田家出資修繕。此舉可提升民心與家臣忠誠度。",
        "stances": {
            "shibatakatsuie": ("中立",   "神明庇佑固然重要，但當前軍費緊張，難以兼顧。", []),
            "niwachoja":      ("支持",   "資助神宮可提振尾張民心，對主公威望有益。",      ["donate"]),
            "kinoshita":      ("支持",   "民心乃制勝之本，此舉看似花費，實則收穫頗豐。",  ["donate"]),
            "maedatoshiie":   ("中立",   "末將尊重神明，但金錢決定請主公自裁。",          []),
        },
        "choices": [
            {"id": "donate",  "label": "🎌 資助修繕（-100金）", "desc": "家臣忠誠度 +2，民心提升"},
            {"id": "partial", "label": "📜 小額資助（-30金）",  "desc": "象徵性支持"},
            {"id": "refuse",  "label": "✕ 婉拒",               "desc": "以軍費緊張為由謝絕"},
        ],
    },
    {
        "id": "ct_06",
        "title": "地方豪族願意投靠",
        "desc": "尾張北方的小豪族犬山衆（兵力約 500）遣使求降，願以旗下土地歸順織田家，但要求封其家主為「部將」。",
        "stances": {
            "shibatakatsuie": ("支持",   "兵力即是實力，犬山衆若歸附可增強北方守備。",    ["accept"]),
            "niwachoja":      ("謹慎",   "投降者是否可靠？臣建議先派人調查底細。",        ["investigate"]),
            "kinoshita":      ("支持",   "接納外様可展現主公之度量，有助招攬人才。",      ["accept"]),
            "maedatoshiie":   ("中立",   "末將認為此事由主公決定為宜。",                  []),
        },
        "choices": [
            {"id": "accept",      "label": "✓ 接納：賜予部將之位", "desc": "新增 500 兵力，但忠誠初期較低"},
            {"id": "investigate", "label": "🥷 調查：先探底細",    "desc": "延後一月，確認誠意"},
            {"id": "reject",      "label": "✕ 婉拒：暫不接納",    "desc": "避免引入潛在隱患"},
        ],
    },
    {
        "id": "ct_07",
        "title": "織田家馬廄需要重建",
        "desc": "清洲城馬廄在上月的暴風雨中受損，騎馬部隊無法正常訓練，需撥款修繕以維持騎兵戰力。",
        "stances": {
            "shibatakatsuie": ("強烈支持", "騎馬乃野戰之精銳，馬廄若廢，騎兵戰力大損！",  ["rebuild"]),
            "niwachoja":      ("支持",     "修繕費用不高，而戰力損失難以估量，應儘速修繕。", ["rebuild"]),
            "kinoshita":      ("中立",     "馬廄確實需要修繕，但可等商路收益再議。",       []),
            "maedatoshiie":   ("支持",     "末將雖為步兵將領，亦認為應維護騎兵戰力。",     ["rebuild"]),
        },
        "choices": [
            {"id": "rebuild",   "label": "🐴 立即修繕（-80金）",  "desc": "下月騎兵戰力恢復"},
            {"id": "temporary", "label": "🔨 臨時修補（-20金）",  "desc": "維持部分騎兵能力"},
            {"id": "delay",     "label": "⏳ 延後修繕",           "desc": "本月無法調動騎兵"},
        ],
    },
    {
        "id": "ct_08",
        "title": "今川間諜潛入尾張",
        "desc": "密探來報，疑似有今川家臥底滲入清洲城附近，蒐集我方兵力情報。是否展開清查行動？",
        "stances": {
            "shibatakatsuie": ("強烈主張", "諜探之患不可輕視！應即刻展開大規模清查！",     ["purge"]),
            "niwachoja":      ("謹慎",     "清查固然必要，但大規模搜查易引起民心不安。",   ["quiet"]),
            "kinoshita":      ("中立",     "臣可暗中調查，無需大動干戈。",                ["quiet"]),
            "maedatoshiie":   ("主張清查", "末將願親率衛兵，徹查可疑人士！",              ["purge"]),
        },
        "choices": [
            {"id": "purge",  "label": "🔍 大規模清查", "desc": "驅逐間諜，但民心稍有不安"},
            {"id": "quiet",  "label": "🥷 秘密調查",   "desc": "低調處理，保持民心穩定"},
            {"id": "ignore", "label": "⚠ 暫且不管",    "desc": "情報可能繼續外洩"},
        ],
    },
]


INITIAL_STATE = {
    "date": {"year": 1560, "month": 5},
    "player_faction": "oda",
    "turn": 1,
    "log": [],
    "council_decision": None,   # 本回合裁決紀錄

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
        {"id": "castle_01", "name": "清洲城",  "faction": "oda",     "level": 2, "garrison": 1000, "max_garrison": 1000, "province": "尾張國", "is_capital": True,  "x": 28, "y": 44, "districts": ["dist_01", "dist_02"]},
        {"id": "castle_02", "name": "小牧山城","faction": "oda",     "level": 1, "garrison": 500,  "max_garrison": 500,  "province": "尾張國", "is_capital": False, "x": 22, "y": 30, "districts": ["dist_03", "dist_04"]},
        {"id": "castle_03", "name": "岡崎城",  "faction": "imagawa", "level": 3, "garrison": 1500, "max_garrison": 1500, "province": "三河國", "is_capital": True,  "x": 62, "y": 50, "districts": ["dist_05", "dist_06"]},
        {"id": "castle_04", "name": "吉田城",  "faction": "imagawa", "level": 1, "garrison": 1000, "max_garrison": 500,  "province": "三河國", "is_capital": False, "x": 75, "y": 36, "districts": ["dist_07", "dist_08"]},
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
        {"id": "nobunaga",       "name": "織田信長",  "faction": "oda",     "rank": "大名", "lineage": "一門",  "loyalty": 100, "loyalty_label": "—",       "forces": 5000, "location": "castle_01", "corps_id": None,
         "mil": 85, "str_": 82, "pol": 78, "cha": 96,
         "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"), "politics": ("B","為政清明"), "charisma": ("S","魅力無雙")}},

        {"id": "shibatakatsuie", "name": "柴田勝家",  "faction": "oda",     "rank": "宿老", "lineage": "譜代",  "loyalty": 80,  "loyalty_label": "忠心耿耿", "forces": 4000, "location": "dist_02",   "corps_id": None,
         "mil": 92, "str_": 52, "pol": 55, "cha": 72,
         "eval": {"military": ("S","無敵猛將"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")}},

        {"id": "niwachoja",      "name": "丹羽長秀",  "faction": "oda",     "rank": "家老", "lineage": "譜代",  "loyalty": 78,  "loyalty_label": "忠心耿耿", "forces": 2000, "location": "dist_01",   "corps_id": None,
         "mil": 75, "str_": 76, "pol": 84, "cha": 73,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("B","奇謀之將"), "politics": ("A","治國之能臣"), "charisma": ("B","人望漸隆")}},

        {"id": "kinoshita",      "name": "木下藤吉郎", "faction": "oda",    "rank": "家老", "lineage": "外樣",  "loyalty": 65,  "loyalty_label": "表面恭敬", "forces": 2000, "location": "dist_03",   "corps_id": None,
         "mil": 58, "str_": 88, "pol": 86, "cha": 90,
         "eval": {"military": ("C","嶄露頭角"), "strategy": ("A","謀略過人"), "politics": ("A","治國之能臣"), "charisma": ("A","呼風喚雨")}},

        {"id": "maedatoshiie",   "name": "前田利家",  "faction": "oda",     "rank": "部將", "lineage": "譜代",  "loyalty": 82,  "loyalty_label": "忠心耿耿", "forces": 1000, "location": "dist_04",   "corps_id": None,
         "mil": 77, "str_": 55, "pol": 58, "cha": 70,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")}},

        {"id": "yoshimoto",      "name": "今川義元",  "faction": "imagawa", "rank": "大名", "lineage": "一門",  "loyalty": 100, "loyalty_label": "—",       "forces": 5000, "location": "castle_03", "corps_id": None,
         "mil": 83, "str_": 84, "pol": 93, "cha": 85,
         "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"), "politics": ("S","天下文臣之宗"), "charisma": ("A","呼風喚雨")}},

        {"id": "matsudasira",    "name": "松平元康",  "faction": "imagawa", "rank": "家老", "lineage": "外樣",  "loyalty": 63,  "loyalty_label": "表面恭敬", "forces": 2000, "location": "dist_06",   "corps_id": None,
         "mil": 82, "str_": 74, "pol": 76, "cha": 75,
         "eval": {"military": ("A","名將之風"), "strategy": ("B","奇謀之將"), "politics": ("B","為政清明"), "charisma": ("B","人望漸隆")}},

        {"id": "okabemotonobu",  "name": "岡部元信",  "faction": "imagawa", "rank": "家老", "lineage": "譜代",  "loyalty": 77,  "loyalty_label": "忠心耿耿", "forces": 2000, "location": "dist_05",   "corps_id": None,
         "mil": 76, "str_": 54, "pol": 57, "cha": 60,
         "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"), "politics": ("C","能幹之材"), "charisma": ("C","巧舌如簧")}},
    ],

    # 家臣團（Feedback 2）— 初始為空，由玩家自行組建
    "corps": [],
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
