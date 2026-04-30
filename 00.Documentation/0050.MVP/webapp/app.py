import sys, os, copy
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request, redirect, url_for
from data.initial import INITIAL_STATE, FACILITY_UPGRADE, loyalty_color
from game.logic import (
    process_turn, upgrade_facility, set_nengu,
    resolve_battle, resolve_siege, mobilize_troops,
    calc_district_output,
)

app = Flask(__name__)
app.secret_key = "sengoku-mvp-2026"

# ── In-memory game state ──────────────────────────────────
_state = copy.deepcopy(INITIAL_STATE)

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

# ── Pages ─────────────────────────────────────────────────

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
    return render_template("retainers.html",
        state=s, retainers=ret, faction_id=faction_id,
        loyalty_color=loyalty_color, active="retainers",
    )

@app.route("/politics")
def politics():
    menu = [
        {"id":1,"name":"家臣管理","icon":"👤","sub":["任命官職","晉升武將","知行分配","家臣廢黜"]},
        {"id":2,"name":"領地治理","icon":"🏯","sub":["設施升級","年貢調整","開墾農田","郡城巡視"]},
        {"id":3,"name":"軍事行動","icon":"⚔️","sub":["徵集農兵","出兵攻打","調防部隊","返還農民"]},
        {"id":4,"name":"外交談判","icon":"📜","sub":["結盟談判","宣戰通告","和議談判","送質子"]},
        {"id":5,"name":"情報活動","icon":"🥷","sub":["派遣忍者","收集情報","召回忍者","設置防諜"]},
        {"id":6,"name":"評定會議","icon":"🏛️","sub":["召開評議","頒布法令","繼承宣告","分封領地"]},
        {"id":7,"name":"儀式典禮","icon":"🎌","sub":["舉行慶典","祭祀神明","茶道接待"]},
        {"id":8,"name":"戰後處置","icon":"🗡️","sub":["領地處置","收編武將","封賞功臣"]},
        {"id":9,"name":"結束回合","icon":"⏭️","sub":[]},
    ]
    return render_template("politics.html", state=gs(), menu=menu, active="politics")

@app.route("/council")
def council():
    s = gs()
    cr = [r for r in s["retainers"] if r["faction"]=="oda" and r["rank"] in ("宿老","家老")]
    return render_template("council.html", state=s, council_retainers=cr, active="council")

# ── API — End Turn ─────────────────────────────────────────

@app.route("/api/end-turn", methods=["POST"])
def api_end_turn():
    global _state
    _state, log = process_turn(_state)
    s = _summarize()
    return jsonify({"ok": True, "log": log, "state": s})

# ── API — District ─────────────────────────────────────────

@app.route("/api/district/<did>")
def api_district(did):
    d = get_district(did)
    if not d:
        return jsonify({"error": "not found"}), 404
    s = gs()
    castle = next((c for c in s["castles"] if c["id"] == d["castle"]), {})
    retainer = get_retainer(d["retainer"]) if d.get("retainer") else None
    spec = next_upgrade_spec(d)
    output = calc_district_output(d)
    return jsonify({
        "district": d,
        "castle_name": castle.get("name",""),
        "castle_faction": castle.get("faction",""),
        "castle_data": castle,
        "retainer": retainer,
        "next_upgrade": spec,
        "output": output,
        "player_gold": s["factions"][s["player_faction"]]["gold"],
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

# ── API — Castle Detail ────────────────────────────────────

@app.route("/api/castle/<cid>")
def api_castle(cid):
    s = gs()
    castle = get_castle(cid)
    if not castle:
        return jsonify({"error": "not found"}), 404
    faction = s["factions"].get(castle["faction"], {})
    districts = [d for d in s["districts"] if d["castle"] == cid]
    return jsonify({
        "castle": castle,
        "faction_name": faction.get("name", castle["faction"]),
        "districts": districts,
    })

# ── API — Mobilize Troops (UC-020/021) ────────────────────

@app.route("/api/mobilize", methods=["POST"])
def api_mobilize():
    global _state
    data = request.json or {}
    did  = data.get("district_id")
    mtype = data.get("type", "city")   # "city" | "farmer"

    d = get_district(did)
    if not d:
        return jsonify({"ok": False, "msg": "找不到郡"})

    s = gs()
    pf = s["player_faction"]
    castle = get_castle(d["castle"])
    if not castle or castle["faction"] != pf:
        return jsonify({"ok": False, "msg": "此郡非我方領地"})

    result, msg = mobilize_troops(_state, did, mtype)
    if result is None:
        return jsonify({"ok": False, "msg": msg})
    _state = result
    return jsonify({"ok": True, "msg": msg, "state": _summarize()})

# ── API — Battle (UC-022/023) ──────────────────────────────

@app.route("/api/battle", methods=["POST"])
def api_battle():
    global _state
    data    = request.json or {}
    atk_rid = data.get("attacker_id")
    tgt_did = data.get("target_district")
    mode    = data.get("mode", "assault")  # "assault" | "siege"

    atk_r = get_retainer(atk_rid)
    tgt_d = get_district(tgt_did)
    if not atk_r or not tgt_d:
        return jsonify({"ok": False, "msg": "無效的武將或目標郡"})

    s = gs()
    pf = s["player_faction"]

    # Check adjacency
    atk_dist_ids = {d["id"] for d in faction_districts(pf)}
    adj_ids = set()
    for d in s["districts"]:
        if d["id"] in atk_dist_ids:
            adj_ids.update(d.get("adjacent", []))
    if tgt_did not in adj_ids:
        return jsonify({"ok": False, "msg": "目標郡與我方領地不鄰接"})

    # Check district is enemy
    tgt_castle = get_castle(tgt_d["castle"])
    if not tgt_castle or tgt_castle["faction"] == pf:
        return jsonify({"ok": False, "msg": "目標郡已是我方領地"})

    # Defender
    dfn_r = get_retainer(tgt_d.get("retainer")) if tgt_d.get("retainer") else None
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

    # Apply results
    atk_r["forces"] = result["atk_remain"]
    if result["result"] == "攻方勝利":
        tgt_castle["faction"] = pf
        tgt_castle["garrison"] = result["dfn_remain"]
        msg = f"攻佔 {tgt_d['name']}！敵守備隊 {result['dfn_remain']} 人投降。"
    elif result["result"] == "圍城進行中":
        # Siege ongoing — reduce enemy military supply
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

# ── API — State / Load / Reset ─────────────────────────────

@app.route("/api/state")
def api_state():
    return jsonify(gs())

@app.route("/api/load-state", methods=["POST"])
def api_load_state():
    global _state
    incoming = request.json
    if not incoming:
        return jsonify({"ok": False, "msg": "無存檔資料"})
    # Basic validation
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

# ── Helper ─────────────────────────────────────────────────

def _summarize():
    s = gs()
    pf = s["player_faction"]
    return {
        "date": s["date"],
        "turn": s["turn"],
        "gold": s["factions"][pf]["gold"],
        "supply": s["factions"][pf]["military_supply"],
        "log": s.get("log", [])[:8],
        "retainers": s["retainers"],
        "player_faction": pf,
    }

# ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
