import sys, os, copy, json, uuid
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request, redirect, url_for
from data.initial import INITIAL_STATE, FACILITY_UPGRADE, loyalty_color, COUNCIL_TOPICS
from game.logic import (
    process_turn, upgrade_facility, set_nengu,
    resolve_battle, resolve_siege, mobilize_troops,
    calc_castle_output, apply_council_decision,
)

app = Flask(__name__)
app.secret_key = "sengoku-mvp-2026"

_state = copy.deepcopy(INITIAL_STATE)

# ── 工具函數 ────────────────────────────────────────────────

def gs():
    return _state

def get_castle(cid):
    return next((c for c in gs()["castles"] if c["id"] == cid), None)

def get_retainer(rid):
    return next((r for r in gs()["retainers"] if r["id"] == rid), None)

def faction_castles(faction_id):
    return [c for c in gs()["castles"] if c["faction"] == faction_id]

def total_forces(faction_id):
    return sum(r["forces"] for r in gs()["retainers"] if r["faction"] == faction_id)

def next_upgrade_spec(c):
    nxt = c["facility_level"] + 1
    return next((r for r in FACILITY_UPGRADE.get(c["type"], []) if r["level"] == nxt), None)

def current_topic():
    idx = (gs()["turn"] - 1) % len(COUNCIL_TOPICS)
    return COUNCIL_TOPICS[idx]

def get_advisor():
    """取得玩家主要直臣（最高忠誠度的宿老/家老，corps_id=None）"""
    s  = gs()
    pf = s["player_faction"]
    direct = [r for r in s["retainers"]
              if r["faction"] == pf
              and r["rank"] in ("宿老", "家老")
              and r.get("corps_id") is None]
    return max(direct, key=lambda r: r["loyalty"]) if direct else None

def corps_map_for_retainers():
    result = {}
    for corps in gs().get("corps", []):
        result[corps["leader"]] = {"corps_id": corps["id"], "corps_name": corps["name"], "is_leader": True}
        for mid in corps.get("members", []):
            result[mid] = {"corps_id": corps["id"], "corps_name": corps["name"], "is_leader": False}
    return result

def get_corps_for_castle(castle_id):
    """回傳管轄此城的家臣團（若有）"""
    for corps in gs().get("corps", []):
        if castle_id in corps.get("territories", []):
            leader = get_retainer(corps["leader"])
            return {"corps_name": corps["name"], "leader_name": leader["name"] if leader else ""}
    return None

# ── 政務選單資料（Feedback 1+5）────────────────────────────

POLITICS_CATEGORIES = [
    {
        "id": "territory",
        "icon": "🏯",
        "name": "領地治理",
        "hint": "設施・年貢・開墾",
        "subs": [
            {"name": "設施升級",  "desc": "提升城內設施等級增加產出",       "enabled": True,  "url": "/politics"},
            {"name": "年貢調整",  "desc": "調整各城年貢率（10%~60%）",      "enabled": True,  "url": "/politics"},
            {"name": "開墾農田",  "desc": "開發荒地，增加農業城產能",       "enabled": False},
            {"name": "城域巡視",  "desc": "視察領地，提升民心與忠誠度",     "enabled": False},
        ],
    },
    {
        "id": "diplomacy",
        "icon": "📜",
        "name": "外交談判",
        "hint": "結盟・宣戰・和議",
        "subs": [
            {"name": "結盟談判",  "desc": "與其他勢力締結同盟",            "enabled": False},
            {"name": "宣戰通告",  "desc": "正式向敵對勢力宣戰",            "enabled": False},
            {"name": "和議談判",  "desc": "與交戰勢力展開和平談判",        "enabled": False},
        ],
    },
    {
        "id": "council",
        "icon": "🏛",
        "name": "評定會議",
        "hint": "召議・評定・裁決",
        "subs": [
            {"name": "召開評議",  "desc": "召集家老評議本月重要事項",      "enabled": True,  "url": "/council"},
            {"name": "頒布法令",  "desc": "頒布政令，影響民心與生產",      "enabled": False},
            {"name": "分封領地",  "desc": "正式分封領地給家臣團",          "enabled": True,  "url": "/retainers?tab=corps"},
        ],
    },
    {
        "id": "ceremony",
        "icon": "🎌",
        "name": "儀式典禮",
        "hint": "慶典・祭祀・茶道",
        "subs": [
            {"name": "舉行慶典",  "desc": "舉辦慶祝活動提升家臣士氣",      "enabled": False},
            {"name": "祭祀神明",  "desc": "祭祀神明，祈求戰場勝利",        "enabled": False},
        ],
    },
    {
        "id": "postwar",
        "icon": "🗡",
        "name": "戰後處置",
        "hint": "領地・收編・封賞",
        "subs": [
            {"name": "領地處置",  "desc": "決定佔領領地的歸屬",            "enabled": False},
            {"name": "收編武將",  "desc": "招攬敵方降將加入己方",          "enabled": False},
            {"name": "封賞功臣",  "desc": "賞賜有功武將，提升忠誠度",      "enabled": False},
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
    advisor = get_advisor()
    return render_template("index.html",
        state=s,
        advisor=advisor,
        oda_forces=total_forces("oda"),
        imagawa_forces=total_forces("imagawa"),
        active="map",
        loyalty_color=loyalty_color,
    )

@app.route("/territory")
def territory():
    return redirect(url_for("politics"))

@app.route("/politics")
def politics():
    s = gs()
    pf = s["player_faction"]
    player_castles = faction_castles(pf)
    outputs = {c["id"]: calc_castle_output(c) for c in player_castles}
    advisor = get_advisor()
    return render_template("politics.html",
        state=s,
        categories=POLITICS_CATEGORIES,
        categories_json=POLITICS_CATEGORIES,
        advisor=advisor or {"name": "柴田勝家", "rank": "宿老", "lineage": "譜代",
                            "loyalty": 80, "loyalty_label": "忠心耿耿"},
        loyalty_color=loyalty_color,
        player_castles=player_castles,
        outputs=outputs,
        corps_map={c["id"]: get_corps_for_castle(c["id"]) for c in player_castles},
        active="politics",
    )

@app.route("/military")
def military():
    s = gs()
    pf = s["player_faction"]
    player_castles = faction_castles(pf)
    # Build adjacency: all enemy castles adjacent to player castles
    adj_enemy = []
    my_ids = {c["id"] for c in player_castles}
    adj_ids = set()
    for c in player_castles:
        adj_ids.update(c.get("adjacent", []))
    adj_enemy = [c for c in s["castles"] if c["id"] in adj_ids and c["faction"] != pf]
    attackers = [r for r in s["retainers"] if r["faction"] == pf and r["rank"] != "大名" and r["forces"] > 0]
    return render_template("military.html",
        state=s,
        player_castles=player_castles,
        adj_enemy=adj_enemy,
        attackers=attackers,
        active="military",
    )

@app.route("/intel")
def intel():
    return render_template("intel.html", state=gs(), active="intel")

@app.route("/retainers")
@app.route("/retainers/<faction_id>")
def retainers(faction_id="oda"):
    s  = gs()
    pf = s["player_faction"]
    ret = [r for r in s["retainers"] if r["faction"] == faction_id]
    cmap = corps_map_for_retainers()

    direct_retainers = [r for r in s["retainers"]
                        if r["faction"] == pf
                        and r["rank"] in ("宿老", "家老")
                        and r.get("corps_id") is None]

    player_castles = [c for c in s["castles"]
                      if c["faction"] == pf and not c.get("is_daimyo_home", False)]

    corps_list   = s.get("corps", [])
    leader_map   = {r["id"]: r for r in s["retainers"]}
    tab = request.args.get("tab", "retainers")

    return render_template("retainers.html",
        state=s, retainers=ret, faction_id=faction_id,
        loyalty_color=loyalty_color, active="retainers",
        corps_map=cmap, corps_list=corps_list,
        direct_retainers=direct_retainers,
        player_castles=player_castles,
        leader_map=leader_map, tab=tab,
    )

@app.route("/council")
def council():
    s = gs()
    topic = current_topic()
    cr = [r for r in s["retainers"]
          if r["faction"] == "oda" and r["rank"] in ("宿老", "家老")]
    stances_for_js = {}
    for rid, (stance, comment, agree_with) in topic["stances"].items():
        stances_for_js[rid] = {"stance": stance, "agree_with": agree_with}
    return render_template("council.html",
        state=s, topic=topic,
        topics_total=len(COUNCIL_TOPICS),
        council_retainers=cr,
        topic_stances_json=stances_for_js,
        active="council",
    )

# ── API — End Turn ──────────────────────────────────

@app.route("/api/end-turn", methods=["POST"])
def api_end_turn():
    global _state
    _state, log = process_turn(_state)
    _state["council_decision"] = None
    return jsonify({"ok": True, "log": log, "state": _summarize()})

# ── API — Castle（統一：城 = 郡） ───────────────────

@app.route("/api/castle/<cid>")
def api_castle(cid):
    c = get_castle(cid)
    if not c:
        return jsonify({"error": "not found"}), 404
    s  = gs()
    pf = s["player_faction"]
    retainer = get_retainer(c["retainer"]) if c.get("retainer") else None
    spec     = next_upgrade_spec(c)
    output   = calc_castle_output(c)
    corps_info = get_corps_for_castle(cid)
    return jsonify({
        "castle": c,
        "castle_name":    c["name"],
        "castle_faction": c["faction"],
        "castle_data":    c,
        # compat fields (used by district modal JS)
        "district": c,
        "retainer":       retainer,
        "next_upgrade":   spec,
        "output":         output,
        "player_gold":    s["factions"][pf]["gold"],
        "corps_info":     corps_info,
        "is_corps_territory": corps_info is not None,
        "is_daimyo_home": c.get("is_daimyo_home", False),
    })

@app.route("/api/castle/<cid>/upgrade", methods=["POST"])
def api_upgrade(cid):
    global _state
    result, msg = upgrade_facility(_state, cid)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    return jsonify({"ok": True, "msg": msg, "state": _summarize()})

@app.route("/api/castle/<cid>/nengu", methods=["POST"])
def api_nengu(cid):
    global _state
    rate = request.json.get("rate", 20)
    result, msg = set_nengu(_state, cid, rate)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    output = calc_castle_output(get_castle(cid))
    return jsonify({"ok": True, "msg": msg, "output": output, "state": _summarize()})

# compat aliases (for old JS calls /api/district/*)
@app.route("/api/district/<did>")
def api_district_compat(did):
    return api_castle(did)

@app.route("/api/district/<did>/upgrade", methods=["POST"])
def api_upgrade_compat(did):
    return api_upgrade(did)

@app.route("/api/district/<did>/nengu", methods=["POST"])
def api_nengu_compat(did):
    return api_nengu(did)

# ── API — Mobilize ──────────────────────────────────

@app.route("/api/mobilize", methods=["POST"])
def api_mobilize():
    global _state
    data      = request.json or {}
    castle_id = data.get("castle_id") or data.get("district_id")
    mtype     = data.get("type", "city")
    c = get_castle(castle_id)
    if not c:
        return jsonify({"ok": False, "msg": "找不到城"})
    s  = gs()
    pf = s["player_faction"]
    if c["faction"] != pf:
        return jsonify({"ok": False, "msg": "此城非我方領地"})
    result, msg = mobilize_troops(_state, castle_id, mtype)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    return jsonify({"ok": True, "msg": msg, "state": _summarize()})

# ── API — Battle ────────────────────────────────────

@app.route("/api/battle", methods=["POST"])
def api_battle():
    global _state
    data    = request.json or {}
    atk_rid = data.get("attacker_id")
    tgt_cid = data.get("target_castle") or data.get("target_district")
    mode    = data.get("mode", "assault")

    atk_r = get_retainer(atk_rid)
    tgt_c = get_castle(tgt_cid)
    if not atk_r or not tgt_c:
        return jsonify({"ok": False, "msg": "無效的武將或目標城"})

    s  = gs()
    pf = s["player_faction"]

    # 鄰接檢查
    adj_ids = set()
    for c in faction_castles(pf):
        adj_ids.update(c.get("adjacent", []))
    if tgt_cid not in adj_ids:
        return jsonify({"ok": False, "msg": "目標城與我方領地不鄰接"})

    if tgt_c["faction"] == pf:
        return jsonify({"ok": False, "msg": "目標城已是我方領地"})

    dfn_r      = get_retainer(tgt_c.get("retainer")) if tgt_c.get("retainer") else None
    dfn_forces = tgt_c.get("garrison", 500)
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
        tgt_c["faction"]  = pf
        tgt_c["garrison"] = result["dfn_remain"]
        msg = f"攻佔 {tgt_c['name']}！敵守備隊 {result['dfn_remain']} 人投降。"
    elif result["result"] == "圍城進行中":
        enemy_fac = tgt_c["faction"]
        s["factions"][enemy_fac]["military_supply"] = max(
            0, s["factions"][enemy_fac]["military_supply"] - result.get("supply_drain", 50)
        )
        msg = f"圍城中：{tgt_c['name']} 軍糧消耗 {result.get('supply_drain',50)}。"
    else:
        msg = f"進攻 {tgt_c['name']} 失敗，殘餘 {result['atk_remain']} 人撤回。"

    s["log"].insert(0, f"【戰報】{result['summary']}")
    s["log"] = s["log"][:20]
    return jsonify({"ok": True, "result": result, "msg": msg, "state": _summarize()})

# ── API — Council Decision ──────────────────────────

@app.route("/api/council-decision", methods=["POST"])
def api_council_decision():
    global _state
    data         = request.json or {}
    topic_id     = data.get("topic_id")
    choice_id    = data.get("choice_id")
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

# ── API — Corps ─────────────────────────────────────

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

    # 過濾掉大名本城
    valid_territories = [t for t in territories
                         if (c := get_castle(t)) and not c.get("is_daimyo_home", False)]

    new_corps = {
        "id": f"corps_{uuid.uuid4().hex[:8]}",
        "name": name, "leader": leader, "members": [],
        "territories": valid_territories,
    }
    _state.setdefault("corps", []).append(new_corps)
    # 更新城的 corps_id
    for tid in valid_territories:
        c = get_castle(tid)
        if c:
            c["corps_id"] = new_corps["id"]

    _state["log"].insert(0, f"【家臣團】成立「{name}」，首領：{r['name']}")
    return jsonify({"ok": True, "msg": f"家臣團「{name}」已成立"})

@app.route("/api/corps/<corps_id>", methods=["DELETE"])
def api_delete_corps(corps_id):
    global _state
    s = gs()
    corps = next((c for c in s.get("corps", []) if c["id"] == corps_id), None)
    if not corps:
        return jsonify({"ok": False, "msg": "找不到家臣團"})

    # 清除城的 corps_id
    for tid in corps.get("territories", []):
        c = get_castle(tid)
        if c:
            c["corps_id"] = None

    for mid in [corps["leader"]] + corps.get("members", []):
        r = get_retainer(mid)
        if r:
            r["corps_id"] = None

    _state["corps"] = [c for c in s["corps"] if c["id"] != corps_id]
    _state["log"].insert(0, f"【家臣團】「{corps['name']}」已解散")
    return jsonify({"ok": True, "msg": f"家臣團「{corps['name']}」已解散"})

@app.route("/api/corps/<corps_id>/members", methods=["POST"])
def api_corps_members(corps_id):
    data        = request.json or {}
    retainer_id = data.get("retainer_id")
    action      = data.get("action", "add")

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
        return jsonify({"ok": True, "msg": f"{r['name']} 已移除"})

@app.route("/api/corps/<corps_id>/territories", methods=["POST"])
def api_corps_territories(corps_id):
    data      = request.json or {}
    castle_id = data.get("castle_id")
    action    = data.get("action", "add")

    s = gs()
    corps  = next((c for c in s.get("corps", []) if c["id"] == corps_id), None)
    castle = get_castle(castle_id)
    if not corps:
        return jsonify({"ok": False, "msg": "找不到家臣團"})
    if not castle:
        return jsonify({"ok": False, "msg": "找不到城"})
    if castle.get("is_daimyo_home", False):
        return jsonify({"ok": False, "msg": "大名本城不可分封給家臣團"})

    if action == "add":
        if castle_id in corps.get("territories", []):
            return jsonify({"ok": False, "msg": "已在此家臣團轄下"})
        corps.setdefault("territories", []).append(castle_id)
        castle["corps_id"] = corps_id
        _state["log"].insert(0, f"【家臣團】{castle['name']} 分配給「{corps['name']}」")
        return jsonify({"ok": True, "msg": f"{castle['name']} 已分配給「{corps['name']}」"})
    else:
        if castle_id not in corps.get("territories", []):
            return jsonify({"ok": False, "msg": "非此家臣團轄地"})
        corps["territories"].remove(castle_id)
        castle["corps_id"] = None
        return jsonify({"ok": True, "msg": f"{castle['name']} 已從「{corps['name']}」撤回"})

# ── API — State / Save / Reset ──────────────────────

@app.route("/api/state")
def api_state():
    return jsonify(gs())

@app.route("/api/load-state", methods=["POST"])
def api_load_state():
    global _state
    incoming = request.json
    if not incoming:
        return jsonify({"ok": False, "msg": "無存檔資料"})
    for key in ("date", "factions", "castles", "retainers"):
        if key not in incoming:
            return jsonify({"ok": False, "msg": f"存檔格式錯誤（缺少 {key}）"})
    _state = copy.deepcopy(incoming)
    return jsonify({"ok": True, "msg": "✓ 存檔讀取成功"})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    global _state
    _state = copy.deepcopy(INITIAL_STATE)
    return jsonify({"ok": True, "msg": "遊戲已重置"})

# ── Helper ──────────────────────────────────────────

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
