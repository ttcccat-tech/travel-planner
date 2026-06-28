// ===== State =====
const state = {
  regions: [],
  currentRegion: null,
  attractions: [],
  itineraries: {},
  transport: {},
  selectedDays: 5,
  wantItems: ['', '', ''],
  dontWantItems: ['', '', ''],
  autocompleteIndex: {},   // { slot: 0|1|2, type: 'want'|'dontwant' }
  highlightedIndex: {}      // { slot: highlighted index in dropdown }
};

// ===== Bootstrap =====
document.addEventListener('DOMContentLoaded', async () => {
  await loadRegions();
  wireEvents();
});

// ===== Load Regions =====
async function loadRegions() {
  try {
    const res = await fetch('data/regions.json');
    const data = await res.json();
    state.regions = data;
    const select = document.getElementById('region-select');
    data.forEach(r => {
      if (r.enabled !== false) {
        const opt = document.createElement('option');
        opt.value = r.name;
        opt.textContent = r.display_name;
        select.appendChild(opt);
      }
    });
  } catch (e) {
    console.error('Failed to load regions', e);
  }
}

// ===== Wire Events =====
function wireEvents() {
  document.getElementById('region-select').addEventListener('change', onRegionChange);
  document.getElementById('days-select').addEventListener('change', onDaysChange);
  document.getElementById('generate-btn').addEventListener('click', onGenerate);

  // Autocomplete inputs
  document.querySelectorAll('.want-input').forEach(input => {
    input.addEventListener('input', debounce(onWantInput, 200));
    input.addEventListener('keydown', onWantKeydown);
    input.addEventListener('focus', () => showDropdown(input.dataset.slot, 'want'));
  });

  document.querySelectorAll('.dontwant-input').forEach(input => {
    input.addEventListener('input', debounce(onDontWantInput, 200));
    input.addEventListener('keydown', onDontWantKeydown);
    input.addEventListener('focus', () => showDropdown(input.dataset.slot, 'dontwant'));
  });

  // Click outside to close dropdowns
  document.addEventListener('click', e => {
    if (!e.target.closest('.autocomplete-wrapper')) {
      closeAllDropdowns();
    }
  });
}

// ===== Region Change =====
async function onRegionChange(e) {
  const region = e.target.value;
  if (!region) {
    document.getElementById('days-select').disabled = true;
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('transport-panel').classList.add('hidden');
    return;
  }

  clearAlerts();
  state.currentRegion = region;

  // Load region data
  const [attRes, itinRes, transRes] = await Promise.all([
    fetch(`data/${region}/attractions.json`),
    fetch(`data/${region}/itineraries.json`),
    fetch(`data/${region}/transport.json`)
  ]);

  const [attData, itinData, transData] = await Promise.all([
    attRes.json(), itinRes.json(), transRes.json()
  ]);

  state.attractions = attData.attractions || [];
  state.itineraries = itinData.itineraries || {};
  state.transport = transData;

  // Populate days select
  const daysSelect = document.getElementById('days-select');
  daysSelect.innerHTML = '<option value="">— 請選擇天數 —</option>';
  Object.keys(state.itineraries).sort((a,b) => Number(a)-Number(b)).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = `${d}天${Number(d)-1}夜（${state.itineraries[d].name}）`;
    daysSelect.appendChild(opt);
  });
  daysSelect.disabled = false;

  // Show transport info
  renderTransportInfo(transData);

  document.getElementById('generate-btn').disabled = false;
}

// ===== Days Change =====
function onDaysChange(e) {
  state.selectedDays = Number(e.target.value);
}

// ===== Want Input (Autocomplete) =====
function onWantInput(e) {
  const slot = Number(e.target.dataset.slot);
  const query = e.target.value.trim();
  state.wantItems[slot] = query;
  showDropdown(slot, 'want', query);
}

function onWantKeydown(e) {
  const slot = Number(e.target.dataset.slot);
  const dropdown = document.querySelector(`.autocomplete-dropdown[data-slot="${slot}"][data-type="want"]`);
  if (!dropdown) return;
  const items = dropdown.querySelectorAll('.autocomplete-item');
  const current = state.highlightedIndex[`${slot}-want`] ?? -1;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-want`] = Math.min(current + 1, items.length - 1);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-want`]);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-want`] = Math.max(current - 1, 0);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-want`]);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (state.highlightedIndex[`${slot}-want`] >= 0) {
      items[state.highlightedIndex[`${slot}-want`]].click();
    }
  } else if (e.key === 'Escape') {
    closeDropdown(dropdown);
  }
}

// ===== DontWant Input =====
function onDontWantInput(e) {
  const slot = Number(e.target.dataset.slot);
  const query = e.target.value.trim();
  state.dontWantItems[slot] = query;
  showDropdown(slot, 'dontwant', query);
}

function onDontWantKeydown(e) {
  const slot = Number(e.target.dataset.slot);
  const dropdown = document.querySelector(`.autocomplete-dropdown[data-slot="${slot}"][data-type="dontwant"]`);
  if (!dropdown) return;
  const items = dropdown.querySelectorAll('.autocomplete-item');
  const current = state.highlightedIndex[`${slot}-dontwant`] ?? -1;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-dontwant`] = Math.min(current + 1, items.length - 1);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-dontwant`]);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-dontwant`] = Math.max(current - 1, 0);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-dontwant`]);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (state.highlightedIndex[`${slot}-dontwant`] >= 0) {
      items[state.highlightedIndex[`${slot}-dontwant`]].click();
    }
  } else if (e.key === 'Escape') {
    closeDropdown(dropdown);
  }
}

// ===== Show Dropdown =====
function showDropdown(slot, type, query = '') {
  const dropdown = document.querySelector(`.autocomplete-dropdown[data-slot="${slot}"][data-type="${type}"]`);
  if (!dropdown) return;

  const items = getFilteredItems(query, type);
  dropdown.innerHTML = items.map((item, i) => {
    const tagClass = `tag-${item.category}`;
    const tagLabel = categoryLabel(item.category);
    return `<div class="autocomplete-item" data-id="${item.id}" data-name="${item.name}" data-slot="${slot}" data-type="${type}">
      <span class="tag ${tagClass}">${tagLabel}</span>
      ${item.name}
    </div>`;
  }).join('');

  if (items.length === 0) {
    dropdown.classList.add('hidden');
    return;
  }

  dropdown.classList.remove('hidden');
  state.highlightedIndex[`${slot}-${type}`] = -1;

  // Wire click
  dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
    el.addEventListener('click', () => onItemSelect(el, type));
  });
}

function getFilteredItems(query, type) {
  if (!query) {
    // Show all when empty (first 20)
    return state.attractions.slice(0, 20);
  }
  const q = query.toLowerCase();
  return state.attractions.filter(a =>
    a.name.toLowerCase().includes(q) ||
    a.name_en.toLowerCase().includes(q) ||
    (a.tags || []).some(t => t.toLowerCase().includes(q))
  ).slice(0, 20);
}

function categoryLabel(cat) {
  const map = {
    attraction: '景點',
    hidden_gem: '秘境',
    food: '美食',
    outlet: 'OUTLET'
  };
  return map[cat] || cat;
}

// ===== Item Select =====
function onItemSelect(el, type) {
  const name = el.dataset.name;
  const id = el.dataset.id;
  const slot = Number(el.dataset.slot);

  if (type === 'want') {
    state.wantItems[slot] = name;
    const input = document.querySelector(`.want-input[data-slot="${slot}"]`);
    input.value = name;
    handleWantSelect(id, slot);
  } else {
    state.dontWantItems[slot] = name;
    const input = document.querySelector(`.dontwant-input[data-slot="${slot}"]`);
    input.value = name;
    handleDontWantSelect(id, slot);
  }

  closeAllDropdowns();
}

function handleWantSelect(itemId, slot) {
  const attr = state.attractions.find(a => a.id === itemId);
  if (!attr) return;

  const alerts = [];

  // If it's a hidden_gem/outlet, auto-add parent
  if (attr.parent) {
    const parent = state.attractions.find(a => a.id === attr.parent);
    if (parent && !state.wantItems.includes(parent.name)) {
      // Check if already in dontWant
      if (state.dontWantItems.includes(parent.name)) {
        // Remove from dontWant
        const idx = state.dontWantItems.indexOf(parent.name);
        state.dontWantItems[idx] = '';
        const dontInput = document.querySelector(`.dontwant-input[data-slot="${idx}"]`);
        if (dontInput) dontInput.value = '';
        alerts.push({ type: 'success', msg: `已自動將「${parent.name}」從「不去」移至「必去」` });
      }
      // Auto-add to first empty want slot
      const emptySlot = state.wantItems.findIndex(w => !w);
      if (emptySlot >= 0) {
        state.wantItems[emptySlot] = parent.name;
        const wantInput = document.querySelector(`.want-input[data-slot="${emptySlot}"]`);
        if (wantInput) wantInput.value = parent.name;
      }
      alerts.push({ type: 'success', msg: `已自動帶入父景點「${parent.name}」至必去（因您選了「${attr.name}」）` });
    }
  }

  // Remove from dontWant if present
  if (state.dontWantItems.includes(attr.name)) {
    const idx = state.dontWantItems.indexOf(attr.name);
    state.dontWantItems[idx] = '';
    const dontInput = document.querySelector(`.dontwant-input[data-slot="${idx}"]`);
    if (dontInput) dontInput.value = '';
    alerts.push({ type: 'success', msg: `已自動將「${attr.name}」從「不去」移除（因已在必去）` });
  }

  if (alerts.length) renderAlerts(alerts);
}

function handleDontWantSelect(itemId, slot) {
  const attr = state.attractions.find(a => a.id === itemId);
  if (!attr) return;

  const alerts = [];

  // If it has children selected in want, warn
  const children = state.attractions.filter(a => a.parent === itemId);
  const selectedChildren = children.filter(c => state.wantItems.includes(c.name));
  if (selectedChildren.length > 0) {
    alerts.push({
      type: 'error',
      msg: `⚠️「${attr.name}」被選為不去，但其下的【${selectedChildren.map(c=>c.name).join('、')}】被選為必去，請確認是否要移除這些子項目`
    });
  }

  // If parent is in want, warn
  if (attr.parent) {
    const parent = state.attractions.find(a => a.id === attr.parent);
    if (parent && state.wantItems.includes(parent.name)) {
      alerts.push({
        type: 'error',
        msg: `⚠️「${attr.name}」被選為不去，但其父景點「${parent.name}」在必去項目中，請確認是否衝突`
      });
    }
  }

  // Remove from want if present
  if (state.wantItems.includes(attr.name)) {
    const idx = state.wantItems.indexOf(attr.name);
    state.wantItems[idx] = '';
    const wantInput = document.querySelector(`.want-input[data-slot="${idx}"]`);
    if (wantInput) wantInput.value = '';
    alerts.push({ type: 'success', msg: `已自動將「${attr.name}」從「必去」移除（因已選為不去）` });
  }

  if (alerts.length) renderAlerts(alerts);
}

// ===== Render Alerts =====
function renderAlerts(alerts) {
  const container = document.getElementById('alerts-container');
  alerts.forEach(a => {
    const div = document.createElement('div');
    div.className = `alert alert-${a.type}`;
    div.textContent = a.msg;
    container.appendChild(div);
    // Auto-remove after 5s
    setTimeout(() => div.remove(), 5000);
  });
}

function clearAlerts() {
  document.getElementById('alerts-container').innerHTML = '';
}

// ===== Dropdown Helpers =====
function updateHighlight(dropdown, items, idx) {
  items.forEach((el, i) => el.classList.toggle('selected', i === idx));
  if (dropdown && idx >= 0 && items[idx]) {
    items[idx].scrollIntoView({ block: 'nearest' });
  }
}

function closeDropdown(dropdown) {
  dropdown.classList.add('hidden');
}

function closeAllDropdowns() {
  document.querySelectorAll('.autocomplete-dropdown').forEach(d => d.classList.add('hidden'));
}

// ===== Transport Info =====
function renderTransportInfo(trans) {
  const panel = document.getElementById('transport-panel');
  const content = document.getElementById('transport-content');

  const card = trans;
  let html = `<div class="transport-item"><strong>🏙️ 城市類型：</strong>${card.city_type === 'metropolitan' ? '都會型（建議大眾交通）' : '郊區型（建議自駕）'}</div>`;

  if (card.airport_to_city) {
    html += `<div class="transport-item"><strong>✈️ 機場進入市區：</strong><p>${card.airport_to_city.method}</p><p>${card.airport_to_city.route}</p><p>時間：${card.airport_to_city.estimated_time}｜費用：${card.airport_to_city.estimated_cost}</p></div>`;
  }

  if (card.within_city) {
    html += `<div class="transport-item"><strong>🚇 市區交通：</strong><p>${card.within_city.main_transport}</p>`;
    html += `<p><strong>建議票卡：</strong>${card.within_city.suggested_card}</p>`;
    if (card.within_city.ticket_options) {
      html += '<p><strong>優惠票券：</strong></p><ul>';
      card.within_city.ticket_options.forEach(t => {
        html += `<li>${t.name}（${t.price}）— ${t.desc}</li>`;
      });
      html += '</ul></p>';
    }
    html += '</div>';
  }

  if (card.driving_assessment) {
    html += `<div class="transport-item"><strong>🚗 自駕評估：</strong><p>${card.driving_assessment.recommendation}</p>`;
    if (card.driving_assessment.rental_tips) html += `<p>${card.driving_assessment.rental_tips}</p>`;
    if (card.driving_assessment.license_note) html += `<p>⚠️${card.driving_assessment.license_note}</p>`;
    html += '</div>';
  }

  if (card.cash_prep) {
    html += `<div class="transport-item"><strong>💴 現金準備：</strong><p>${card.cash_prep.recommendation}</p><p>${card.cash_prep.breakdown}</p><p>${card.cash_prep.note}</p></div>`;
  }

  if (card.transfer_tips && card.transfer_tips.length) {
    html += `<div class="transport-item"><strong>🔄 換乘注意：</strong><ul>`;
    card.transfer_tips.forEach(t => {
      html += `<li>${t.from} → ${t.to}：${t.note}</li>`;
    });
    html += '</ul></div>';
  }

  content.innerHTML = html;
  panel.classList.remove('hidden');
}

// ===== Generate Itinerary =====
async function onGenerate() {
  clearAlerts();

  const days = state.selectedDays;
  const wantItems = state.wantItems.filter(w => w);
  const dontWantItems = state.dontWantItems.filter(w => w);
  const otherNeeds = document.getElementById('other-needs').value.trim();

  // === Validation ===
  const errors = [];

  if (!state.currentRegion) errors.push('請先選擇地區');
  if (!days) errors.push('請選擇天數');

  // Find selected attraction IDs
  const wantIds = wantItems.map(name => findAttrIdByName(name)).filter(Boolean);
  const dontWantIds = dontWantItems.map(name => findAttrIdByName(name)).filter(Boolean);

  // Check capacity
  const maxPerDay = 2;
  const capacity = (days - 1) * maxPerDay + 1; // last day is half
  if (wantIds.length > capacity) {
    errors.push(`必去景點（${wantIds.length}個）超過${days}天能容納的上限（約${capacity}個），請拉長天數或減少必去`);
  }

  if (errors.length) {
    renderAlerts(errors.map(e => ({ type: 'error', msg: e })));
    return;
  }

  // === Generate ===
  const itin = state.itineraries[String(days)];
  if (!itin) {
    renderAlerts([{ type: 'error', msg: `尚無${days}天行程資料` }]);
    return;
  }

  // Build want map
  const wantMap = {};
  wantIds.forEach(id => {
    const attr = state.attractions.find(a => a.id === id);
    if (!attr) return;
    // Mark self
    wantMap[id] = true;
    // Mark parent if hidden_gem
    if (attr.parent) wantMap[attr.parent] = true;
  });

  // Filter out dontWant
  const dontWantMap = {};
  dontWantIds.forEach(id => {
    const attr = state.attractions.find(a => a.id === id);
    if (!attr) return;
    dontWantMap[id] = true;
    // Also mark children
    state.attractions.filter(a => a.parent === id).forEach(c => { dontWantMap[c.id] = true; });
  });

  // Zone-aware random draw: rebuild each day's activities from the zone pool
  const TIME_SLOTS = ['上午', '中午', '下午', '傍晚', '晚上'];
  const filteredDays = itin.days.map((day, dayIdx) => {
    // For arrival/departure, keep static transport/general activities
    if (day.type === 'arrival' || day.type === 'departure') {
      return {
        ...day,
        activities: day.activities.map(act => {
          if (act.type === 'transport' || act.type === 'shopping' || act.type === 'general') return act;
          const attr = state.attractions.find(a => a.name === act.item);
          if (!attr) return act;
          if (dontWantMap[attr.id]) return { ...act, _skipped: true };
          return act;
        }).filter(act => !act._skipped)
      };
    }

    // Normal day: draw from zone pool with shuffle
    const zones = day.zones || [];
    // Collect candidates from all listed zones
    const candidates = [];
    zones.forEach(zone => {
      state.attractions
        .filter(a => a.zone === zone)
        .forEach(a => candidates.push(a));
    });

    // Shuffle candidates (seeded by day index for reproducibility per session)
    for (let i = candidates.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [candidates[i], candidates[j]] = [candidates[j], candidates[i]];
    }

    // Fill with shuffled attractions, respecting want/dontWant
    const picked = [];
    const added = new Set();
    for (const attr of candidates) {
      if (added.has(attr.id)) continue;
      if (dontWantMap[attr.id]) continue;
      picked.push(attr);
      added.add(attr.id);
      if (picked.length >= 4) break;
    }

    // If want items are specified and not yet covered, inject them
    const pickedNames = new Set(picked.map(a => a.name));
    wantIds.forEach(id => {
      if (picked.length >= 5) return;
      const attr = state.attractions.find(a => a.id === id);
      if (!attr) return;
      if (added.has(attr.id)) return;
      if (dontWantMap[attr.id]) return;
      // Zone filter: only add if in same zone as this day or no zone restriction
      if (zones.length > 0 && attr.zone && !zones.includes(attr.zone)) return;
      picked.push(attr);
      added.add(attr.id);
    });

    // Build activity objects from picked attractions
    const activities = picked.map((attr, i) => {
      const timeSlot = TIME_SLOTS[i % TIME_SLOTS.length];
      const srcs = attr.sources || [];
      const youtube = srcs.find(s => s.includes('youtube')) || null;
      const blog = srcs.find(s => s) || null;
      return {
        time: timeSlot,
        item: attr.name,
        type: attr.category || 'attraction',
        stay: attr.stay_duration || '1小時',
        ticket: attr.ticket || '免費',
        need_reservation: attr.need_reservation || false,
        details: {
          note: attr.description || '',
          google_maps: null,
          youtube,
          blog_article: blog,
        }
      };
    });

    // Fallback: if pool was too small, keep original activities
    if (activities.length < 2) {
      return {
        ...day,
        activities: day.activities.map(act => {
          if (act.type === 'transport' || act.type === 'shopping' || act.type === 'general') return act;
          const attr = state.attractions.find(a => a.name === act.item);
          if (!attr) return act;
          if (dontWantMap[attr.id]) return { ...act, _skipped: true };
          return act;
        }).filter(act => !act._skipped)
      };
    }

    return { ...day, activities };
  });

  // If wantItems includes things NOT in base itinerary, add them
  const baseItems = filteredDays.flatMap(d => d.activities.map(a => a.item));
  const extraWantIds = wantIds.filter(id => {
    const attr = state.attractions.find(a => a.id === id);
    if (!attr) return false;
    return !baseItems.includes(attr.name);
  });

  const outputDiv = document.getElementById('itinerary-content');
  let html = '';

  filteredDays.forEach(day => {
    html += renderDayCard(day);
  });

  // Add extra want items note
  if (extraWantIds.length > 0) {
    html += `<div class="alert alert-warning" style="margin-top:12px">
      ⚠️ 以下必去景點未在標準行程中，將以順遊方式安排：${extraWantIds.map(id => state.attractions.find(a=>a.id===id)?.name).join('、')}
    </div>`;
  }

  outputDiv.innerHTML = html;

  document.getElementById('itinerary-output').classList.remove('hidden');
  document.getElementById('empty-state').classList.add('hidden');

  // Scroll to output
  document.getElementById('itinerary-output').scrollIntoView({ behavior: 'smooth' });
}

// ===== Render Day Card =====
function renderDayCard(day) {
  const isDeparture = day.type === 'departure';
  const title = isDeparture ? `${day.title}（下午留給機場/採買）` : day.title;

  let activitiesHtml = day.activities.map(act => {
    const badge = getBadgeHtml(act);
    const meta = getMetaHtml(act);
    const source = getSourceHtml(act);
    const timeLabel = act.time || '';

    // Wrap activity name in link if google_maps is available
    const itemLabel = (act.details?.google_maps)
      ? `<a href="${act.details.google_maps}" target="_blank" class="activity-name-link">${act.item}</a>`
      : act.item;

    return `<div class="activity-row">
      <div class="activity-time">${timeLabel}</div>
      <div class="activity-name">
        ${itemLabel}
        ${badge}
        ${source}
      </div>
      <div class="activity-meta">${meta}</div>
    </div>`;
  }).join('');

  return `<div class="day-card">
    <div class="day-header">Day ${day.day} — ${title}</div>
    ${activitiesHtml}
  </div>`;
}

function getBadgeHtml(act) {
  const type = act.type;
  const badges = {
    attraction: '<span class="badge badge-attr">景點</span>',
    hidden_gem: '<span class="badge badge-attr" style="background:#fff3e0;color:#e65100">秘境</span>',
    food: '<span class="badge badge-food">美食</span>',
    outlet: '<span class="badge badge-shop">OUTLET</span>',
    transport: '<span class="badge badge-trans">交通</span>',
    shopping: '<span class="badge badge-shop">購物</span>',
    mixed: '<span class="badge badge-mixed">順遊</span>',
    general: ''
  };
  let html = badges[type] || '';

  if (act.ticket && act.ticket !== '免費（消費即可入座）' && act.ticket !== '免費') {
    html += '<span class="badge badge-ticket">🎫 ' + act.ticket + '</span>';
  } else if (act.ticket === '免費（消費即可入座）' || act.ticket === '免費') {
    html += '<span class="badge badge-free">免費</span>';
  }

  if (act.need_reservation) {
    html += '<span class="badge badge-reserve">⚠️ 需預約</span>';
  }

  if (act.cash_only || act.ticket?.includes('現金')) {
    html += '<span class="badge badge-cash">💴 現金</span>';
  }

  return html;
}

function getMetaHtml(act) {
  let meta = '';
  if (act.stay) meta += `<span>⏱️ ${act.stay}</span>`;
  if (act.ticket && !act.ticket.includes('免費') && act.type !== 'transport') {
    meta += `<span>${act.ticket}</span>`;
  }
  if (act.note) meta += `<span style="color:#e65100">💡 ${act.note}</span>`;
  return meta || '<span style="color:#bdbdbd">—</span>';
}

// ===== Render Source Links =====
function getSourceHtml(act) {
  const links = [];

  // Priority 1: act.details (enriched itinerary data)
  if (act.details) {
    if (act.details.google_maps)
      links.push(`<a href="${act.details.google_maps}" target="_blank" class="source-link">📍 Google Maps</a>`);
    if (act.details.youtube)
      links.push(`<a href="${act.details.youtube}" target="_blank" class="source-link">🎬 YouTube</a>`);
    if (act.details.blog_article)
      links.push(`<a href="${act.details.blog_article}" target="_blank" class="source-link">📝 部落格</a>`);
    if (act.details.address && act.details.phone)
      links.push(`<span class="source-contact">📞 ${act.details.phone}</span>`);
  }

  // Priority 2: fall back to state.attractions sources
  if (links.length === 0) {
    const attr = state.attractions.find(a => a.name === act.item);
    if (attr?.sources?.length > 0) {
      links.push(`<div class="activity-source">📎 ${attr.sources[0]}</div>`);
    }
  }

  if (links.length === 0) return '';

  // Render contact info (if present)
  const contactHtml = links.filter(l => l.includes('source-contact')).map(l => l.replace('source-contact', 'source-link')).join('');
  const linkHtml = links.filter(l => !l.includes('source-contact')).join('');

  let html = `<div class="activity-source-links">${linkHtml}`;
  if (contactHtml) html += `<span class="source-contact-inline">${contactHtml}</span>`;
  html += '</div>';
  return html;
}

// ===== Find Attraction by Name =====
function findAttrIdByName(name) {
  const attr = state.attractions.find(a => a.name === name);
  return attr ? attr.id : null;
}

// ===== Print =====
document.getElementById('print-btn')?.addEventListener('click', () => {
  window.print();
});

// ===== Debounce =====
function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
