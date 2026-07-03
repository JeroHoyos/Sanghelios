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

/* ══ Ventana didáctica de indicadores ══ */
const INFO_KPI = {
  stock: {
    emoji: '🩸', titulo: 'Stock vigente',
    que: 'Las bolsas de sangre que el banco tiene listas para usar hoy.',
    como: 'Se suman las donaciones de los últimos 40 días y se reparten entre los 8 grupos ABO/Rh según la proporción de donantes de cada uno.',
    porque: 'La sangre caduca a los 40 días: una unidad vieja se descarta aunque nunca se haya usado. Contar solo lo vigente evita creer que hay más reserva de la real.',
    analogia: 'Como la leche en la nevera: no importa cuánta compraste en el año, importa cuánta no se ha vencido.',
  },
  autonomia: {
    emoji: '⏳', titulo: 'Autonomía',
    que: 'Cuántos días aguanta el banco si no entra ni una donación más.',
    como: 'Stock vigente ÷ consumo diario estimado. Bajo 8 días se enciende la vigilancia; bajo 5, la alarma.',
    porque: 'Es el tiempo de reacción real: montar una campaña toma ~14 días entre convocatoria y procesamiento.',
    analogia: 'Es el tanque de gasolina del banco: no esperas a la reserva para buscar estación.',
  },
  presion: {
    emoji: '⚖️', titulo: 'Presión del sistema',
    que: 'El desbalance entre la sangre que se necesita y la que entra.',
    como: 'Demanda (hospitalizados + muertes asociadas a sangre) menos oferta (donaciones), ambas en media móvil de 7 días. El umbral τ es el percentil 75 histórico.',
    porque: 'Si la presión sostiene el umbral τ, el sistema proyecta escasez en 14 días: es la señal que dispara las campañas.',
    analogia: 'Una balanza: cuando el platillo de la demanda pesa más que el de las donaciones por varios días seguidos, hay que actuar.',
  },
  riesgo: {
    emoji: '🤖', titulo: 'Riesgo del modelo',
    que: 'La probabilidad de escasez a 14 días que estima el modelo de machine learning.',
    como: 'Un XGBoost entrenado con 50 señales de la serie diaria (presión, rezagos, tendencias, estacionalidad), validado respetando el orden temporal.',
    porque: 'Complementa la regla del umbral: el modelo ve patrones que la resta simple no captura, y su corte se eligió para no perder alertas (mejor una falsa alarma que una escasez sorpresa).',
    analogia: 'Un meteorólogo de la sangre: no espera a ver nubes, pronostica la tormenta con dos semanas de ventaja.',
  },
  grafica: {
    emoji: '📈', titulo: 'La curva de presión',
    que: 'La historia de los últimos 90 días del pulso oferta-demanda.',
    como: 'La línea roja es la presión diaria; la punteada es el umbral τ, centrado en la gráfica. El área sombreada es la integral respecto a τ: suave mientras hay calma, roja intensa cuando lo supera.',
    porque: 'Ver la distancia al umbral (y cuánta área se acumula al cruzarlo) dice no solo si hay riesgo, sino qué tan hondo es.',
    analogia: 'Como el nivel de un río contra la línea de inundación: lo importante no es solo tocarla, sino cuánta agua pasa por encima.',
  },
  semaforo: {
    emoji: '🚦', titulo: 'Semáforo por grupo sanguíneo',
    que: 'La cobertura de cada tipo de sangre: cuántos días dura su stock frente a su propia demanda.',
    como: 'Unidades vigentes del grupo ÷ su demanda diaria. Crítico < 4 días, vigilancia < 7, estable ≥ 7.',
    porque: 'El total engaña: puede haber mucha sangre y a la vez faltar O−. Cada grupo cubre a receptores distintos, como muestra el grafo.',
    analogia: 'El O− es el comodín del mazo: sirve para todos, así que se gasta primero y hay que vigilarlo aparte.',
    extra: 'grafo',
  },
};

function openInfo(key) {
  const d = INFO_KPI[key];
  if (!d) return;
  document.getElementById('im-emoji').textContent = d.emoji;
  document.getElementById('im-titulo').textContent = d.titulo;
  document.getElementById('im-que').textContent = d.que;
  document.getElementById('im-como').textContent = d.como;
  document.getElementById('im-porque').textContent = d.porque;
  const extra = document.getElementById('im-extra');
  extra.innerHTML = '';
  const builder = IX_EXTRAS[key];
  if (builder) builder(extra);
  document.getElementById('info-modal').classList.add('open');
}
function closeInfo() {
  const m = document.getElementById('info-modal');
  if (m) m.classList.remove('open');
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeInfo(); });

/* ══ Diagramas interactivos de cada ventana ══ */

/* Stock: la vida de una unidad — arrastra la edad y mira si sigue vigente. */
function ixStock(box) {
  box.innerHTML = `
    <div class="im-extra-label">Arrastra la edad de una unidad donada</div>
    <div class="ix">
      <div class="ix-row"><span class="ix-big" id="ixs-bag">🩸</span>
        <input type="range" min="0" max="60" value="12" id="ixs-edad"></div>
      <div class="ix-bar"><div class="ix-fill" id="ixs-fill"></div><span class="ix-marca" style="left:${40 / 60 * 100}%"></span></div>
      <p class="ix-txt" id="ixs-txt"></p>
    </div>`;
  const upd = () => {
    const edad = +box.querySelector('#ixs-edad').value;
    const vigente = edad <= 40;
    const fill = box.querySelector('#ixs-fill');
    fill.style.width = Math.min(100, edad / 60 * 100) + '%';
    fill.style.background = !vigente ? '#9CA3AF' : edad >= 30 ? '#D97706' : '#16A34A';
    box.querySelector('#ixs-bag').textContent = vigente ? '🩸' : '🗑️';
    box.querySelector('#ixs-txt').innerHTML = vigente
      ? `Día <b>${edad}</b> de 40 — la unidad sigue <b style="color:#16A34A">vigente</b>${edad >= 30 ? ' (¡úsala pronto!)' : ''}.`
      : `Día <b>${edad}</b> — pasó los 40 días: <b style="color:#BF1212">caducó</b> y se descarta aunque nadie la haya usado.`;
  };
  box.querySelector('#ixs-edad').addEventListener('input', upd);
  upd();
}

/* Autonomía: mueve el consumo diario y mira cuántos días aguanta el banco. */
function ixAutonomia(box) {
  const base = Math.max(20, Math.round(consumoDia));
  box.innerHTML = `
    <div class="im-extra-label">¿Y si el consumo diario cambia?</div>
    <div class="ix">
      <div class="ix-row"><span class="ix-big">🏥</span>
        <input type="range" min="20" max="90" value="${base}" id="ixa-con"></div>
      <p class="ix-txt" id="ixa-txt"></p>
    </div>`;
  const upd = () => {
    const con = +box.querySelector('#ixa-con').value;
    const dias = stockTotal / con;
    const color = dias < 5 ? '#BF1212' : dias < 8 ? '#D97706' : '#16A34A';
    const estado = dias < 5 ? 'alarma' : dias < 8 ? 'vigilancia' : 'saludable';
    box.querySelector('#ixa-txt').innerHTML =
      `Con <b>${con}</b> unidades/día, las <b>${stockTotal.toLocaleString('es-CO')}</b> vigentes duran ` +
      `<b style="color:${color}">${dias.toFixed(1)} días</b> (${estado}).`;
  };
  box.querySelector('#ixa-con').addEventListener('input', upd);
  upd();
}

/* Presión: balanza de oferta vs demanda contra el umbral τ. */
function ixPresion(box) {
  const o = Math.max(5, Math.round(donHoy)), d = Math.max(5, Math.round(demHoy));
  const esc = Math.max(50, TAU * 1.8);
  box.innerHTML = `
    <div class="im-extra-label">Juega con la balanza</div>
    <div class="ix">
      <label class="ix-lbl">Donaciones/día <b id="ixp-ov">${o}</b>
        <input type="range" min="5" max="50" value="${o}" id="ixp-o"></label>
      <label class="ix-lbl">Demanda/día <b id="ixp-dv">${d}</b>
        <input type="range" min="5" max="60" value="${d}" id="ixp-d"></label>
      <div class="ix-bar"><div class="ix-fill" id="ixp-fill"></div><span class="ix-marca" style="left:${TAU / esc * 100}%"></span></div>
      <p class="ix-txt" id="ixp-txt"></p>
    </div>`;
  const upd = () => {
    const ov = +box.querySelector('#ixp-o').value, dv = +box.querySelector('#ixp-d').value;
    box.querySelector('#ixp-ov').textContent = ov;
    box.querySelector('#ixp-dv').textContent = dv;
    const p = dv - ov;
    const sobre = p > TAU;
    const fill = box.querySelector('#ixp-fill');
    fill.style.width = Math.max(0, Math.min(100, p / esc * 100)) + '%';
    fill.style.background = sobre ? '#BF1212' : '#16A34A';
    box.querySelector('#ixp-txt').innerHTML = sobre
      ? `Presión = <b>${p.toFixed(0)}</b> &gt; τ (${TAU.toFixed(1)}) → <b style="color:#BF1212">escasez proyectada a 14 días</b> ⚠`
      : `Presión = <b>${p.toFixed(0)}</b> ≤ τ (${TAU.toFixed(1)}) → <b style="color:#16A34A">zona estable</b>`;
  };
  box.querySelectorAll('input').forEach(i => i.addEventListener('input', upd));
  upd();
}

/* Riesgo: mueve la probabilidad y mira cuándo el modelo dispara la alerta. */
function ixRiesgo(box) {
  const corte = (MODEL_THR || 0.008) * 100;
  const val = Math.min(2, probHoy * 100);
  box.innerHTML = `
    <div class="im-extra-label">¿Cuándo dispara la alerta el modelo?</div>
    <div class="ix">
      <div class="ix-row"><span class="ix-big" id="ixr-ico">🤖</span>
        <input type="range" min="0" max="2" step="0.01" value="${val.toFixed(2)}" id="ixr-p"></div>
      <div class="ix-bar"><div class="ix-fill" id="ixr-fill"></div><span class="ix-marca" style="left:${corte / 2 * 100}%"></span></div>
      <p class="ix-txt" id="ixr-txt"></p>
    </div>`;
  const upd = () => {
    const p = +box.querySelector('#ixr-p').value;
    const alerta = p >= corte;
    const fill = box.querySelector('#ixr-fill');
    fill.style.width = (p / 2 * 100) + '%';
    fill.style.background = alerta ? '#BF1212' : '#16A34A';
    box.querySelector('#ixr-ico').textContent = alerta ? '🚨' : '🤖';
    box.querySelector('#ixr-txt').innerHTML = alerta
      ? `P(escasez) = <b>${p.toFixed(2)}%</b> ≥ corte (${corte.toFixed(2)}%) → <b style="color:#BF1212">el modelo pide campaña ya</b>`
      : `P(escasez) = <b>${p.toFixed(2)}%</b> &lt; corte (${corte.toFixed(2)}%) → <b style="color:#16A34A">sin alerta</b>`;
  };
  box.querySelector('#ixr-p').addEventListener('input', upd);
  upd();
}

/* Gráfica: recorre la curva de presión — datos reales o un ejemplo de crisis. */
function ixGrafica(box) {
  const n = data.fecha.length, span = Math.min(90, n);
  const presReal = data.presion.slice(n - span);
  const fechas = data.fecha.slice(n - span);

  /* Ejemplo de crisis (didáctico): la presión sube semana a semana, cruza τ
     alrededor del día 55 y se queda arriba — el patrón del colapso de 2023. */
  const presCrisis = [];
  for (let i = 0; i < span; i++) {
    const base = TAU - 16 + i * 0.42;
    const onda = 4.2 * Math.sin(i / 5.2) + 2.4 * Math.sin(i / 2.1 + 1.3);
    presCrisis.push(+(base + onda).toFixed(1));
  }

  const W = 480, H = 190, PAD = 12;
  const todos = presReal.filter(v => v != null).concat(presCrisis, [TAU]);
  const lo = Math.min(...todos) - 2, hi = Math.max(...todos) + 4;
  const X = i => PAD + i / (span - 1) * (W - 2 * PAD);
  const Y = v => H - PAD - (v - lo) / (hi - lo) * (H - 2 * PAD);

  let serie = presReal, esCrisis = false;

  const render = () => {
    const pts = serie.map((v, i) => v == null ? null : `${X(i).toFixed(1)},${Y(v).toFixed(1)}`)
      .filter(Boolean).join(' ');
    /* Integral sobre τ: se sombrea solo lo que queda por encima del umbral. */
    const clamp = serie.map((v, i) => `${X(i).toFixed(1)},${Y(Math.max(v == null ? lo : v, TAU)).toFixed(1)}`).join(' ');
    const area = `${clamp} ${X(span - 1).toFixed(1)},${Y(TAU).toFixed(1)} ${X(0).toFixed(1)},${Y(TAU).toFixed(1)}`;
    const cruceI = serie.findIndex((v, i) => v != null && v > TAU && (i === 0 || serie[i - 1] <= TAU));
    const cruce = cruceI >= 0
      ? `<circle cx="${X(cruceI)}" cy="${Y(serie[cruceI])}" r="6" fill="#BF1212" stroke="#fff" stroke-width="2.5"/>
         <text x="${(X(cruceI) - 14).toFixed(1)}" y="${(Y(serie[cruceI]) - 12).toFixed(1)}" text-anchor="middle"
           font-family="Inter,sans-serif" font-size="20" font-weight="800" fill="#BF1212">!</text>`
      : '';
    box.querySelector('#ixg-plot').innerHTML = `
      <polygon points="${area}" fill="rgba(191,18,18,0.28)"/>
      <line x1="${PAD}" y1="${Y(TAU)}" x2="${W - PAD}" y2="${Y(TAU)}" stroke="#BF1212" stroke-dasharray="7 5" stroke-width="1.8"/>
      <text x="${W - PAD - 4}" y="${Y(TAU) - 7}" text-anchor="end" font-family="Inter,sans-serif"
        font-size="11" font-weight="700" fill="#BF1212">τ</text>
      <polyline points="${pts}" fill="none" stroke="#BF1212" stroke-width="2.2"/>
      ${cruce}
      <line id="ixg-cursor" x1="0" y1="${PAD}" x2="0" y2="${H - PAD}" stroke="#1F2937" stroke-width="1" opacity="0"/>
      <circle id="ixg-dot" r="5" fill="#BF1212" stroke="#fff" stroke-width="2" opacity="0"/>`;
    box.querySelector('#ixg-txt').innerHTML = esCrisis
      ? 'Así se ve una crisis: la presión sube sostenida, <b style="color:#BF1212">cruza τ</b> y el área roja (la escasez acumulada) crece día a día.'
      : 'Pasa el cursor por la curva.';
  };

  box.innerHTML = `
    <div class="ix-toggle">
      <button id="ixg-real" class="active">Datos reales</button>
      <button id="ixg-crisis">⚠ Ejemplo de crisis</button>
    </div>
    <svg viewBox="0 0 ${W} ${H}" id="ixg-svg" style="cursor:crosshair"><g id="ixg-plot"></g></svg>
    <p class="ix-txt" id="ixg-txt"></p>`;

  const setSerie = crisis => {
    esCrisis = crisis;
    serie = crisis ? presCrisis : presReal;
    box.querySelector('#ixg-real').classList.toggle('active', !crisis);
    box.querySelector('#ixg-crisis').classList.toggle('active', crisis);
    render();
  };
  box.querySelector('#ixg-real').addEventListener('click', () => setSerie(false));
  box.querySelector('#ixg-crisis').addEventListener('click', () => setSerie(true));

  const svg = box.querySelector('#ixg-svg');
  svg.addEventListener('mousemove', e => {
    const r = svg.getBoundingClientRect();
    const i = Math.max(0, Math.min(span - 1, Math.round((e.clientX - r.left) / r.width * (span - 1))));
    const v = serie[i];
    if (v == null) return;
    const cur = box.querySelector('#ixg-cursor'), dot = box.querySelector('#ixg-dot');
    if (!cur || !dot) return;
    cur.setAttribute('x1', X(i)); cur.setAttribute('x2', X(i)); cur.setAttribute('opacity', '.5');
    dot.setAttribute('cx', X(i)); dot.setAttribute('cy', Y(v)); dot.setAttribute('opacity', '1');
    const f = esCrisis ? `día ${i + 1}` : fechas[i].toLocaleDateString('es-CO', { day: 'numeric', month: 'short' });
    const sobre = v > TAU;
    box.querySelector('#ixg-txt').innerHTML =
      `<b>${f}</b> · presión <b>${v.toFixed(1)}</b> → ` +
      (sobre ? `<b style="color:#BF1212">zona crítica: escasez proyectada</b>` : `<b style="color:#16A34A">zona estable</b>`);
  });

  render();
}

/* Semáforo: grafo de compatibilidad interactivo (hover = dona / recibe). */
function ixGrafo(box) {
  const TIPOS = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
  const ABO = { O: ['O', 'A', 'B', 'AB'], A: ['A', 'AB'], B: ['B', 'AB'], AB: ['AB'] };
  const abo = t => t.slice(0, -1), rh = t => t.slice(-1);
  const puede = (d, r) => ABO[abo(d)].includes(abo(r)) && (rh(d) === '-' || rh(r) === '+');
  const W = 480, H = 290, cx = W / 2, cy = H / 2, R = 100, LR = R + 26;
  const ang = i => (-90 + i * 45) * Math.PI / 180;
  const pos = TIPOS.map((t, i) => ({ t, x: cx + R * Math.cos(ang(i)), y: cy + R * Math.sin(ang(i)) }));
  let edges = '', nodes = '';
  pos.forEach((a, i) => pos.forEach((b, j) => {
    if (i === j || !puede(a.t, b.t)) return;
    const mx = (a.x + b.x) / 2 + (cx - (a.x + b.x) / 2) * 0.42;
    const my = (a.y + b.y) / 2 + (cy - (a.y + b.y) / 2) * 0.42;
    edges += `<path class="mg-e" data-f="${a.t}" data-t="${b.t}"
      d="M${a.x.toFixed(0)} ${a.y.toFixed(0)} Q${mx.toFixed(0)} ${my.toFixed(0)} ${b.x.toFixed(0)} ${b.y.toFixed(0)}"
      fill="none" stroke="#9CA3AF" stroke-opacity="0.18" stroke-width="1.2"/>`;
  }));
  pos.forEach((p, i) => {
    const lx = cx + LR * Math.cos(ang(i)), ly = cy + LR * Math.sin(ang(i));
    nodes += `<g class="mg-n" data-t="${p.t}" style="cursor:pointer">
      <circle cx="${p.x.toFixed(0)}" cy="${p.y.toFixed(0)}" r="10" fill="#1F2937"/>
      <text x="${lx.toFixed(0)}" y="${(ly + 4).toFixed(0)}" text-anchor="middle"
        font-family="Inter, sans-serif" font-size="12.5" font-weight="700" fill="#374151">${p.t}</text></g>`;
  });
  box.innerHTML = `
    <div class="im-extra-label">Toca un grupo: rojo = a quién dona · azul = de quién recibe</div>
    <svg viewBox="0 0 ${W} ${H}" id="mg-svg">${edges}${nodes}</svg>
    <p class="ix-txt" id="mg-txt">Pasa el cursor por un grupo sanguíneo.</p>`;
  const svg = box.querySelector('#mg-svg');
  const focus = t => {
    svg.querySelectorAll('.mg-e').forEach(e => {
      const out = e.dataset.f === t, inn = e.dataset.t === t;
      e.setAttribute('stroke', out ? '#BF1212' : inn ? '#1D4ED8' : '#9CA3AF');
      e.setAttribute('stroke-opacity', out ? '0.9' : inn ? '0.7' : '0.05');
      e.setAttribute('stroke-width', out || inn ? '2.2' : '1');
    });
    svg.querySelectorAll('.mg-n').forEach(g => {
      const es = g.dataset.t === t;
      g.querySelector('circle').setAttribute('fill', es ? '#BF1212' : '#1F2937');
      g.style.opacity = es || puede(t, g.dataset.t) || puede(g.dataset.t, t) ? '1' : '0.3';
    });
    const dona = TIPOS.filter(r => puede(t, r)).length;
    const recibe = TIPOS.filter(d => puede(d, t)).length;
    box.querySelector('#mg-txt').innerHTML =
      `<b>${t}</b> dona a <b style="color:#BF1212">${dona}</b> tipos · recibe de <b style="color:#1D4ED8">${recibe}</b>`;
  };
  svg.querySelectorAll('.mg-n').forEach(g => {
    g.addEventListener('mouseenter', () => focus(g.dataset.t));
    g.addEventListener('click', () => focus(g.dataset.t));
  });
}

const IX_EXTRAS = {
  stock: ixStock, autonomia: ixAutonomia, presion: ixPresion,
  riesgo: ixRiesgo, grafica: ixGrafica, semaforo: ixGrafo,
};

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

  /* B · Presión vs τ — estilo "integral": área rellena hasta la base, umbral
     punteado y un punto marcando el primer cruce sobre el umbral. */
  const elP = document.getElementById('chart-presion');
  if (elP) {
    const presion = lastN(data.presion);
    const radios = presion.map((v, i) =>
      (v != null && v > TAU && (i === 0 || presion[i - 1] <= TAU)) ? 6 : 0);

    /* Escala simétrica alrededor de τ para que el umbral quede centrado. */
    const desv = Math.max(8, ...presion.filter(v => v != null).map(v => Math.abs(v - TAU)));
    const yMin = TAU - desv * 1.15, yMax = TAU + desv * 1.15;

    /* Señas de zonas: crítica sobre el umbral, estable debajo. */
    const zonasPlugin = {
      id: 'zonas',
      afterDatasetsDraw(chart) {
        const { ctx, chartArea: { left }, scales: { y } } = chart;
        const yTau = y.getPixelForValue(TAU);
        ctx.save();
        ctx.font = "800 12px 'Inter', sans-serif";
        ctx.textAlign = 'left';
        ctx.fillStyle = 'rgba(191,18,18,0.9)';
        ctx.fillText('▲ ZONA CRÍTICA', left + 10, yTau - 12);
        ctx.fillStyle = 'rgba(22,163,74,0.95)';
        ctx.fillText('▼ ZONA ESTABLE', left + 10, yTau + 22);
        ctx.restore();
      },
    };

    chartPresion = new Chart(elP, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Presión', data: presion,
            borderColor: C_DEMANDA, borderWidth: 2.5, tension: 0.3,
            pointRadius: radios, pointHoverRadius: 6,
            pointBackgroundColor: C_DEMANDA, pointBorderColor: '#fff', pointBorderWidth: 2,
            fill: { target: { value: TAU }, above: 'rgba(191,18,18,0.32)', below: 'rgba(191,18,18,0.14)' } },
          { label: 'Umbral de escasez', data: labels.map(() => TAU),
            borderColor: C_DEMANDA, borderDash: [8, 6], borderWidth: 2, pointRadius: 0 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, interaction: interaccion,
        plugins: { legend: { ...leyenda, onClick: null,
          labels: { ...leyenda.labels, font: { size: 13, weight: '600' }, padding: 14 } } },
        scales: { ...ejes, y: { ...ejes.y, min: yMin, max: yMax } },
      },
      plugins: [zonasPlugin],
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
