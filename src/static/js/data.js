/* ════════════════════════════════════════════════════════════
   SANGHELIOS · data.js
   Capa de datos. Hoy genera un dataset sintético de 180 días
   siguiendo el esquema del plan (donaciones, hospitalizados,
   muertes_sangre, medias móviles 7d, presión, umbral τ).

   PUNTO DE INTEGRACIÓN (el más importante):
   - Reemplazar la generación sintética por fetch() al backend:
       GET /api/serie-diaria   → llena `data`
       GET /api/stock          → llena `STOCK`
       GET /api/campanas       → llena `campaigns`
   - Mantener los nombres exportados (data, TAU, presionHoy, …)
     y el resto de la app funciona sin cambios.
   ════════════════════════════════════════════════════════════ */

const N_DAYS = 180;
const today = new Date();

/* La sangre donada caduca: cada donación se descarta a los 40 días. */
const VIDA_UTIL_DIAS = 40;

/* Perfil por grupo sanguíneo: [tipo, proporción de donantes (EDA), demanda clínica diaria]. */
const PERFIL_RH = [
  ['O+', 0.537, 26.0], ['A+', 0.255, 11.0], ['O−', 0.090, 3.1], ['B+', 0.064, 3.6],
  ['A−', 0.028, 1.4], ['AB+', 0.016, 0.8], ['B−', 0.008, 0.5], ['AB−', 0.002, 0.25],
];

/* Serie diaria — una fila por día */
let data = { fecha: [], don: [], hosp: [], muertes: [], donM7: [], demM7: [], presion: [], prob: [] };
let TAU = 0, presionHoy = 0, donHoy = 0, demHoy = 0, enRiesgo = false;
let MODEL_THR = 0, probHoy = 0;   // señal del modelo XGBoost (escasez a 14 días)
let STOCK = [];
let stockTotal = 0, consumoDia = 0, autonomia = 0;
let campaigns = [];

function generateCoreData(params) {
  const bDon   = params?.baseDon   ?? 42;
  const bHosp  = params?.baseHosp  ?? 112;
  const bMuerte = params?.baseMuertes ?? 3;
  const stk    = params?.stockLevels ?? [
    { tipo: 'O+',  uds: 182, demandaDia: 26.0 },
    { tipo: 'A+',  uds: 84,  demandaDia: 11.0 },
    { tipo: 'B+',  uds: 31,  demandaDia: 3.6  },
    { tipo: 'O−',  uds: 9,   demandaDia: 3.1  },
    { tipo: 'A−',  uds: 8,   demandaDia: 1.4  },
    { tipo: 'AB+', uds: 7,   demandaDia: 0.8  },
    { tipo: 'B−',  uds: 4,   demandaDia: 0.5  },
    { tipo: 'AB−', uds: 2,   demandaDia: 0.25 }
  ];

  data = { fecha: [], don: [], hosp: [], muertes: [], donM7: [], demM7: [], presion: [] };

  for (let i = N_DAYS - 1; i >= 0; i--) {
    const d = new Date(today); d.setDate(d.getDate() - i);
    const dow = d.getDay();
    const t = N_DAYS - 1 - i;
    const wk = (dow === 0 || dow === 6) ? 0.55 : 1;
    const season = 6 * Math.sin(2 * Math.PI * t / 90);
    const decline = t > 140 ? -(t - 140) * 0.18 : 0;
    const don = Math.max(8, Math.round((bDon + season + decline) * wk + (rng() - 0.5) * 12));
    const surge = t > 145 ? (t - 145) * 0.65 : 0;
    const hosp = Math.max(60, Math.round(bHosp + 8 * Math.sin(2 * Math.PI * t / 60) + surge + (rng() - 0.5) * 16));
    const mue = Math.max(0, Math.round(bMuerte + (t > 150 ? 1.5 : 0) + (rng() - 0.5) * 3));
    data.fecha.push(d); data.don.push(don); data.hosp.push(hosp); data.muertes.push(mue);
  }

  for (let t = 0; t < N_DAYS; t++) {
    if (t < 6) { data.donM7.push(null); data.demM7.push(null); data.presion.push(null); continue; }
    let so = 0, sd = 0;
    for (let k = 0; k < 7; k++) { so += data.don[t-k]; sd += data.hosp[t-k] + data.muertes[t-k]; }
    const o = so / 7, dm = sd / 7;
    data.donM7.push(+o.toFixed(1)); data.demM7.push(+dm.toFixed(1)); data.presion.push(+(dm - o).toFixed(1));
  }

  const presValid = data.presion.filter(v => v !== null).slice().sort((a, b) => a - b);
  TAU = +presValid[Math.floor(presValid.length * 0.75)].toFixed(1);
  presionHoy = data.presion[N_DAYS - 1];
  donHoy = data.donM7[N_DAYS - 1];
  demHoy = data.demM7[N_DAYS - 1];
  enRiesgo = presionHoy > TAU;

  STOCK = stk.slice();
  stockTotal = STOCK.reduce((s, r) => s + r.uds, 0);
  consumoDia = STOCK.reduce((s, r) => s + r.demandaDia, 0);
  autonomia = stockTotal / consumoDia;

  campaigns = params?.noCampaigns ? [] : [
    { id: 1, zonaKey: 'laureles',   tipo: 'O−',    meta: 120, captadas: 46,  dia: new Date(today.getTime() + 3*86400000), unidad: '#1' },
    { id: 2, zonaKey: 'candelaria', tipo: 'Todos', meta: 200, captadas: 131, dia: new Date(today.getTime() + 1*86400000), unidad: '#2' }
  ];
}

generateCoreData(null);

function regenerateForScenario(params) {
  campaigns.length = 0;
  generateCoreData(params);
}

/* Helpers de formato de fecha (es-CO) */
const fmtDate = d => d.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const fmtShort = d => d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });

/* ════════════════════════════════════════════════════════════
   INTEGRACIÓN CON EL BACKEND (BD del modelo)
   Sustituye el dataset sintético por la serie real servida en
   /api/serie-diaria, /api/stock y /api/campanas. Mantiene los
   mismos nombres globales (data, TAU, STOCK, …).
   ════════════════════════════════════════════════════════════ */

function recomputeTau(p) {
  const v = data.presion.filter(x => x != null).slice().sort((a, b) => a - b);
  if (!v.length) return TAU;
  return +v[Math.min(v.length - 1, Math.floor(v.length * p))].toFixed(1);
}

async function loadRealData() {
  const [serie, meta] = await Promise.all([
    fetch('/api/serie-diaria').then(r => r.json()),
    fetch('/api/meta').then(r => r.json()),
  ]);
  if (!Array.isArray(serie) || serie.length === 0) return false;

  const rows = serie.slice(-N_DAYS);
  data = { fecha: [], don: [], hosp: [], muertes: [], donM7: [], demM7: [], presion: [], prob: [] };
  for (const r of rows) {
    data.fecha.push(new Date(r.fecha + 'T00:00:00'));
    data.don.push(r.donaciones);
    data.hosp.push(r.hospitalizados);
    data.muertes.push(r.muertes_sangre);
    data.donM7.push(r.don_ma7);
    data.demM7.push(r.dem_ma7);
    data.presion.push(r.presion);
    data.prob.push(r.prob_escasez);
  }

  const last = rows[rows.length - 1];
  TAU = parseFloat(meta && meta.tau) || recomputeTau(0.75);
  MODEL_THR = parseFloat(meta && meta.threshold) || 0;
  probHoy = last.prob_escasez || 0;
  presionHoy = last.presion;
  donHoy = last.don_ma7;
  demHoy = last.dem_ma7;
  enRiesgo = last.escasez_pred === 1 || presionHoy > TAU;

  // Caducidad: cada donación se descarta a los VIDA_UTIL_DIAS días. El stock
  // vigente son las donaciones de esa ventana (las más viejas ya caducaron),
  // repartido por grupo sanguíneo (proporción de donantes del EDA) y con un
  // perfil de demanda clínica diaria por tipo.
  const stockVigente = data.don.slice(-VIDA_UTIL_DIAS).reduce((a, v) => a + (v || 0), 0);
  STOCK = PERFIL_RH.map(([tipo, share, demandaDia]) => ({
    tipo,
    uds: Math.round(stockVigente * share),
    demandaDia,
  }));
  stockTotal = STOCK.reduce((a, r) => a + r.uds, 0);
  consumoDia = STOCK.reduce((a, r) => a + r.demandaDia, 0) || 1;
  autonomia = stockTotal / consumoDia;

  try {
    const camps = await fetch('/api/campanas').then(r => r.json());
    const toKey = s => String(s || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');
    // El mapa muestra las campañas de los últimos 7 días (y las próximas).
    const lim = Date.now() - 7 * 86400000;
    campaigns = (Array.isArray(camps) ? camps : [])
      .filter(c => new Date(c.fecha + 'T00:00:00').getTime() >= lim)
      .map((c, i) => ({
        id: i + 1, zonaKey: toKey(c.comuna), tipo: c.tipo || 'Todos',
        meta: 150, captadas: 0, dia: new Date(c.fecha + 'T00:00:00'),
        unidad: '#' + (i + 1), titulo: c.titulo, estado: c.estado,
        flyer: c.flyer || '',
      }));
  } catch (_) { /* campañas opcionales */ }

  return true;
}

/* Carga los datos reales (BD del modelo) al iniciar: sin sintéticos y con τ fija
   del modelo (percentil 75). Se ejecuta tras cargar el DOM y todos los módulos,
   así `currentScenario` (scenario-manager.js) ya está definido cuando refresca. */
async function bootstrapDashboardData() {
  // Sólo actúa si el dashboard está en el DOM (data.js se carga en todas las vistas).
  if (!document.getElementById('kpi-stock')) return;
  const status = document.getElementById('cfg-status');
  if (status) status.textContent = 'Cargando…';
  try {
    const ok = await loadRealData();
    if (status) {
      status.textContent = ok
        ? 'Datos reales · BD del modelo · τ fija'
        : 'BD no disponible — ejecuta scripts/build_db_and_model.py';
    }
  } catch (e) {
    if (status) status.textContent = 'Error cargando la BD: ' + e.message;
  }
  if (typeof refreshDashboard === 'function') refreshDashboard();
  if (typeof initCharts === 'function' &&
      ((typeof chartOD !== 'undefined' && chartOD) ||
       (typeof chartPresion !== 'undefined' && chartPresion))) {
    initCharts();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrapDashboardData);
} else {
  bootstrapDashboardData();
}
