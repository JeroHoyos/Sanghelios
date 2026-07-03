/* ════════════════════════════════════════════════════════════
   SANGHELIOS · image_generation.js
   Asistente conversacional de campañas: guía al usuario paso a
   paso (zona → grupo → fecha → objetivo), pide la propuesta a la
   IA (/api/asistente-campana), genera el flyer (/generate-image)
   y despliega la campaña en el mapa (POST /api/campanas).
   Solo se activa si la vista del chat existe (#chat).
   ════════════════════════════════════════════════════════════ */

const S = {
  zonaKey: null, lugar: '', tipo: null, tipos: [], fecha: '', fechaISO: '', objetivo: '', plan: null,
  flyerUrl: '', template: 'gotita-feliz', fotoId: '', mode: 'zona',
  textos: { titular: '', mensaje: '', fecha: '', lugar: '', publico: '', nota: '' },
  persona: { nombre: '', tipo: '', lugar: 'Hospital General de Medellín', mensaje: '', foto: null },
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

/* Reconocimientos variados para que la charla se sienta natural. */
const ACKS = ['¡Buena elección!', '¡Perfecto!', 'Me gusta 👌', '¡Listo, anotado!', 'Excelente.'];
const ack = () => ACKS[Math.floor(Math.random() * ACKS.length)];

/* Ideas de lugar según el perfil de la zona. */
const IDEAS_LUGAR = {
  universitarios: ['La cafetería central del campus', 'La biblioteca en hora de descanso', 'La estación de metro más cercana'],
  trabajadores: ['El centro comercial de la zona', 'La plaza principal a mediodía', 'La estación del metro en hora pico'],
  comunidad: ['El parque principal el fin de semana', 'La cancha del barrio un domingo', 'La salida de la parroquia'],
};

/* ── Flujo ── */
function stepInicio() {
  botMsg('¡Hola! 👋 Soy el asistente de campañas de <b>Sanghelios</b>. ¿Qué hacemos hoy?');
  chips([
    { label: '📢 Campaña en una zona', primary: true, action: () => { userMsg('Una campaña en una zona'); stepZona(); } },
    { label: '🧍 Ayudar a una persona', action: () => { userMsg('Quiero ayudar a una persona'); stepPNombre(); } },
  ]);
}

function stepZona() {
  botMsg('¡De una! 💪 ¿En qué zona de Medellín la montamos?');
  const opts = Object.entries(ZONAS).map(([key, z]) => ({
    label: z.nombre,
    action: () => { S.zonaKey = key; userMsg(z.nombre); updatePanel(); stepLugar(); },
  }));
  chips(opts);
}

function stepLugar() {
  const z = ZONAS[S.zonaKey];
  botMsg(`${ack()} ¿Y en qué <b>lugar exacto</b> de ${z.nombre} ponemos la unidad móvil?`);
  mostrarOpcionesLugar();
}
function mostrarOpcionesLugar() {
  const z = ZONAS[S.zonaKey];
  chips([
    { label: `📍 ${z.lugar} (recomendado)`, primary: true, action: () => pickLugar(z.lugar) },
    { label: '💡 Dame ideas', action: () => {
        userMsg('Dame ideas');
        const ideas = IDEAS_LUGAR[z.perfil] || IDEAS_LUGAR.comunidad;
        botMsg(`En ${z.nombre} la gente ${z.perfil === 'universitarios' ? 'joven se mueve por el campus' : z.perfil === 'trabajadores' ? 'trabaja y circula a mediodía' : 'vive el barrio los fines de semana'}, así que te sugiero:`);
        chips(ideas.map(i => ({ label: i, action: () => pickLugar(i) }))
          .concat([{ label: '✏️ Otro lugar…', action: pedirLugarLibre }]));
      } },
    { label: '✏️ Otro lugar…', action: pedirLugarLibre },
  ]);
}
function pedirLugarLibre() {
  pendingStep = 'lugar';
  botMsg('Escríbelo abajo (ej. <i>Entrada del Éxito de la 65</i>).');
}
function pickLugar(lugar) {
  S.lugar = lugar;
  userMsg(lugar);
  stepTipo();
}

/* Cuando el lugar lo escribe el usuario (dirección propia) se busca el lugar
   real (IA + OpenStreetMap) y se confirma antes de seguir. */
const escHtml = s => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;');
async function buscarLugarReal(texto, zona) {
  const think = typingStart();
  try {
    const d = await fetch('/api/buscar-lugar', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto, zona }),
    }).then(r => r.json());
    think.remove();
    return d && d.encontrado && d.nombre ? d : null;
  } catch (_) { think.remove(); return null; }
}
const lugarConDir = c => c.direccion ? `${c.nombre} · ${c.direccion}` : c.nombre;

async function confirmarLugar(val) {
  userMsg(val);
  const z = ZONAS[S.zonaKey];
  const cand = await buscarLugarReal(val, z.nombre);
  if (cand) {
    botMsg(`🔎 Creo que te refieres a <b>${escHtml(cand.nombre)}</b>` +
      (cand.direccion ? ` — ${escHtml(cand.direccion)}` : '') +
      (cand.nota ? `<br><small>${escHtml(cand.nota)}</small>` : '') + ' ¿Es ese?');
    chips([
      { label: `✅ Sí, es ${cand.nombre}`, primary: true, action: () => { S.lugar = lugarConDir(cand); userMsg(`Sí, ${cand.nombre}`); stepTipo(); } },
      { label: '📝 Dejar mi texto tal cual', action: () => confirmarLugarManual(val) },
      { label: '✏️ Corregirlo', action: pedirLugarLibre },
    ]);
    return;
  }
  botMsg('🔎 No encontré un lugar con ese nombre, pero igual podemos usarlo.');
  confirmarLugarManual(val);
}
function confirmarLugarManual(val) {
  const z = ZONAS[S.zonaKey];
  botMsg(`📍 Anoté <b>«${escHtml(val)}»</b>. Al desplegar la campaña quedará marcada en la zona de <b>${z.nombre}</b> del Mapa 3D. ¿Lo confirmamos?`);
  chips([
    { label: '✅ Sí, ese es el lugar', primary: true, action: () => { S.lugar = val; userMsg('Confirmado'); stepTipo(); } },
    { label: '🗺 Ver la zona en el mapa', action: () => {
        userMsg('Déjame ver la zona');
        botMsg(`Te abro el Mapa 3D enfocado en <b>${z.nombre}</b> en otra pestaña. Cuando vuelvas, confirma o corrige el lugar 😉`);
        try { localStorage.setItem('sang-focus-zona', S.zonaKey); } catch (_) { /* sin storage */ }
        window.open('/#mapa', '_blank');
        chips([
          { label: '✅ Sí, ese es el lugar', primary: true, action: () => { S.lugar = val; userMsg('Confirmado'); stepTipo(); } },
          { label: '✏️ Corregirlo', action: pedirLugarLibre },
        ]);
      } },
    { label: '✏️ Corregirlo', action: pedirLugarLibre },
  ]);
}
async function confirmarPLugar(val) {
  userMsg(val);
  const cand = await buscarLugarReal(val, '');
  if (cand) {
    botMsg(`🔎 Creo que te refieres a <b>${escHtml(cand.nombre)}</b>` +
      (cand.direccion ? ` — ${escHtml(cand.direccion)}` : '') + '. ¿Lo pongo así en el flyer?');
    chips([
      { label: `✅ Sí, es ${cand.nombre}`, primary: true, action: () => { S.persona.lugar = lugarConDir(cand); userMsg(`Sí, ${cand.nombre}`); stepPMensaje(); } },
      { label: '📝 Dejar mi texto tal cual', action: () => confirmarPLugarManual(val) },
      { label: '✏️ Corregirlo', action: () => { pendingStep = 'plugar'; botMsg('Escríbelo de nuevo 👇'); } },
    ]);
    return;
  }
  confirmarPLugarManual(val);
}
function confirmarPLugarManual(val) {
  botMsg(`📍 ¿Confirmas que las donaciones se reciben en <b>«${escHtml(val)}»</b>? Ese texto saldrá tal cual en el flyer.`);
  chips([
    { label: '✅ Sí, confirmar', primary: true, action: () => { S.persona.lugar = val; userMsg('Confirmado'); stepPMensaje(); } },
    { label: '✏️ Corregirlo', action: () => { pendingStep = 'plugar'; botMsg('Escríbelo de nuevo 👇'); } },
  ]);
}

function stepTipo() {
  botMsg(`${ack()} ¿Qué grupos sanguíneos priorizamos? Puedes <b>elegir varios</b> y luego tocar «Listo».`);
  const grupos = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
  S.tipos = [];
  clearChips();
  const box = document.createElement('div');
  box.className = 'chips';

  const rec = document.createElement('button');
  rec.className = 'chip';
  rec.textContent = '🤖 Recomiéndame';
  rec.onclick = async () => {
    clearChips();
    userMsg('Recomiéndame');
    await typing(600);
    botMsg('Según el análisis del banco, el <b>O−</b> es el de mayor riesgo estructural: dona a los 8 tipos pero es apenas el 9% de los donantes. Vamos con <b>O−</b>.');
    S.tipos = ['O-']; S.tipo = 'O-'; updatePanel(); stepFecha();
  };
  box.appendChild(rec);

  const done = document.createElement('button');
  grupos.forEach(g => {
    const b = document.createElement('button');
    b.className = 'chip';
    b.textContent = g;
    b.onclick = () => {
      const i = S.tipos.indexOf(g);
      if (i >= 0) { S.tipos.splice(i, 1); b.classList.remove('primary'); b.textContent = g; }
      else { S.tipos.push(g); b.classList.add('primary'); b.textContent = '✓ ' + g; }
      done.disabled = !S.tipos.length;
      done.textContent = S.tipos.length ? `✅ Listo (${S.tipos.join(', ')})` : '✅ Listo';
    };
    box.appendChild(b);
  });

  done.className = 'chip primary';
  done.textContent = '✅ Listo';
  done.disabled = true;
  done.onclick = () => {
    if (!S.tipos.length) return;
    clearChips();
    S.tipo = S.tipos.join(', ');
    userMsg(S.tipo);
    updatePanel(); stepFecha();
  };
  box.appendChild(done);

  $('chat').appendChild(box);
  scrollChat();
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
  S.mode = 'zona';
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
      lugar: S.lugar || z.lugar,
      publico: S.tipo ? `${S.tipos && S.tipos.length > 1 ? 'Grupos prioritarios' : 'Grupo prioritario'} ${S.tipo}` : '',
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
  botMsg('🎨 ¡Flyer listo! Lo tienes arriba en el panel. Puedes <b>editar los textos</b>, ponerle una <b>foto</b> o cambiar de plantilla. ¿Desplegamos la campaña en el mapa?');
  flyerChips();
}

function flyerChips() {
  chips([
    { label: '📍 Desplegar en el mapa', primary: true, action: runDeploy },
    { label: '✏️ Editar textos', action: openEditorModal },
    { label: S.fotoId ? '📸 Cambiar foto' : '📸 Ponerle foto', action: () => $('zfoto-input').click() },
    ...(S.fotoId ? [{ label: '🚫 Quitar foto', action: quitarFotoZona }] : []),
    { label: '🔁 Otra propuesta', action: runPlan },
    { label: '🖼 Otra plantilla', action: otherTemplate },
  ]);
}

/* Foto para el flyer de zona: se sube una vez y se reutiliza por id. */
async function zfotoSeleccionada(input) {
  const file = input.files && input.files[0];
  if (!file) return;
  input.value = '';
  clearChips();
  const el = document.createElement('div');
  el.className = 'msg user';
  el.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="Foto" style="max-width:130px;border-radius:12px;display:block;">`;
  $('chat').appendChild(el);
  scrollChat();
  const think = typingStart();
  try {
    const body = new FormData();
    body.append('foto', file);
    const d = await fetch('/upload-foto', { method: 'POST', body }).then(r => r.json());
    S.fotoId = d.id;
    await renderFlyer();
    think.remove();
    botMsg('📸 ¡Foto puesta! Quedó como insignia en el flyer.');
  } catch (_) {
    think.remove();
    botMsg('⚠️ No pude subir la foto. Intenta de nuevo.');
  }
  flyerChips();
}
function quitarFotoZona() {
  S.fotoId = '';
  userMsg('Quita la foto');
  renderFlyer().then(() => { botMsg('Listo, flyer sin foto.'); flyerChips(); });
}

/* Genera el flyer con la plantilla y textos actuales (S.template / S.textos). */
async function renderFlyer() {
  try {
    const res = await fetch('/generate-flyer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ template: S.template, foto: S.fotoId || '', ...S.textos }),
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
  if (S.mode === 'persona') { openEditorP(); return; }
  DRAFT = { template: S.template, url: S.flyerUrl, foto: S.fotoId, ...S.textos };
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
          template: DRAFT.template, foto: DRAFT.foto || '',
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

/* ── Editor del flyer PERSONAL (nombre, tipo, lugar, mensaje, foto) ── */
let DRAFT_P = null;
let livePTimer = null;

function openEditorP() {
  DRAFT_P = {
    nombre: S.persona.nombre, tipo: S.persona.tipo || 'O+',
    lugar: S.persona.lugar, mensaje: S.persona.mensaje,
    foto: S.persona.foto, url: S.flyerUrl,
  };
  $('edp-nombre').value = DRAFT_P.nombre || '';
  $('edp-tipo').value = DRAFT_P.tipo;
  $('edp-lugar').value = DRAFT_P.lugar || '';
  $('edp-mensaje').value = DRAFT_P.mensaje || '';
  $('empp-img').src = S.flyerUrl ? S.flyerUrl + '?t=' + Date.now() : '';
  $('editorp-modal').classList.add('open');
}
function closeEditorP() {
  clearTimeout(livePTimer);
  $('editorp-modal').classList.remove('open');
}
function editorPInput(campo, valor) {
  if (!DRAFT_P) return;
  DRAFT_P[campo] = valor;
  livePreviewP();
}
function editorPFotoSeleccionada(input) {
  const file = input.files && input.files[0];
  if (!file || !DRAFT_P) return;
  input.value = '';
  DRAFT_P.foto = file;
  livePreviewP(0);
}
function editorPQuitarFoto() {
  if (!DRAFT_P || !DRAFT_P.foto) return;
  DRAFT_P.foto = null;
  livePreviewP(0);
}
function livePreviewP(delay = 700) {
  clearTimeout(livePTimer);
  livePTimer = setTimeout(async () => {
    const live = $('empp-live');
    if (live) live.hidden = false;
    try {
      const body = new FormData();
      body.append('nombre', DRAFT_P.nombre || '');
      body.append('tipo', DRAFT_P.tipo || 'O+');
      body.append('lugar', DRAFT_P.lugar || 'Hospital General de Medellín');
      body.append('mensaje', DRAFT_P.mensaje || '');
      if (DRAFT_P.foto) body.append('foto', DRAFT_P.foto);
      const d = await fetch('/generate-personal', { method: 'POST', body }).then(r => r.json());
      if (d && d.url) {
        DRAFT_P.url = d.url;
        $('empp-img').src = d.url + '?t=' + Date.now();
      }
    } catch (_) { /* la siguiente tecla reintenta */ }
    if (live) live.hidden = true;
  }, delay);
}
function applyEditorP() {
  if (!DRAFT_P) return;
  S.persona.nombre = (DRAFT_P.nombre || '').trim();
  S.persona.tipo = DRAFT_P.tipo;
  S.persona.lugar = (DRAFT_P.lugar || '').trim() || 'Hospital General de Medellín';
  S.persona.mensaje = (DRAFT_P.mensaje || '').trim();
  S.persona.foto = DRAFT_P.foto;
  if (DRAFT_P.url) {
    S.flyerUrl = DRAFT_P.url;
    $('rp-img').src = DRAFT_P.url + '?t=' + Date.now();
    $('rp-download').href = DRAFT_P.url;
  }
  closeEditorP();
  showToast('Flyer personal actualizado.');
}

/* Foto dentro del editor: sube y refresca la vista previa al instante. */
async function editorFotoSeleccionada(input) {
  const file = input.files && input.files[0];
  if (!file || !DRAFT) return;
  input.value = '';
  try {
    const body = new FormData();
    body.append('foto', file);
    const d = await fetch('/upload-foto', { method: 'POST', body }).then(r => r.json());
    DRAFT.foto = d.id;
    livePreview(0);
  } catch (_) { showToast('No se pudo subir la foto.'); }
}
function editorQuitarFoto() {
  if (!DRAFT || !DRAFT.foto) return;
  DRAFT.foto = '';
  livePreview(0);
}

/* Commit: el borrador pasa a ser el flyer oficial del asistente. */
function applyEditorModal() {
  if (!DRAFT) return;
  S.template = DRAFT.template;
  S.fotoId = DRAFT.foto || '';
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
  Object.assign(S, { zonaKey: null, lugar: '', tipo: null, tipos: [], fecha: '', fechaISO: '', objetivo: '', plan: null, flyerUrl: '', fotoId: '', mode: 'zona' });
  S.persona = { nombre: '', tipo: '', lugar: 'Hospital General de Medellín', mensaje: '', foto: null };
  pendingStep = null;
  $('chat').innerHTML = '';
  ['rp-flyer', 'rp-done'].forEach(id => { $(id).hidden = true; });
  const ph = $('rp-placeholder');
  if (ph) ph.hidden = false;
  updatePanel(); setEstado('Configurando…');
  stepInicio();
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
  if (e.key === 'Escape') { closeLightbox(); closeCampsModal(); closeEditorModal(); closeEditorP(); }
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

/* ══ Flujo persona: flyer para alguien que necesita sangre ══ */
function stepPNombre() {
  botMsg('Qué bonito gesto 💛. ¿Cómo se llama la persona que necesita la donación?');
  pendingStep = 'pnombre';
}
function stepPTipo() {
  botMsg(`${ack()} ¿Qué tipo de sangre tiene <b>${S.persona.nombre}</b>?`);
  const grupos = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
  chips(grupos.map(g => ({ label: g, action: () => {
    S.persona.tipo = g;
    userMsg(g);
    const compat = compatiblesDe(g);
    botMsg(`Anotado: <b>${g}</b>. Pueden donarle personas <b>${compat.join(', ')}</b> — eso irá en el flyer para que nadie se quede con la duda.`);
    stepPFoto();
  } })));
}
function compatiblesDe(tipo) {
  const tipos = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
  const aboOk = { O: ['O'], A: ['O', 'A'], B: ['O', 'B'], AB: ['O', 'A', 'B', 'AB'] };
  const abo = tipo.slice(0, -1), rh = tipo.slice(-1);
  return tipos.filter(d => aboOk[abo].includes(d.slice(0, -1)) && (d.slice(-1) === '-' || rh === '+'));
}
function stepPFoto() {
  botMsg('¿Tienes una <b>foto</b> de la persona? Le da mucha más cercanía al flyer (es opcional).');
  chips([
    { label: '📷 Subir foto', primary: true, action: () => $('pfoto-input').click() },
    { label: 'Seguir sin foto', action: () => { userMsg('Sin foto'); stepPLugar(); } },
  ]);
}
function fotoSeleccionada(input) {
  const file = input.files && input.files[0];
  if (!file) return;
  S.persona.foto = file;
  clearChips();
  const el = document.createElement('div');
  el.className = 'msg user';
  el.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="Foto" style="max-width:130px;border-radius:12px;display:block;">`;
  $('chat').appendChild(el);
  scrollChat();
  botMsg('¡Qué buena foto! 🤗 Irá en el flyer.');
  stepPLugar();
}
function stepPLugar() {
  botMsg('¿Dónde recibirán las donaciones?');
  chips([
    { label: '🏥 Hospital General de Medellín', primary: true, action: () => {
        S.persona.lugar = 'Hospital General de Medellín';
        userMsg('Hospital General de Medellín');
        stepPMensaje();
      } },
    { label: '✏️ Otro lugar…', action: () => {
        pendingStep = 'plugar';
        botMsg('Escríbelo abajo (ej. <i>Clínica Las Américas, piso 2</i>).');
      } },
  ]);
}
function stepPMensaje() {
  botMsg('¿Quieres agregar un mensaje personal? (ej. <i>"Cada gota cuenta, gracias por ayudar a mi mamá"</i>)');
  chips([
    { label: '✨ Sin mensaje, así está bien', primary: true, action: () => { userMsg('Así está bien'); runPersonalFlyer(); } },
    { label: '✏️ Escribir mensaje', action: () => {
        pendingStep = 'pmensaje';
        botMsg('Escríbelo abajo 👇');
      } },
  ]);
}
async function runPersonalFlyer() {
  const think = typingStart();
  const body = new FormData();
  body.append('nombre', S.persona.nombre);
  body.append('tipo', S.persona.tipo);
  body.append('lugar', S.persona.lugar);
  body.append('mensaje', S.persona.mensaje);
  if (S.persona.foto) body.append('foto', S.persona.foto);
  let d;
  try {
    const res = await fetch('/generate-personal', { method: 'POST', body });
    d = await res.json();
    if (!res.ok || d.error) throw new Error(d.error || 'error');
  } catch (e) {
    think.remove();
    botMsg('⚠️ No pude generar el flyer. ¿Reintentamos?');
    chips([{ label: '🔁 Reintentar', primary: true, action: runPersonalFlyer }]);
    return;
  }
  think.remove();
  S.mode = 'persona';
  S.flyerUrl = d.url;
  $('rp-img').src = d.url + '?t=' + Date.now();
  $('rp-download').href = d.url;
  $('rp-flyer').hidden = false;
  const ph = $('rp-placeholder');
  if (ph) ph.hidden = true;
  botMsg(`🫶 ¡El flyer para <b>${S.persona.nombre}</b> está listo! Incluye su tipo (${S.persona.tipo}) y quiénes pueden donarle (${(d.compatibles || []).join(', ')}). Descárgalo del panel y compártelo. ¿Qué más hacemos?`);
  chips([
    { label: '✏️ Editar el flyer', primary: true, action: openEditorP },
    { label: '📢 Hacer una campaña de zona', action: () => { userMsg('Ahora una campaña de zona'); stepZona(); } },
    { label: '🧍 Ayudar a otra persona', action: () => {
        S.persona = { nombre: '', tipo: '', lugar: 'Hospital General de Medellín', mensaje: '', foto: null };
        userMsg('Otra persona');
        stepPNombre();
      } },
    { label: '🔁 Regenerar este flyer', action: runPersonalFlyer },
    { label: '🆕 Empezar de cero', action: restart },
  ]);
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
  } else if (pendingStep === 'lugar') {
    pendingStep = null;
    clearChips();
    confirmarLugar(val);
  } else if (pendingStep === 'pnombre') {
    pendingStep = null;
    S.persona.nombre = val;
    userMsg(val);
    stepPTipo();
  } else if (pendingStep === 'plugar') {
    pendingStep = null;
    confirmarPLugar(val);
  } else if (pendingStep === 'pmensaje') {
    pendingStep = null;
    S.persona.mensaje = val;
    userMsg(val);
    runPersonalFlyer();
  } else if (!S.zonaKey) {
    // intenta casar el texto con una zona
    const key = Object.keys(ZONAS).find(k =>
      ZONAS[k].nombre.toLowerCase().includes(val.toLowerCase()) || k.includes(val.toLowerCase()));
    userMsg(val);
    if (key) { clearChips(); S.zonaKey = key; updatePanel(); stepLugar(); }
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
    stepInicio();
    loadHistorial();
    fetch('/api/flyer-templates').then(r => r.json())
      .then(t => { if (Array.isArray(t)) FLYER_TPLS = t; })
      .catch(() => {});
  }
});
