/* ════════════════════════════════════════════════════════════
   SANGHELIOS · dashboard.js
   Vista Dashboard: KPIs, alerta, campañas en curso, tabla de
   stock y gráficas Chart.js (oferta/demanda, presión vs τ y la
   señal del modelo XGBoost).

   Depende de: data.js (data, TAU, MODEL_THR, probHoy, STOCK, …)
   Expone: initCharts() — llamada por app.js (lazy)
   ════════════════════════════════════════════════════════════ */

/* Identidad de series (par de alta separación de luminosidad):
   demanda = rojo marca, oferta = grafito. Estados solo en semáforos,
   siempre acompañados de etiqueta de texto. */
const C_DEMANDA = '#BF1212';
const C_OFERTA = '#1F2937';
const C_TAU = '#9CA3AF';
const C_MODELO = '#7A0C0C';
const C_UMBRAL_MODELO = '#B45309';
const C_GRID = '#F1F2F4';

let chartOD = null, chartPresion = null, chartModelo = null;

function _set(id, txt) { const el = document.getElementById(id); if (el) el.textContent = txt; }
function _badge(id, cls, txt) {
  const el = document.getElementById(id);
  if (el) { el.className = 'kpi-badge ' + cls; el.textContent = txt; }
}
function _delta(actual, previo) {
  if (!previo) return null;
  return (actual - previo) / previo * 100;
}

/* ── Refrescar KPIs, campañas y tabla (carga y cambio de escenario) ── */
function refreshDashboard() {
  const scenarioLabel = currentScenario && currentScenario.id !== 'normal'
    ? ' · ' + currentScenario.name
    : ' · banco de sangre + mortalidad regional';
  _set('today-label',
    'Corte operativo · ' + fmtDate(today).replace(/^\w/, c => c.toUpperCase()) + scenarioLabel);

  const dashTitle = document.querySelector('.dash-title');
  if (dashTitle) {
    dashTitle.textContent = currentScenario && currentScenario.id !== 'normal'
      ? 'Banco de Sangre — ' + currentScenario.centerName
      : 'Banco de Sangre — Hospital General de Medellín';
  }

  const n = data.fecha.length;

  /* KPI 1-2: stock y autonomía */
  _set('kpi-stock', stockTotal.toLocaleString('es-CO'));
  _set('kpi-autonomia', autonomia.toFixed(1) + 'd');
  if (autonomia < 5)      _badge('kpi-autonomia-badge', 'b-red', '⚠ Bajo el mínimo (5d)');
  else if (autonomia < 8) _badge('kpi-autonomia-badge', 'b-amber', 'Zona de vigilancia');
  else                    _badge('kpi-autonomia-badge', 'b-green', 'Nivel saludable');

  /* KPI 3-4: oferta y demanda con delta semanal */
  _set('kpi-oferta', donHoy.toFixed(1));
  const dOf = _delta(donHoy, data.donM7[n - 8]);
  if (dOf === null) _badge('kpi-oferta-badge', 'b-gray', 'sin semana previa');
  else _badge('kpi-oferta-badge', dOf < 0 ? 'b-red' : 'b-green',
    (dOf >= 0 ? '↑ +' : '↓ ') + dOf.toFixed(1) + '% vs semana ant.');

  _set('kpi-demanda', demHoy.toFixed(1));
  const dDe = _delta(demHoy, data.demM7[n - 8]);
  if (dDe === null) _badge('kpi-demanda-badge', 'b-gray', 'sin semana previa');
  else _badge('kpi-demanda-badge', dDe > 0 ? 'b-red' : 'b-green',
    (dDe >= 0 ? '↑ +' : '↓ ') + dDe.toFixed(1) + '% vs semana ant.');

  /* KPI 5: presión vs τ */
  _set('kpi-presion', presionHoy.toFixed(1));
  _set('kpi-presion-sub', 'presiónₜ = D̄ₜ − Ōₜ · τ = ' + TAU.toFixed(1));
  const gap = presionHoy - TAU;
  if (gap > 0)       _badge('kpi-presion-badge', 'b-red', '⚠ ' + gap.toFixed(1) + ' sobre el umbral');
  else if (gap > -5) _badge('kpi-presion-badge', 'b-amber', 'A ' + Math.abs(gap).toFixed(1) + ' del umbral');
  else               _badge('kpi-presion-badge', 'b-green', Math.abs(gap).toFixed(1) + ' bajo el umbral');

  /* KPI 6: señal del modelo (probabilidad de escasez a 14 días) */
  const sobreModelo = MODEL_THR > 0 && probHoy >= MODEL_THR;
  _set('kpi-riesgo', (probHoy * 100).toFixed(2) + '%');
  _set('kpi-riesgo-sub', 'P(escasez t+14) · corte del modelo: ' + (MODEL_THR * 100).toFixed(2) + '%');
  _badge('kpi-riesgo-badge', (sobreModelo || enRiesgo) ? 'b-red' : 'b-green',
    (sobreModelo || enRiesgo) ? '⚠ Escasez proyectada' : 'Sin alerta del modelo');

  /* Banner de alerta */
  const banner = document.getElementById('alert-banner');
  if (banner) {
    if (enRiesgo || sobreModelo) {
      banner.style.display = 'flex';
      _set('alert-title', 'Alerta — escasez proyectada para el ' +
        fmtShort(new Date(today.getTime() + 14 * 86400000)));
      _set('alert-desc', 'La señal del banco supera el punto de operación. Protocolo: lanzar campaña hoy ' +
        '(+7d convocatoria, +7d procesamiento).');
    } else {
      banner.style.display = 'none';
    }
  }

  /* Campañas en curso */
  renderDashCamps();

  /* Tabla de stock (semáforo con etiqueta de texto, nunca solo color) */
  const tbody = document.getElementById('stock-tbody');
  if (tbody) {
    tbody.innerHTML = '';
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
  }

  if (chartOD || chartPresion || chartModelo) initCharts();
}

/* Lista de campañas en curso (mismas del mapa: últimos 7 días y próximas) */
function renderDashCamps() {
  const box = document.getElementById('dash-camps');
  if (!box) return;
  if (!campaigns.length) {
    box.innerHTML = '<span class="dc-empty">Sin campañas recientes — crea una desde el estudio.</span>';
    return;
  }
  box.innerHTML = campaigns.slice(0, 5).map(c => {
    const z = (typeof ZONAS !== 'undefined' && ZONAS[c.zonaKey]) || null;
    const nombre = z ? z.nombre : c.zonaKey;
    const est = String(c.estado || 'desplegada').toLowerCase();
    const f = c.dia.toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
    return `<div class="dc-row">
      <span class="dc-emoji">🩸</span>
      <div class="dc-main">
        <div class="dc-title">${c.titulo || ('Campaña ' + c.tipo)}</div>
        <div class="dc-sub">📍 ${nombre} · 📅 ${f} · grupo ${c.tipo}</div>
      </div>
      <span class="dc-estado ${est}">${est}</span>
    </div>`;
  }).join('');
}

/* ── Gráficas (lazy) ── */
function initCharts() {
  if (chartOD) { chartOD.destroy(); chartOD = null; }
  if (chartPresion) { chartPresion.destroy(); chartPresion = null; }
  if (chartModelo) { chartModelo.destroy(); chartModelo = null; }

  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 13;
  Chart.defaults.color = '#9CA3AF';

  const n = data.fecha.length;
  const span = Math.min(90, n);
  const lastN = a => a.slice(n - span);
  const labels = lastN(data.fecha).map(fmtShort);
  const ejes = {
    x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
    y: { grid: { color: C_GRID }, border: { display: false } },
  };
  const interaccion = { mode: 'index', intersect: false };
  const leyenda = {
    position: 'top', align: 'end',
    labels: { boxWidth: 11, boxHeight: 11, usePointStyle: true, pointStyle: 'circle', font: { size: 12.5 } },
  };
  const linea = { tension: 0.35, pointRadius: 0, pointHoverRadius: 5, borderWidth: 2 };

  /* A · Oferta vs Demanda — 2 series, leyenda presente */
  const elOD = document.getElementById('chart-od');
  if (elOD) {
    chartOD = new Chart(elOD, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Demanda (D̄ₜ)', data: lastN(data.demM7),
            borderColor: C_DEMANDA, backgroundColor: 'rgba(191,18,18,0.06)', fill: true, ...linea },
          { label: 'Oferta ×3 (equiv. componentes)',
            data: lastN(data.donM7).map(v => v == null ? null : +(v * 3).toFixed(1)),
            borderColor: C_OFERTA, ...linea },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false, interaction: interaccion,
        plugins: { legend: leyenda }, scales: ejes },
    });
  }

  /* B · Presión vs τ — la zona sobre el umbral se rellena en rojo */
  const elP = document.getElementById('chart-presion');
  if (elP) {
    chartPresion = new Chart(elP, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'presiónₜ', data: lastN(data.presion),
            borderColor: C_DEMANDA, ...linea,
            fill: { target: { value: TAU }, above: 'rgba(191,18,18,0.16)', below: 'transparent' } },
          { label: 'Umbral τ (' + TAU.toFixed(1) + ')', data: labels.map(() => TAU),
            borderColor: C_TAU, borderDash: [6, 5], borderWidth: 1.5, pointRadius: 0 },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false, interaction: interaccion,
        plugins: { legend: leyenda }, scales: ejes },
    });
  }

  /* C · Señal del modelo — probabilidad diaria de escasez a 14 días */
  const elM = document.getElementById('chart-modelo');
  if (elM && data.prob && data.prob.some(v => v != null)) {
    const probPct = lastN(data.prob).map(v => v == null ? null : +(v * 100).toFixed(3));
    const ds = [{ label: 'P(escasez t+14)', data: probPct,
      borderColor: C_MODELO, backgroundColor: 'rgba(122,12,12,0.09)', fill: true, ...linea }];
    if (MODEL_THR > 0) {
      ds.push({ label: 'Corte del modelo', data: labels.map(() => +(MODEL_THR * 100).toFixed(3)),
        borderColor: C_UMBRAL_MODELO, borderDash: [6, 5], borderWidth: 1.5, pointRadius: 0 });
    }
    chartModelo = new Chart(elM, {
      type: 'line',
      data: { labels, datasets: ds },
      options: {
        responsive: true, maintainAspectRatio: false, interaction: interaccion,
        plugins: {
          legend: MODEL_THR > 0 ? leyenda : { display: false },
          tooltip: { callbacks: { label: c => c.dataset.label + ': ' + c.parsed.y + '%' } },
        },
        scales: { ...ejes, y: { ...ejes.y, ticks: { callback: v => v + '%' } } },
      },
    });
  }
}
