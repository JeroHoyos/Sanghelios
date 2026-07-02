/* ════════════════════════════════════════════════════════════
   SANGHELIOS · screener.js
   Motor del verificador de aptitud para donación de sangre.
   Controla el flujo de preguntas, historial y renderizado de
   resultados, sin depender de frameworks externos.
   ════════════════════════════════════════════════════════════ */

'use strict';

/* ── Estado global ── */
let currentIndex = 0;        // índice en QUESTIONS[]
let history      = [];        // [{index, subShown}] para el botón "volver"
let waitingForSub = false;    // true si estamos en el sub-paso de una pregunta

/* ════════════════════════════════════════════════════════════
   NAVEGACIÓN ENTRE ESTADOS (intro → pregunta → resultado)
   ════════════════════════════════════════════════════════════ */

function showState(id) {
  document.querySelectorAll('.state').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function startScreener() {
  currentIndex  = 0;
  history       = [];
  waitingForSub = false;
  showState('state-question');
  renderQuestion();
}

function resetScreener() {
  showState('state-intro');
}

/* ════════════════════════════════════════════════════════════
   RENDERIZADO DE PREGUNTAS
   ════════════════════════════════════════════════════════════ */

function renderQuestion() {
  const q   = QUESTIONS[currentIndex];
  const num = currentIndex + 1;
  const total = QUESTIONS.length;

  /* Progress */
  document.getElementById('progress-fill').style.width = `${(num / total) * 100}%`;
  document.getElementById('progress-label').textContent = `Pregunta ${num} de ${total}`;

  /* Número, icono, texto, pista */
  document.getElementById('q-number').textContent = String(num).padStart(2, '0');
  document.getElementById('q-icon').textContent   = q.icon;
  document.getElementById('q-text').textContent   = q.text;
  document.getElementById('q-hint').textContent   = q.hint || '';

  /* Resetear sub-pregunta */
  const subEl = document.getElementById('q-sub');
  subEl.style.display = 'none';
  waitingForSub = false;

  /* Botón volver */
  const backEl = document.getElementById('btn-back');
  backEl.style.display = history.length > 0 ? 'flex' : 'none';

  /* Forzar re-animación de la card */
  const card = document.getElementById('q-card');
  card.style.animation = 'none';
  void card.offsetWidth;          // reflow
  card.style.animation = '';
}

/* ════════════════════════════════════════════════════════════
   RESPUESTAS
   ════════════════════════════════════════════════════════════ */

function answer(value) {
  /* value = 'yes' | 'no' */
  const q      = QUESTIONS[currentIndex];
  const choice = value === 'yes' ? q.yes : q.no;

  if (choice.action === 'next') {
    advanceTo(currentIndex + 1);

  } else if (choice.action === 'sub') {
    /* Mostrar sub-pregunta */
    document.getElementById('q-sub-text').textContent = choice.subText;
    document.getElementById('q-sub').style.display = 'block';
    waitingForSub = true;
    /* Guardar la sub-lógica para usarla en answerSub */
    window._pendingSub = choice;

  } else {
    /* eligible | deferred | ineligible */
    showResult(choice.action, choice.reason, choice.detail);
  }
}

function answerSub(value) {
  const sub    = window._pendingSub;
  const choice = value === 'yes' ? sub.subYes : sub.subNo;

  if (choice.action === 'next') {
    document.getElementById('q-sub').style.display = 'none';
    waitingForSub = false;
    advanceTo(currentIndex + 1);
  } else {
    showResult(choice.action, choice.reason, choice.detail);
  }
}

function advanceTo(nextIndex) {
  /* Guardar historial para poder retroceder */
  history.push(currentIndex);
  currentIndex = nextIndex;

  if (currentIndex >= QUESTIONS.length) {
    /* Por si acaso se llega al final sin un resultado explicit (no debería ocurrir) */
    const last = QUESTIONS[QUESTIONS.length - 1];
    showResult('eligible', last.yes.reason, last.yes.detail);
    return;
  }

  renderQuestion();
}

/* ── Retroceder ── */
function goBack() {
  if (history.length === 0) return;
  currentIndex  = history.pop();
  waitingForSub = false;
  renderQuestion();
}

/* ════════════════════════════════════════════════════════════
   RENDERIZADO DE RESULTADOS
   ════════════════════════════════════════════════════════════ */

const OUTCOMES = {
  eligible: {
    verdict:     '¡Puedes donar sangre!',
    verdictSub:  'Cumples los criterios de aptitud para donar el día de hoy.',
    tag:         '✅ APTO/A PARA DONAR',
    nextLabel:   '¿Qué hacer ahora?',
    nextText:    '<strong>Dirígete al banco de sangre más cercano.</strong> Lleva tu documento de identidad, mantente hidratado/a y ve con ropa de manga ancha. El personal médico realizará una última evaluación antes de la extracción.',
    icon:        '✓',
  },
  deferred: {
    verdict:     'Por el momento no puedes donar',
    verdictSub:  'Existe una condición temporal que difiere tu donación.',
    tag:         '⏳ DIFERIDO/A TEMPORALMENTE',
    nextLabel:   '¿Qué puedes hacer?',
    nextText:    'Esta situación es <strong>temporal</strong>. Una vez superada la causa de diferimiento, podrás volver a intentarlo. Si tienes dudas sobre tu período de espera, consulta directamente con el banco de sangre.',
    icon:        '⏳',
  },
  ineligible: {
    verdict:     'No puedes donar en este momento',
    verdictSub:  'Existe una condición que impide la donación.',
    tag:         '⚠️ NO APTO/A EN ESTE MOMENTO',
    nextLabel:   '¿Qué hacer?',
    nextText:    'Te recomendamos hablar con el <strong>personal médico del banco de sangre</strong> o con tu médico de cabecera. En algunos casos, la condición puede resolverse con el tiempo o con tratamiento.',
    icon:        '!',
  }
};

function showResult(outcome, reason, detail) {
  const meta   = OUTCOMES[outcome];
  const wrap   = document.getElementById('result-wrap');

  wrap.innerHTML = `
    <div class="result-card">

      <!-- Header -->
      <div class="result-header ${outcome}">
        <div class="result-badge ${outcome}">
          ${getResultIcon(outcome)}
        </div>
        <h2 class="result-verdict ${outcome}">${meta.verdict}</h2>
        <p class="result-verdict-sub">${meta.verdictSub}</p>
      </div>

      <!-- Body -->
      <div class="result-body">
        <p class="result-reason-label">Motivo de la evaluación</p>
        <div class="result-reason">
          <strong>${reason}</strong><br>
          <span style="display:block;margin-top:6px;">${detail}</span>
        </div>

        <div class="result-tag ${outcome}">${meta.tag}</div>

        <div class="result-next">
          <p class="result-next-label">${meta.nextLabel}</p>
          <p class="result-next-text">${meta.nextText}</p>
        </div>

        ${outcome === 'eligible' ? `
        <div class="result-puntos">
          <p class="result-next-label">📍 Puntos para donar hoy</p>
          <div class="rp-lista" id="rp-lista"><span class="rp-cargando">Buscando campañas cercanas…</span></div>
        </div>` : ''}

        <div class="result-actions">
          <button class="btn-retry" onclick="resetScreener()">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
              <path d="M4 4v5h5M20 20v-5h-5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 9a9 9 0 0114.13-1.13L20 9M4 15l1.87 1.13A9 9 0 0020 15" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Hacer otra verificación
          </button>
          <button class="btn-share" onclick="shareResult('${outcome}', '${encodeURIComponent(reason)}')">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
              <path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Compartir
          </button>
        </div>
      </div>

      <!-- Disclaimer -->
      <p class="result-disclaimer">
        Esta evaluación es orientativa y no reemplaza la valoración médica presencial.
        El personal del banco de sangre tomará la decisión final tras evaluarte en persona.
      </p>
    </div>
  `;

  showState('state-result');
  if (outcome === 'eligible') fillPuntosDonacion();
}

/* Rellena la lista de puntos (HGM + campañas activas) en el resultado apto. */
async function fillPuntosDonacion() {
  const box = document.getElementById('rp-lista');
  if (!box) return;
  const puntos = await _puntosDonacion();
  box.innerHTML = puntos.map((p, i) => {
    const emoji = p.slice(0, 2);
    const texto = p.slice(2).trim();
    return `<div class="rp-item${i === 0 ? ' rp-main' : ''}">
      <span class="rp-emoji">${emoji}</span><span>${texto}</span>
    </div>`;
  }).join('');
}

function getResultIcon(outcome) {
  if (outcome === 'eligible') {
    return `<svg width="34" height="34" fill="none" viewBox="0 0 24 24">
      <path d="M5 13l4 4L19 7" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  }
  if (outcome === 'deferred') {
    return `<svg width="34" height="34" fill="none" viewBox="0 0 24 24">
      <path d="M12 8v4l3 3" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="12" cy="12" r="9" stroke="white" stroke-width="2.5"/>
    </svg>`;
  }
  /* ineligible */
  return `<svg width="34" height="34" fill="none" viewBox="0 0 24 24">
    <path d="M12 9v4M12 17h.01" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

/* ════════════════════════════════════════════════════════════
   COMPARTIR
   ════════════════════════════════════════════════════════════ */

const SHARE_URL = 'https://main.jero98772.page/sanghelios/donation';

/* Puntos de donación para el mensaje: el HGM siempre encabeza y se suman las
   campañas activas más recientes (mismas del mapa). */
async function _puntosDonacion() {
  const lineas = ['🏥 Hospital General de Medellín — banco de sangre (Cra. 48 #32-102)'];
  try {
    const rows = await fetch('/api/campanas').then(r => r.json());
    const toKey = s => String(s || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');
    const lim = Date.now() - 7 * 86400000;
    (Array.isArray(rows) ? rows : [])
      .filter(c => String(c.estado || '').toLowerCase() !== 'finalizada'
        && new Date(c.fecha + 'T00:00:00').getTime() >= lim)
      .slice(0, 3)
      .forEach(c => {
        const z = (typeof ZONAS !== 'undefined') ? ZONAS[toKey(c.comuna)] : null;
        if (z) {
          const f = new Date(c.fecha + 'T00:00:00')
            .toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short' });
          const linea = `🩸 Campaña en ${z.nombre} — ${z.lugar} · ${f}`;
          if (!lineas.includes(linea)) lineas.push(linea);   // sin repetidos
        }
      });
  } catch (_) { /* con el HGM basta */ }
  return lineas;
}

async function shareResult(outcome, encodedReason) {
  const reason = decodeURIComponent(encodedReason);
  let text;

  const puntos = await _puntosDonacion();
  const listaPuntos = puntos.map(p => `  • ${p}`).join('\n');

  if (outcome === 'eligible') {
    text =
      `✅ ¡Puedo donar sangre! (${reason})\n\n` +
      `Una donación de 10 minutos salva hasta 3 vidas. Estos son los puntos para donar:\n` +
      listaPuntos +
      `\n\n¿Me acompañas? Verifica si tú también puedes donar: ${SHARE_URL}`;
  } else {
    const motivo = outcome === 'deferred'
      ? `⏳ Por ahora no puedo donar sangre (${reason}), pero es temporal.`
      : `⚠️ Yo no puedo donar sangre (${reason}).`;
    text =
      `${motivo}\n\n` +
      `Por eso te lo pido a ti: una donación de 10 minutos salva hasta 3 vidas. Hazlo por mí 🙏 ` +
      `Estos son los puntos para donar:\n` +
      listaPuntos +
      `\n\nVerifica en 1 minuto si puedes donar: ${SHARE_URL}`;
  }

  if (navigator.share) {
    navigator.share({ title: 'Verificador de Donación · SANGHELIOS', text }).catch(() => {});
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToast('Mensaje copiado al portapapeles — pégalo donde quieras 💬');
    }).catch(() => {});
  }
}

/* ── Toast ligero ── */
function showToast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  Object.assign(t.style, {
    position: 'fixed', bottom: '28px', left: '50%', transform: 'translateX(-50%)',
    background: '#111827', color: 'white', fontSize: '13px', fontWeight: '600',
    padding: '10px 20px', borderRadius: '8px', zIndex: '9999',
    boxShadow: '0 4px 20px rgba(0,0,0,0.25)',
    fontFamily: "'Inter', sans-serif",
    opacity: '0', transition: 'opacity .2s'
  });
  document.body.appendChild(t);
  requestAnimationFrame(() => { t.style.opacity = '1'; });
  setTimeout(() => {
    t.style.opacity = '0';
    setTimeout(() => t.remove(), 300);
  }, 2400);
}