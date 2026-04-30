"""
遊戲邏輯層 — 回合結算、資源計算、戰鬥
對應 PM006 第 4 章
"""
import copy
import random
from data.initial import FACILITY_UPGRADE, loyalty_label

# ────────────────────────────────────────────────────
# 1. 資源計算（PM006 §4.2.2）
# ────────────────────────────────────────────────────

def calc_district_output(d):
    """依郡類型、設施等級、年貢率計算當月產出"""
    dtype = d["type"]
    lv = d["facility_level"]
    nengu = d["nengu_rate"] / 100.0

    spec = FACILITY_UPGRADE.get(dtype, [])
    row = next((r for r in spec if r["level"] == lv), spec[0] if spec else None)
    if not row:
        return {"gold": 0, "supply": 0}

    gold = int(row.get("gold_out", 0) * nengu)
    supply = int(row.get("supply_out", 0) * nengu)
    return {"gold": gold, "supply": supply}


def calc_garrison_cost(state, faction_id):
    """城兵每 100 人消耗 5 金"""
    total = 0
    for c in state["castles"]:
        if c["faction"] == faction_id:
            total += (c["garrison"] // 100) * 5
    return total


# ────────────────────────────────────────────────────
# 2. 回合結算（PM006 §4.1.2）
# ────────────────────────────────────────────────────

def process_turn(state):
    log = []
    pf = state["player_faction"]

    # Step 1 — 設施建設進度
    for d in state["districts"]:
        if d["building"] and d["building_turns"] > 0:
            d["building_turns"] -= 1
            if d["building_turns"] == 0:
                d["building"] = False
                d["facility_level"] += 1
                dtype = d["type"]
                new_name = next((r["name"] for r in FACILITY_UPGRADE.get(dtype, []) if r["level"] == d["facility_level"]), d["facility_name"])
                d["facility_name"] = new_name
                log.append(f"【建設完工】{d['name']} 的 {d['facility_name']} 升至 Lv{d['facility_level']}")

    # Step 2 — 資源產出（玩家勢力）
    gold_income = 0
    supply_income = 0
    player_castle_ids = {c["id"] for c in state["castles"] if c["faction"] == pf}

    for d in state["districts"]:
        if d["castle"] in player_castle_ids:
            out = calc_district_output(d)
            gold_income += out["gold"]
            supply_income += out["supply"]

    # Step 3 — 城兵維持費
    gold_cost = calc_garrison_cost(state, pf)
    net_gold = gold_income - gold_cost

    state["factions"][pf]["gold"] += net_gold
    state["factions"][pf]["military_supply"] += supply_income
    log.append(f"【資源結算】金收入 +{gold_income}（維持費 -{gold_cost}）= 淨 {net_gold:+d}　軍糧 +{supply_income}")

    # Step 4 — 忠誠度影響（PM006 §4.2.4，年貢 > 30% 扣忠誠）
    for d in state["districts"]:
        if d["castle"] in player_castle_ids and d["nengu_rate"] > 30 and d["retainer"]:
            delta = -round((d["nengu_rate"] - 30) * 0.5)
            r = next((r for r in state["retainers"] if r["id"] == d["retainer"]), None)
            if r and r["rank"] != "大名":
                r["loyalty"] = max(0, min(100, r["loyalty"] + delta))
                r["loyalty_label"] = loyalty_label(r["loyalty"])
                if delta < 0:
                    log.append(f"【忠誠度】{r['name']} 因高年貢 {d['nengu_rate']}%，忠誠度 {delta}")

    # Step 5 — NPC 今川簡易 AI（每月固定補充資源）
    state["factions"]["imagawa"]["gold"] += 150
    state["factions"]["imagawa"]["military_supply"] += 100

    # Step 6 — 月份推進
    state["date"]["month"] += 1
    if state["date"]["month"] > 12:
        state["date"]["month"] = 1
        state["date"]["year"] += 1
    state["turn"] += 1

    state["log"] = log + state.get("log", [])
    state["log"] = state["log"][:20]  # 保留最近 20 條
    return state, log


# ────────────────────────────────────────────────────
# 3. 設施升級（PM006 §4.2.3 / UC-011）
# ────────────────────────────────────────────────────

def upgrade_facility(state, district_id):
    d = next((x for x in state["districts"] if x["id"] == district_id), None)
    if not d:
        return None, "找不到郡"
    if d["building"]:
        return None, "該郡設施正在建設中"
    if d["facility_level"] >= d["facility_max"]:
        return None, "已達最高等級"

    dtype = d["type"]
    next_lv = d["facility_level"] + 1
    spec = next((r for r in FACILITY_UPGRADE.get(dtype, []) if r["level"] == next_lv), None)
    if not spec:
        return None, "無升級規格"

    pf = state["player_faction"]
    cost = spec["cost"]
    if state["factions"][pf]["gold"] < cost:
        return None, f"金錢不足（需要 {cost} 金，現有 {state['factions'][pf]['gold']} 金）"

    state["factions"][pf]["gold"] -= cost
    d["building"] = True
    d["building_turns"] = spec["turns"]
    if spec["turns"] == 0:
        d["facility_level"] = next_lv
        d["facility_name"] = spec["name"]
        d["building"] = False

    msg = f"【開始建設】{d['name']} 升級中（{spec['turns']} 月後完工）" if spec["turns"] > 0 else f"【升級完成】{d['name']} 升至 {spec['name']}"
    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 4. 年貢調整（PM006 §4.2.4）
# ────────────────────────────────────────────────────

def set_nengu(state, district_id, rate):
    rate = max(10, min(60, int(rate)))
    d = next((x for x in state["districts"] if x["id"] == district_id), None)
    if not d:
        return None, "找不到郡"
    old = d["nengu_rate"]
    d["nengu_rate"] = rate
    msg = f"【年貢調整】{d['name']} {old}% → {rate}%"
    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 5. 野戰結算（PM006 §4.3.3）
# ────────────────────────────────────────────────────

def resolve_battle(attacker, defender):
    """
    attacker / defender = {forces: int, command: int (0-100), name: str}
    回傳 {result, rounds, atk_remain, dfn_remain, summary}
    """
    atk = attacker["forces"]
    dfn = defender["forces"]
    atk_cmd = attacker.get("command", 60) / 100.0
    dfn_cmd = defender.get("command", 60) / 100.0

    atk_power = atk * atk_cmd
    dfn_power = dfn * dfn_cmd

    rounds = []
    max_rounds = 30

    for _ in range(max_rounds):
        if atk <= 0 or dfn <= 0:
            break
        atk_loss = max(1, int(dfn_power * 0.05 * random.uniform(0.8, 1.2)))
        dfn_loss = max(1, int(atk_power * 0.05 * random.uniform(0.8, 1.2)))
        atk = max(0, atk - atk_loss)
        dfn = max(0, dfn - dfn_loss)
        rounds.append({"atk": atk, "dfn": dfn})

    if dfn <= 0 and atk > 0:
        result = "攻方勝利"
        summary = f"{attacker['name']} 擊敗 {defender['name']}，殘餘兵力 {atk} 人佔領目標。"
    elif atk <= 0:
        result = "守方勝利"
        summary = f"{defender['name']} 成功防守，{attacker['name']} 全軍覆沒。"
    else:
        result = "平局（回合數耗盡）"
        summary = f"雙方激戰，攻方 {atk} 人 vs 守方 {dfn} 人，陷入膠著。"

    return {
        "result": result,
        "rounds": rounds,
        "atk_remain": atk,
        "dfn_remain": dfn,
        "summary": summary,
        "attacker_name": attacker["name"],
        "defender_name": defender["name"],
    }
