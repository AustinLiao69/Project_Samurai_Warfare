"""
遊戲邏輯層 — 回合結算、資源計算、戰鬥、徵兵、圍城
對應 PM006 §4 / UC-004/011/012/020/021/022/023
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
    lv    = d["facility_level"]
    nengu = d["nengu_rate"] / 100.0

    spec = FACILITY_UPGRADE.get(dtype, [])
    row  = next((r for r in spec if r["level"] == lv), spec[0] if spec else None)
    if not row:
        return {"gold": 0, "supply": 0}

    gold   = int(row.get("gold_out", 0) * nengu)
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
    pf  = state["player_faction"]

    # Step 1 — 設施建設進度
    for d in state["districts"]:
        if d.get("building") and d.get("building_turns", 0) > 0:
            d["building_turns"] -= 1
            if d["building_turns"] == 0:
                d["building"] = False
                d["facility_level"] += 1
                dtype    = d["type"]
                new_name = next(
                    (r["name"] for r in FACILITY_UPGRADE.get(dtype, []) if r["level"] == d["facility_level"]),
                    d["facility_name"]
                )
                d["facility_name"] = new_name
                log.append(f"【建設完工】{d['name']} 的 {d['facility_name']} 升至 Lv{d['facility_level']}")

    # Step 2 — 農兵徵集完成（UC-021，farmers 等待計時器）
    for c in state["castles"]:
        if c["faction"] == pf and c.get("farmer_pending", 0) > 0:
            c["farmer_pending"] -= 1
            if c["farmer_pending"] == 0 and c.get("farmer_incoming", 0) > 0:
                c["garrison"] += c["farmer_incoming"]
                log.append(f"【徵兵完成】{c['name']} 農兵 {c['farmer_incoming']} 人完成訓練，編入守備隊。")
                c["farmer_incoming"] = 0

    # Step 3 — 資源產出（玩家勢力）
    gold_income   = 0
    supply_income = 0
    player_cids   = {c["id"] for c in state["castles"] if c["faction"] == pf}

    for d in state["districts"]:
        if d["castle"] in player_cids:
            out = calc_district_output(d)
            gold_income   += out["gold"]
            supply_income += out["supply"]

    # Step 4 — 城兵維持費
    gold_cost = calc_garrison_cost(state, pf)
    net_gold  = gold_income - gold_cost

    state["factions"][pf]["gold"]             += net_gold
    state["factions"][pf]["military_supply"]  += supply_income
    log.append(f"【資源結算】金 +{gold_income}（維持 -{gold_cost}）= {net_gold:+d}　軍糧 +{supply_income}")

    # Step 5 — 忠誠度影響（年貢 > 30%）
    for d in state["districts"]:
        if d["castle"] in player_cids and d["nengu_rate"] > 30 and d.get("retainer"):
            delta = -round((d["nengu_rate"] - 30) * 0.5)
            r = next((x for x in state["retainers"] if x["id"] == d["retainer"]), None)
            if r and r["rank"] != "大名":
                r["loyalty"] = max(0, min(100, r["loyalty"] + delta))
                r["loyalty_label"] = loyalty_label(r["loyalty"])
                if delta < 0:
                    log.append(f"【忠誠度】{r['name']} 因高年貢，忠誠度 {delta:+d}")

    # Step 6 — NPC 今川 AI（簡易補充資源）
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
# 3. 設施升級（PM006 §4.2.3 / UC-011）
# ────────────────────────────────────────────────────

def upgrade_facility(state, district_id):
    d = next((x for x in state["districts"] if x["id"] == district_id), None)
    if not d:
        return None, "找不到郡"
    if d.get("building"):
        return None, "該郡設施正在建設中"
    if d["facility_level"] >= d["facility_max"]:
        return None, "已達最高等級"

    dtype  = d["type"]
    nxt_lv = d["facility_level"] + 1
    spec   = next((r for r in FACILITY_UPGRADE.get(dtype, []) if r["level"] == nxt_lv), None)
    if not spec:
        return None, "無升級規格"

    pf   = state["player_faction"]
    cost = spec["cost"]
    if state["factions"][pf]["gold"] < cost:
        return None, f"金錢不足（需 {cost} 金，現有 {state['factions'][pf]['gold']} 金）"

    state["factions"][pf]["gold"] -= cost
    if spec["turns"] == 0:
        d["facility_level"] = nxt_lv
        d["facility_name"]  = spec["name"]
        msg = f"【升級完成】{d['name']} → {spec['name']}（即時）"
    else:
        d["building"]       = True
        d["building_turns"] = spec["turns"]
        msg = f"【開始建設】{d['name']} 升級中（{spec['turns']} 月後完工，費用 {cost} 金）"

    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 4. 年貢調整（PM006 §4.2.4 / UC-012）
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
# 5. 徵兵（PM006 §4.3.1 / UC-020/021）
# ────────────────────────────────────────────────────

# 城兵容量：castle level * 500
CASTLE_GARRISON_MAX = {1: 1000, 2: 2000, 3: 4000, 4: 8000, 5: 15000}
# 每次徵兵量
CITY_MOBILIZE   = 300   # UC-020: 城兵徵召，即時，消耗 50 金
FARMER_MOBILIZE = 500   # UC-021: 農民兵，1 月後完成，消耗 30 金

def mobilize_troops(state, district_id, mtype):
    """
    mtype = "city"   → 城兵徵召（即時，UC-020）
    mtype = "farmer" → 農民兵（1月等待，UC-021）
    """
    d = next((x for x in state["districts"] if x["id"] == district_id), None)
    if not d:
        return None, "找不到郡"

    pf     = state["player_faction"]
    castle = next((c for c in state["castles"] if c["id"] == d["castle"]), None)
    if not castle or castle["faction"] != pf:
        return None, "此郡非我方領地"

    cap = CASTLE_GARRISON_MAX.get(castle.get("level", 1), 1000)

    if mtype == "city":
        cost = 50
        amt  = CITY_MOBILIZE
        if state["factions"][pf]["gold"] < cost:
            return None, f"城兵徵召需 {cost} 金（現有 {state['factions'][pf]['gold']} 金）"
        if castle["garrison"] >= cap:
            return None, f"城兵已達上限（{cap} 人）"
        actual = min(amt, cap - castle["garrison"])
        state["factions"][pf]["gold"] -= cost
        castle["garrison"] += actual
        msg = f"【城兵徵召】{castle['name']} 即時補充 {actual} 人（費用 {cost} 金）"
        state["log"].insert(0, msg)
        return state, msg

    elif mtype == "farmer":
        cost = 30
        amt  = FARMER_MOBILIZE
        if state["factions"][pf]["gold"] < cost:
            return None, f"農民兵徵集需 {cost} 金（現有 {state['factions'][pf]['gold']} 金）"
        if castle.get("farmer_pending", 0) > 0:
            return None, "已有農民兵正在訓練中（需等待完成）"
        if castle["garrison"] >= cap:
            return None, f"城兵已達上限（{cap} 人）"
        state["factions"][pf]["gold"] -= cost
        castle["farmer_pending"]  = 1   # 1 月後完成
        castle["farmer_incoming"] = min(amt, cap - castle["garrison"])
        msg = f"【農民徵集】{castle['name']} 農民兵 {castle['farmer_incoming']} 人將於下月編入守備隊（費用 {cost} 金）"
        state["log"].insert(0, msg)
        return state, msg

    return None, "未知的徵兵類型"


# ────────────────────────────────────────────────────
# 6. 野戰結算（PM006 §4.3.3 / UC-022）
# ────────────────────────────────────────────────────

def resolve_battle(attacker, defender):
    """
    attacker / defender = {forces: int, command: int (0-100), name: str}
    回傳 {result, atk_remain, dfn_remain, summary}
    """
    atk     = attacker["forces"]
    dfn     = defender["forces"]
    atk_cmd = max(1, attacker.get("command", 60)) / 100.0
    dfn_cmd = max(1, defender.get("command", 60)) / 100.0

    atk_power = atk * atk_cmd
    dfn_power = dfn * dfn_cmd

    rounds    = []
    max_rounds = 40

    for _ in range(max_rounds):
        if atk <= 0 or dfn <= 0:
            break
        atk_loss = max(1, int(dfn_power * 0.05 * random.uniform(0.8, 1.2)))
        dfn_loss = max(1, int(atk_power * 0.05 * random.uniform(0.8, 1.2)))
        atk = max(0, atk - atk_loss)
        dfn = max(0, dfn - dfn_loss)
        rounds.append({"atk": atk, "dfn": dfn})

    if dfn <= 0 and atk > 0:
        result  = "攻方勝利"
        summary = f"{attacker['name']} 擊敗 {defender['name']}！殘餘兵力 {atk} 人，佔領目標郡。"
    elif atk <= 0:
        result  = "守方勝利"
        summary = f"{defender['name']} 成功防守，{attacker['name']} 全軍覆沒。"
    else:
        result  = "守方勝利"
        summary = f"雙方激戰 {len(rounds)} 回合，攻方 {atk} 人 vs 守方 {dfn} 人，攻方兵疲撤退。"

    return {
        "result":        result,
        "atk_remain":   atk,
        "dfn_remain":   dfn,
        "summary":      summary,
        "attacker_name":attacker["name"],
        "defender_name":defender["name"],
    }


# ────────────────────────────────────────────────────
# 7. 圍城結算（PM006 §4.3.4 / UC-023）
# ────────────────────────────────────────────────────

def resolve_siege(attacker, defender):
    """
    圍城戰：每回合消耗守方 supply；supply 歸零則城陷。
    本次呼叫代表 1 回合圍城施壓。
    """
    atk = attacker["forces"]
    dfn = defender["forces"]

    atk_cmd = max(1, attacker.get("command", 60)) / 100.0
    dfn_cmd = max(1, defender.get("command", 60)) / 100.0

    # 圍城：攻方施壓損耗守方軍糧（非兵力）
    supply_drain = max(20, int(atk * atk_cmd * 0.05))
    # 守方可能反擊突圍（低機率）
    sortie_prob  = dfn_cmd * 0.3  # 30% * 統率率
    atk_loss = 0
    if random.random() < sortie_prob:
        atk_loss = max(10, int(dfn * dfn_cmd * 0.03))
        atk = max(0, atk - atk_loss)
        sortie_msg = f"，守方突圍造成攻方損失 {atk_loss} 人"
    else:
        sortie_msg = ""

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
        "result":       result,
        "atk_remain":  atk,
        "dfn_remain":  dfn,
        "supply_drain":supply_drain,
        "summary":     summary,
        "attacker_name":attacker["name"],
        "defender_name":defender["name"],
    }
