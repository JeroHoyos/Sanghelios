/* ════════════════════════════════════════════════════════════
   SANGHELIOS · mapa.js
   Mapas 3D con MapLibre GL + OpenFreeMap (tiles vectoriales,
   sin API key). Dos instancias:
     - previewMap: mini-mapa no interactivo del hero (Inicio)
     - map3d:      mapa completo de la pestaña Mapa 3D (lazy)
   Las campañas desplegadas son las zonas de recogida y se
   actualizan en vivo (ticker cada 3 s).

   Depende de: config.js (HGM, ZONAS, INGRESOS, MAP_STYLE_URL),
               data.js (campaigns)
   Expone: initMap3D(), resetMapView(), orbitMap(),
           renderCampaignMarkers(), updateCampList()

   PUNTO DE INTEGRACIÓN:
   - El ticker setInterval simula la recogida en vivo; reemplazar
     por WebSocket/polling al backend de campañas.
   ════════════════════════════════════════════════════════════ */

let map3d = null, styleReady = false;
let previewMap = null;
let campMarkers = [];

function popupHTML(t, s, n) {
  return '<div class="popup-t">' + t + '</div><div class="popup-s">' + s + '</div>' +
         (n ? '<div class="popup-n">' + n + '</div>' : '');
}

function campPopupHTML(c) {
  const z = ZONAS[c.zonaKey];
  const f = c.dia.toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short' });
  const pct = Math.min(100, Math.round(c.captadas / c.meta * 100));
  return popupHTML('🩸 Zona de recogida — ' + c.tipo, z.lugar + ' · ' + f + ' · unidad móvil ' + c.unidad,
    c.captadas + ' / ' + c.meta + ' uds recogidas (' + pct + '%)');
}

/* Pinta (o repinta) los marcadores de campañas activas en el mapa 3D */
function renderCampaignMarkers() {
  if (!map3d) return;
  campMarkers.forEach(m => m.remove());
  campMarkers = [];
  campaigns.forEach(c => {
    const z = ZONAS[c.zonaKey];
    const el = document.createElement('div');
    el.className = 'mk-camp';
    const m = new maplibregl.Marker({ element: el })
      .setLngLat([z.lng, z.lat])
      .setPopup(new maplibregl.Popup({ offset: 16 }).setHTML(campPopupHTML(c)))
      .addTo(map3d);
    m._campId = c.id;
    campMarkers.push(m);
  });
}

/* Lista "Recogida en vivo" del panel lateral */
function updateCampList() {
  const list = document.getElementById('camp-list');
  if (!list) return;
  list.innerHTML = campaigns.map(c => {
    const z = ZONAS[c.zonaKey];
    const pct = Math.min(100, Math.round(c.captadas / c.meta * 100));
    return '<div class="camp-item">' +
      '<div class="ci-top"><span class="ci-name">' + z.nombre + '</span><span class="ci-tipo">' + c.tipo + '</span></div>' +
      '<div class="ci-bar"><div class="ci-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="ci-meta"><span>' + c.captadas + ' / ' + c.meta + ' uds</span><span>' + pct + '%</span></div>' +
    '</div>';
  }).join('');
}
updateCampList();

/* Recogida en vivo: las campañas suman unidades cada pocos segundos.
   ⚠ Simulación — reemplazar por datos reales del backend. */
setInterval(() => {
  let changed = false;
  campaigns.forEach(c => {
    if (c.captadas < c.meta && rng() > 0.35) {
      c.captadas = Math.min(c.meta, c.captadas + Math.ceil(rng() * 3));
      changed = true;
    }
  });
  if (!changed) return;
  updateCampList();
  campMarkers.forEach(m => {
    const c = campaigns.find(x => x.id === m._campId);
    if (c && m.getPopup()) m.getPopup().setHTML(campPopupHTML(c));
  });
}, 3000);

/* Capa de edificios 3D (extrusión sobre la fuente vectorial del estilo) */
function add3DBuildings(map, layerId) {
  const style = map.getStyle();
  const srcId = Object.keys(style.sources).find(k => style.sources[k].type === 'vector');
  if (!srcId) return;
  map.addLayer({
    id: layerId,
    source: srcId,
    'source-layer': 'building',
    type: 'fill-extrusion',
    minzoom: 13,
    paint: {
      'fill-extrusion-color': '#d8dbe2',
      'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 12],
      'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
      'fill-extrusion-opacity': 0.78
    }
  });
}

/* ── Mini-mapa de preview en el hero (no interactivo; clic → pestaña Mapa 3D) ── */
(function initPreviewMap() {
  previewMap = new maplibregl.Map({
    container: 'map-preview',
    style: MAP_STYLE_URL,
    center: [HGM.lng, HGM.lat],
    zoom: 13.4, pitch: 55, bearing: -18,
    interactive: false, attributionControl: false
  });
  previewMap.on('load', () => add3DBuildings(previewMap, 'edificios-3d-preview'));

  const hgmEl = document.createElement('div');
  hgmEl.className = 'mk-hgm';
  hgmEl.style.width = '30px'; hgmEl.style.height = '30px';
  hgmEl.innerHTML = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none"><path d="M8 1.5C8 1.5 12.5 7 12.5 10A4.5 4.5 0 0 1 3.5 10C3.5 7 8 1.5 8 1.5Z" fill="white"/></svg>';
  new maplibregl.Marker({ element: hgmEl, anchor: 'bottom' }).setLngLat([HGM.lng, HGM.lat]).addTo(previewMap);

  campaigns.forEach(c => {
    const z = ZONAS[c.zonaKey];
    const el = document.createElement('div');
    el.className = 'mk-camp';
    el.style.width = '16px'; el.style.height = '16px';
    new maplibregl.Marker({ element: el }).setLngLat([z.lng, z.lat]).addTo(previewMap);
  });
  INGRESOS.forEach(p => {
    const el = document.createElement('div');
    el.className = 'mk-hosp';
    const s = 8 + p.v * 0.09;
    el.style.width = s + 'px'; el.style.height = s + 'px';
    new maplibregl.Marker({ element: el }).setLngLat([p.lng, p.lat]).addTo(previewMap);
  });
})();

/* ── Mapa 3D completo (lazy: app.js lo inicializa al abrir la pestaña) ── */
function initMap3D() {
  map3d = new maplibregl.Map({
    container: 'map3d',
    style: MAP_STYLE_URL,
    center: [HGM.lng, HGM.lat],
    zoom: 14.6, pitch: 58, bearing: -22,
    antialias: true
  });
  map3d.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');

  map3d.on('load', () => {
    styleReady = true;
    add3DBuildings(map3d, 'edificios-3d');
  });

  // Marcador del HGM
  const hgmEl = document.createElement('div');
  hgmEl.className = 'mk-hgm';
  hgmEl.innerHTML = '<svg width="17" height="17" viewBox="0 0 16 16" fill="none"><path d="M8 1.5C8 1.5 12.5 7 12.5 10A4.5 4.5 0 0 1 3.5 10C3.5 7 8 1.5 8 1.5Z" fill="white"/></svg>';
  new maplibregl.Marker({ element: hgmEl, anchor: 'bottom' })
    .setLngLat([HGM.lng, HGM.lat])
    .setPopup(new maplibregl.Popup({ offset: 20 }).setHTML(
      popupHTML('Hospital General de Medellín', 'Luz Castro de Gutiérrez · banco de sangre central', 'Nodo central de Sanghelios')))
    .addTo(map3d);

  // Campañas activas = zonas de recogida de sangre (se actualizan en vivo)
  renderCampaignMarkers();

  // Puntos de ingreso de hospitalizados (grafito, tamaño ∝ volumen)
  INGRESOS.forEach(p => {
    const el = document.createElement('div');
    el.className = 'mk-hosp';
    const s = 11 + p.v * 0.14;
    el.style.width = s + 'px'; el.style.height = s + 'px';
    new maplibregl.Marker({ element: el })
      .setLngLat([p.lng, p.lat])
      .setPopup(new maplibregl.Popup({ offset: 12 }).setHTML(
        popupHTML('🏥 ' + p.n, p.s, p.v + ' ingresos/semana')))
      .addTo(map3d);
  });
}

function resetMapView() {
  if (map3d) map3d.flyTo({ center: [HGM.lng, HGM.lat], zoom: 14.6, pitch: 58, bearing: -22, duration: 1600 });
}

function orbitMap() {
  if (!map3d) return;
  map3d.flyTo({ center: [HGM.lng, HGM.lat], zoom: 15.2, pitch: 65, duration: 1200 });
  let b = map3d.getBearing();
  const start = performance.now();
  function spin(now) {
    if (!document.getElementById('view-mapa').classList.contains('active')) return;
    const dt = now - start;
    if (dt > 14000) return;
    map3d.setBearing(b + dt * 0.012);
    requestAnimationFrame(spin);
  }
  setTimeout(() => requestAnimationFrame(spin), 1250);
}
