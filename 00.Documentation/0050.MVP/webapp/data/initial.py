"""
PM006 MVP 初始資料 — 永祿三年・桶狹間前夕
[架構] 城（軍事設施）/ 郡（行政設施）分離，保持 1:1 對應
  城 castle ── 軍事屬性：等級、守備、位置、鄰接
  郡 district ── 行政屬性：類型、設施、年貢、家臣分封
"""

# ── 評定議題池（8 主題輪換） ────────────────────────────────
COUNCIL_TOPICS = [
    {
        "id": "ct_01",
        "title": "是否向今川家發動奇襲？",
        "desc": "今川義元率軍二萬五千沿東海道西進，清洲守備不足三千。各家老意見分歧，主公需作最終裁決。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("主戰派", "我軍雖寡，奇兵可以克敵。不戰而退，士氣必潰！", ["strike"]),
            "niwachoja":      ("主戰派", "桶狹間地勢崎嶇，若伏兵得當，可一擊制勝。",     ["strike"]),
            "kinoshita":      ("中立",   "請容我先探明敵情，再定攻守之策。",              []),
            "maedatoshiie":   ("謹慎",   "末將謹遵主公之命，但兵力確實懸殊。",            ["defend"]),
            "sakumanobumori": ("主戰派", "北方犬山城可作策應，請主公下令！",              ["strike"]),
            "takigawakazumasu":("中立",  "若能整備兵力，方可決一勝負。",                 []),
            "hayashihidesada": ("謹慎",  "兵力差距甚大，老臣以為應以守為主。",           ["defend"]),
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
        "desc": "今川使者到訪，要求織田家獻出那古野城（含那古野郡）以示歸順。此辱難忍，但若拒絕恐激化衝突。",
        "cede_castle": "castle_05",
        "stances": {
            "shibatakatsuie": ("強硬派", "獻城之事，有損主公威名！應即刻驅逐使者！",    ["reject"]),
            "niwachoja":      ("外交派", "可先虛與委蛇，爭取時間整備兵力。",            ["negotiate"]),
            "kinoshita":      ("外交派", "以談拖時，暗中備戰，方為上策。",              ["negotiate"]),
            "maedatoshiie":   ("中立",   "末將一切聽從主公裁量。",                      []),
            "sakumanobumori": ("強硬派", "不戰而屈，犬山武士顏面盡失！",               ["reject"]),
            "takigawakazumasu":("外交派","此時低調應對可爭取備戰時機。",                ["negotiate"]),
            "hayashihidesada": ("謹慎",  "今川勢大，驟然對抗恐招禍端。",               ["negotiate"]),
        },
        "choices": [
            {"id": "reject",    "label": "✕ 拒絕：驅逐使者",   "desc": "強硬宣示不服從"},
            {"id": "negotiate", "label": "📜 談判：虛與委蛇",   "desc": "以外交爭取時間"},
            {"id": "comply",    "label": "🤝 屈服：獻出那古野城", "desc": "喪失那古野城與那古野郡"},
        ],
    },
    {
        "id": "ct_03",
        "title": "小牧山城守備兵力不足",
        "desc": "探子回報，小牧山城守備僅五百人。若敵軍繞路奇攻，恐難堅守，需調兵補防。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("主張補防", "小牧山城是北方屏障，一旦失守清洲門戶大開！", ["reinforce"]),
            "niwachoja":      ("中立",     "補防固然重要，但兵力分散亦有風險。",         []),
            "kinoshita":      ("反對調兵", "此時調兵恐減弱清洲主力，不如加強本城防禦。", ["hold"]),
            "maedatoshiie":   ("主張補防", "末將可率精兵前往支援！",                     ["reinforce"]),
            "sakumanobumori": ("主張補防", "末將願從犬山城調兵策應小牧山！",            ["reinforce"]),
            "takigawakazumasu":("中立",   "需視今川動向而定，不可輕易分兵。",           []),
            "hayashihidesada": ("謹慎",   "分兵之策需謹慎，不宜倉促決定。",            []),
        },
        "choices": [
            {"id": "reinforce", "label": "🪖 調兵：增援小牧山城", "desc": "從清洲調兵補防"},
            {"id": "hold",      "label": "🏯 堅守：集中清洲防禦", "desc": "暫不分兵，固守本城"},
            {"id": "recruit",   "label": "🌾 徵兵：就地補充",     "desc": "命令當地徵集農兵"},
        ],
    },
    {
        "id": "ct_04",
        "title": "商人提議開通津島新商路",
        "desc": "津島豪商提議從津島湊至熱田港開設新商路，每月可增收約 60 金，但需前期投資 200 金。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("反對",   "亂世之際，金錢當用於備兵！",                ["reject"]),
            "niwachoja":      ("支持",   "長遠之計，商路可持續挹注軍費。",            ["approve"]),
            "kinoshita":      ("支持",   "財源廣進方能持久作戰，臣以為應批准。",      ["approve"]),
            "maedatoshiie":   ("中立",   "末將不懂商業，一切聽主公定奪。",            []),
            "sakumanobumori": ("反對",   "亂世財貨不如刀兵，臣反對。",               ["reject"]),
            "takigawakazumasu":("支持",  "津島商業可強化西線後勤。",                 ["approve"]),
            "hayashihidesada": ("支持",  "津島湊乃尾張商業命脈，應善加利用。",       ["approve"]),
        },
        "choices": [
            {"id": "approve", "label": "✓ 批准：投資商路（-200金）", "desc": "每月 +60 金"},
            {"id": "reject",  "label": "✕ 拒絕：暫不投資",           "desc": "保留金錢備戰"},
            {"id": "delay",   "label": "⏳ 延議：再議一月",           "desc": "等待更好時機"},
        ],
    },
    {
        "id": "ct_05",
        "title": "熱田神宮請求修繕資助",
        "desc": "熱田神宮神官來訪，稱宮殿年久失修，請求織田家出資修繕。此舉可提升民心與家臣忠誠度。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("中立",   "神明庇佑固然重要，但當前軍費緊張。",        []),
            "niwachoja":      ("支持",   "資助神宮可提振尾張民心，對主公威望有益。",  ["donate"]),
            "kinoshita":      ("支持",   "民心乃制勝之本，此舉看似花費實則收穫豐。",  ["donate"]),
            "maedatoshiie":   ("中立",   "末將尊重神明，但金錢決定請主公自裁。",      []),
            "sakumanobumori": ("反對",   "戰時修廟，難免有本末倒置之嫌。",           ["refuse"]),
            "takigawakazumasu":("支持",  "熱田神宮乃尾張守護，應予資助。",           ["donate"]),
            "hayashihidesada": ("支持",  "與神宮交好可增強在地豪族向心力。",         ["donate"]),
        },
        "choices": [
            {"id": "donate",  "label": "🎌 資助修繕（-100金）", "desc": "家臣忠誠度 +2"},
            {"id": "partial", "label": "📜 小額資助（-30金）",  "desc": "象徵性支持"},
            {"id": "refuse",  "label": "✕ 婉拒",               "desc": "以軍費緊張為由謝絕"},
        ],
    },
    {
        "id": "ct_06",
        "title": "北方豪族犬山衆請求歸附",
        "desc": "尾張北方的犬山衆（兵力約 600）遣使求降，願以旗下土地歸順織田家，但要求封其家主為「部將」。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("支持",   "犬山衆若歸附可增強北方守備。",             ["accept"]),
            "niwachoja":      ("謹慎",   "投降者是否可靠？臣建議先派人調查。",       ["investigate"]),
            "kinoshita":      ("支持",   "接納外様可展現主公之度量。",               ["accept"]),
            "maedatoshiie":   ("中立",   "末將認為此事由主公決定為宜。",             []),
            "sakumanobumori": ("謹慎",   "身為北方鎮守，末將建議謹慎評估此事。",    ["investigate"]),
            "takigawakazumasu":("支持",  "兵力即是實力，應接納此歸附。",            ["accept"]),
            "hayashihidesada": ("中立",  "外様之心難測，需謹慎。",                  []),
        },
        "choices": [
            {"id": "accept",      "label": "✓ 接納：賜予部將之位", "desc": "新增兵力，但初期忠誠較低"},
            {"id": "investigate", "label": "🥷 調查：先探底細",    "desc": "延後一月，確認誠意"},
            {"id": "reject",      "label": "✕ 婉拒：暫不接納",    "desc": "避免引入潛在隱患"},
        ],
    },
    {
        "id": "ct_07",
        "title": "清洲城馬廄受損需修繕",
        "desc": "清洲城馬廄在上月的暴風雨中受損，騎馬部隊無法正常訓練，需撥款修繕以維持騎兵戰力。",
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("強烈支持", "騎馬乃野戰精銳，馬廄若廢，騎兵戰力大損！",  ["rebuild"]),
            "niwachoja":      ("支持",     "修繕費用不高，而戰力損失難以估量。",          ["rebuild"]),
            "kinoshita":      ("中立",     "馬廄確實需要修繕，但可等商路收益再議。",     []),
            "maedatoshiie":   ("支持",     "末將雖為步兵，亦認為應維護騎兵戰力。",       ["rebuild"]),
            "sakumanobumori": ("強烈支持", "騎兵乃攻守兩用，請主公即刻下令修繕！",      ["rebuild"]),
            "takigawakazumasu":("中立",   "機動力固然重要，但時機需要考量。",           []),
            "hayashihidesada": ("中立",   "老臣以為此事不算緊急，可延後處置。",         []),
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
        "cede_castle": None,
        "stances": {
            "shibatakatsuie": ("強烈主張", "諜探之患不可輕視！應即刻大規模清查！",       ["purge"]),
            "niwachoja":      ("謹慎",     "清查固然必要，但大規模搜查易引起民心不安。",  ["quiet"]),
            "kinoshita":      ("中立",     "臣可暗中調查，無需大動干戈。",               ["quiet"]),
            "maedatoshiie":   ("主張清查", "末將願親率衛兵，徹查可疑人士！",             ["purge"]),
            "sakumanobumori": ("主張清查", "北方邊境亦有異動，應全面清查！",            ["purge"]),
            "takigawakazumasu":("謹慎",   "秘密調查更能抓到真正的間諜。",              ["quiet"]),
            "hayashihidesada": ("謹慎",   "老臣以為擴大搜查只會打草驚蛇。",            ["quiet"]),
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
    "council_decision": None,

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

    # ── 城（軍事設施）── 守備・等級・城主・位置・鄰接 ───────────────
    # chatelain（城主）= 統轄城防的武將（軍事職）
    "castles": [
        # ────────── 尾張國・織田家 ──────────
        {
            "id": "castle_01", "name": "清洲城", "faction": "oda",
            "level": 2, "garrison": 1500, "max_garrison": 2000,
            "province": "尾張國", "is_capital": True, "is_daimyo_home": True,
            "chatelain": "shibatakatsuie",
            "x": 32, "y": 46,
            "adjacent": ["castle_02", "castle_04", "castle_05"],
            "district_id": "district_01",
        },
        {
            "id": "castle_02", "name": "小牧山城", "faction": "oda",
            "level": 1, "garrison": 500, "max_garrison": 1000,
            "province": "尾張國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": "niwachoja",
            "x": 24, "y": 28,
            "adjacent": ["castle_01", "castle_03"],
            "district_id": "district_02",
        },
        {
            "id": "castle_03", "name": "犬山城", "faction": "oda",
            "level": 1, "garrison": 500, "max_garrison": 1000,
            "province": "尾張國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": "sakumanobumori",
            "x": 16, "y": 14,
            "adjacent": ["castle_02"],
            "district_id": "district_03",
        },
        {
            "id": "castle_04", "name": "津島湊", "faction": "oda",
            "level": 1, "garrison": 200, "max_garrison": 500,
            "province": "尾張國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": "hayashihidesada",
            "x": 14, "y": 60,
            "adjacent": ["castle_01", "castle_05"],
            "district_id": "district_04",
        },
        {
            "id": "castle_05", "name": "那古野城", "faction": "oda",
            "level": 1, "garrison": 300, "max_garrison": 1000,
            "province": "尾張國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": "kinoshita",
            "x": 38, "y": 64,
            "adjacent": ["castle_01", "castle_04", "castle_08"],
            "district_id": "district_05",
        },
        # ────────── 三河國・今川家 ──────────
        {
            "id": "castle_06", "name": "岡崎城", "faction": "imagawa",
            "level": 3, "garrison": 2000, "max_garrison": 4000,
            "province": "三河國", "is_capital": True, "is_daimyo_home": False,
            "chatelain": "okabemotonobu",
            "x": 68, "y": 50,
            "adjacent": ["castle_07", "castle_08"],
            "district_id": "district_06",
        },
        {
            "id": "castle_07", "name": "吉田城", "faction": "imagawa",
            "level": 2, "garrison": 1000, "max_garrison": 2000,
            "province": "三河國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": None,
            "x": 80, "y": 36,
            "adjacent": ["castle_06"],
            "district_id": "district_07",
        },
        {
            "id": "castle_08", "name": "大高城", "faction": "imagawa",
            "level": 1, "garrison": 800, "max_garrison": 1000,
            "province": "三河國", "is_capital": False, "is_daimyo_home": False,
            "chatelain": "matsudasira",
            "x": 50, "y": 70,
            "adjacent": ["castle_05", "castle_06"],
            "district_id": "district_08",
        },
    ],

    # ── 郡（行政設施）── 設施・年貢・代官・農業 ───────────────────
    # daikan（代官）= 代理郡務的行政官（行政職，與城主分開）
    "districts": [
        # ────────── 尾張國・織田家 ──────────
        {
            "id": "district_01", "name": "清洲郡", "castle_id": "castle_01",
            "type": "軍事郡", "facility_name": "兵營",
            "facility_level": 2, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 20, "daikan": "shibatakatsuie",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_02", "name": "小牧郡", "castle_id": "castle_02",
            "type": "軍事郡", "facility_name": "駐屯地",
            "facility_level": 1, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 20, "daikan": "maedatoshiie",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_03", "name": "犬山郡", "castle_id": "castle_03",
            "type": "軍事郡", "facility_name": "駐屯地",
            "facility_level": 1, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 20, "daikan": "sakumanobumori",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_04", "name": "津島郡", "castle_id": "castle_04",
            "type": "商業郡", "facility_name": "市集",
            "facility_level": 1, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 20, "daikan": "hayashihidesada",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_05", "name": "那古野郡", "castle_id": "castle_05",
            "type": "商業郡", "facility_name": "市集",
            "facility_level": 1, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 20, "daikan": "takigawakazumasu",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        # ────────── 三河國・今川家 ──────────
        {
            "id": "district_06", "name": "岡崎郡", "castle_id": "castle_06",
            "type": "軍事郡", "facility_name": "軍陣營",
            "facility_level": 3, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 25, "daikan": "okabemotonobu",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_07", "name": "吉田郡", "castle_id": "castle_07",
            "type": "農業郡", "facility_name": "農村",
            "facility_level": 2, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 25, "daikan": None,
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
        {
            "id": "district_08", "name": "大高郡", "castle_id": "castle_08",
            "type": "軍事郡", "facility_name": "駐屯地",
            "facility_level": 1, "facility_max": 3,
            "building": False, "building_turns": 0,
            "nengu_rate": 25, "daikan": "matsudasira",
            "corps_id": None, "farmer_pending": 0, "farmer_incoming": 0,
        },
    ],

    # ── 武將 ─────────────────────────────────────────────────
    "retainers": [
        # ────── 織田家 ──────
        {
            "id": "nobunaga", "name": "織田信長", "faction": "oda",
            "rank": "大名", "lineage": "一門", "loyalty": 100,
            "loyalty_label": "—", "forces": 3000, "location": "castle_01", "corps_id": None,
            "mil": 85, "str_": 82, "pol": 78, "cha": 96,
            "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"),
                     "politics": ("B","為政清明"), "charisma": ("S","魅力無雙")},
        },
        {
            "id": "shibatakatsuie", "name": "柴田勝家", "faction": "oda",
            "rank": "宿老", "lineage": "譜代", "loyalty": 80,
            "loyalty_label": "忠心耿耿", "forces": 3000, "location": "castle_01", "corps_id": None,
            "mil": 92, "str_": 52, "pol": 55, "cha": 72,
            "eval": {"military": ("S","無敵猛將"), "strategy": ("C","聰明機智"),
                     "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")},
        },
        {
            "id": "hayashihidesada", "name": "林秀貞", "faction": "oda",
            "rank": "宿老", "lineage": "譜代", "loyalty": 58,
            "loyalty_label": "表面恭敬", "forces": 800, "location": "castle_04", "corps_id": None,
            "mil": 55, "str_": 58, "pol": 82, "cha": 65,
            "eval": {"military": ("C","嶄露頭角"), "strategy": ("C","聰明機智"),
                     "politics": ("A","治國之能臣"), "charisma": ("B","人望漸隆")},
        },
        {
            "id": "niwachoja", "name": "丹羽長秀", "faction": "oda",
            "rank": "家老", "lineage": "譜代", "loyalty": 78,
            "loyalty_label": "忠心耿耿", "forces": 1500, "location": "castle_02", "corps_id": None,
            "mil": 75, "str_": 76, "pol": 84, "cha": 73,
            "eval": {"military": ("B","頗有勇名"), "strategy": ("B","奇謀之將"),
                     "politics": ("A","治國之能臣"), "charisma": ("B","人望漸隆")},
        },
        {
            "id": "sakumanobumori", "name": "佐久間信盛", "faction": "oda",
            "rank": "家老", "lineage": "譜代", "loyalty": 74,
            "loyalty_label": "忠心耿耿", "forces": 1200, "location": "castle_03", "corps_id": None,
            "mil": 78, "str_": 52, "pol": 45, "cha": 58,
            "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"),
                     "politics": ("D","略有所長"), "charisma": ("C","巧舌如簧")},
        },
        {
            "id": "kinoshita", "name": "木下藤吉郎", "faction": "oda",
            "rank": "家老", "lineage": "外樣", "loyalty": 65,
            "loyalty_label": "表面恭敬", "forces": 1200, "location": "castle_05", "corps_id": None,
            "mil": 58, "str_": 88, "pol": 86, "cha": 90,
            "eval": {"military": ("C","嶄露頭角"), "strategy": ("A","謀略過人"),
                     "politics": ("A","治國之能臣"), "charisma": ("A","呼風喚雨")},
        },
        {
            "id": "takigawakazumasu", "name": "瀧川一益", "faction": "oda",
            "rank": "家老", "lineage": "外樣", "loyalty": 70,
            "loyalty_label": "表面恭敬", "forces": 1000, "location": "castle_05", "corps_id": None,
            "mil": 80, "str_": 78, "pol": 55, "cha": 62,
            "eval": {"military": ("A","名將之風"), "strategy": ("B","奇謀之將"),
                     "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")},
        },
        {
            "id": "maedatoshiie", "name": "前田利家", "faction": "oda",
            "rank": "部將", "lineage": "譜代", "loyalty": 82,
            "loyalty_label": "忠心耿耿", "forces": 800, "location": "castle_02", "corps_id": None,
            "mil": 77, "str_": 55, "pol": 58, "cha": 70,
            "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"),
                     "politics": ("C","能幹之材"), "charisma": ("B","人望漸隆")},
        },
        # ────── 今川家 ──────
        {
            "id": "yoshimoto", "name": "今川義元", "faction": "imagawa",
            "rank": "大名", "lineage": "一門", "loyalty": 100,
            "loyalty_label": "—", "forces": 5000, "location": "castle_06", "corps_id": None,
            "mil": 83, "str_": 84, "pol": 93, "cha": 85,
            "eval": {"military": ("A","名將之風"), "strategy": ("A","謀略過人"),
                     "politics": ("S","天下文臣之宗"), "charisma": ("A","呼風喚雨")},
        },
        {
            "id": "matsudasira", "name": "松平元康", "faction": "imagawa",
            "rank": "家老", "lineage": "外樣", "loyalty": 63,
            "loyalty_label": "表面恭敬", "forces": 2000, "location": "castle_08", "corps_id": None,
            "mil": 82, "str_": 74, "pol": 76, "cha": 75,
            "eval": {"military": ("A","名將之風"), "strategy": ("B","奇謀之將"),
                     "politics": ("B","為政清明"), "charisma": ("B","人望漸隆")},
        },
        {
            "id": "okabemotonobu", "name": "岡部元信", "faction": "imagawa",
            "rank": "家老", "lineage": "譜代", "loyalty": 77,
            "loyalty_label": "忠心耿耿", "forces": 2000, "location": "castle_06", "corps_id": None,
            "mil": 76, "str_": 54, "pol": 57, "cha": 60,
            "eval": {"military": ("B","頗有勇名"), "strategy": ("C","聰明機智"),
                     "politics": ("C","能幹之材"), "charisma": ("C","巧舌如簧")},
        },
    ],

    "corps": [],
}

FACILITY_UPGRADE = {
    "農業郡": [
        {"level": 1, "name": "村落",  "cost": 0,   "turns": 0, "gold_out": 50,  "supply_out": 10},
        {"level": 2, "name": "農村",  "cost": 100, "turns": 1, "gold_out": 80,  "supply_out": 16},
        {"level": 3, "name": "農莊",  "cost": 300, "turns": 2, "gold_out": 120, "supply_out": 24},
    ],
    "商業郡": [
        {"level": 1, "name": "市集",  "cost": 0,   "turns": 0, "gold_out": 80,  "supply_out": 5},
        {"level": 2, "name": "商街",  "cost": 120, "turns": 1, "gold_out": 130, "supply_out": 8},
        {"level": 3, "name": "行會",  "cost": 360, "turns": 2, "gold_out": 200, "supply_out": 12},
    ],
    "軍事郡": [
        {"level": 1, "name": "駐屯地", "cost": 0,   "turns": 0, "supply_out": 40, "cap_bonus": 0},
        {"level": 2, "name": "兵營",   "cost": 150, "turns": 1, "supply_out": 65, "cap_bonus": 500},
        {"level": 3, "name": "軍陣營", "cost": 400, "turns": 2, "supply_out": 95, "cap_bonus": 1000},
    ],
}

LOYALTY_GRADES = [
    (91, 100, "臣服如山", "#f1c40f"),
    (71,  90, "忠心耿耿", "#27ae60"),
    (51,  70, "表面恭敬", "#3498db"),
    (31,  50, "意圖未明", "#e67e22"),
    (11,  30, "暗懷異志", "#e74c3c"),
    (0,   10, "叛意已決", "#922b21"),
]

def loyalty_label(v):
    for lo, hi, label, _ in LOYALTY_GRADES:
        if lo <= v <= hi:
            return label
    return "—"

def loyalty_color(v):
    for lo, hi, _, color in LOYALTY_GRADES:
        if lo <= v <= hi:
            return color
    return "#555"
