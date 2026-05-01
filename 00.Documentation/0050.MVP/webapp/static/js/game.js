/* 《戰國三代記》MVP Webapp — game.js
   [重構] 一城一郡：district → castle 統一，家臣團轄地限制 */

'use strict';

// ── 工具函數 ─────────────────────────────────────────────
function showToast(msg, duration = 3000) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), duration);
}

function updateHUD(s) {
  const d = document.getElementById('hud-date');
  const g = document.getElementById('hud-gold');
  const u = document.getElementById('hud-supply');
  if (d) d.textContent = `永祿${s.date.year - 1557}年（${s.date.year}）${s.date.month}月`;
  if (g) g.textContent = s.gold;
  if (u) u.textContent  = s.supply;
}

function updateLog(logArr) {
  const el = document.getElementById('event-log');
  if (!el || !logArr) return;
  el.innerHTML = logArr.slice(0, 8).map(l => `<div class="log-entry">${l}</div>`).join('');
}

function playerFaction() {
  return document.body.dataset.player || 'oda';
}

async function apiFetch(url, method = 'GET', body = null) {
  const opts = { method, headers: {} };
  if (body) { opts.body = JSON.stringify(body); opts.headers['Content-Type'] = 'application/json'; }
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// ── 回合結算（UC-004） ────────────────────────────────────
function bindEndTurn() {
  document.querySelectorAll('.end-turn-btn, .js-end-turn').forEach(btn => {
    btn.addEventListener('click', endTurn);
  });
}

async function endTurn() {
  const btns = document.querySelectorAll('.end-turn-btn, .js-end-turn');
  btns.forEach(b => { b.disabled = true; b.textContent = '結算中…'; });
  try {
    const data = await apiFetch('/api/end-turn', 'POST');
    if (data.ok) {
      updateHUD(data.state);
      updateLog(data.state.log);
      showTurnOverlay(data.state);
    } else {
      showToast('結算失敗');
      btns.forEach(b => { b.disabled = false; b.textContent = '⏭ 結束本月'; });
    }
  } catch(e) {
    showToast('結算失敗：' + e.message);
    btns.forEach(b => { b.disabled = false; b.textContent = '⏭ 結束本月'; });
  }
}

function showTurnOverlay(state) {
  const overlay = document.getElementById('turn-overlay');
  const title   = document.getElementById('turn-overlay-title');
  const logEl   = document.getElementById('turn-overlay-log');
  if (!overlay) { location.reload(); return; }
  title.textContent = `回合結算 — 永祿${state.date.year - 1557}年（${state.date.year}）${state.date.month}月`;
  const logItems = (state.log || []).slice(0, 8);
  logEl.innerHTML = logItems.length
    ? logItems.map(l => `<div class="turn-log-item">${l}</div>`).join('')
    : '<div class="turn-log-item" style="color:var(--text-dim)">本月平靜無事。</div>';
  overlay.classList.add('open');
}

function closeTurnOverlay() {
  const overlay = document.getElementById('turn-overlay');
  if (overlay) overlay.classList.remove('open');
  location.reload();
}

// ── 城詳情 Modal（UC-010/011/012/020/021/022/023）─────────
// 一城一郡：district modal = castle modal，統一入口
let _currentCastleId = null;
let _attackMode = 'assault';

function setAttackMode(mode) {
  _attackMode = mode;
  document.getElementById('tab-assault').classList.toggle('active', mode === 'assault');
  document.getElementById('tab-siege').classList.toggle('active', mode === 'siege');
  const desc = document.getElementById('dm-mode-desc');
  if (mode === 'assault') {
    desc.textContent = '野戰：立即決戰，勝者取得此城。';
    document.getElementById('dm-attack-btn').textContent = '⚔ 出兵攻城';
  } else {
    desc.textContent = '圍城：每回合消耗守方軍糧，軍糧歸零時城池陷落。';
    document.getElementById('dm-attack-btn').textContent = '🏯 開始圍城';
  }
}

function openDistrictModal(castleId) {
  _currentCastleId = castleId;
  _attackMode = 'assault';

  apiFetch(`/api/castle/${castleId}`)
    .then(data => {
      const d  = data.castle;      // castle 物件（同時包含 district 屬性）
      const pf = playerFaction();
      const own = (data.castle_faction === pf);

      // --- Header ---
      document.getElementById('dm-title').textContent = d.name;
      document.getElementById('dm-type').textContent  =
        `${d.type}　${d.province}　${own ? '我方' : '敵方（' + data.castle_faction + '）'}`;

      // --- Basic info ---
      document.getElementById('dm-level').textContent   = `Lv${d.level}`;
      document.getElementById('dm-garrison').textContent= `${d.garrison} 人`;
      document.getElementById('dm-facility').textContent = d.building
        ? `${d.facility_name} Lv${d.facility_level}（建設中 ${d.building_turns}月後）`
        : `${d.facility_name} Lv${d.facility_level}`;
      document.getElementById('dm-gold-out').textContent   = `${data.output.gold} 金/月`;
      document.getElementById('dm-supply-out').textContent = `${data.output.supply} 糧/月`;
      document.getElementById('dm-chatelain').textContent  = data.chatelain ? data.chatelain.name : '（未設置）';
      document.getElementById('dm-daikan').textContent     = data.daikan    ? data.daikan.name    : '（未設置）';

      // --- Corps / Daimyo notice ---
      const noticeEl     = document.getElementById('dm-corps-notice');
      const noticeTextEl = document.getElementById('dm-corps-notice-text');
      const playerSec    = document.getElementById('dm-player-section');
      const atkSec       = document.getElementById('dm-attack-section');

      if (own) {
        atkSec.style.display = 'none';

        // 家臣團轄地 OR 大名本城 → 限制直接管理
        if (data.is_corps_territory) {
          noticeEl.style.display = '';
          noticeTextEl.innerHTML =
            `🏴 此城由家臣團「${data.corps_info.corps_name}」（首領：${data.corps_info.leader_name}）統轄。<br>` +
            `年貢・郡政升級・城防徵兵・出兵均已委任首領代理，玩家不可直接操作。`;
          playerSec.style.display = 'none';
        } else if (data.is_daimyo_home) {
          noticeEl.style.display = '';
          noticeTextEl.textContent = '👑 此為大名本城，年貢・設施・徵兵均可直接管理。此城不可分封給家臣團。';
          noticeEl.style.borderColor = 'rgba(201,162,39,0.4)';
          playerSec.style.display = '';
          _bindOwnControls(castleId, d, data);
        } else {
          noticeEl.style.display = 'none';
          playerSec.style.display = '';
          _bindOwnControls(castleId, d, data);
        }

      } else {
        // 敵方城
        noticeEl.style.display = 'none';
        playerSec.style.display = 'none';
        atkSec.style.display    = '';
        setAttackMode('assault');
        document.getElementById('dm-battle-result').style.display = 'none';
        document.getElementById('dm-attack-btn').style.display    = '';

        apiFetch('/api/state').then(st => {
          const opts = st.retainers.filter(r => r.faction === pf && r.rank !== '大名' && r.forces > 0);
          const sel  = document.getElementById('dm-attacker-select');
          sel.innerHTML = opts.length
            ? opts.map(r => `<option value="${r.id}">${r.name}（${r.rank}，${r.forces}兵）</option>`).join('')
            : '<option value="">— 無可出兵武將 —</option>';
          document.getElementById('dm-attack-btn').disabled = opts.length === 0;
        });

        document.getElementById('dm-attack-btn').onclick = () =>
          doAction(castleId, document.getElementById('dm-attacker-select').value);
      }

      document.getElementById('district-modal').classList.add('open');
    })
    .catch(e => {
      console.error('openDistrictModal failed:', e);
      showToast('載入城詳情失敗：' + e.message);
    });
}

function _bindOwnControls(castleId, d, data) {
  // Nengu slider
  const slider    = document.getElementById('dm-nengu-slider');
  const nenguVal  = document.getElementById('dm-nengu-val');
  const nenguPrev = document.getElementById('dm-nengu-preview');
  slider.value = d.nengu_rate;
  nenguVal.textContent  = d.nengu_rate + '%';
  nenguPrev.textContent = `預估本月金收入：${data.output.gold} 金`;
  slider.oninput = () => {
    nenguVal.textContent = slider.value + '%';
    const baseGold = data.output.gold / ((d.nengu_rate || 20) / 100);
    nenguPrev.textContent = `預估本月金收入：約 ${Math.round(baseGold * (slider.value / 100))} 金`;
  };
  slider.onchange = () => {
    apiFetch(`/api/castle/${castleId}/nengu`, 'POST', { rate: parseInt(slider.value) })
      .then(r => { if (r.ok) showToast(r.msg); else showToast(r.msg); })
      .catch(() => showToast('年貢調整失敗'));
  };

  // Upgrade card
  const upCard = document.getElementById('dm-upgrade-card');
  const upBtn  = document.getElementById('dm-upgrade-btn');
  if (data.next_upgrade) {
    const spec = data.next_upgrade;
    document.getElementById('dm-upgrade-name').textContent =
      `升級 → ${spec.name}（Lv${spec.level}）`;
    document.getElementById('dm-upgrade-meta').textContent =
      `費用：${spec.cost} 金　建設時間：${spec.turns} 月` +
      (spec.gold_out ? `　完工後月收約 +${Math.round(spec.gold_out * d.nengu_rate / 100)} 金` : '');
    upBtn.disabled = d.building || data.player_gold < spec.cost;
    upBtn.textContent = d.building ? '設施建設中' : data.player_gold < spec.cost ? '金錢不足' : '發出建設命令';
    upCard.style.display = '';
    upBtn.onclick = () => doUpgrade(castleId);
  } else {
    upCard.style.display = 'none';
  }

  // Mobilize
  const cityBtn   = document.getElementById('dm-city-btn');
  const farmerBtn = document.getElementById('dm-farmer-btn');
  const mobStatus = document.getElementById('dm-mobilize-status');
  cityBtn.disabled   = false;
  farmerBtn.disabled = false;
  mobStatus.textContent = '';
  cityBtn.onclick   = () => doMobilize(castleId, 'city');
  farmerBtn.onclick = () => doMobilize(castleId, 'farmer');
}

function closeDistrictModal() {
  document.getElementById('district-modal').classList.remove('open');
  _currentCastleId = null;
}

// 舊 API compat
function openCastleModal(id) { openDistrictModal(id); }
function closeCastleModal() { closeDistrictModal(); }

// ── 設施升級（UC-011） ───────────────────────────────────
async function doUpgrade(castleId) {
  const btn = document.getElementById('dm-upgrade-btn');
  btn.disabled = true; btn.textContent = '送出中…';
  try {
    const data = await apiFetch(`/api/castle/${castleId}/upgrade`, 'POST');
    if (data.ok) {
      updateHUD(data.state);
      showToast(data.msg);
      closeDistrictModal();
      setTimeout(() => location.reload(), 600);
    } else {
      showToast('升級失敗：' + data.msg);
      btn.disabled = false; btn.textContent = '發出建設命令';
    }
  } catch(e) { showToast('升級失敗：' + e.message); btn.disabled = false; btn.textContent = '發出建設命令'; }
}

// ── 徵兵（UC-020/021） ───────────────────────────────────
async function doMobilize(castleId, type) {
  const cityBtn   = document.getElementById('dm-city-btn');
  const farmerBtn = document.getElementById('dm-farmer-btn');
  const status    = document.getElementById('dm-mobilize-status');
  if (cityBtn) cityBtn.disabled = true;
  if (farmerBtn) farmerBtn.disabled = true;
  try {
    const data = await apiFetch('/api/mobilize', 'POST', { castle_id: castleId, type });
    if (data.ok) {
      updateHUD(data.state);
      showToast(data.msg);
      if (status) { status.textContent = data.msg; status.style.color = '#27ae60'; }
    } else {
      showToast(data.msg);
      if (status) { status.textContent = data.msg; status.style.color = '#e74c3c'; }
    }
  } catch(e) { showToast('徵兵失敗：' + e.message); }
  finally {
    if (cityBtn) cityBtn.disabled = false;
    if (farmerBtn) farmerBtn.disabled = false;
  }
}

// ── 軍事行動（UC-022 野戰 / UC-023 圍城） ──────────────────
async function doAction(castleId, attackerRetainerId) {
  if (!attackerRetainerId) { showToast('請先選擇出兵武將'); return; }
  const btn = document.getElementById('dm-attack-btn');
  btn.disabled = true; btn.textContent = '出兵中…';
  try {
    const data = await apiFetch('/api/battle', 'POST', {
      attacker_id: attackerRetainerId,
      target_castle: castleId,
      mode: _attackMode,
    });
    updateHUD(data.state);
    updateLog(data.state.log);

    const resultEl  = document.getElementById('dm-battle-result');
    const titleEl   = document.getElementById('dm-battle-result-title');
    const summaryEl = document.getElementById('dm-battle-summary');

    if (data.ok) {
      const r   = data.result;
      const cls = r.result.includes('攻方勝利') ? 'win' : r.result.includes('守方勝利') ? 'lose' : 'draw';
      resultEl.className = `battle-result ${cls}`;
      titleEl.textContent   = r.result;
      summaryEl.textContent = r.summary;
    } else {
      resultEl.className = 'battle-result lose';
      titleEl.textContent   = '無法出兵';
      summaryEl.textContent = data.msg;
    }
    resultEl.style.display = '';
    btn.style.display = 'none';
    showToast(data.msg || data.result?.result || '出兵完成');
    setTimeout(() => location.reload(), 3000);
  } catch(e) {
    showToast('出兵失敗：' + e.message);
    btn.disabled = false; btn.textContent = '⚔ 出兵';
  }
}

// ── 存檔 / 讀檔（UC-003/031 — localStorage） ──────────────
async function saveGame() {
  try {
    const st = await apiFetch('/api/state');
    localStorage.setItem('ssk_save', JSON.stringify(st));
    showToast('✓ 遊戲已存入快速存檔槽');
  } catch(e) { showToast('存檔失敗：' + e.message); }
}

async function loadGame() {
  const raw = localStorage.getItem('ssk_save');
  if (!raw) { showToast('尚無存檔資料'); return; }
  if (!confirm('確定讀取存檔？當前進度將被覆蓋。')) return;
  try {
    const data = await apiFetch('/api/load-state', 'POST', JSON.parse(raw));
    if (data.ok) { showToast('✓ 存檔讀取成功'); setTimeout(() => location.reload(), 800); }
    else showToast('讀取失敗：' + data.msg);
  } catch(e) { showToast('讀取失敗：' + e.message); }
}

function resetGame() {
  if (!confirm('確定重置遊戲回到初始狀態？')) return;
  apiFetch('/api/reset', 'POST').then(() => { showToast('遊戲已重置'); setTimeout(() => location.reload(), 800); });
}

// ── 地圖拖移 Pan（map-inner 整體平移）──────────────────────
function initMapDrag() {
  const container = document.getElementById('map-container');
  const inner     = document.getElementById('map-inner');
  if (!container || !inner) return;

  let isDragging = false;
  let startX = 0, startY = 0;
  let panX = 0, panY = 0;

  container.style.cursor = 'grab';

  container.addEventListener('mousedown', e => {
    if (e.target.closest('[data-castle]')) return;
    isDragging = true;
    startX = e.clientX - panX;
    startY = e.clientY - panY;
    container.style.cursor = 'grabbing';
    e.preventDefault();
  });

  document.addEventListener('mousemove', e => {
    if (!isDragging) return;
    panX = e.clientX - startX;
    panY = e.clientY - startY;
    inner.style.transform = `translate(${panX}px, ${panY}px)`;
  });

  document.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    container.style.cursor = 'grab';
  });

  // 觸控支援
  container.addEventListener('touchstart', e => {
    if (e.target.closest('[data-castle]')) return;
    const t = e.touches[0];
    isDragging = true;
    startX = t.clientX - panX;
    startY = t.clientY - panY;
  }, { passive: true });

  document.addEventListener('touchmove', e => {
    if (!isDragging) return;
    const t = e.touches[0];
    panX = t.clientX - startX;
    panY = t.clientY - startY;
    inner.style.transform = `translate(${panX}px, ${panY}px)`;
  }, { passive: true });

  document.addEventListener('touchend', () => { isDragging = false; });
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindEndTurn();
  initMapDrag();

  // Castle nodes on map / right panel → open territory modal
  document.querySelectorAll('[data-castle]').forEach(el => {
    el.addEventListener('click', e => {
      e.stopPropagation();
      openDistrictModal(el.dataset.castle);
    });
  });

  // Close modal on overlay background click
  const distModal = document.getElementById('district-modal');
  if (distModal) distModal.addEventListener('click', e => {
    if (e.target === distModal) distModal.classList.remove('open');
  });

  // ESC closes modals
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      ['district-modal', 'turn-overlay'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('open');
      });
    }
  });
});
