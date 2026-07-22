// ============================================================
//  app.js — Phase 2: 車站錨點 × Zone-Aware 行程生成
// ============================================================

// ----- State -----
// Expose as window.state for debugging / monkey-patching
window.state = state = {
  regions: [],
  currentRegion: null,

  // 資料
  attractions: [],   // attractions.json
  stations: [],     // stations.json
  outlets: [],      // outlets.json
  itineraries: {},  // itineraries.json
  transport: {},    // transport.json
  foodOptions: [],  // food_preferences.json

  // 車站錨點（必經車站，最多8個）
  wantStations: ['', '', '', '', '', '', '', ''],

  // 景點（必去，最多4個）
  wantItems: ['', '', '', ''],

  // Outlets（想去）
  wantOutlets: ['', ''],

  // 用餐習慣（多選）
  selectedFoods: [],

  // 天數
  selectedDays: 5,

  // Dropdown state
  highlightedIndex: {},
};

// ----- Bootstrap -----
document.addEventListener('DOMContentLoaded', async () => {
  await loadRegions();
  wireEvents();
  initFoodOptions();
  initDaysSlider();
});

// ----- Load Regions -----
async function loadRegions() {
  try {
    const res = await fetch('data/regions.json');
    const data = await res.json();
    state.regions = data;
    const select = document.getElementById('region-select');
    data.forEach(r => {
      if (r.enabled !== false) {
        const opt = document.createElement('option');
        opt.value = r.name;    // <-- 用名稱而非 index，fetch 路徑需要
        opt.textContent = r.display_name;
        select.appendChild(opt);
      }
    });
  } catch (e) {
    console.error('Failed to load regions', e);
  }
}

// ----- Init Days Slider -----
function initDaysSlider() {
  const slider = document.getElementById('days-range');
  const display = document.getElementById('days-display');
  if (!slider) return;
  const update = () => {
    const d = parseInt(slider.value);
    display.textContent = `${d}天${d - 1}夜`;
    state.selectedDays = d;
  };
  slider.addEventListener('input', update);
  update();
}

// ----- Init Food Options -----
async function initFoodOptions() {
  const container = document.getElementById('food-checkboxes');
  if (!container) return;

  const defaults = [
    '燒肉', '壽司', '拉麵', '懷石料理', '居酒屋', '甜點',
    '海鮮', '和牛', 'B級美食', '早餐', '宵夜', '素食'
  ];

  let options = defaults;

  try {
    const res = await fetch('data/food_preferences.json');
    if (res.ok) {
      const data = await res.json();
      options = [...new Set([...defaults, ...(data.foods || []).filter(f => f !== '素食')])];
    }
  } catch (_) {
    // use defaults
  }

  state.foodOptions = options;
  container.innerHTML = options.map((f, i) => `
    <label class="food-chip">
      <input type="checkbox" value="${f}" data-food-index="${i}">
      <span>${f}</span>
    </label>
  `).join('');

  // Wire checkboxes
  container.querySelectorAll('input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
      state.selectedFoods = [...container.querySelectorAll('input:checked')].map(c => c.value);
    });
  });
}

// ----- Wire Events -----
function wireEvents() {
  document.getElementById('region-select').addEventListener('change', onRegionChange);
  document.getElementById('generate-btn').addEventListener('click', onGenerate);

  // Autocomplete: station / want / outlet
  ['station', 'want', 'outlet'].forEach(type => {
    const cls = `${type}-input`;
    document.querySelectorAll(`.${cls}`).forEach(input => {
      input.addEventListener('input', debounce(e => onAutocompleteInput(e, type), 200));
      input.addEventListener('keydown', e => onAutocompleteKeydown(e, type));
      input.addEventListener('focus', () => showDropdown(Number(input.dataset.slot), type));
    });
  });

  // Click outside to close dropdowns
  document.addEventListener('click', e => {
    if (!e.target.closest('.autocomplete-wrapper')) {
      closeAllDropdowns();
    }
  });

  // Print
  document.getElementById('print-btn')?.addEventListener('click', () => window.print());
}

// ----- Region Change -----
async function onRegionChange(e) {
  const region = e.target.value;
  console.log('[DEBUG] onRegionChange called, region =', region);
  if (!region) {
    const daysSelect = document.getElementById('days-select');
    if (daysSelect) daysSelect.disabled = true;
    document.getElementById('generate-btn').disabled = true;
    document.getElementById('transport-panel').classList.add('hidden');
    return;
  }

  clearAlerts();
  state.currentRegion = region;

  // Load all region data in parallel via API
  // 生產：nginx reverse proxy /api/ → FastAPI（docker network）
  // 開發：直接連 API（window.__API_BASE__ 可外部注入）
  const API_BASE = window.__API_BASE__ || (location.hostname === 'localhost' ? 'http://localhost:8001/api' : '/api');

  let attData = [], staData = [], outData = [], itinData = {}, transData = {};
  try {
    const [attRes, staRes, outRes, itinRes, transRes] = await Promise.all([
      fetch(`${API_BASE}/${region}/attractions`),
      fetch(`${API_BASE}/${region}/stations`),
      fetch(`${API_BASE}/${region}/outlets`),
      fetch(`${API_BASE}/${region}/itineraries`),
      fetch(`data/${region}/transport.json`),
    ]);

    [attData, staData, outData, itinData, transData] = await Promise.all([
      attRes.json().catch(() => []),
      staRes.json().catch(() => []),
      outRes.json().catch(() => []),
      itinRes.json().catch(() => ({})),
      transRes.json().catch(() => ({})),
    ]);
  } catch(err) {
    console.error('[DEBUG] loadRegionData FAILED:', err.message);
    return;
  }

  // API returns raw arrays / dict; JSON wrapped data needs .attractions accessor
  state.attractions = attData.attractions || attData.data || attData || [];
  state.stations    = staData.stations    || staData.data || staData || [];
  state.outlets     = outData.outlets     || outData.data || outData || [];
  // API returns raw arrays / dict; JSON wrapped data needs .attractions accessor
  // 重要：itineraries API 回傳 array，但舊程式期待 dict {day_key: row}，需要轉換
  const rawItineraries = itinData.itineraries || itinData || [];
  state.itineraries = Array.isArray(rawItineraries)
    ? Object.fromEntries(rawItineraries.map(r => [String(r.day_key), r]))
    : (itinData.itineraries || itinData || {});
  state.transport    = transData || {};

  console.log('[DEBUG] state after load:', {
    attractions: state.attractions.length,
    stations: state.stations.length,
    itineraries_isArray: Array.isArray(state.itineraries),
  });

  // Init days slider max based on available itineraries
  const availableDays = Object.keys(state.itineraries).map(Number).filter(d => !isNaN(d));
  const maxDay = availableDays.length ? Math.max(...availableDays) : 10;
  const minDay = availableDays.length ? Math.min(...availableDays) : 1;
  const slider = document.getElementById('days-range');
  if (slider) {
    slider.min = minDay;
    slider.max = Math.min(maxDay, 10);
    if (state.selectedDays > slider.max) {
      state.selectedDays = Math.min(slider.max, 10);
      slider.value = state.selectedDays;
      document.getElementById('days-display').textContent = `${state.selectedDays}天${state.selectedDays - 1}夜`;
    }
  }

  // Show transport
  renderTransportInfo(state.transport);

  document.getElementById('generate-btn').disabled = false;
}

// ============================================================
//  Autocomplete
// ============================================================

function onAutocompleteInput(e, type) {
  const slot = Number(e.target.dataset.slot);
  const query = e.target.value.trim();
  if (type === 'station') state.wantStations[slot] = query;
  if (type === 'want')    state.wantItems[slot]    = query;
  if (type === 'outlet')  state.wantOutlets[slot]  = query;
  showDropdown(slot, type, query);
}

function onAutocompleteKeydown(e, type) {
  const slot = Number(e.target.dataset.slot);
  const dropdown = document.querySelector(`.autocomplete-dropdown[data-slot="${slot}"][data-type="${type}"]`);
  if (!dropdown) return;
  const items = [...dropdown.querySelectorAll('.autocomplete-item')];
  const current = state.highlightedIndex[`${slot}-${type}`] ?? -1;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-${type}`] = Math.min(current + 1, items.length - 1);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-${type}`]);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    state.highlightedIndex[`${slot}-${type}`] = Math.max(current - 1, 0);
    updateHighlight(dropdown, items, state.highlightedIndex[`${slot}-${type}`]);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (state.highlightedIndex[`${slot}-${type}`] >= 0) {
      items[state.highlightedIndex[`${slot}-${type}`]]?.click();
    }
  } else if (e.key === 'Escape') {
    closeDropdown(dropdown);
  }
}

function showDropdown(slot, type, query = '') {
  closeAllDropdowns(); // 先關閉所有其他 dropdown，避免多個同時出現
  const dropdown = document.querySelector(`.autocomplete-dropdown[data-slot="${slot}"][data-type="${type}"]`);
  if (!dropdown) return;

  const items = getFilteredItems(query, type).slice(0, 20);
  dropdown.innerHTML = ''; // 先清除舊內容，避免 debounce 累積
  if (items.length === 0) {
    dropdown.classList.add('hidden');
    return;
  }

  dropdown.innerHTML = items.map((item, i) => {
    const tagLabel = tagForType(type, item);
    return `<div class="autocomplete-item"
                  data-id="${item.id}"
                  data-name="${item.name}"
                  data-slot="${slot}"
                  data-type="${type}">
      ${tagLabel ? `<span class="tag tag-${type}">${tagLabel}</span>` : ''}
      ${item.name}
      ${item.zone ? `<span class="zone-hint">${item.zone}</span>` : ''}
    </div>`;
  }).join('');

  dropdown.classList.remove('hidden');
  state.highlightedIndex[`${slot}-${type}`] = -1;

  dropdown.querySelectorAll('.autocomplete-item').forEach(el => {
    el.addEventListener('click', () => onItemSelect(el, type));
  });
}

function tagForType(type, item) {
  if (type === 'station') {
    const companyMap = { 'JR': 'JR', '地下鐵': '地鐵', '南海': '南海', '阪神': '阪神', '近鐵': '近鐵', '西鐵': '西鐵', '泉北': '泉北', '東京Metro': 'Metro', '都營': '都營', '小田急': '小田急', '東鐵': '東鐵' };
    return companyMap[item.company] || item.company || '';
  }
  if (type === 'outlet') return 'OUTLET';
  const map = { attraction: '景點', hidden_gem: '秘境', food: '美食' };
  return map[item.category] || item.category || '';
}

function getFilteredItems(query, type) {
  const q = query.toLowerCase().trim();

  if (type === 'station') {
    const list = state.stations.filter(s => s.active !== false);
    if (!q) return list.slice(0, 20);
    return list.filter(s =>
      s.name.toLowerCase().includes(q) ||
      (s.name_en || '').toLowerCase().includes(q) ||
      (s.zone || '').toLowerCase().includes(q)
    );
  }

  if (type === 'outlet') {
    const list = state.outlets;
    if (!q) return list.slice(0, 20);
    return list.filter(o =>
      o.name.toLowerCase().includes(q) ||
      (o.zone || '').toLowerCase().includes(q)
    );
  }

  if (type === 'want') {
    const list = [...state.attractions, ...state.outlets];
    if (!q) return list.slice(0, 20);
    return list.filter(a =>
      a.name.toLowerCase().includes(q) ||
      (a.name_en || '').toLowerCase().includes(q) ||
      (a.tags || []).some(t => t.toLowerCase().includes(q))
    );
  }

  return [];
}

function onItemSelect(el, type) {
  const name = el.dataset.name;
  const id   = el.dataset.id;
  const slot = Number(el.dataset.slot);

  if (type === 'station') {
    state.wantStations[slot] = name;
    document.querySelector(`.station-input[data-slot="${slot}"]`).value = name;
    handleStationSelect(id, slot);
  } else if (type === 'want') {
    state.wantItems[slot] = name;
    document.querySelector(`.want-input[data-slot="${slot}"]`).value = name;
    handleWantSelect(id, slot);
  } else if (type === 'outlet') {
    state.wantOutlets[slot] = name;
    document.querySelector(`.outlet-input[data-slot="${slot}"]`).value = name;
    handleOutletSelect(id, slot);
  }

  closeAllDropdowns();
}

// ----- Handle Selections -----
function handleStationSelect(stationId, slot) {
  // No special logic yet; station anchors are used in itinerary generation
}

function handleWantSelect(itemId, slot) {
  const attr = state.attractions.find(a => a.id === itemId) ||
                state.outlets.find(a => a.id === itemId);
  if (!attr) return;

  const alerts = [];

  // If hidden_gem / sub-item, auto-add parent
  if (attr.parent) {
    const parent = state.attractions.find(a => a.id === attr.parent);
    if (parent && !state.wantItems.includes(parent.name)) {
      const emptySlot = state.wantItems.findIndex(w => !w);
      if (emptySlot >= 0) {
        state.wantItems[emptySlot] = parent.name;
        document.querySelector(`.want-input[data-slot="${emptySlot}"]`).value = parent.name;
        alerts.push({ type: 'info', msg: `已自動帶入父景點「${parent.name}」` });
      }
    }
  }

  // Phase 1.2: 自動推薦同車站的景點與美食（station_id 相同者）
  if (attr.station_id) {
    // 找同 station_id 的其他景點（排除自己）
    const sameStation = state.attractions.filter(a =>
      a.station_id === attr.station_id &&
      a.id !== attr.id &&
      !state.wantItems.includes(a.name)
    );
    sameStation.slice(0, 2).forEach(a => {
      const emptySlot = state.wantItems.findIndex(w => !w);
      if (emptySlot >= 0) {
        state.wantItems[emptySlot] = a.name;
        document.querySelector(`.want-input[data-slot="${emptySlot}"]`).value = a.name;
        alerts.push({ type: 'success', msg: `已自動推薦同車站景點「${a.name}」` });
      }
    });

    // 找同 station_id 的美食，先匹配用餐喜好，再按 priority 排序
    const selectedFoods = state.selectedFoods; // e.g. ['燒肉','拉麵','壽司']
    const sameStationFood = state.attractions.filter(a =>
      a.station_id === attr.station_id &&
      a.category === 'food' &&
      a.id !== attr.id &&
      !state.wantItems.includes(a.name)
    );

    // 用餐喜好評分：tag/sub_category 有 match 即得 1 分，priority 加權
    const scored = sameStationFood.map(a => {
      const tags = a.tags || [];
      const subCat = a.sub_category || '';
      let score = 0;
      selectedFoods.forEach(pref => {
        if (tags.some(t => t.includes(pref) || pref.includes(t))) score++;
        if (subCat.includes(pref) || pref.includes(subCat)) score++;
      });
      score += (a.priority || 1);
      return { ...a, _score: score };
    });

    // 分數 > 0（有匹配）優先；沒匹配但有 priority 的食物也可推薦
    scored.sort((a, b) => b._score - a._score);
    const bestFood = scored[0];
    if (bestFood && bestFood._score > 0) {
      const emptySlot = state.wantItems.findIndex(w => !w);
      if (emptySlot >= 0) {
        state.wantItems[emptySlot] = bestFood.name;
        document.querySelector(`.want-input[data-slot="${emptySlot}"]`).value = bestFood.name;
        alerts.push({ type: 'success', msg: `已自動推薦符合飲食偏好的美食「${bestFood.name}」` });
      }
    } else if (scored.length > 0) {
      // 沒有完美匹配時，推薦最高 priority 的食物
      const emptySlot = state.wantItems.findIndex(w => !w);
      if (emptySlot >= 0) {
        state.wantItems[emptySlot] = scored[0].name;
        document.querySelector(`.want-input[data-slot="${emptySlot}"]`).value = scored[0].name;
        alerts.push({ type: 'success', msg: `已自動推薦美食「${scored[0].name}」` });
      }
    }
  }

  if (alerts.length) renderAlerts(alerts);
}

// Phase 1.2: 自動推薦同車站的景點與美食（station_id 相同者）

function handleOutletSelect(itemId, slot) {
  // Outlets: if already selected in want-items, skip
  // Otherwise auto-add to wantItems if there's space
  const outlet = state.outlets.find(a => a.id === itemId);
  if (!outlet) return;

  if (state.wantItems.includes(outlet.name)) {
    renderAlerts([{ type: 'info', msg: `「${outlet.name}」已在必去景點中` }]);
    return;
  }

  const emptySlot = state.wantItems.findIndex(w => !w);
  if (emptySlot >= 0) {
    state.wantItems[emptySlot] = outlet.name;
    document.querySelector(`.want-input[data-slot="${emptySlot}"]`).value = outlet.name;
    renderAlerts([{ type: 'success', msg: `已自動將「${outlet.name}」加入必去景點` }]);
  }
}

// ============================================================
//  Generate Itinerary
// ============================================================

async function onGenerate() {
  clearAlerts();
  try {
  const days = state.selectedDays;
  const wantItems    = state.wantItems.filter(w => w).map(name => findItemByName(name)).filter(Boolean);
  const wantOutlets  = state.wantOutlets.filter(w => w).map(name => findOutletByName(name)).filter(Boolean);
  const wantStations = state.wantStations.filter(w => w).map(name => findStationByName(name)).filter(Boolean);
  const otherNeeds   = document.getElementById('other-needs').value.trim();

  // --- Validation (Phase 4) ---
  const errors = [];
  if (!state.currentRegion) errors.push('請先選擇地區');
  if (!days) errors.push('請選擇天數');
  if (errors.length) {
    renderAlerts(errors.map(e => ({ type: 'error', msg: e })));
    return;
  }

  // Phase 4.1: 天數超容警告
  const warnCapacity = (days - 1) * 2 + 1;
  const totalSelected = wantItems.length + wantStations.length;
  if (totalSelected > warnCapacity) {
    renderAlerts([{
      type: 'warning',
      msg: `⚠️ 已選 ${totalSelected} 個項目（含 ${wantItems.length} 景點 + ${wantStations.length} 車站），超過 ${days} 天可容納上限（約 ${warnCapacity} 個）。系統將優先保留您選擇的景點，超出的項目會排在備選。`
    }]);
  }

  // Phase 4.2: 父子景點連動警告（秘境/子景點被選時，自動帶入父景點）
  const infoAlerts = [];
  wantItems.forEach(attr => {
    if (attr.parent) {
      const parent = state.attractions.find(a => a.id === attr.parent);
      if (parent && !wantItems.find(w => w.id === parent.id)) {
        infoAlerts.push({ type: 'info', msg: `ℹ️ 「${attr.name}」的父景點「${parent.name}」已自動帶入行程` });
      }
    }
  });
  if (infoAlerts.length) renderAlerts(infoAlerts);

  // --- Phase 1.2 邏輯：只選車站 → 自動把車站標記的景點加入行程 ---
  let finalWantItems = [...wantItems];
  const userSelectedIds = new Set(wantItems.map(a => a.id));

  wantStations.forEach(station => {
    if (station.zone) {
      // 找同 zone 的景點（category=attraction/hidden_gem）
      const fromStation = state.attractions.filter(a =>
        a.zone === station.zone &&
        !userSelectedIds.has(a.id) &&
        (a.category === 'attraction' || a.category === 'hidden_gem')
      );
      fromStation.slice(0, 3).forEach(a => {
        if (!userSelectedIds.has(a.id)) {
          finalWantItems.push(a);
          userSelectedIds.add(a.id);
        }
      });
    }
  });

  // --- Phase 1.2 邏輯：當天數不足，優先放使用者選擇的景點，車站由系統自動填充 ---
  // Phase 6: 將使用者選擇的 outlets 也加入行程（不佔主要景點額度）
  const outletItems = wantOutlets.filter(o => !userSelectedIds.has(o.id));
  outletItems.forEach(o => {
    finalWantItems.push(o);
    userSelectedIds.add(o.id);
  });
  const capacity = (days - 1) * 2 + 1;
  const finalItems = finalWantItems.slice(0, capacity); // 優先取使用者選擇的，超過則截斷
  const overflowItems = finalWantItems.slice(capacity); // 車站自動帶入但放不下的

  // --- Load itinerary template ---
  const itin = state.itineraries[String(days)];
  if (!itin) {
    renderAlerts([{ type: 'error', msg: `尚無${days}天行程資料` }]);
    return;
  }

  const itinDays = itin.days_json || itin.days || [];
  console.log('[DEBUG] itinDays:', itinDays, 'type:', typeof itinDays, 'isArray:', Array.isArray(itinDays));

  // --- Zone pools ---
  const zonePools = buildZonePools(wantStations, finalItems);

  // --- Generate each day ---
  const generatedDays = itinDays.map((day, dayIdx) => {
    if (day.type === 'arrival' || day.type === 'departure') {
      return buildSpecialDay(day);
    }
    return buildNormalDay(day, dayIdx, zonePools, finalItems, wantStations, otherNeeds);
  });

  // --- Render ---
  renderItinerary(generatedDays, days);
  document.getElementById('itinerary-output').classList.remove('hidden');
  document.getElementById('empty-state').classList.add('hidden');
  } catch(err) {
    console.error('[onGenerate ERROR]:', err.message, err.stack);
  }
}

// ----- Build zone pools (attractions+outlets grouped by zone, with station anchors) -----
function buildZonePools(wantStations, wantItems) {
  // Find station zones from selected stations
  const forcedZones = new Set(wantStations.map(s => s.zone).filter(Boolean));

  // Also collect zones from wantItems (景點+美食+outlet 都算 zone 線索)
  wantItems.forEach(attr => {
    if (attr.zone) forcedZones.add(attr.zone);
  });

  // Group all items by zone (attraction/hidden_gem/outlet/shopping/meal 都納入)
  const zoneMap = {};
  state.attractions.forEach(a => {
    const z = a.zone || '其他';
    if (!zoneMap[z]) zoneMap[z] = [];
    zoneMap[z].push(a);
  });
  // 美食（meals 表）也加入 zone pool
  if (state.meals) {
    state.meals.forEach(m => {
      const z = m.zone || '其他';
      if (!zoneMap[z]) zoneMap[z] = [];
      zoneMap[z].push(m);
    });
  }
  // outlets 同様
  if (state.outlets) {
    state.outlets.forEach(o => {
      const z = o.zone || '其他';
      if (!zoneMap[z]) zoneMap[z] = [];
      zoneMap[z].push(o);
    });
  }

  return { zoneMap, forcedZones: [...forcedZones] };
}

// ----- Build normal day -----
// Strategy: template as skeleton, real DB data as flesh
// 1. Extract zones from template activities
// 2. Find REAL attractions from state.attractions matching those zones
// 3. Template meals → render directly (they're named restaurant suggestions)
// 4. Zone pool fill → random DB items for zones with no template coverage
function buildNormalDay(day, dayIdx, zonePools, finalItems, wantStations, otherNeeds) {
  const { zoneMap, forcedZones } = zonePools;
  const zones = day.zones || [];
  const selectedZones = zones.length ? zones : forcedZones.slice(0, 2);

  // ── Step 0: Collect template info ────────────────────────────────────────
  const templateZones = new Set();
  const templateMeals = [];   // {slot, item}
  const templateActivityNames = []; // attraction names from template to try to match DB
  [...day.activities || []].forEach(act => {
    if (act.zone) templateZones.add(act.zone);
    if (act.type === 'meal' && act.slot && act.item && !act.item.includes('彈性用餐')) {
      templateMeals.push({ slot: act.slot, item: act.item });
    }
    if ((act.type === 'attraction' || act.type === 'shopping' || act.type === 'general') && act.item) {
      templateActivityNames.push(act.item);
    }
  });

  // ── Step 1: Resolve zones and build candidate pool ─────────────────────────
  const allZonesAvailable = Object.keys(zoneMap);
  const enrichedZones = [...new Set([...forcedZones, ...selectedZones, ...templateZones])];

  // planned Set must be declared before addToPool closure captures it
  const planned = new Set();
  const chosen = [];  // final attraction/shopping items for this day
  const userSelectedIds = new Set(finalItems.map(w => w.id));

  // Build name→attraction map for template name matching
  const attractionByName = {};
  state.attractions.forEach(a => { attractionByName[a.name] = a; });

  // Candidate pool from enriched zones
  const candidatePool = [];
  const addToPool = (zoneList) => zoneList.forEach(z => {
    if (zoneMap[z]) {
      zoneMap[z].forEach(a => {
        if (!planned.has(a.id) && ['attraction','hidden_gem','outlet','shopping'].includes(a.category)) {
          candidatePool.push(a);
        }
      });
    }
  });
  addToPool(enrichedZones);

  // Deep fallback: if pool is empty, broaden to ALL zones
  if (candidatePool.length === 0 && allZonesAvailable.length > 0) {
    addToPool(shuffle(allZonesAvailable).slice(0, 10));
  }

  // ── Step 2: Match template activity names to real DB attractions ────────────
  templateActivityNames.forEach(name => {
    let match = attractionByName[name];
    if (!match) {
      const parts = name.split('、');
      match = attractionByName[parts[0].trim()];
    }
    if (match && !planned.has(match.id)) {
      chosen.push(match);
      planned.add(match.id);
    }
  });

  // Add user-selected items (priority)
  finalItems.forEach(w => {
    if (!planned.has(w.id) && ['attraction','hidden_gem','outlet','shopping'].includes(w.category)) {
      chosen.push(w);
      planned.add(w.id);
    }
  });

  // ── Step 3: Zone pool fill — random DB items for empty slots ────────────────
  const finalZones = candidatePool.length > 0 ? enrichedZones : shuffle(allZonesAvailable).slice(0, 10);
  if (candidatePool.length === 0) {
    addToPool(finalZones);
  }
  const shuffled = shuffle(candidatePool);
  const maxAttractions = 2;
  for (let i = 0; i < maxAttractions && i < shuffled.length; i++) {
    if (!planned.has(shuffled[i].id)) {
      chosen.push(shuffled[i]);
      planned.add(shuffled[i].id);
    }
  }

  // ── Step 4: Build activity list ──────────────────────────────────────────
  const activities = [];

  // Station anchor
  const anchorStation = wantStations.find(s => finalZones.some(z => z === s.zone));
  if (anchorStation) {
    activities.push({
      type: 'transport_anchor',
      station: anchorStation.name,
      station_id: anchorStation.id,
      note: `必經車站：${anchorStation.name}`
    });
  }

  // Meals — 5 slots: template meals first, then fill from meals DB by zone
  const mealSlots = ['上午', '中午', '下午', '傍晚', '晚上'];
  const foodPref = otherNeeds || state.selectedFoods.join('、');

  // Build a meals-by-zone map for fast lookup
  const mealsByZone = {};
  if (state.meals) {
    state.meals.forEach(m => {
      const z = m.zone || '其他';
      if (!mealsByZone[z]) mealsByZone[z] = [];
      mealsByZone[z].push(m);
    });
  }

  mealSlots.forEach(slot => {
    const tmpl = templateMeals.find(m => m.slot === slot);
    if (tmpl) {
      activities.push({ type: 'meal', slot, note: `${tmpl.item}（模板推薦）` });
    } else {
      let foundMeal = null;
      for (const z of finalZones) {
        const pool = mealsByZone[z] || [];
        const unused = pool.filter(m => !planned.has(m.id));
        if (unused.length > 0) {
          foundMeal = unused[0];
          planned.add(foundMeal.id);
          break;
        }
      }
      if (foundMeal) {
        activities.push({
          type: 'meal',
          slot,
          note: `${foundMeal.name}`,
          details: foundMeal.details || {},
        });
      } else {
        activities.push({
          type: 'meal',
          slot,
          note: `${slot} — 彈性用餐（${foodPref || '參考用餐習慣'})`
        });
      }
    }
  });

  // Attractions (max 2)
  chosen.forEach(attr => {
    activities.push({
      type: attr.category || 'attraction',
      item: attr.name,
      item_id: attr.id,
      station_id: attr.station_id,
      duration: attr.stay_duration || '1-2小時',
      ticket: attr.ticket || '',
      description: attr.description || '',
      details: attr.details || {},
      sources: attr.sources || [],
    });
  });

  return {
    ...day,
    day: dayIdx + 1,
    activities,
    zones: finalZones.slice(0, 2),
  };
}

// ----- Build special day (arrival/departure) -----
// Strategy: keep transport/shopping/general, fill all 5 meal slots
function buildSpecialDay(day) {
  const templateMeals = {};
  const otherActivities = [];

  [...(day.activities || [])].forEach(act => {
    if (act.type === 'meal' && act.slot && act.item && !act.item.includes('彈性用餐')) {
      templateMeals[act.slot] = act.item;
    } else {
      otherActivities.push(act);
    }
  });

  // Build all 5 meal slots
  const mealSlots = ['上午', '中午', '下午', '傍晚', '晚上'];
  const mealActivities = mealSlots.map(slot => {
    const item = templateMeals[slot];
    if (item) {
      return { type: 'meal', slot, note: `${item}（模板推薦）` };
    }
    return null;
  }).filter(Boolean);

  return {
    ...day,
    activities: [...otherActivities, ...mealActivities],
  };
}

// ----- Render -----
function renderItinerary(days, totalDays) {
  const container = document.getElementById('itinerary-content');
  container.innerHTML = days.map((day, i) => {
    const typeLabel = { arrival: '🚅 抵達日', departure: '🚄 離開日' }[day.type] || `📅 Day ${day.day}`;
    const zoneTags = (day.zones || []).map(z => `<span class="zone-tag">${z}</span>`).join('');

    return `
      <div class="itinerary-day">
        <div class="day-header">
          <h3>${typeLabel} ${day.name ? `— ${day.name}` : ''}</h3>
          ${zoneTags ? `<div class="day-zones">${zoneTags}</div>` : ''}
        </div>
        <div class="day-activities">
          ${day.activities.map(act => renderActivity(act)).join('')}
        </div>
      </div>
    `;
  }).join('');
}

function renderActivity(act) {
  if (act._skipped) return '';
  if (act.type === 'transport_anchor') {
    return `<div class="activity activity-transport-anchor">
      <div class="act-icon">🚉</div>
      <div class="act-content">
        <div class="act-title">${act.note}</div>
      </div>
    </div>`;
  }
  if (act.type === 'meal') {
    const linksHtml = (act.details?.google_maps || act.details?.youtube || act.details?.blog_article)
      ? `<div class="act-links">
          ${act.details.google_maps ? `<a href="${act.details.google_maps}" target="_blank" rel="noopener" class="act-link-btn">📍 Maps</a>` : ''}
          ${act.details.youtube    ? `<a href="${act.details.youtube}" target="_blank" rel="noopener" class="act-link-btn">🎬 YouTube</a>` : ''}
          ${act.details.blog_article ? `<a href="${act.details.blog_article}" target="_blank" rel="noopener" class="act-link-btn">📖 部落格</a>` : ''}
         </div>` : '';
    return `<div class="activity activity-meal">
      <div class="act-icon">🍽️</div>
      <div class="act-content">
        <div class="act-title">${act.note}</div>
        ${linksHtml}
      </div>
    </div>`;
  }
  if (act.type === 'transport') {
    return `<div class="activity activity-transport">
      <div class="act-icon">🚇</div>
      <div class="act-content">
        <div class="act-title">${act.item}</div>
        ${act.note ? `<div class="act-note">${act.note}</div>` : ''}
      </div>
    </div>`;
  }
  if (act.type === 'shopping' || act.type === 'general') {
    return `<div class="activity activity-shopping">
      <div class="act-icon">🛍️</div>
      <div class="act-content">
        <div class="act-title">${act.item}</div>
        ${act.note ? `<div class="act-note">${act.note}</div>` : ''}
      </div>
    </div>`;
  }

  // Attraction
  // Attraction / outlet (food/shrine/hotel don't use the 📍 icon path)
  const icon = act.type === 'outlet' ? '🛍️' : (act.type === 'food' ? '🍽️' : (act.type === 'shrine' ? '⛩️' : '📍'));
  const ticketInfo = act.ticket ? `<div class="act-ticket">🎟️ ${act.ticket}</div>` : '';
  const descInfo   = act.description ? `<div class="act-desc">${act.description.slice(0, 100)}${act.description.length > 100 ? '…' : ''}</div>` : '';
  const details    = act.details || {};

  // Phase 3: 來源標註（SPEC 9.9）
  const sourceUrls = act.sources || [];
  const sourceLabel = sourceUrls.length
    ? `<div class="act-sources">
        <span class="source-label">📎 來源：</span>
        ${sourceUrls.map(url => `<a href="${url}" target="_blank" rel="noopener" class="source-link">${new URL(url).hostname.replace('www.','')}</a>`).join(' · ')}
       </div>`
    : '';

  // Phase 3: 三種連結（Google Maps / YouTube / 部落格）
  const linksHtml = (details.google_maps || details.youtube || details.blog_article)
    ? `<div class="act-links">
        ${details.google_maps ? `<a href="${details.google_maps}" target="_blank" rel="noopener" class="act-link-btn">📍 Maps</a>` : ''}
        ${details.youtube    ? `<a href="${details.youtube}" target="_blank" rel="noopener" class="act-link-btn">🎬 YouTube</a>` : ''}
        ${details.blog_article ? `<a href="${details.blog_article}" target="_blank" rel="noopener" class="act-link-btn">📖 部落格</a>` : ''}
       </div>`
    : '';

  return `<div class="activity activity-attraction">
    <div class="act-icon">${icon}</div>
    <div class="act-content">
      <div class="act-title">${act.item}</div>
      ${act.duration ? `<div class="act-duration">⏱️ ${act.duration}</div>` : ''}
      ${ticketInfo}
      ${descInfo}
      ${linksHtml}
      ${sourceLabel}
    </div>
  </div>`;
}

// ----- Transport -----
function renderTransportInfo(trans) {
  const panel  = document.getElementById('transport-panel');
  const content = document.getElementById('transport-content');
  if (!trans || !Object.keys(trans).length) {
    panel.classList.add('hidden');
    return;
  }

  const card = trans;
  let html = `<div class="transport-item"><strong>🏙️ 城市類型：</strong>${
    card.city_type === 'metropolitan' ? '都會型（建議大眾交通）' : '郊區型（建議自駕）'
  }</div>`;

  if (card.airport_to_city) {
    const a = card.airport_to_city;
    html += `<div class="transport-item"><strong>✈️ 機場進入市區：</strong><p>${a.method}</p><p>${a.route}</p><p>時間：${a.estimated_time}｜費用：${a.estimated_cost}</p></div>`;
  }
  if (card.within_city) {
    const w = card.within_city;
    html += `<div class="transport-item"><strong>🚇 市區交通：</strong><p>${w.main_transport}</p><p><strong>建議票卡：</strong>${w.suggested_card}</p>`;
    if (w.ticket_options) {
      html += '<p><strong>優惠票券：</strong></p><ul>';
      w.ticket_options.forEach(t => { html += `<li>${t.name}（${t.price}）— ${t.desc}</li>`; });
      html += '</ul>';
    }
    html += '</div>';
  }
  if (card.driving_assessment) {
    const d = card.driving_assessment;
    html += `<div class="transport-item"><strong>🚗 自駕評估：</strong><p>${d.recommendation}</p>`;
    if (d.rental_tips) html += `<p>${d.rental_tips}</p>`;
    if (d.license_note) html += `<p>⚠️${d.license_note}</p>`;
    html += '</div>';
  }
  if (card.cash_prep) {
    const c = card.cash_prep;
    html += `<div class="transport-item"><strong>💴 現金準備：</strong><p>${c.recommendation}</p><p>${c.breakdown}</p><p>${c.note}</p></div>`;
  }
  if (card.transfer_tips?.length) {
    html += `<div class="transport-item"><strong>🔄 換乘注意：</strong><ul>`;
    card.transfer_tips.forEach(t => { html += `<li>${t.from} → ${t.to}：${t.note}</li>`; });
    html += '</ul></div>';
  }

  content.innerHTML = html;
  panel.classList.remove('hidden');
}

// ----- Helpers -----
function findItemByName(name) {
  return state.attractions.find(a =>
    a.name === name ||
    a.name_en === name ||
    a.name.includes(name) ||
    (a.name_en && a.name_en.toLowerCase().includes(name.toLowerCase()))
  ) || state.outlets.find(a =>
    a.name === name ||
    a.name_en === name ||
    a.name.includes(name) ||
    (a.name_en && a.name_en.toLowerCase().includes(name.toLowerCase()))
  ) || null;
}

function findOutletByName(name) {
  return state.outlets.find(a =>
    a.name === name ||
    a.name_en === name ||
    a.name.includes(name) ||
    (a.name_en && a.name_en.toLowerCase().includes(name.toLowerCase()))
  ) || null;
}

function findStationByName(name) {
  return state.stations.find(s =>
    s.name === name ||
    s.name_en === name ||
    s.name.includes(name) ||
    name.includes(s.name) ||
    (s.name_en && (s.name_en.toLowerCase() === name.toLowerCase() || s.name_en.toLowerCase().includes(name.toLowerCase()))) ||
    (name_en => s.name_en && name.toLowerCase().includes(s.name_en.toLowerCase()))(s.name_en)
  ) || null;
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function updateHighlight(dropdown, items, idx) {
  items.forEach((el, i) => el.classList.toggle('selected', i === idx));
  if (idx >= 0 && items[idx]) {
    items[idx].scrollIntoView({ block: 'nearest' });
  }
}

function closeDropdown(dropdown) {
  dropdown?.classList.add('hidden');
}

function closeAllDropdowns() {
  document.querySelectorAll('.autocomplete-dropdown').forEach(d => d.classList.add('hidden'));
}

// ----- Alerts -----
function renderAlerts(alerts) {
  const container = document.getElementById('alerts-container');
  alerts.forEach(a => {
    const div = document.createElement('div');
    div.className = `alert alert-${a.type}`;
    div.textContent = a.msg;
    container.appendChild(div);
    setTimeout(() => div.remove(), 5000);
  });
}

function clearAlerts() {
  const c = document.getElementById('alerts-container');
  if (c) c.innerHTML = '';
}
