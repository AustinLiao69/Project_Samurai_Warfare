import sys, os, copy
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request, redirect, url_for
from data.initial import INITIAL_STATE, FACILITY_UPGRADE, loyalty_color
from game.logic import process_turn, upgrade_facility, set_nengu, resolve_battle

app = Flask(__name__)
app.secret_key = "sengoku-mvp-2026"

# ── In-memory game state ──────────────────────────────────
_state = copy.deepcopy(INITIAL_STATE)

def gs():
    return _state

def get_district(district_id):
    return next((d for d in gs()["districts"] if d["id"] == district_id), None)

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
        next_upgrade_spec=next_upgrade_spec,
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
    from data.initial import INITIAL_STATE
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
    return jsonify({"ok": True, "log": log, "state": _summarize()})

# ── API — District ─────────────────────────────────────────

@app.route("/api/district/<did>")
def api_district(did):
    d = get_district(did)
    if not d:
        return jsonify({"error": "not found"}), 404
    s = gs()
    castle = next((c for c in s["castles"] if c["id"] == d["castle"]), {})
    retainer = get_retainer(d["retainer"]) if d["retainer"] else None
    spec = next_upgrade_spec(d)
    from game.logic import calc_district_output
    output = calc_district_output(d)
    return jsonify({
        "district": d,
        "castle_name": castle.get("name",""),
        "castle_faction": castle.get("faction",""),
        "retainer": retainer,
        "next_upgrade": spec,
        "output": output,
        "player_gold": s["factions"][s["player_faction"]]["gold"],
    })

@app.route("/api/district/<did>/upgrade", methods=["POST"])
def api_upgrade(did):
    global _state
    _state, msg = upgrade_facility(_state, did)
    if _state is None:
        return jsonify({"ok": False, "msg": msg})
    return jsonify({"ok": True, "msg": msg, "state": _summarize(), "district": get_district(did)})

@app.route("/api/district/<did>/nengu", methods=["POST"])
def api_nengu(did):
    global _state
    rate = request.json.get("rate", 20)
    _state, msg = set_nengu(_state, did, rate)
    if _state is None:
        return jsonify({"ok": False, "msg": msg})
    from game.logic import calc_district_output
    output = calc_district_output(get_district(did))
    return jsonify({"ok": True, "msg": msg, "output": output, "state": _summarize()})

# ── API — Battle ───────────────────────────────────────────

@app.route("/api/battle", methods=["POST"])
def api_battle():
    global _state
    data = request.json
    # attacker_id: retainer id, target_district: district id
    atk_rid = data.get("attacker_id")
    tgt_did = data.get("target_district")

    atk_r = get_retainer(atk_rid)
    tgt_d = get_district(tgt_did)
    if not atk_r or not tgt_d:
        return jsonify({"ok": False, "msg": "無效的出兵目標"})

    # 檢查鄰接
    s = gs()
    pf = s["player_faction"]
    atk_castle_ids = {c["id"] for c in faction_castles(pf)}
    atk_district_ids = {d["id"] for d in s["districts"] if d["castle"] in atk_castle_ids}

    if tgt_did not in [adj for d in s["districts"] if d["id"] in atk_district_ids for adj in d["adjacent"]]:
        return jsonify({"ok": False, "msg": "目標郡與我方領地不鄰接"})

    # 找守方武將
    tgt_castle = next((c for c in s["castles"] if c["id"] == tgt_d["castle"]), None)
    dfn_r = get_retainer(tgt_d.get("retainer")) if tgt_d.get("retainer") else None
    dfn_forces = tgt_castle["garrison"] if tgt_castle else 500
    dfn_cmd = dfn_r["mil"] if dfn_r else 50

    result = resolve_battle(
        {"name": atk_r["name"], "forces": atk_r["forces"], "command": atk_r["mil"]},
        {"name": dfn_r["name"] if dfn_r else "守備隊", "forces": dfn_forces, "command": dfn_cmd},
    )

    # 套用結果
    if result["result"] == "攻方勝利":
        # 轉移郡歸屬
        tgt_castle["faction"] = pf
        for d in s["districts"]:
            if d["castle"] == tgt_castle["id"]:
                d["castle"] = tgt_castle["id"]
        # 損失兵力
        atk_r["forces"] = result["atk_remain"]
        if tgt_castle:
            tgt_castle["garrison"] = 0
        msg = f"攻佔 {tgt_d['name']}！"
    else:
        atk_r["forces"] = result["atk_remain"]
        msg = f"進攻 {tgt_d['name']} 失敗，殘餘 {result['atk_remain']} 人撤回。"

    s["log"].insert(0, f"【戰報】{result['summary']}")
    return jsonify({"ok": True, "result": result, "msg": msg, "state": _summarize()})

# ── API — State / Reset ────────────────────────────────────

@app.route("/api/state")
def api_state():
    return jsonify(gs())

@app.route("/api/reset", methods=["POST"])
def api_reset():
    global _state
    _state = copy.deepcopy(INITIAL_STATE)
    return jsonify({"ok": True, "msg": "遊戲已重置"})

# ── Helper ─────────────────────────────────────────────────

def _summarize():
    s = gs()
    return {
        "date": s["date"],
        "turn": s["turn"],
        "gold": s["factions"][s["player_faction"]]["gold"],
        "supply": s["factions"][s["player_faction"]]["military_supply"],
        "log": s["log"][:5],
    }

# ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
