/* ════════════════════════════════════════════════════════════
   SANGHELIOS · dashboard.js
   Vista Dashboard: KPIs, banner de alerta, tabla de stock y
   gráficas Chart.js (se inicializan al abrir la pestaña).

   Depende de: data.js (data, TAU, presionHoy, STOCK, …)
   Expone: initCharts()  — llamada por app.js (lazy)
   ════════════════════════════════════════════════════════════ */

/* ── KPIs y alerta (se llenan al cargar la página) ── */
document.getElementById('today-label').textContent =
  'Corte operativo · ' + fmtDate(today).replace(/^\w/, c => c.toUpperCase()) + ' · banco de sangre + mortalidad regional';

document.getElementById('kpi-stock').textContent = stockTotal;
document.getElementById('kpi-autonomia').textContent = autonomia.toFixed(1) + 'd';
const autBadge = document.getElementById('kpi-autonomia-badge');
if (autonomia < 5) { autBadge.className = 'kpi-badge b-red'; autBadge.textContent = '⚠ Bajo el mínimo (5d)'; }
else if (autonomia < 8) { autBadge.className = 'kpi-badge b-amber'; autBadge.textContent = 'Zona de vigilancia'; }
else { autBadge.className = 'kpi-badge b-green'; autBadge.textContent = 'Nivel saludable'; }

document.getElementById('kpi-oferta').textContent = donHoy.toFixed(1);
const ofertaPrev = data.donM7[N_DAYS - 8];
const ofertaDelta = ((donHoy - ofertaPrev) / ofertaPrev * 100);
const ofBadge = document.getElementById('kpi-oferta-badge');
ofBadge.className = 'kpi-badge ' + (ofertaDelta < 0 ? 'b-red' : 'b-green');
ofBadge.textContent = (ofertaDelta >= 0 ? '↑ +' : '↓ ') + ofertaDelta.toFixed(1) + '% vs semana ant.';

document.getElementById('kpi-demanda').textContent = demHoy.toFixed(1);

document.getElementById('kpi-riesgo').textContent = enRiesgo ? 'ALTO' : 'MODERADO';
document.getElementById('kpi-riesgo-sub').textContent = 'presiónₜ = ' + presionHoy.toFixed(1) + ' · τ = ' + TAU.toFixed(1);
const rBadge = document.getElementById('kpi-riesgo-badge');
rBadge.className = 'kpi-badge ' + (enRiesgo ? 'b-red' : 'b-amber');
rBadge.textContent = enRiesgo ? '⚠ Escasez proyectada en 14d' : 'Presión cerca del umbral';

if (enRiesgo) {
  const banner = document.getElementById('alert-banner');
  banner.style.display = 'flex';
  document.getElementById('alert-title').textContent =
    'Alerta Roja — escasez proyectada para el ' + fmtShort(new Date(today.getTime() + 14 * 86400000));
  document.getElementById('alert-desc').textContent =
    'La presión (' + presionHoy.toFixed(1) + ') supera el umbral τ (' + TAU.toFixed(1) + ') de forma sostenida. Protocolo: lanzar campaña hoy (+7d convocatoria, +7d procesamiento).';
}

/* ── Tabla de stock por tipo con semáforo ── */
const tbody = document.getElementById('stock-tbody');
STOCK.forEach(r => {
  const cob = r.uds / r.demandaDia;
  let color, label;
  if (cob < 4)      { color = '#BF1212'; label = 'Crítico'; }
  else if (cob < 7) { color = '#D97706'; label = 'Vigilancia'; }
  else              { color = '#16A34A'; label = 'Estable'; }
  const pct = Math.min(100, cob / 12 * 100);
  tbody.insertAdjacentHTML('beforeend', `
    <tr>
      <td><span class="bt-tag">${r.tipo}</span></td>
      <td style="font-weight:700">${r.uds}</td>
      <td><div class="stock-bar-track"><div class="stock-bar-fill" style="width:${pct}%;background:${color}"></div></div></td>
      <td style="font-weight:600">${cob.toFixed(1)}d</td>
      <td><span class="sem"><span class="sem-dot" style="background:${color}"></span>${label}</span></td>
    </tr>`);
});

/* ── Gráficas (lazy: app.js llama initCharts() al abrir la pestaña,
      porque Chart.js no mide bien canvas en contenedores ocultos) ── */
function initCharts() {
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 13;
  Chart.defaults.color = '#9CA3AF';

  const last90 = a => a.slice(N_DAYS - 90);
  const labels90 = last90(data.fecha).map(fmtShort);
  const legendOpts = { position: 'top', align: 'end', labels: { boxWidth: 11, boxHeight: 11, usePointStyle: true, pointStyle: 'circle', font: { size: 12.5 } } };

  new Chart(document.getElementById('chart-od'), {
    type: 'line',
    data: {
      labels: labels90,
      datasets: [
        { label: 'Demanda (D̄ₜ)', data: last90(data.demM7),
          borderColor: '#BF1212', backgroundColor: 'rgba(191,18,18,0.07)',
          fill: true, tension: 0.35, pointRadius: 0, borderWidth: 2 },
        { label: 'Oferta ×3 (equiv. componentes)', data: last90(data.donM7).map(v => v === null ? null : +(v * 3).toFixed(1)),
          borderColor: '#1F2937', tension: 0.35, pointRadius: 0, borderWidth: 2 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: legendOpts },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
        y: { grid: { color: '#F1F2F4' }, border: { display: false } }
      }
    }
  });

  new Chart(document.getElementById('chart-presion'), {
    type: 'line',
    data: {
      labels: labels90,
      datasets: [
        { label: 'presiónₜ', data: last90(data.presion),
          borderColor: '#BF1212', borderWidth: 2, tension: 0.35, pointRadius: 0,
          fill: { target: { value: TAU } }, backgroundColor: 'rgba(191,18,18,0.12)' },
        { label: 'Umbral τ (p75)', data: labels90.map(() => TAU),
          borderColor: '#9CA3AF', borderDash: [6, 5], borderWidth: 1.5, pointRadius: 0 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: legendOpts },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
        y: { grid: { color: '#F1F2F4' }, border: { display: false } }
      }
    }
  });
}
