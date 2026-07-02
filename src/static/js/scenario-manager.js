/* ════════════════════════════════════════════════════════════
   SANGHELIOS · scenario-manager.js
   Gestor de escenarios: permite alternar entre el modo normal
   (Medellín) y escenarios de desastre (Venezuela terremoto, …).
   Cada escenario vive en su propio archivo en static/js/scenarios/.
   ════════════════════════════════════════════════════════════ */

let currentScenarioId = 'normal';
let currentScenario = null;

const SCENARIO_DEFAULTS = {
  hgm: { lng: HGM.lng, lat: HGM.lat },
  zonas: Object.assign({}, ZONAS),
  ingresos: INGRESOS.slice(),
  mapStyle: MAP_STYLE_URL,
};

const SCENARIO_REGISTRY = {};

function registerScenario(id, config) {
  SCENARIO_REGISTRY[id] = config;
}

registerScenario('normal', {
  id: 'normal',
  name: 'Medellín',
  description: 'Operación normal · Hospital General de Medellín',
  center: { lng: SCENARIO_DEFAULTS.hgm.lng, lat: SCENARIO_DEFAULTS.hgm.lat },
  centerName: 'Hospital General de Medellín',
  centerAddr: 'Cra. 48 #32-102 · banco de sangre central',
  zones: SCENARIO_DEFAULTS.zonas,
  ingresos: SCENARIO_DEFAULTS.ingresos,
  mapStyle: SCENARIO_DEFAULTS.mapStyle,
  overlayTitle: 'Medellín en tiempo real',
  overlaySubtitle: 'Hospital General de Medellín · Cra. 48 #32-102',
  overlayInfo: 'Las zonas de recogida se actualizan en tiempo real con cada campaña desplegada. Ctrl + arrastrar rota la vista 3D.',
  legendItems: [
    { color: 'var(--red)', shape: 'teardrop', pulse: true, label: 'HGM · banco de sangre central' },
    { color: 'var(--red)', shape: 'circle', pulse: true, label: 'Campañas activas · zonas de recogida' },
    { color: 'var(--graphite)', shape: 'circle', pulse: false, label: 'Ingresos hospitalizados · demanda' },
  ],
  dataParams: null,
});

if (typeof SCENARIOS !== 'undefined') {
  Object.entries(SCENARIOS).forEach(([id, config]) => registerScenario(id, config));
}

function applyScenarioGlobals(config) {
  HGM.lng = config.center.lng;
  HGM.lat = config.center.lat;
  MAP_STYLE_URL = config.mapStyle || SCENARIO_DEFAULTS.mapStyle;

  Object.keys(ZONAS).forEach(k => delete ZONAS[k]);
  Object.entries(config.zones).forEach(([k, v]) => { ZONAS[k] = v; });

  INGRESOS.length = 0;
  config.ingresos.forEach(v => INGRESOS.push(v));
}

function updateOverlay(config) {
  const nameEl = document.querySelector('.map-overlay-name');
  const addrEl = document.querySelector('.map-overlay-addr');
  const footEl = document.querySelector('.map-overlay-foot');
  const legendEl = document.querySelector('.map-legend');
  const campLabelEl = document.querySelector('.camp-list-label');

  if (nameEl) nameEl.textContent = config.overlayTitle;
  if (addrEl) addrEl.textContent = config.overlaySubtitle;
  if (footEl) footEl.textContent = config.overlayInfo || '';

  if (legendEl && config.legendItems) {
    legendEl.innerHTML = config.legendItems.map(item => {
      const parts = item.label.split('·').map(s => s.trim());
      const bold = parts[0];
      const rest = parts.slice(1).join(' · ').trim();
      return '<div class="mli">' +
        '<span class="mli-dot' + (item.pulse ? ' mli-pulse' : '') + '" style="background:' + item.color + ';' + (item.shape === 'teardrop' ? ' border-radius:50% 50% 50% 20%' : '') + '"></span>' +
        '<b>' + bold + '</b>' + (rest ? '&nbsp;· ' + rest : '') +
      '</div>';
    }).join('');
  }

  if (campLabelEl) {
    campLabelEl.style.display = config.id === 'normal' ? 'flex' : 'none';
    campLabelEl.textContent = config.id === 'normal'
      ? 'Recogida en vivo <span class="live-dot"></span>'
      : 'Respuesta a emergencia <span class="live-dot"></span>';
  }
}

function updateScenarioToggle(id) {
  document.querySelectorAll('.scenario-opt').forEach(el => {
    el.classList.toggle('active', el.dataset.scenario === id);
  });
}

function switchScenario(id) {
  if (id === currentScenarioId) return;
  const config = SCENARIO_REGISTRY[id];
  if (!config) return;

  currentScenarioId = id;
  currentScenario = config;

  applyScenarioGlobals(config);
  updateOverlay(config);

  clearMap3DMarkers();
  if (map3d) {
    renderMap3DScenario();
    setTimeout(() => flyToScenarioCenter(), 100);
  }

  clearPreviewMapMarkers();
  if (previewMap) {
    renderPreviewMapScenario();
    previewMap.setCenter([config.center.lng, config.center.lat]);
  }

  if (typeof regenerateForScenario === 'function') {
    regenerateForScenario(config.dataParams);
  }

  if (typeof refreshDashboard === 'function') refreshDashboard();

  updateScenarioToggle(id);

  const statusEl = document.querySelector('.nav-status');
  if (statusEl) {
    statusEl.innerHTML = `<span class="nav-status-dot"></span>${config.name}`;
  }

  const centerBtn = document.querySelector('[onclick="resetMapView()"]');
  if (centerBtn && config.id !== 'normal') {
    centerBtn.setAttribute('onclick', 'flyToScenarioCenter()');
  } else if (centerBtn) {
    centerBtn.setAttribute('onclick', 'resetMapView()');
  }
}

function flyToScenarioCenter() {
  if (!map3d || !currentScenario) return;
  map3d.flyTo({ center: [currentScenario.center.lng, currentScenario.center.lat], zoom: 13, pitch: 58, bearing: 0, duration: 1600 });
}

function getCurrentScenario() {
  return currentScenario || SCENARIO_REGISTRY.normal;
}

function getScenario(id) {
  return SCENARIO_REGISTRY[id] || SCENARIO_REGISTRY.normal;
}
