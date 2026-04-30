"""
遊戲邏輯層 — 回合結算、資源計算、戰鬥、徵兵、圍城
[重構] 一城一郡：所有 district 相關邏輯改為操作 castle 物件
"""
import copy
import random
from data.initial import FACILITY_UPGRADE, loyalty_label

# ────────────────────────────────────────────────────
# 1. 資源計算（城即郡，使用城的 type/facility/nengu 屬性）
# ────────────────────────────────────────────────────

def calc_castle_output(c):
    """依城類型、設施等級、年貢率計算當月產出（城 = 郡）"""
    dtype = c["type"]
    lv    = c["facility_level"]
    nengu = c["nengu_rate"] / 100.0

    spec = FACILITY_UPGRADE.get(dtype, [])
    row  = next((r for r in spec if r["level"] == lv), spec[0] if spec else None)
    if not row:
        return {"gold": 0, "supply": 0}

    gold   = int(row.get("gold_out", 0) * nengu)
    supply = int(row.get("supply_out", 0) * nengu)
    return {"gold": gold, "supply": supply}

# 舊名相容
calc_district_output = calc_castle_output


def calc_garrison_cost(state, faction_id):
    """城兵每 100 人消耗 5 金"""
    total = 0
    for c in state["castles"]:
        if c["faction"] == faction_id:
            total += (c["garrison"] // 100) * 5
    return total


# ────────────────────────────────────────────────────
# 2. 回合結算
# ────────────────────────────────────────────────────

def process_turn(state):
    log = []
    pf  = state["player_faction"]

    # Step 1 — 設施建設進度
    for c in state["castles"]:
        if c.get("building") and c.get("building_turns", 0) > 0:
            c["building_turns"] -= 1
            if c["building_turns"] == 0:
                c["building"] = False
                c["facility_level"] += 1
                new_name = next(
                    (r["name"] for r in FACILITY_UPGRADE.get(c["type"], []) if r["level"] == c["facility_level"]),
                    c["facility_name"]
                )
                c["facility_name"] = new_name
                log.append(f"【建設完工】{c['name']} 的 {c['facility_name']} 升至 Lv{c['facility_level']}")

    # Step 2 — 農兵徵集完成
    for c in state["castles"]:
        if c["faction"] == pf and c.get("farmer_pending", 0) > 0:
            c["farmer_pending"] -= 1
            if c["farmer_pending"] == 0 and c.get("farmer_incoming", 0) > 0:
                c["garrison"] = min(c["garrison"] + c["farmer_incoming"], c.get("max_garrison", 9999))
                log.append(f"【徵兵完成】{c['name']} 農兵 {c['farmer_incoming']} 人完成訓練。")
                c["farmer_incoming"] = 0

    # Step 3 — 資源產出（玩家勢力）
    gold_income   = 0
    supply_income = 0
    for c in state["castles"]:
        if c["faction"] == pf:
            out = calc_castle_output(c)
            gold_income   += out["gold"]
            supply_income += out["supply"]

    # Step 4 — 城兵維持費
    gold_cost = calc_garrison_cost(state, pf)
    net_gold  = gold_income - gold_cost

    state["factions"][pf]["gold"]            = max(0, state["factions"][pf]["gold"] + net_gold)
    state["factions"][pf]["military_supply"] += supply_income
    log.append(f"【資源結算】金 +{gold_income}（維持 -{gold_cost}）= {net_gold:+d}　軍糧 +{supply_income}")

    # Step 5 — 忠誠度影響（年貢 > 30%）
    for c in state["castles"]:
        if c["faction"] == pf and c["nengu_rate"] > 30 and c.get("retainer"):
            delta = -round((c["nengu_rate"] - 30) * 0.5)
            r = next((x for x in state["retainers"] if x["id"] == c["retainer"]), None)
            if r and r["rank"] != "大名":
                r["loyalty"] = max(0, min(100, r["loyalty"] + delta))
                r["loyalty_label"] = loyalty_label(r["loyalty"])
                if delta < 0:
                    log.append(f"【忠誠度】{r['name']} 因高年貢，忠誠度 {delta:+d}")

    # Step 6 — NPC 今川 AI
    state["factions"]["imagawa"]["gold"]            += 150
    state["factions"]["imagawa"]["military_supply"] += 100

    # Step 7 — 月份推進
    state["date"]["month"] += 1
    if state["date"]["month"] > 12:
        state["date"]["month"] = 1
        state["date"]["year"] += 1
    state["turn"] += 1

    state["log"] = log + state.get("log", [])
    state["log"] = state["log"][:20]
    return state, log


# ────────────────────────────────────────────────────
# 3. 設施升級（城即郡）
# ────────────────────────────────────────────────────

def upgrade_facility(state, castle_id):
    c = next((x for x in state["castles"] if x["id"] == castle_id), None)
    if not c:
        return None, "找不到城"
    if c.get("building"):
        return None, "該城設施正在建設中"
    if c["facility_level"] >= c["facility_max"]:
        return None, "已達最高等級"

    dtype  = c["type"]
    nxt_lv = c["facility_level"] + 1
    spec   = next((r for r in FACILITY_UPGRADE.get(dtype, []) if r["level"] == nxt_lv), None)
    if not spec:
        return None, "無升級規格"

    pf   = state["player_faction"]
    cost = spec["cost"]
    if state["factions"][pf]["gold"] < cost:
        return None, f"金錢不足（需 {cost} 金，現有 {state['factions'][pf]['gold']} 金）"

    state["factions"][pf]["gold"] -= cost
    if spec["turns"] == 0:
        c["facility_level"] = nxt_lv
        c["facility_name"]  = spec["name"]
        msg = f"【升級完成】{c['name']} → {spec['name']}（即時）"
    else:
        c["building"]       = True
        c["building_turns"] = spec["turns"]
        msg = f"【開始建設】{c['name']} 升級中（{spec['turns']} 月後完工，費用 {cost} 金）"

    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 4. 年貢調整
# ────────────────────────────────────────────────────

def set_nengu(state, castle_id, rate):
    rate = max(10, min(60, int(rate)))
    c = next((x for x in state["castles"] if x["id"] == castle_id), None)
    if not c:
        return None, "找不到城"
    old = c["nengu_rate"]
    c["nengu_rate"] = rate
    msg = f"【年貢調整】{c['name']} {old}% → {rate}%"
    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 5. 徵兵
# ────────────────────────────────────────────────────

CASTLE_GARRISON_MAX = {1: 1000, 2: 2000, 3: 4000, 4: 8000, 5: 15000}
CITY_MOBILIZE   = 300
FARMER_MOBILIZE = 500

def mobilize_troops(state, castle_id, mtype):
    c = next((x for x in state["castles"] if x["id"] == castle_id), None)
    if not c:
        return None, "找不到城"

    pf = state["player_faction"]
    if c["faction"] != pf:
        return None, "此城非我方領地"

    cap = CASTLE_GARRISON_MAX.get(c.get("level", 1), 1000)

    if mtype == "city":
        cost = 50
        amt  = CITY_MOBILIZE
        if state["factions"][pf]["gold"] < cost:
            return None, f"城兵徵召需 {cost} 金（現有 {state['factions'][pf]['gold']} 金）"
        if c["garrison"] >= cap:
            return None, f"城兵已達上限（{cap} 人）"
        actual = min(amt, cap - c["garrison"])
        state["factions"][pf]["gold"] -= cost
        c["garrison"] += actual
        msg = f"【城兵徵召】{c['name']} 即時補充 {actual} 人（費用 {cost} 金）"
        state["log"].insert(0, msg)
        return state, msg

    elif mtype == "farmer":
        cost = 30
        amt  = FARMER_MOBILIZE
        if state["factions"][pf]["gold"] < cost:
            return None, f"農民兵徵集需 {cost} 金（現有 {state['factions'][pf]['gold']} 金）"
        if c.get("farmer_pending", 0) > 0:
            return None, "已有農民兵正在訓練中"
        if c["garrison"] >= cap:
            return None, f"城兵已達上限（{cap} 人）"
        state["factions"][pf]["gold"] -= cost
        c["farmer_pending"]  = 1
        c["farmer_incoming"] = min(amt, cap - c["garrison"])
        msg = f"【農民徵集】{c['name']} 農民兵 {c['farmer_incoming']} 人將於下月編入（費用 {cost} 金）"
        state["log"].insert(0, msg)
        return state, msg

    return None, "未知的徵兵類型"


# ────────────────────────────────────────────────────
# 6. 野戰結算
# ────────────────────────────────────────────────────

def resolve_battle(attacker, defender):
    atk     = attacker["forces"]
    dfn     = defender["forces"]
    atk_cmd = max(1, attacker.get("command", 60)) / 100.0
    dfn_cmd = max(1, defender.get("command", 60)) / 100.0

    atk_power = atk * atk_cmd
    dfn_power = dfn * dfn_cmd

    rounds = []
    for _ in range(40):
        if atk <= 0 or dfn <= 0:
            break
        atk_loss = max(1, int(dfn_power * 0.05 * random.uniform(0.8, 1.2)))
        dfn_loss = max(1, int(atk_power * 0.05 * random.uniform(0.8, 1.2)))
        atk = max(0, atk - atk_loss)
        dfn = max(0, dfn - dfn_loss)
        rounds.append({"atk": atk, "dfn": dfn})

    if dfn <= 0 and atk > 0:
        result  = "攻方勝利"
        summary = f"{attacker['name']} 擊敗 {defender['name']}！殘餘兵力 {atk} 人，佔領目標城。"
    elif atk <= 0:
        result  = "守方勝利"
        summary = f"{defender['name']} 成功防守，{attacker['name']} 全軍覆沒。"
    else:
        result  = "守方勝利"
        summary = f"雙方激戰 {len(rounds)} 回合，攻方 {atk} 人 vs 守方 {dfn} 人，攻方兵疲撤退。"

    return {
        "result": result, "atk_remain": atk, "dfn_remain": dfn,
        "summary": summary,
        "attacker_name": attacker["name"], "defender_name": defender["name"],
    }


# ────────────────────────────────────────────────────
# 7. 圍城結算
# ────────────────────────────────────────────────────

def resolve_siege(attacker, defender):
    atk = attacker["forces"]
    dfn = defender["forces"]
    atk_cmd = max(1, attacker.get("command", 60)) / 100.0
    dfn_cmd = max(1, defender.get("command", 60)) / 100.0

    supply_drain = max(20, int(atk * atk_cmd * 0.05))
    sortie_prob  = dfn_cmd * 0.3
    atk_loss = 0
    sortie_msg = ""
    if random.random() < sortie_prob:
        atk_loss = max(10, int(dfn * dfn_cmd * 0.03))
        atk = max(0, atk - atk_loss)
        sortie_msg = f"，守方突圍造成攻方損失 {atk_loss} 人"

    if atk <= 0:
        result  = "守方勝利"
        summary = f"{defender['name']} 突圍成功，{attacker['name']} 潰散撤退。"
    else:
        result  = "圍城進行中"
        summary = (
            f"{attacker['name']} 圍困 {defender['name']}，"
            f"消耗守方軍糧 {supply_drain}{sortie_msg}。"
            f"（攻 {atk} 人 | 守 {dfn} 人）繼續圍困中。"
        )

    return {
        "result": result, "atk_remain": atk, "dfn_remain": dfn,
        "supply_drain": supply_drain, "summary": summary,
        "attacker_name": attacker["name"], "defender_name": defender["name"],
    }


# ────────────────────────────────────────────────────
# 8. 評定裁決忠誠度影響
# ────────────────────────────────────────────────────

def apply_council_decision(state, topic, choice_id):
    changes = []
    pf      = state["player_faction"]

    for r in state["retainers"]:
        if r["faction"] != pf or r["rank"] == "大名":
            continue

        stance_data = topic["stances"].get(r["id"])
        if not stance_data:
            continue

        stance_label, comment, agree_with = stance_data
        is_neutral  = (agree_with == [])
        old_loyalty = r["loyalty"]
        old_label   = loyalty_label(old_loyalty)

        if choice_id == "delay":
            delta = -1 if not is_neutral else 0
        elif choice_id in agree_with:
            delta = +3
        elif not is_neutral:
            delta = -2
        else:
            delta = 0

        if delta != 0:
            r["loyalty"]       = max(0, min(100, old_loyalty + delta))
            r["loyalty_label"] = loyalty_label(r["loyalty"])
            changes.append({
                "name":         r["name"],
                "delta":        delta,
                "before_label": old_label,
                "after_label":  r["loyalty_label"],
            })
            state["log"].insert(0,
                f"【裁決影響】{r['name']} 忠誠度 {delta:+d}（{old_label} → {r['loyalty_label']}）")

    state["log"] = state["log"][:20]
    return state, changes
