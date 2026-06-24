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

/* Serie diaria — una fila por día (ver plan_dataset.pdf) */
const data = { fecha: [], don: [], hosp: [], muertes: [], donM7: [], demM7: [], presion: [] };

for (let i = N_DAYS - 1; i >= 0; i--) {
  const d = new Date(today); d.setDate(d.getDate() - i);
  const dow = d.getDay();
  const t = N_DAYS - 1 - i;
  // Donaciones: caen los fines de semana; declive reciente (simula crisis)
  const wk = (dow === 0 || dow === 6) ? 0.55 : 1;
  const season = 6 * Math.sin(2 * Math.PI * t / 90);
  const decline = t > 140 ? -(t - 140) * 0.18 : 0;
  const don = Math.max(8, Math.round((42 + season + decline) * wk + (rng() - 0.5) * 12));
  // Hospitalizados: pico reciente (simula temporada de accidentalidad)
  const surge = t > 145 ? (t - 145) * 0.65 : 0;
  const hosp = Math.max(60, Math.round(112 + 8 * Math.sin(2 * Math.PI * t / 60) + surge + (rng() - 0.5) * 16));
  const mue = Math.max(0, Math.round(3 + (t > 150 ? 1.5 : 0) + (rng() - 0.5) * 3));
  data.fecha.push(d); data.don.push(don); data.hosp.push(hosp); data.muertes.push(mue);
}

/* Medias móviles 7d:  Ōₜ (oferta) y D̄ₜ (demanda = hosp + muertes); presión = D̄ₜ − Ōₜ */
for (let t = 0; t < N_DAYS; t++) {
  if (t < 6) { data.donM7.push(null); data.demM7.push(null); data.presion.push(null); continue; }
  let so = 0, sd = 0;
  for (let k = 0; k < 7; k++) { so += data.don[t-k]; sd += data.hosp[t-k] + data.muertes[t-k]; }
  const o = so / 7, dm = sd / 7;
  data.donM7.push(+o.toFixed(1)); data.demM7.push(+dm.toFixed(1)); data.presion.push(+(dm - o).toFixed(1));
}

/* Umbral crítico τ = percentil 75 de la presión histórica */
const presValid = data.presion.filter(v => v !== null).slice().sort((a, b) => a - b);
const TAU = +presValid[Math.floor(presValid.length * 0.75)].toFixed(1);
const presionHoy = data.presion[N_DAYS - 1];
const donHoy = data.donM7[N_DAYS - 1];
const demHoy = data.demM7[N_DAYS - 1];
const enRiesgo = presionHoy > TAU;

/* Stock por tipo de sangre (distribución poblacional Colombia aprox.) */
const STOCK = [
  { tipo: 'O+',  uds: 182, demandaDia: 26.0 },
  { tipo: 'A+',  uds: 84,  demandaDia: 11.0 },
  { tipo: 'B+',  uds: 31,  demandaDia: 3.6  },
  { tipo: 'O−',  uds: 9,   demandaDia: 3.1  },
  { tipo: 'A−',  uds: 8,   demandaDia: 1.4  },
  { tipo: 'AB+', uds: 7,   demandaDia: 0.8  },
  { tipo: 'B−',  uds: 4,   demandaDia: 0.5  },
  { tipo: 'AB−', uds: 2,   demandaDia: 0.25 }
];
const stockTotal = STOCK.reduce((s, r) => s + r.uds, 0);
const consumoDia = STOCK.reduce((s, r) => s + r.demandaDia, 0);
const autonomia = stockTotal / consumoDia;

/* Campañas desplegadas = zonas de recogida de sangre en el mapa.
   Arrancan 2 de ejemplo; deployCampaign() (campana.js) agrega más. */
const campaigns = [
  { id: 1, zonaKey: 'laureles',   tipo: 'O−',    meta: 120, captadas: 46,  dia: new Date(today.getTime() + 3*86400000), unidad: '#1' },
  { id: 2, zonaKey: 'candelaria', tipo: 'Todos', meta: 200, captadas: 131, dia: new Date(today.getTime() + 1*86400000), unidad: '#2' }
];

/* Helpers de formato de fecha (es-CO) */
const fmtDate = d => d.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const fmtShort = d => d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
