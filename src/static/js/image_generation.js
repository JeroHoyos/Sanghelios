/* ════════════════════════════════════════════════════════════
   SANGHELIOS · image_generation.js
   Asistente conversacional de campañas: guía al usuario paso a
   paso (zona → grupo → fecha → objetivo), pide la propuesta a la
   IA (/api/asistente-campana), genera el flyer (/generate-image)
   y despliega la campaña en el mapa (POST /api/campanas).
   Solo se activa si la vista del chat existe (#chat).
   ════════════════════════════════════════════════════════════ */

const S = {
  zonaKey: null, tipo: null, fecha: '', fechaISO: '', objetivo: '', plan: null,
  flyerUrl: '', template: 'gotita-feliz',
  textos: { titular: '', mensaje: '', fecha: '', lugar: '', publico: '', nota: '' },
};

/* Consejos heredados de la plantilla clásica: uno acompaña cada flyer. */
const NOTAS_FLYER = [
  'No olvides tomar agua y desayunar antes de donar. ¡Te esperamos!',
  'Es seguro y solo toma 30 minutos. Tu donación puede salvar hasta 3 vidas.',
  'Un pequeño gesto, un gran impacto: todos podemos ser el héroe de alguien.',
];
let FLYER_TPLS = [];   // catálogo de plantillas (GET /api/flyer-templates)
let pendingStep = null;   // paso que espera texto libre
const $ = id => document.getElementById(id);

/* ── Helpers de chat ── */
function botMsg(html) {
  const el = document.createElement('div');
  el.className = 'msg bot';
  el.innerHTML = html;
  $('chat').appendChild(el);
  scrollChat();
  return el;
}
function userMsg(text) {
  const el = document.createElement('div');
  el.className = 'msg user';
  el.textContent = text;
  $('chat').appendChild(el);
  scrollChat();
}
function chips(options) {
  clearChips();
  const box = document.createElement('div');
  box.className = 'chips';
  options.forEach(o => {
    const b = document.createElement('button');
    b.className = 'chip' + (o.primary ? ' primary' : '');
    b.textContent = o.label;
    b.onclick = () => { clearChips(); o.action(); };
    box.appendChild(b);
  });
  $('chat').appendChild(box);
  scrollChat();
}
function clearChips() { document.querySelectorAll('.chips').forEach(c => c.remove()); }
function scrollChat() { const c = $('chat'); c.scrollTop = c.scrollHeight; }
async function typing(ms = 700) {
  const el = botMsg('<span class="typing"><i></i><i></i><i></i></span>');
  await new Promise(r => setTimeout(r, ms));
  el.remove();
}

/* Puntos "pensando" que permanecen mientras dura una operación async. */
function typingStart() {
  return botMsg('<span class="typing"><i></i><i></i><i></i></span>');
}

/* ── Panel lateral (el resumen se quitó; se mantienen como no-op seguros) ── */
function updatePanel() {}
function setEstado(_t) {}

/* ── Fechas sugeridas ── */
function proximoDia(dow) {          // dow: 6=sábado, 0=domingo
  const d = new Date();
  d.setDate(d.getDate() + ((dow - d.getDay() + 7) % 7 || 7));
  return d;
}
const fmtDia = d => d.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'short' });
const iso = d => d.toISOString().slice(0, 10);

/* ── Flujo ── */
function stepZona() {
  botMsg('¡Hola! 👋 Soy el asistente de campañas de <b>Sanghelios</b>. Vamos a montar una campaña de donación en 4 pasos.<br><br><b>1.</b> ¿En qué zona de Medellín la hacemos?');
  const opts = Object.entries(ZONAS).map(([key, z]) => ({
    label: z.nombre,
    action: () => { S.zonaKey = key; userMsg(z.nombre); updatePanel(); stepTipo(); },
  }));
  chips(opts);
}

function stepTipo() {
  botMsg('<b>2.</b> ¿Qué grupo sanguíneo priorizamos?');
  const grupos = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
  chips([
    { label: '🤖 Recomiéndame', primary: true, action: async () => {
        userMsg('Recomiéndame');
        await typing(600);
        botMsg('Según el análisis del banco, el <b>O−</b> es el de mayor riesgo estructural: dona a los 8 tipos pero es apenas el 9% de los donantes. Vamos con <b>O−</b>.');
        S.tipo = 'O-'; updatePanel(); stepFecha();
      } },
    ...grupos.map(g => ({ label: g, action: () => { S.tipo = g; userMsg(g); updatePanel(); stepFecha(); } })),
  ]);
}

function stepFecha() {
  botMsg('<b>3.</b> ¿Cuándo? Te sugiero fines de semana en la mañana (mayor asistencia).');
  const sab = proximoDia(6), dom = proximoDia(0);
  chips([
    { label: `Sáb ${fmtDia(sab)} · 8am–2pm`, action: () => pickFecha(`${fmtDia(sab)} · 8am–2pm`, iso(sab)) },
    { label: `Dom ${fmtDia(dom)} · 9am–1pm`, action: () => pickFecha(`${fmtDia(dom)} · 9am–1pm`, iso(dom)) },
    { label: '✏️ Otra fecha…', action: () => {
        pendingStep = 'fecha';
        botMsg('Escríbela abajo (ej. <i>Sábado 12 jul · 8am–2pm</i>).');
      } },
  ]);
}
function pickFecha(txt, isoDate) {
  S.fecha = txt; S.fechaISO = isoDate;
  userMsg(txt); updatePanel(); stepObjetivo();
}

function stepObjetivo() {
  botMsg('<b>4.</b> ¿Cuál es el objetivo principal?');
  chips([
    { label: 'Cubrir la escasez proyectada', action: () => pickObjetivo('cubrir la escasez proyectada por el modelo a 14 días') },
    { label: `Reforzar reservas de ${S.tipo}`, action: () => pickObjetivo(`reforzar las reservas de ${S.tipo}`) },
    { label: 'Captar donantes nuevos', action: () => pickObjetivo('captar donantes de primera vez') },
    { label: 'Omitir', action: () => pickObjetivo('') },
  ]);
}
function pickObjetivo(obj) {
  S.objetivo = obj;
  userMsg(obj || 'Sin objetivo específico');
  runPlan();
}

async function runPlan() {
  setEstado('Diseñando publicidad…');
  const z = ZONAS[S.zonaKey];
  const think = typingStart();   // puntos animados mientras la IA piensa
  let d;
  try {
    const res = await fetch('/api/asistente-campana', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comuna: z.nombre, tipo: S.tipo, fecha: S.fecha, objetivo: S.objetivo }),
    });
    d = await res.json();
    if (!res.ok) throw new Error(d.detail || 'error');
  } catch (e) {
    think.remove();
    botMsg('⚠️ No pude contactar a la IA. ¿Reintentamos?');
    chips([{ label: '🔁 Reintentar', primary: true, action: runPlan }]);
    return;
  }
  think.remove();
  S.plan = d;
  setEstado('Propuesta lista');

  botMsg('Así se vería la publicación ✨');
  postPreview(d);
  runFlyer(true);   // el flyer se genera siempre, sin pedirlo
}

/* Vista previa de la publicación (como post de red social) dentro del chat */
function postPreview(d) {
  const esc = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const tags = (d.hashtags || []).map(h => `<span class="post-tag">${esc(h)}</span>`).join('');
  const el = document.createElement('div');
  el.className = 'post';
  el.innerHTML =
    `<div class="post-head"><span class="post-avatar">🩸</span>` +
    `<div><b>Sanghelios · Banco de Sangre HGM</b><span>Publicación patrocinada · Medellín</span></div>` +
    `<span class="post-src">${d.fuente === 'gemini' ? 'Gemini' : 'Reglas'}</span></div>` +
    `<div class="post-body"><h4>${esc(d.titular)}</h4><p>${esc(d.mensaje)}</p>` +
    `<div class="post-tags">${tags}</div></div>` +
    `<div class="post-canal"><b>Dónde publicar:</b> ${esc(d.canal)}</div>`;
  $('chat').appendChild(el);
  scrollChat();
}

async function runFlyer(auto) {
  if (!auto) userMsg('Regenera el flyer');
  setEstado('Generando flyer…');
  const thinkFlyer = typingStart();
  const z = ZONAS[S.zonaKey];
  if (auto) {
    // Textos base a partir de la propuesta; plantilla al azar del catálogo.
    S.textos = {
      titular: (S.plan && S.plan.titular) || `Dona sangre en ${z.nombre}`,
      mensaje: (S.plan && (S.plan.poster_mensaje || S.plan.mensaje)) || '',
      fecha: (S.plan && S.plan.poster_fecha) || S.fecha,
      lugar: z.lugar,
      publico: S.tipo ? `Grupo prioritario ${S.tipo}` : '',
      nota: NOTAS_FLYER[Math.floor(Math.random() * NOTAS_FLYER.length)],
    };
    if (FLYER_TPLS.length) {
      S.template = FLYER_TPLS[Math.floor(Math.random() * FLYER_TPLS.length)].key;
    }
  }
  const ok = await renderFlyer();
  thinkFlyer.remove();
  if (!ok) {
    botMsg('⚠️ Falló la generación del flyer. ¿Reintentamos?');
    chips([{ label: '🔁 Reintentar', primary: true, action: () => runFlyer(true) }]);
    return;
  }
  setEstado('Flyer listo');
  botMsg('🎨 ¡Flyer listo! Lo tienes arriba en el panel. Puedes <b>editar los textos</b> o cambiar de plantilla si quieres. ¿Desplegamos la campaña en el mapa?');
  chips([
    { label: '📍 Desplegar en el mapa', primary: true, action: runDeploy },
    { label: '✏️ Editar textos', action: openEditorModal },
    { label: '🔁 Otra propuesta', action: runPlan },
    { label: '🖼 Otra plantilla', action: otherTemplate },
  ]);
}

/* Genera el flyer con la plantilla y textos actuales (S.template / S.textos). */
async function renderFlyer() {
  try {
    const res = await fetch('/generate-flyer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template: S.template, ...S.textos }),
    });
    const d = await res.json();
    if (!res.ok || d.error) throw new Error(d.error || 'error');
    S.flyerUrl = d.url;
    $('rp-img').src = d.url + '?t=' + Date.now();
    $('rp-download').href = d.url;
    $('rp-flyer').hidden = false;
    const ph = $('rp-placeholder');
    if (ph) ph.hidden = true;
    return true;
  } catch (e) {
    return false;
  }
}

function otherTemplate() {
  if (FLYER_TPLS.length > 1) {
    const others = FLYER_TPLS.filter(t => t.key !== S.template);
    S.template = others[Math.floor(Math.random() * others.length)].key;
  }
  renderFlyer().then(ok => { if (ok) { markSelectedTpl(); showToast('Plantilla: ' + tplName(S.template)); } });
}

/* ── Editor del flyer (modal con vista previa en vivo) ── */
const CAMPOS_ED = ['titular', 'mensaje', 'fecha', 'lugar', 'publico', 'nota'];
let DRAFT = null;          // borrador del editor (se descarta al cancelar)
let liveTimer = null;

function tplName(key) {
  const t = FLYER_TPLS.find(x => x.key === key);
  return t ? t.nombre : key;
}
function buildEditorTpls() {
  const box = $('ed-tpls');
  if (!box || !FLYER_TPLS.length) return;
  box.innerHTML = FLYER_TPLS.map(t =>
    `<div class="ed-tpl${t.key === DRAFT.template ? ' sel' : ''}" data-k="${t.key}" title="${t.nombre}">
       <img src="${t.url}" alt="${t.nombre}"></div>`).join('');
  box.querySelectorAll('.ed-tpl').forEach(el => {
    el.onclick = () => {
      DRAFT.template = el.dataset.k;
      document.querySelectorAll('.ed-tpl').forEach(x =>
        x.classList.toggle('sel', x.dataset.k === DRAFT.template));
      livePreview(0);
    };
  });
}
function markSelectedTpl() {
  document.querySelectorAll('.ed-tpl').forEach(el =>
    el.classList.toggle('sel', el.dataset.k === S.template));
}

function openEditorModal() {
  DRAFT = { template: S.template, url: S.flyerUrl, ...S.textos };
  buildEditorTpls();
  CAMPOS_ED.forEach(k => { const el = $('ed-' + k); if (el) el.value = DRAFT[k] || ''; });
  $('em-img').src = S.flyerUrl ? S.flyerUrl + '?t=' + Date.now() : '';
  $('editor-modal').classList.add('open');
}
function closeEditorModal() {
  clearTimeout(liveTimer);
  $('editor-modal').classList.remove('open');
}

/* Cada tecla actualiza el borrador y reprograma la vista previa (debounce). */
function editorInput(campo, valor) {
  if (!DRAFT) return;
  DRAFT[campo] = valor;
  livePreview();
}
function livePreview(delay = 650) {
  clearTimeout(liveTimer);
  liveTimer = setTimeout(async () => {
    const live = $('em-live');
    if (live) live.hidden = false;
    try {
      const res = await fetch('/generate-flyer', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template: DRAFT.template,
          titular: DRAFT.titular, mensaje: DRAFT.mensaje, fecha: DRAFT.fecha,
          lugar: DRAFT.lugar, publico: DRAFT.publico, nota: DRAFT.nota,
        }),
      });
      const d = await res.json();
      if (res.ok && d.url) {
        DRAFT.url = d.url;
        $('em-img').src = d.url + '?t=' + Date.now();
      }
    } catch (_) { /* siguiente tecla reintenta */ }
    if (live) live.hidden = true;
  }, delay);
}

/* Commit: el borrador pasa a ser el flyer oficial del asistente. */
function applyEditorModal() {
  if (!DRAFT) return;
  S.template = DRAFT.template;
  CAMPOS_ED.forEach(k => { S.textos[k] = (DRAFT[k] || '').trim(); });
  if (DRAFT.url) {
    S.flyerUrl = DRAFT.url;
    $('rp-img').src = DRAFT.url + '?t=' + Date.now();
    $('rp-download').href = DRAFT.url;
  }
  closeEditorModal();
  showToast('Flyer actualizado con tus textos.');
}

async function runDeploy() {
  userMsg('Despliégala en el mapa');
  setEstado('Desplegando…');
  const thinkDeploy = typingStart();
  setTimeout(() => thinkDeploy.remove(), 600);
  const z = ZONAS[S.zonaKey];
  try {
    const res = await fetch('/api/campanas', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        comuna: S.zonaKey,
        titulo: (S.plan && S.plan.titular) || `Campaña ${S.tipo} · ${z.nombre}`,
        fecha: S.fechaISO || iso(proximoDia(6)),
        tipo: S.tipo,
        estado: 'desplegada',
        flyer: S.flyerUrl || '',
      }),
    });
    if (!res.ok) throw new Error('error');
  } catch (e) {
    botMsg('⚠️ No pude registrar la campaña. ¿Reintentamos?');
    chips([{ label: '🔁 Reintentar', primary: true, action: runDeploy }]);
    return;
  }
  $('rp-done').hidden = false;
  setEstado('✅ Desplegada');
  loadHistorial();
  botMsg(`🚀 <b>Campaña desplegada.</b> Ya aparece como zona de recogida en <b>${z.nombre}</b> dentro del Mapa 3D.`);
  chips([
    { label: '🗺 Ver en el mapa', primary: true, action: () => { location.href = '/#mapa'; } },
    { label: '🆕 Nueva campaña', action: restart },
  ]);
}

function restart() {
  Object.assign(S, { zonaKey: null, tipo: null, fecha: '', fechaISO: '', objetivo: '', plan: null, flyerUrl: '' });
  $('chat').innerHTML = '';
  ['rp-flyer', 'rp-done'].forEach(id => { $(id).hidden = true; });
  const ph = $('rp-placeholder');
  if (ph) ph.hidden = false;
  updatePanel(); setEstado('Configurando…');
  stepZona();
}

/* ── Lightbox del flyer ── */
function openLightbox() {
  if (!S.flyerUrl) return;
  $('lightbox-img').src = $('rp-img').src;
  $('lightbox').classList.add('open');
}
function closeLightbox() { $('lightbox').classList.remove('open'); }

/* ── Modal del registro de campañas ── */
function openCampsModal() {
  loadHistorial();
  $('camps-modal').classList.add('open');
}
function closeCampsModal() { $('camps-modal').classList.remove('open'); }

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeLightbox(); closeCampsModal(); closeEditorModal(); }
});

/* ── Registro de campañas anteriores ── */
async function loadHistorial() {
  const box = $('hist-list');
  if (!box) return;
  try {
    const rows = await fetch('/api/campanas').then(r => r.json());
    if (!Array.isArray(rows) || !rows.length) {
      box.innerHTML = '<span class="hist-empty">Aún no hay campañas registradas.</span>';
      return;
    }
    const zona = k => (typeof ZONAS !== 'undefined' && ZONAS[String(k || '').toLowerCase()]) || null;
    box.innerHTML = rows.slice().reverse().map(c => {
      const est = String(c.estado || 'programada').toLowerCase();
      const z = zona(c.comuna);
      const nombre = z ? z.nombre : c.comuna;
      const lugar = z ? z.lugar : 'Medellín';
      const thumb = c.flyer
        ? `<img class="h-flyer" src="${c.flyer}" alt="Flyer" title="Click para ampliar"
             onclick="window.__flyerZoom('${c.flyer}')">`
        : '';
      return `<div class="hist-item">
        <div class="h-main">
          <div class="h-top"><b>${nombre}${c.tipo ? ' · ' + c.tipo : ''}</b>
          <span class="h-estado ${est}">${est}</span></div>
          <div class="h-sub">${c.titulo || ''}</div>
          <div class="h-sub">📍 ${lugar} · 📅 ${c.fecha}</div>
          ${z ? `<button class="h-mapa" onclick="verEnMapa('${String(c.comuna).toLowerCase()}')">🗺 Ver en el mapa →</button>` : ''}
        </div>
        ${thumb}
      </div>`;
    }).join('');
  } catch (_) {
    box.innerHTML = '<span class="hist-empty">No se pudo cargar el registro.</span>';
  }
}

/* ── Texto libre ── */
function sendFree() {
  const input = $('chat-input');
  const val = (input.value || '').trim();
  if (!val) return;
  input.value = '';
  if (pendingStep === 'fecha') {
    pendingStep = null;
    clearChips();
    pickFecha(val, iso(proximoDia(6)));
  } else if (!S.zonaKey) {
    // intenta casar el texto con una zona
    const key = Object.keys(ZONAS).find(k =>
      ZONAS[k].nombre.toLowerCase().includes(val.toLowerCase()) || k.includes(val.toLowerCase()));
    userMsg(val);
    if (key) { clearChips(); S.zonaKey = key; updatePanel(); stepTipo(); }
    else botMsg('No tengo esa zona en el mapa 🙈 — elige una de las opciones de arriba.');
  } else {
    userMsg(val);
    botMsg('Usa las opciones de arriba para continuar 😉');
  }
}

/* "Ver en el mapa": guarda la zona a enfocar y navega al Mapa 3D. */
function verEnMapa(zonaKey) {
  try { localStorage.setItem('sang-focus-zona', zonaKey); } catch (_) { /* sin storage */ }
  location.href = '/#mapa';
}

let toastTimer;
function showToast(msg) {
  const t = $('toast');
  if (!t) { console.warn(msg); return; }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
}

/* ── Arranque (solo en la página del estudio) ── */
document.addEventListener('DOMContentLoaded', () => {
  if ($('chat')) {
    stepZona();
    loadHistorial();
    fetch('/api/flyer-templates').then(r => r.json())
      .then(t => { if (Array.isArray(t)) FLYER_TPLS = t; })
      .catch(() => {});
  }
});
