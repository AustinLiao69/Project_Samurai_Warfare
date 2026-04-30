/* 《戰國三代記》 MVP Webapp — Interactive JS
   遵照 PM006.MVP_SRS.md Use Case 實作基本互動
*/

// ── Toast ────────────────────────────────────────────────
function showToast(msg, duration = 2800) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), duration);
}

// ── HUD update (date, gold, supply) ─────────────────────
function updateHUD(s) {
  const dateEl = document.getElementById('hud-date');
  const goldEl = document.getElementById('hud-gold');
  const supEl  = document.getElementById('hud-supply');
  if (dateEl) dateEl.textContent = `永祿${s.date.year - 1557}年（${s.date.year}）${s.date.month}月`;
  if (goldEl) goldEl.textContent = s.gold;
  if (supEl)  supEl.textContent  = s.supply;
}

function updateLog(logArr) {
  const el = document.getElementById('event-log');
  if (!el) return;
  el.innerHTML = logArr.map(l => `<div class="log-entry">${l}</div>`).join('');
}

// ── End Turn (UC-004) ────────────────────────────────────
function bindEndTurn() {
  document.querySelectorAll('.end-turn-btn, .js-end-turn').forEach(btn => {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      btn.textContent = '結算中…';
      try {
        const res = await fetch('/api/end-turn', { method: 'POST' });
        const data = await res.json();
        if (data.ok) {
          updateHUD(data.state);
          updateLog(data.state.log);
          showToast('回合結算完成：' + (data.log[0] || '月份推進'));
          // reload to reflect state changes visually
          setTimeout(() => location.reload(), 1200);
        }
      } catch(e) {
        showToast('結算失敗，請重試');
        btn.disabled = false;
        btn.textContent = '結束回合';
      }
    });
  });
}

// ── District Modal (UC-010, UC-011, UC-012, UC-022) ──────
let currentDistrictId = null;

function openDistrictModal(districtId) {
  currentDistrictId = districtId;
  const overlay = document.getElementById('district-modal');
  if (!overlay) return;

  fetch(`/api/district/${districtId}`)
    .then(r => r.json())
    .then(data => {
      const d = data.district;
      const faction = data.castle_faction;

      // title
      document.getElementById('dm-title').textContent = d.name;
      document.getElementById('dm-type').textContent  = d.type;

      // info grid
      document.getElementById('dm-castle').textContent   = data.castle_name;
      document.getElementById('dm-facility').textContent = d.building
        ? `${d.facility_name} Lv${d.facility_level}（建設中 ${d.building_turns}月）`
        : `${d.facility_name} Lv${d.facility_level}`;
      document.getElementById('dm-gold-out').textContent   = data.output.gold + ' 金/月';
      document.getElementById('dm-supply-out').textContent = data.output.supply + ' 糧/月';
      document.getElementById('dm-retainer').textContent   = data.retainer ? data.retainer.name : '（未分封）';

      // nengu (UC-012)
      const slider = document.getElementById('dm-nengu-slider');
      const nenguVal = document.getElementById('dm-nengu-val');
      const nenguPrev = document.getElementById('dm-nengu-preview');
      slider.value = d.nengu_rate;
      nenguVal.textContent = d.nengu_rate + '%';
      nenguPrev.textContent = `預估本月收入：${data.output.gold} 金`;
      slider.oninput = () => {
        nenguVal.textContent = slider.value + '%';
        const est = Math.round(data.output.gold * (slider.value / d.nengu_rate));
        nenguPrev.textContent = `預估本月收入：約 ${est} 金`;
      };
      slider.onchange = () => saveNengu(districtId, slider.value);

      // upgrade (UC-011)
      const upCard = document.getElementById('dm-upgrade-card');
      const upBtn  = document.getElementById('dm-upgrade-btn');
      if (data.next_upgrade && faction === document.body.dataset.player) {
        const spec = data.next_upgrade;
        document.getElementById('dm-upgrade-name').textContent = `升級 → ${spec.name} (Lv${spec.level})`;
        document.getElementById('dm-upgrade-meta').textContent =
          `費用：${spec.cost} 金　建設時間：${spec.turns} 月　完工後月收 +${Math.round((spec.gold_out||spec.supply_out)*d.nengu_rate/100)}`;
        upBtn.disabled = d.building || data.player_gold < spec.cost;
        upBtn.textContent = d.building ? '建設中' : (data.player_gold < spec.cost ? '金錢不足' : '發出建設命令');
        upCard.style.display = '';
        upBtn.onclick = () => doUpgrade(districtId);
      } else {
        upCard.style.display = 'none';
      }

      // attack section (UC-022)
      const atkSection = document.getElementById('dm-attack-section');
      const atkSelect  = document.getElementById('dm-attacker-select');
      const atkBtn     = document.getElementById('dm-attack-btn');
      const battleResult = document.getElementById('dm-battle-result');
      battleResult.style.display = 'none';

      if (faction !== document.body.dataset.player) {
        atkSection.style.display = '';
        // populate attacker options from player retainers with forces > 0
        fetch('/api/state').then(r => r.json()).then(st => {
          const pf = st.player_faction;
          const opts = st.retainers.filter(r => r.faction === pf && r.rank !== '大名' && r.forces > 0);
          atkSelect.innerHTML = opts.map(r =>
            `<option value="${r.id}">${r.name}（${r.rank}，${r.forces}人）</option>`
          ).join('');
          atkBtn.onclick = () => doBattle(districtId, atkSelect.value);
        });
      } else {
        atkSection.style.display = 'none';
      }

      overlay.classList.add('open');
    });
}

function closeDistrictModal() {
  document.getElementById('district-modal').classList.remove('open');
  currentDistrictId = null;
}

// ── Save Nengu (US-014) ──────────────────────────────────
async function saveNengu(districtId, rate) {
  const res = await fetch(`/api/district/${districtId}/nengu`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ rate: parseInt(rate) }),
  });
  const data = await res.json();
  if (data.ok) showToast(data.msg);
}

// ── Upgrade Facility (UC-011) ────────────────────────────
async function doUpgrade(districtId) {
  const btn = document.getElementById('dm-upgrade-btn');
  btn.disabled = true;
  btn.textContent = '送出中…';

  const res = await fetch(`/api/district/${districtId}/upgrade`, { method: 'POST' });
  const data = await res.json();
  if (data.ok) {
    updateHUD(data.state);
    showToast(data.msg);
    closeDistrictModal();
    setTimeout(() => location.reload(), 800);
  } else {
    showToast('升級失敗：' + data.msg);
    btn.disabled = false;
    btn.textContent = '發出建設命令';
  }
}

// ── Battle (UC-022) ──────────────────────────────────────
async function doBattle(targetDistrictId, attackerRetainerId) {
  const btn = document.getElementById('dm-attack-btn');
  btn.disabled = true;
  btn.textContent = '出兵中…';

  const res = await fetch('/api/battle', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ attacker_id: attackerRetainerId, target_district: targetDistrictId }),
  });
  const data = await res.json();
  if (!data.ok) {
    showToast('出兵失敗：' + data.msg);
    btn.disabled = false;
    btn.textContent = '發動攻擊';
    return;
  }

  const r = data.result;
  const resultEl = document.getElementById('dm-battle-result');
  const titleEl  = document.getElementById('dm-battle-result-title');
  const summaryEl= document.getElementById('dm-battle-summary');
  const cls = r.result === '攻方勝利' ? 'win' : r.result === '守方勝利' ? 'lose' : 'draw';
  resultEl.className = `battle-result ${cls}`;
  titleEl.textContent  = r.result;
  summaryEl.textContent = r.summary;
  resultEl.style.display = '';

  updateHUD(data.state);
  updateLog(data.state.log);
  showToast(data.msg);
  btn.style.display = 'none';

  setTimeout(() => location.reload(), 2500);
}

// ── Reset Game ────────────────────────────────────────────
function resetGame() {
  if (!confirm('確定重置遊戲回到初始狀態？')) return;
  fetch('/api/reset', {method:'POST'}).then(() => location.reload());
}

// ── District dot click bindings ──────────────────────────
function bindDistrictDots() {
  document.querySelectorAll('[data-district]').forEach(el => {
    el.addEventListener('click', e => {
      e.stopPropagation();
      openDistrictModal(el.dataset.district);
    });
  });
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindEndTurn();
  bindDistrictDots();

  // close modal on overlay click
  const overlay = document.getElementById('district-modal');
  if (overlay) {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeDistrictModal();
    });
  }
});
