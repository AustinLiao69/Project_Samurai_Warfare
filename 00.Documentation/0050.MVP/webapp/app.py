import sys, os, copy, json, uuid
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request, redirect, url_for
from data.initial import INITIAL_STATE, FACILITY_UPGRADE, loyalty_color, COUNCIL_TOPICS
from game.logic import (
    process_turn, upgrade_facility, set_nengu,
    resolve_battle, resolve_siege, mobilize_troops,
    calc_district_output, apply_council_decision,
)

app = Flask(__name__)
app.secret_key = "sengoku-mvp-2026"

_state = copy.deepcopy(INITIAL_STATE)

# ── 工具函數 ────────────────────────────────────────────────

def gs():
    return _state

def get_district(did):
    return next((d for d in gs()["districts"] if d["id"] == did), None)

def get_castle(cid):
    return next((c for c in gs()["castles"] if c["id"] == cid), None)

def get_retainer(rid):
    return next((r for r in gs()["retainers"] if r["id"] == rid), None)

def faction_castles(faction_id):
    return [c for c in gs()["castles"] if c["faction"] == faction_id]

def faction_districts(faction_id):
    cids = {c["id"] for c in faction_castles(faction_id)}
    return [d for d in gs()["districts"] if d["castle"] in cids]

def total_forces(faction_id):
    return sum(r["forces"] for r in gs()["retainers"] if r["faction"] == faction_id)

def next_upgrade_spec(d):
    nxt = d["facility_level"] + 1
    return next((r for r in FACILITY_UPGRADE.get(d["type"], []) if r["level"] == nxt), None)

def current_topic():
    """回合號決定當前議題（輪換）"""
    idx = (gs()["turn"] - 1) % len(COUNCIL_TOPICS)
    return COUNCIL_TOPICS[idx]

def get_advisor():
    """取得玩家的主要直臣（最高忠誠度的宿老/家老）"""
    s = gs()
    pf = s["player_faction"]
    direct = [r for r in s["retainers"]
              if r["faction"] == pf
              and r["rank"] in ("宿老", "家老")
              and r.get("corps_id") is None]
    if not direct:
        direct = [r for r in s["retainers"] if r["faction"] == pf and r["rank"] != "大名"]
    return max(direct, key=lambda r: r["loyalty"]) if direct else None

def corps_map_for_retainers():
    """回傳 {retainer_id: {corps_id, corps_name, is_leader}} 的映射"""
    result = {}
    for corps in gs().get("corps", []):
        result[corps["leader"]] = {
            "corps_id":   corps["id"],
            "corps_name": corps["name"],
            "is_leader":  True,
        }
        for mid in corps.get("members", []):
            result[mid] = {
                "corps_id":   corps["id"],
                "corps_name": corps["name"],
                "is_leader":  False,
            }
    return result

# 政務選單分類 + 子選項（Feedback 1+5）
POLITICS_CATEGORIES = [
    {
        "id": "military",
        "icon": "⚔",
        "name": "軍事行動",
        "hint": "徵兵・出兵・調防",
        "subs": [
            {"name": "徵集農兵",  "desc": "從郡縣徵集農民兵（需 1 月訓練）",  "enabled": True,  "url": "/territory"},
            {"name": "出兵攻打",  "desc": "在地圖選擇目標郡發動攻擊",        "enabled": True,  "url": "/"},
            {"name": "調防部隊",  "desc": "調整各城守備兵力配置",            "enabled": False, "toast": ""},
            {"name": "返還農民",  "desc": "解散農兵還田，恢復農業生產",       "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "territory",
        "icon": "🏯",
        "name": "領地治理",
        "hint": "設施・年貢・開墾",
        "subs": [
            {"name": "設施升級",  "desc": "提升郡縣設施等級增加產出",         "enabled": True,  "url": "/territory"},
            {"name": "年貢調整",  "desc": "調整各郡年貢率（10%~60%）",        "enabled": True,  "url": "/territory"},
            {"name": "開墾農田",  "desc": "開發荒地，增加農業郡產能",         "enabled": False, "toast": ""},
            {"name": "郡城巡視",  "desc": "視察領地，提升民心與忠誠度",       "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "retainer",
        "icon": "👤",
        "name": "家臣管理",
        "hint": "任命・晉升・家臣團",
        "subs": [
            {"name": "成立家臣團", "desc": "組建家臣團，委託首領統治領地",    "enabled": True,  "url": "/retainers?tab=corps"},
            {"name": "知行分配",   "desc": "將郡縣知行地分封給家臣",          "enabled": True,  "url": "/retainers"},
            {"name": "任命官職",   "desc": "調整家臣的官位與職責",            "enabled": False, "toast": ""},
            {"name": "家臣廢黜",   "desc": "剝奪家臣知行，迫其離去",          "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "diplomacy",
        "icon": "📜",
        "name": "外交談判",
        "hint": "結盟・宣戰・和議",
        "subs": [
            {"name": "結盟談判",  "desc": "與其他勢力締結同盟",              "enabled": False, "toast": ""},
            {"name": "宣戰通告",  "desc": "正式向敵對勢力宣戰",              "enabled": False, "toast": ""},
            {"name": "和議談判",  "desc": "與交戰勢力展開和平談判",          "enabled": False, "toast": ""},
            {"name": "送質子",    "desc": "以人質鞏固同盟關係",              "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "intel",
        "icon": "🥷",
        "name": "情報活動",
        "hint": "忍者・諜報・反諜",
        "subs": [
            {"name": "派遣忍者",  "desc": "派遣忍者滲透敵方收集情報",        "enabled": False, "toast": ""},
            {"name": "收集情報",  "desc": "了解敵方兵力與動向",              "enabled": False, "toast": ""},
            {"name": "召回忍者",  "desc": "召回潛伏中的忍者",               "enabled": False, "toast": ""},
            {"name": "設置防諜",  "desc": "加強本國反間諜防禦",              "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "council",
        "icon": "🏛",
        "name": "評定會議",
        "hint": "召議・評定・裁決",
        "subs": [
            {"name": "召開評議",  "desc": "召集家老評議本月重要事項",        "enabled": True,  "url": "/council"},
            {"name": "頒布法令",  "desc": "頒布政令，影響民心與生產",        "enabled": False, "toast": ""},
            {"name": "繼承宣告",  "desc": "宣告繼承人，影響家臣忠誠",        "enabled": False, "toast": ""},
            {"name": "分封領地",  "desc": "正式分封領地給家臣團",            "enabled": True,  "url": "/retainers?tab=corps"},
        ],
    },
    {
        "id": "ceremony",
        "icon": "🎌",
        "name": "儀式典禮",
        "hint": "慶典・祭祀・茶道",
        "subs": [
            {"name": "舉行慶典",  "desc": "舉辦慶祝活動提升家臣士氣",        "enabled": False, "toast": ""},
            {"name": "祭祀神明",  "desc": "祭祀神明，祈求戰場勝利",          "enabled": False, "toast": ""},
            {"name": "茶道接待",  "desc": "接待武將，增進感情與忠誠",        "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "postwar",
        "icon": "🗡",
        "name": "戰後處置",
        "hint": "領地・收編・封賞",
        "subs": [
            {"name": "領地處置",  "desc": "決定佔領領地的歸屬",              "enabled": False, "toast": ""},
            {"name": "收編武將",  "desc": "招攬敵方降將加入己方",            "enabled": False, "toast": ""},
            {"name": "封賞功臣",  "desc": "賞賜有功武將，提升忠誠度",        "enabled": False, "toast": ""},
        ],
    },
    {
        "id": "endturn",
        "icon": "⏭",
        "name": "結束本月",
        "hint": "進入下一回合",
        "subs": [],
    },
]

# ── 頁面路由 ────────────────────────────────────────────────

@app.route("/")
def index():
    s = gs()
    return render_template("index.html",
        state=s,
        oda_forces=total_forces("oda"),
        imagawa_forces=total_forces("imagawa"),
        active="map",
        loyalty_color=loyalty_color,
    )

@app.route("/territory")
def territory():
    s = gs()
    pf = s["player_faction"]
    pcastles = [c for c in s["castles"] if c["faction"] == pf]
    castle_districts = {}
    outputs = {}
    for c in pcastles:
        dists = [d for d in s["districts"] if d["castle"] == c["id"]]
        castle_districts[c["id"]] = dists
        for d in dists:
            outputs[d["id"]] = calc_district_output(d)
    return render_template("territory.html",
        state=s,
        player_castles=pcastles,
        castle_districts=castle_districts,
        outputs=outputs,
        active="territory",
    )

@app.route("/retainers")
@app.route("/retainers/<faction_id>")
def retainers(faction_id="oda"):
    s = gs()
    ret = [r for r in s["retainers"] if r["faction"] == faction_id]
    pf  = s["player_faction"]
    cmap = corps_map_for_retainers()

    # 直臣：rank=宿老/家老 且 corps_id=None
    direct_retainers = [r for r in s["retainers"]
                        if r["faction"] == pf
                        and r["rank"] in ("宿老", "家老")
                        and r.get("corps_id") is None
                        and r["rank"] != "大名"]

    player_castles = [c for c in s["castles"] if c["faction"] == pf]

    corps_list = s.get("corps", [])
    leader_map = {r["id"]: r for r in s["retainers"]}

    tab = request.args.get("tab", "retainers")

    return render_template("retainers.html",
        state=s, retainers=ret, faction_id=faction_id,
        loyalty_color=loyalty_color, active="retainers",
        corps_map=cmap, corps_list=corps_list,
        direct_retainers=direct_retainers,
        player_castles=player_castles,
        leader_map=leader_map,
        tab=tab,
    )

@app.route("/politics")
def politics():
    s = gs()
    advisor = get_advisor()
    cats_json = json.dumps(POLITICS_CATEGORIES)
    return render_template("politics.html",
        state=s,
        categories=POLITICS_CATEGORIES,
        categories_json=POLITICS_CATEGORIES,
        advisor=advisor or {"name": "柴田勝家", "rank": "宿老", "lineage": "譜代", "loyalty": 80, "loyalty_label": "忠心耿耿"},
        loyalty_color=loyalty_color,
        active="politics",
    )

@app.route("/council")
def council():
    s = gs()
    topic = current_topic()
    cr = [r for r in s["retainers"]
          if r["faction"] == "oda" and r["rank"] in ("宿老", "家老")]
    # topic_stances_json: {retainer_id: [stance_label, agree_with]}
    stances_for_js = {}
    for rid, (stance, comment, agree_with) in topic["stances"].items():
        stances_for_js[rid] = {"stance": stance, "agree_with": agree_with}

    return render_template("council.html",
        state=s,
        topic=topic,
        topics_total=len(COUNCIL_TOPICS),
        council_retainers=cr,
        topic_stances_json=stances_for_js,
        active="council",
    )

# ── API — End Turn ──────────────────────────────────────────

@app.route("/api/end-turn", methods=["POST"])
def api_end_turn():
    global _state
    _state, log = process_turn(_state)
    # 回合結束，重置本月裁決
    _state["council_decision"] = None
    return jsonify({"ok": True, "log": log, "state": _summarize()})

# ── API — District ──────────────────────────────────────────

@app.route("/api/district/<did>")
def api_district(did):
    d = get_district(did)
    if not d:
        return jsonify({"error": "not found"}), 404
    s = gs()
    castle  = next((c for c in s["castles"] if c["id"] == d["castle"]), {})
    retainer = get_retainer(d["retainer"]) if d.get("retainer") else None
    spec    = next_upgrade_spec(d)
    output  = calc_district_output(d)

    # 確認是否有家臣團管轄
    corps_info = None
    for corps in s.get("corps", []):
        if castle.get("id") in corps.get("territories", []):
            leader = get_retainer(corps["leader"])
            corps_info = {"corps_name": corps["name"], "leader_name": leader["name"] if leader else ""}
            break

    return jsonify({
        "district": d,
        "castle_name": castle.get("name", ""),
        "castle_faction": castle.get("faction", ""),
        "castle_data": castle,
        "retainer": retainer,
        "next_upgrade": spec,
        "output": output,
        "player_gold": s["factions"][s["player_faction"]]["gold"],
        "corps_info": corps_info,
    })

@app.route("/api/district/<did>/upgrade", methods=["POST"])
def api_upgrade(did):
    global _state
    result, msg = upgrade_facility(_state, did)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    return jsonify({"ok": True, "msg": msg, "state": _summarize()})

@app.route("/api/district/<did>/nengu", methods=["POST"])
def api_nengu(did):
    global _state
    rate = request.json.get("rate", 20)
    result, msg = set_nengu(_state, did, rate)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    output = calc_district_output(get_district(did))
    return jsonify({"ok": True, "msg": msg, "output": output, "state": _summarize()})

# ── API — Castle ────────────────────────────────────────────

@app.route("/api/castle/<cid>")
def api_castle(cid):
    s = gs()
    castle = get_castle(cid)
    if not castle:
        return jsonify({"error": "not found"}), 404
    faction  = s["factions"].get(castle["faction"], {})
    districts = [d for d in s["districts"] if d["castle"] == cid]
    return jsonify({
        "castle": castle,
        "faction_name": faction.get("name", castle["faction"]),
        "districts": districts,
    })

# ── API — Mobilize ──────────────────────────────────────────

@app.route("/api/mobilize", methods=["POST"])
def api_mobilize():
    global _state
    data  = request.json or {}
    did   = data.get("district_id")
    mtype = data.get("type", "city")
    d     = get_district(did)
    if not d:
        return jsonify({"ok": False, "msg": "找不到郡"})
    s  = gs()
    pf = s["player_faction"]
    castle = get_castle(d["castle"])
    if not castle or castle["faction"] != pf:
        return jsonify({"ok": False, "msg": "此郡非我方領地"})
    result, msg = mobilize_troops(_state, did, mtype)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    return jsonify({"ok": True, "msg": msg, "state": _summarize()})

# ── API — Battle ────────────────────────────────────────────

@app.route("/api/battle", methods=["POST"])
def api_battle():
    global _state
    data    = request.json or {}
    atk_rid = data.get("attacker_id")
    tgt_did = data.get("target_district")
    mode    = data.get("mode", "assault")

    atk_r = get_retainer(atk_rid)
    tgt_d = get_district(tgt_did)
    if not atk_r or not tgt_d:
        return jsonify({"ok": False, "msg": "無效的武將或目標郡"})

    s  = gs()
    pf = s["player_faction"]

    adj_ids = set()
    for d in faction_districts(pf):
        adj_ids.update(d.get("adjacent", []))
    if tgt_did not in adj_ids:
        return jsonify({"ok": False, "msg": "目標郡與我方領地不鄰接"})

    tgt_castle = get_castle(tgt_d["castle"])
    if not tgt_castle or tgt_castle["faction"] == pf:
        return jsonify({"ok": False, "msg": "目標郡已是我方領地"})

    dfn_r      = get_retainer(tgt_d.get("retainer")) if tgt_d.get("retainer") else None
    dfn_forces = tgt_castle.get("garrison", 500)
    dfn_cmd    = dfn_r["mil"] if dfn_r else 50

    if mode == "siege":
        result = resolve_siege(
            {"name": atk_r["name"], "forces": atk_r["forces"], "command": atk_r["mil"]},
            {"name": dfn_r["name"] if dfn_r else "守備隊", "forces": dfn_forces, "command": dfn_cmd},
        )
    else:
        result = resolve_battle(
            {"name": atk_r["name"], "forces": atk_r["forces"], "command": atk_r["mil"]},
            {"name": dfn_r["name"] if dfn_r else "守備隊", "forces": dfn_forces, "command": dfn_cmd},
        )

    atk_r["forces"] = result["atk_remain"]
    if result["result"] == "攻方勝利":
        tgt_castle["faction"]  = pf
        tgt_castle["garrison"] = result["dfn_remain"]
        msg = f"攻佔 {tgt_d['name']}！敵守備隊 {result['dfn_remain']} 人投降。"
    elif result["result"] == "圍城進行中":
        enemy_fac = tgt_castle["faction"]
        s["factions"][enemy_fac]["military_supply"] = max(
            0, s["factions"][enemy_fac]["military_supply"] - result.get("supply_drain", 50)
        )
        msg = f"圍城中：{tgt_castle['name']} 軍糧消耗 {result.get('supply_drain',50)}。"
    else:
        msg = f"進攻 {tgt_d['name']} 失敗，殘餘 {result['atk_remain']} 人撤回。"

    s["log"].insert(0, f"【戰報】{result['summary']}")
    s["log"] = s["log"][:20]
    return jsonify({"ok": True, "result": result, "msg": msg, "state": _summarize()})

# ── API — Council Decision（Feedback 3）────────────────────

@app.route("/api/council-decision", methods=["POST"])
def api_council_decision():
    global _state
    data      = request.json or {}
    topic_id  = data.get("topic_id")
    choice_id = data.get("choice_id")
    choice_label = data.get("choice_label", "")

    if gs().get("council_decision"):
        return jsonify({"ok": False, "msg": "本月裁決已下達"})

    topic = next((t for t in COUNCIL_TOPICS if t["id"] == topic_id), None)
    if not topic:
        return jsonify({"ok": False, "msg": "無效的議題"})

    _state, changes = apply_council_decision(_state, topic, choice_id)
    _state["council_decision"] = {"choice_id": choice_id, "label": choice_label}

    return jsonify({
        "ok": True,
        "msg": f"裁決已下達：{choice_label}",
        "loyalty_changes": changes,
        "state": _summarize(),
    })

# ── API — Corps（Feedback 2）───────────────────────────────

@app.route("/api/corps", methods=["GET"])
def api_get_corps():
    return jsonify({"corps": gs().get("corps", [])})

@app.route("/api/corps", methods=["POST"])
def api_create_corps():
    global _state
    data   = request.json or {}
    name   = data.get("name", "").strip()
    leader = data.get("leader")
    territories = data.get("territories", [])

    if not name:
        return jsonify({"ok": False, "msg": "請輸入家臣團名稱"})

    s  = gs()
    pf = s["player_faction"]
    r  = get_retainer(leader)
    if not r or r["faction"] != pf:
        return jsonify({"ok": False, "msg": "無效的首領"})
    if r["rank"] not in ("宿老", "家老"):
        return jsonify({"ok": False, "msg": "首領必須是宿老或家老"})
    if any(c.get("leader") == leader for c in s.get("corps", [])):
        return jsonify({"ok": False, "msg": f"{r['name']} 已是其他家臣團首領"})

    new_corps = {
        "id": f"corps_{uuid.uuid4().hex[:8]}",
        "name": name,
        "leader": leader,
        "members": [],
        "territories": [t for t in territories if get_castle(t)],
    }
    _state.setdefault("corps", []).append(new_corps)
    r["corps_id"] = new_corps["id"]

    _state["log"].insert(0, f"【家臣團】成立「{name}」，首領：{r['name']}")
    return jsonify({"ok": True, "msg": f"家臣團「{name}」已成立"})

@app.route("/api/corps/<corps_id>", methods=["DELETE"])
def api_delete_corps(corps_id):
    global _state
    s = gs()
    corps = next((c for c in s.get("corps", []) if c["id"] == corps_id), None)
    if not corps:
        return jsonify({"ok": False, "msg": "找不到家臣團"})

    # 清除成員的 corps_id
    for mid in [corps["leader"]] + corps.get("members", []):
        r = get_retainer(mid)
        if r:
            r["corps_id"] = None

    _state["corps"] = [c for c in s["corps"] if c["id"] != corps_id]
    _state["log"].insert(0, f"【家臣團】「{corps['name']}」已解散")
    return jsonify({"ok": True, "msg": f"家臣團「{corps['name']}」已解散"})

@app.route("/api/corps/<corps_id>/members", methods=["POST"])
def api_corps_members(corps_id):
    global _state
    data       = request.json or {}
    retainer_id = data.get("retainer_id")
    action     = data.get("action", "add")

    s = gs()
    corps = next((c for c in s.get("corps", []) if c["id"] == corps_id), None)
    if not corps:
        return jsonify({"ok": False, "msg": "找不到家臣團"})
    r = get_retainer(retainer_id)
    if not r:
        return jsonify({"ok": False, "msg": "找不到武將"})

    if action == "add":
        if retainer_id in corps["members"] or retainer_id == corps["leader"]:
            return jsonify({"ok": False, "msg": "已是成員或首領"})
        corps["members"].append(retainer_id)
        r["corps_id"] = corps_id
        return jsonify({"ok": True, "msg": f"{r['name']} 加入「{corps['name']}」"})
    else:
        if retainer_id not in corps["members"]:
            return jsonify({"ok": False, "msg": "非此家臣團成員"})
        corps["members"].remove(retainer_id)
        r["corps_id"] = None
        return jsonify({"ok": True, "msg": f"{r['name']} 已從「{corps['name']}」移除"})

@app.route("/api/corps/<corps_id>/territories", methods=["POST"])
def api_corps_territories(corps_id):
    global _state
    data     = request.json or {}
    castle_id = data.get("castle_id")
    action   = data.get("action", "add")

    s = gs()
    corps = next((c for c in s.get("corps", []) if c["id"] == corps_id), None)
    castle = get_castle(castle_id)
    if not corps:
        return jsonify({"ok": False, "msg": "找不到家臣團"})
    if not castle:
        return jsonify({"ok": False, "msg": "找不到城"})

    if action == "add":
        if castle_id in corps.get("territories", []):
            return jsonify({"ok": False, "msg": "已在此家臣團轄下"})
        corps.setdefault("territories", []).append(castle_id)
        _state["log"].insert(0, f"【家臣團】{castle['name']} 分配給「{corps['name']}」")
        return jsonify({"ok": True, "msg": f"{castle['name']} 已分配給「{corps['name']}」"})
    else:
        if castle_id not in corps.get("territories", []):
            return jsonify({"ok": False, "msg": "非此家臣團轄地"})
        corps["territories"].remove(castle_id)
        return jsonify({"ok": True, "msg": f"{castle['name']} 已從「{corps['name']}」撤回"})

# ── API — State / Load / Reset ──────────────────────────────

@app.route("/api/state")
def api_state():
    return jsonify(gs())

@app.route("/api/load-state", methods=["POST"])
def api_load_state():
    global _state
    incoming = request.json
    if not incoming:
        return jsonify({"ok": False, "msg": "無存檔資料"})
    for key in ("date", "factions", "castles", "districts", "retainers"):
        if key not in incoming:
            return jsonify({"ok": False, "msg": f"存檔格式錯誤（缺少 {key}）"})
    _state = copy.deepcopy(incoming)
    return jsonify({"ok": True, "msg": "✓ 存檔讀取成功"})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    global _state
    _state = copy.deepcopy(INITIAL_STATE)
    return jsonify({"ok": True, "msg": "遊戲已重置"})

# ── Helper ──────────────────────────────────────────────────

def _summarize():
    s  = gs()
    pf = s["player_faction"]
    return {
        "date":           s["date"],
        "turn":           s["turn"],
        "gold":           s["factions"][pf]["gold"],
        "supply":         s["factions"][pf]["military_supply"],
        "log":            s.get("log", [])[:8],
        "retainers":      s["retainers"],
        "player_faction": pf,
    }

# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
