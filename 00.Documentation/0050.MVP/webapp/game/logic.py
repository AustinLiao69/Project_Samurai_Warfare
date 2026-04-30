"""
遊戲邏輯層 — 回合結算、資源計算、戰鬥、徵兵、圍城
[架構] 城（軍事）/ 郡（行政）分離：
  - 資源計算、設施升級、年貢調整 → 操作 district
  - 守備兵力、戰鬥、鄰接判斷  → 操作 castle
  - 每回合 log 重置（只保留本回合訊息）
"""
import copy
import random
from data.initial import FACILITY_UPGRADE, loyalty_label


# ────────────────────────────────────────────────────
# 0. 郡查詢 helper
# ────────────────────────────────────────────────────

def get_district_by_castle(state, castle_id):
    """回傳與指定城 1:1 對應的郡物件"""
    return next((d for d in state.get("districts", []) if d["castle_id"] == castle_id), None)

def get_castle_by_id(state, castle_id):
    return next((c for c in state["castles"] if c["id"] == castle_id), None)


# ────────────────────────────────────────────────────
# 1. 資源計算（操作郡物件）
# ────────────────────────────────────────────────────

def calc_district_output(d):
    """依郡類型、設施等級、年貢率計算當月產出"""
    dtype = d["type"]
    lv    = d["facility_level"]
    nengu = d["nengu_rate"] / 100.0
    spec  = FACILITY_UPGRADE.get(dtype, [])
    row   = next((r for r in spec if r["level"] == lv), spec[0] if spec else None)
    if not row:
        return {"gold": 0, "supply": 0}
    gold   = int(row.get("gold_out", 0) * nengu)
    supply = int(row.get("supply_out", 0) * nengu)
    return {"gold": gold, "supply": supply}

# 向後相容別名（部分呼叫仍用舊名）
def calc_castle_output(c_or_d):
    """接受城或郡物件，若為城則用 type/facility_level/nengu_rate 欄位（向後相容）"""
    return calc_district_output(c_or_d)


def calc_garrison_cost(state, faction_id):
    """城兵每 100 人消耗 5 金"""
    return sum((c["garrison"] // 100) * 5
               for c in state["castles"] if c["faction"] == faction_id)


# ────────────────────────────────────────────────────
# 2. 回合結算（log 每回合重置）
# ────────────────────────────────────────────────────

def process_turn(state):
    log = []            # 本回合事件（重置）
    pf  = state["player_faction"]

    # Step 1 — 郡設施建設進度
    for d in state.get("districts", []):
        if d.get("building") and d.get("building_turns", 0) > 0:
            d["building_turns"] -= 1
            if d["building_turns"] == 0:
                d["building"] = False
                d["facility_level"] += 1
                new_name = next(
                    (r["name"] for r in FACILITY_UPGRADE.get(d["type"], [])
                     if r["level"] == d["facility_level"]),
                    d["facility_name"]
                )
                d["facility_name"] = new_name
                # 同步城等級（軍事郡升級 → 城等級提升）
                if d["type"] == "軍事郡":
                    c = get_castle_by_id(state, d["castle_id"])
                    if c:
                        c["level"] = d["facility_level"]
                castle_name = next(
                    (c["name"] for c in state["castles"] if c["id"] == d["castle_id"]), d["name"]
                )
                log.append(f"【建設完工】{castle_name}（{d['name']}）的 {d['facility_name']} 升至 Lv{d['facility_level']}")

    # Step 2 — 農兵徵集完成（郡 farmer 欄位）
    for d in state.get("districts", []):
        c = get_castle_by_id(state, d["castle_id"])
        if not c or c["faction"] != pf:
            continue
        if d.get("farmer_pending", 0) > 0:
            d["farmer_pending"] -= 1
            if d["farmer_pending"] == 0 and d.get("farmer_incoming", 0) > 0:
                c["garrison"] = min(c["garrison"] + d["farmer_incoming"],
                                    c.get("max_garrison", 9999))
                log.append(f"【徵兵完成】{c['name']} 農兵 {d['farmer_incoming']} 人完成訓練。")
                d["farmer_incoming"] = 0

    # Step 3 — 資源產出（我方郡產出）
    gold_income = supply_income = 0
    for d in state.get("districts", []):
        c = get_castle_by_id(state, d["castle_id"])
        if c and c["faction"] == pf:
            out = calc_district_output(d)
            gold_income   += out["gold"]
            supply_income += out["supply"]

    # Step 4 — 城兵維持費
    gold_cost = calc_garrison_cost(state, pf)
    net_gold  = gold_income - gold_cost

    state["factions"][pf]["gold"]            = max(0, state["factions"][pf]["gold"] + net_gold)
    state["factions"][pf]["military_supply"] += supply_income
    log.append(f"【資源結算】金 +{gold_income}（維持 -{gold_cost}）= {net_gold:+d}　軍糧 +{supply_income}")

    # Step 5 — 忠誠度影響（郡年貢 > 30%）
    for d in state.get("districts", []):
        c = get_castle_by_id(state, d["castle_id"])
        if c and c["faction"] == pf and d["nengu_rate"] > 30 and d.get("retainer"):
            delta = -round((d["nengu_rate"] - 30) * 0.5)
            r = next((x for x in state["retainers"] if x["id"] == d["retainer"]), None)
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

    # 【重要】本回合 log 重置（只保留本回合事件）
    state["log"] = log
    return state, log


# ────────────────────────────────────────────────────
# 3. 設施升級（操作郡）
# ────────────────────────────────────────────────────

def upgrade_facility(state, castle_id):
    d = get_district_by_castle(state, castle_id)
    c = get_castle_by_id(state, castle_id)
    if not d or not c:
        return None, "找不到城或郡"
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
        if dtype == "軍事郡":
            c["level"] = nxt_lv
        msg = f"【升級完成】{c['name']}（{d['name']}）→ {spec['name']}（即時）"
    else:
        d["building"]       = True
        d["building_turns"] = spec["turns"]
        msg = f"【開始建設】{c['name']}（{d['name']}）升級中（{spec['turns']} 月後完工，費用 {cost} 金）"

    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 4. 年貢調整（操作郡）
# ────────────────────────────────────────────────────

def set_nengu(state, castle_id, rate):
    rate = max(10, min(60, int(rate)))
    d = get_district_by_castle(state, castle_id)
    c = get_castle_by_id(state, castle_id)
    if not d or not c:
        return None, "找不到城或郡"
    old = d["nengu_rate"]
    d["nengu_rate"] = rate
    msg = f"【年貢調整】{c['name']}（{d['name']}）{old}% → {rate}%"
    state["log"].insert(0, msg)
    return state, msg


# ────────────────────────────────────────────────────
# 5. 徵兵（城守備 + 郡 farmer）
# ────────────────────────────────────────────────────

CASTLE_GARRISON_MAX = {1: 1000, 2: 2000, 3: 4000, 4: 8000, 5: 15000}
CITY_MOBILIZE   = 300
FARMER_MOBILIZE = 500

def mobilize_troops(state, castle_id, mtype):
    c = get_castle_by_id(state, castle_id)
    d = get_district_by_castle(state, castle_id)
    if not c or not d:
        return None, "找不到城或郡"

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
        if d.get("farmer_pending", 0) > 0:
            return None, "已有農民兵正在訓練中"
        if c["garrison"] >= cap:
            return None, f"城兵已達上限（{cap} 人）"
        state["factions"][pf]["gold"] -= cost
        d["farmer_pending"]  = 1
        d["farmer_incoming"] = min(amt, cap - c["garrison"])
        msg = f"【農民徵集】{c['name']} 農民兵 {d['farmer_incoming']} 人將於下月編入（費用 {cost} 金）"
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
# 8. 評定裁決
#    - 忠誠度影響
#    - 特殊效果：獻城（ct_02 + comply）
# ────────────────────────────────────────────────────

def apply_council_decision(state, topic, choice_id):
    changes = []
    pf      = state["player_faction"]

    # ── 忠誠度影響 ──
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

    # ── 特殊效果：獻城 ──
    cede_castle_id = topic.get("cede_castle")
    if cede_castle_id and choice_id == "comply":
        c = get_castle_by_id(state, cede_castle_id)
        d = get_district_by_castle(state, cede_castle_id)
        if c and c["faction"] == pf:
            enemy_faction = next(
                (fid for fid in state["factions"] if fid != pf), "imagawa"
            )
            c["faction"] = enemy_faction
            if d:
                d["corps_id"] = None
            # 解除家臣駐守
            for retainer in state["retainers"]:
                if retainer.get("location") == cede_castle_id and retainer["faction"] == pf:
                    retainer["location"] = "castle_01"
            state["log"].insert(0, f"【獻城】{c['name']}（含{d['name'] if d else '其郡'}）已割讓予今川家！")

    return state, changes
