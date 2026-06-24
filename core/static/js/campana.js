/* ════════════════════════════════════════════════════════════
   SANGHELIOS · campana.js
   Vista Campaña: formulario + chat del Agente de Marketing.
   El "sistema multi-agente" está simulado en el cliente:
     - buildPlan()      → Agente de Optimización Territorial
     - buildMessages()  → Agente de Marketing (textos por canal)
     - renderPoster()   → "generación de imagen" (pieza HTML/CSS)
     - sendChat()       → intenciones por palabras clave

   Depende de: config.js, data.js, mapa.js (deploy), app.js (switchView)
   Expone: bootChat(), generateFromForm(), sendChat(),
           regenPoster(), deployCampaign()

   PUNTOS DE INTEGRACIÓN:
   - buildMessages(): reemplazar plantillas por una llamada a un
     LLM (POST /api/agente/convocatoria con el plan como contexto).
   - renderPoster(): reemplazar por un endpoint de generación de
     imágenes; el bubble ya soporta <img> en lugar del div .poster.
   - sendChat(): reemplazar los regex por el mismo LLM con tools.
   - deployCampaign(): persistir en backend (POST /api/campanas).
   ════════════════════════════════════════════════════════════ */

const chatScroll = document.getElementById('chat-scroll');
let chatBooted = false, lastPlan = null, posterVariant = 0;

/* Fecha por defecto: hoy + 7 (protocolo: +7d convocatoria, +7d procesamiento) */
const defDate = new Date(today.getTime() + 7 * 86400000);
document.getElementById('f-fecha').value = defDate.toISOString().slice(0, 10);

/* Controles del formulario */
document.querySelectorAll('#f-urgencia button').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('#f-urgencia button').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
  });
});
document.querySelectorAll('#f-canales .check-pill').forEach(p => {
  p.addEventListener('click', e => {
    e.preventDefault();
    const input = p.querySelector('input');
    input.checked = !input.checked;
    p.classList.toggle('checked', input.checked);
  });
});

/* ── Primitivas del chat ── */
function bubble(html, who = 'bot', wide = false) {
  const el = document.createElement('div');
  el.className = 'bub ' + who + (wide ? ' wide' : '');
  el.innerHTML = html;
  chatScroll.appendChild(el);
  chatScroll.scrollTop = chatScroll.scrollHeight;
  return el;
}
function botText(t) { return bubble(t, 'bot'); }
function userText(t) {
  const el = document.createElement('div');
  el.className = 'bub user';
  el.textContent = t;
  chatScroll.appendChild(el);
  chatScroll.scrollTop = chatScroll.scrollHeight;
}
function typingOn() {
  return bubble('<span class="tdot"></span><span class="tdot"></span><span class="tdot"></span>', 'bot typing');
}

/* Saludo inicial (app.js lo dispara la primera vez que se abre la pestaña) */
function bootChat() {
  if (chatBooted) return;
  chatBooted = true;
  setTimeout(() => botText('👋 ¡Hola! Soy el <b>Agente de Marketing</b> de Sanghelios. Configura los parámetros de la izquierda y pulsa <b>Generar Campaña con IA</b>: redactaré la convocatoria por canal y crearé la pieza gráfica de la campaña.'), 350);
  setTimeout(() => botText('Luego puedes pedirme ajustes por aquí: <i>«más juvenil»</i>, <i>«tono formal»</i>, <i>«otra imagen»</i>, <i>«cambia a El Poblado»</i> o <i>«desplegar»</i>.'), 1200);
}

function readForm() {
  const p = {
    tipo: document.getElementById('f-tipo').value,
    urgencia: document.querySelector('#f-urgencia button.active').dataset.val,
    unidades: Math.max(10, parseInt(document.getElementById('f-unidades').value) || 120),
    fecha: new Date(document.getElementById('f-fecha').value + 'T12:00:00'),
    duracion: parseInt(document.getElementById('f-duracion').value),
    zona: document.getElementById('f-zona').value,
    publico: document.getElementById('f-publico').value,
    canales: [...document.querySelectorAll('#f-canales input:checked')].map(i => i.value)
  };
  if (p.canales.length === 0) p.canales = ['redes'];
  return p;
}

function generateFromForm() {
  const p = readForm();
  userText('Genera una campaña de ' + (p.tipo === 'TODOS' ? 'todos los tipos' : p.tipo) +
    ' · ' + p.unidades + ' uds · zona ' + (p.zona === 'auto' ? 'automática (IA)' : ZONAS[p.zona].nombre) +
    ' · público: ' + p.publico);
  runPipeline(p);
}

/* Pipeline conversacional: predicción → territorio → textos → imagen */
function runPipeline(p) {
  const t1 = typingOn();
  setTimeout(() => {
    t1.remove();
    botText('📊 <b>Motor Predictivo:</b> presión actual ' + presionHoy.toFixed(1) + ' sobre el umbral τ = ' + TAU.toFixed(1) + ' → déficit proyectado en 14 días. Optimizo la campaña.');
    const t2 = typingOn();
    setTimeout(() => {
      t2.remove();
      lastPlan = buildPlan(p);
      posterVariant = 0;
      const f = lastPlan.dia.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
      botText('📍 <b>Agente Territorial:</b> recomiendo <b>' + lastPlan.zona.lugar + '</b> (' + lastPlan.zona.nombre + ') el <b>' + f + '</b>, ' + lastPlan.horario + '. Captación estimada: <b>' + lastPlan.udsTotal + ' unidades</b> (' + lastPlan.cobertura + '% de la meta).');
      const t3 = typingOn();
      setTimeout(() => {
        t3.remove();
        renderChatMessages(lastPlan);
        const t4 = typingOn();
        setTimeout(() => {
          t4.remove();
          botText('🎨 Generando pieza gráfica de la campaña…');
          setTimeout(() => {
            renderPoster(lastPlan);
            renderChatActions();
          }, 1000);
        }, 900);
      }, 1400);
    }, 1200);
  }, 900);
}

/* ── "Agente de Optimización Territorial" ── */
function buildPlan(p) {
  let zonaKey = p.zona;
  if (zonaKey === 'auto') {
    const ranking = {
      universitarios: ['laureles', 'robledo'],
      trabajadores: ['poblado', 'candelaria'],
      comunidad: ['belen', 'castilla', 'buenosaires', 'manrique']
    };
    zonaKey = ranking[p.publico][0];
  }
  const zona = ZONAS[zonaKey];
  // Día óptimo por público: mié (universitarios), jue (corporativo), sáb (comunidad)
  const targetDow = { universitarios: 3, trabajadores: 4, comunidad: 6 }[p.publico];
  const dia = new Date(p.fecha);
  while (dia.getDay() !== targetDow) dia.setDate(dia.getDate() + 1);

  const tasaBase = { universitarios: 0.34, trabajadores: 0.27, comunidad: 0.22 }[p.publico];
  const boost = p.urgencia === 'alerta' ? 1.25 : 1;
  const udsDia = Math.round((38 + rng() * 14) * tasaBase * 4 * boost);
  const udsTotal = Math.min(p.unidades * 2, udsDia * p.duracion);
  const cobertura = Math.min(100, Math.round(udsTotal / p.unidades * 100));

  return { ...p, zonaKey, zona, dia, udsDia, udsTotal, cobertura,
    horario: p.publico === 'comunidad' ? '9:00 a.m. – 4:00 p.m.' : '8:00 a.m. – 5:00 p.m.' };
}

/* ── "Agente de Marketing": textos por canal con tono según público ──
   PUNTO DE INTEGRACIÓN: reemplazar por llamada a LLM. */
function buildMessages(plan) {
  const f = plan.dia.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
  const tipoTxt = plan.tipo === 'TODOS' ? 'todos los tipos de sangre' : 'sangre tipo ' + plan.tipo;
  const urgTag = plan.urgencia === 'alerta' ? '🚨 ALERTA ROJA · ' : '';
  const msgs = {};

  if (plan.publico === 'universitarios') {
    msgs.redes = urgTag + `🩸 ¡Parce, tu sangre salva vidas!\n\nEl Hospital General de Medellín necesita ${tipoTxt} con urgencia. Este ${f} la unidad móvil estará en ${plan.zona.lugar} de ${plan.horario}.\n\n☕ Refrigerio incluido + certificado de donante\n⏱ Solo te toma 30 minutos\n\nTráete al combo 💪 #DonaSangreMedellín #Sanghelios`;
    msgs.correo = `Asunto: ${plan.urgencia === 'alerta' ? '[URGENTE] ' : ''}Jornada de donación de sangre — ${plan.zona.nombre}\n\nHola,\n\nEl Banco de Sangre del Hospital General de Medellín convoca a la comunidad universitaria a la jornada de donación que se realizará el ${f} en ${plan.zona.lugar}, de ${plan.horario}.\n\nNuestro sistema de predicción anticipa un déficit de ${tipoTxt} en los próximos 14 días, y tu donación puede marcar la diferencia para pacientes de urgencias y cirugías.\n\nRequisitos: tener entre 18 y 65 años, pesar más de 50 kg y haber dormido bien. ¡Te esperamos!\n\nEquipo Sanghelios · Hospital General de Medellín`;
    msgs.sms = `HGM: ${plan.urgencia === 'alerta' ? 'URGENTE. ' : ''}Necesitamos ${tipoTxt}. Dona este ${f} en ${plan.zona.lugar}, ${plan.horario}. 30 min que salvan 3 vidas.`;
  } else if (plan.publico === 'trabajadores') {
    msgs.redes = urgTag + `🩸 Tu pausa activa puede salvar 3 vidas.\n\nEl Hospital General de Medellín requiere ${tipoTxt}. Este ${f}, la unidad móvil de donación estará en ${plan.zona.lugar} de ${plan.horario}.\n\n✓ Proceso de 30 minutos\n✓ Certificado de donación para tu empresa\n✓ Valoración médica gratuita\n\n#DonaSangreMedellín #Sanghelios`;
    msgs.correo = `Asunto: ${plan.urgencia === 'alerta' ? '[ALERTA ROJA] ' : ''}Invitación corporativa — Jornada de donación HGM en ${plan.zona.nombre}\n\nEstimado equipo,\n\nEl Hospital General de Medellín, a través de su plataforma de inteligencia predictiva Sanghelios, ha identificado un déficit proyectado de ${tipoTxt} para las próximas dos semanas.\n\nPor ello, los invitamos a la jornada de donación del ${f} en ${plan.zona.lugar} (${plan.horario}). La donación toma 30 minutos e incluye valoración médica y refrigerio.\n\nSu participación contribuye directamente a la atención de urgencias, cirugías y tratamientos oncológicos de la ciudad.\n\nCordialmente,\nBanco de Sangre · Hospital General de Medellín`;
    msgs.sms = `HGM: ${plan.urgencia === 'alerta' ? 'ALERTA. ' : ''}Déficit de ${tipoTxt} proyectado. Jornada de donación: ${f}, ${plan.zona.lugar}, ${plan.horario}. Tu donación salva vidas.`;
  } else {
    msgs.redes = urgTag + `🩸 Medellín necesita tu ayuda.\n\nLas reservas de ${tipoTxt} del Hospital General están en nivel ${plan.urgencia === 'alerta' ? 'CRÍTICO' : 'de vigilancia'}. Este ${f} ven con tu familia a ${plan.zona.lugar}, de ${plan.horario}.\n\n❤️ Donar es seguro, rápido y gratuito\n👨‍👩‍👧 Actividades para los niños mientras donas\n☕ Refrigerio para todos los donantes\n\n#DonaSangreMedellín #Sanghelios`;
    msgs.correo = `Asunto: ${plan.urgencia === 'alerta' ? '[URGENTE] ' : ''}Jornada comunitaria de donación de sangre — ${plan.zona.nombre}\n\nApreciada comunidad de ${plan.zona.nombre},\n\nEl Hospital General de Medellín los invita a la gran jornada de donación de sangre que se realizará el ${f} en ${plan.zona.lugar}, de ${plan.horario}.\n\nNuestro sistema de monitoreo anticipa una posible escasez de ${tipoTxt} en los próximos días. Cada donación puede salvar hasta tres vidas en nuestra ciudad.\n\nDonar es un acto seguro, realizado por personal médico certificado. ¡Los esperamos en familia!\n\nBanco de Sangre · Hospital General de Medellín`;
    msgs.sms = `HGM: ${plan.urgencia === 'alerta' ? 'URGENTE. ' : ''}Jornada de donación en ${plan.zona.lugar} este ${f}, ${plan.horario}. Se necesita ${tipoTxt}. ¡Te esperamos!`;
  }
  return msgs;
}

/* ── Render en el chat: mensajes por canal ── */
function renderChatMessages(plan) {
  const msgs = buildMessages(plan);
  const bub = bubble('<div class="bub-label">✍️ Convocatorias por canal</div>', 'bot', true);
  plan.canales.forEach(ch => {
    const body = msgs[ch];
    const block = document.createElement('div');
    block.className = 'msg-block';
    block.innerHTML = `
      <div class="msg-head">
        <span class="msg-channel">${CHANNEL_META[ch].label}</span>
        <button class="msg-copy">Copiar</button>
      </div>
      <div class="msg-body"></div>`;
    block.querySelector('.msg-body').textContent = body;
    block.querySelector('.msg-copy').addEventListener('click', function() {
      navigator.clipboard.writeText(body).then(() => {
        this.textContent = '✓ Copiado';
        setTimeout(() => { this.textContent = 'Copiar'; }, 1600);
      });
    });
    bub.appendChild(block);
  });
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

/* ── "Generación de imagen": pieza gráfica (3 variantes rotativas) ──
   PUNTO DE INTEGRACIÓN: reemplazar el div .poster por un <img>
   con la URL devuelta por el servicio de generación de imágenes. */
function renderPoster(plan) {
  const th = POSTER_THEMES[posterVariant % POSTER_THEMES.length];
  const f = plan.dia.toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
  const tipo = plan.tipo === 'TODOS' ? 'TODOS LOS TIPOS' : plan.tipo;
  const tagline = {
    universitarios: '30 minutos. 3 vidas. Tráete al combo.',
    trabajadores: 'Tu pausa activa puede salvar 3 vidas.',
    comunidad: 'Medellín te necesita. Ven en familia.'
  }[plan.publico];
  const html =
    '<div class="bub-label">🖼 Pieza generada · variante ' + ((posterVariant % 3) + 1) + ' de 3</div>' +
    '<div class="poster" style="background:' + th.bg + ';color:' + th.fg + '">' +
      '<div class="poster-brand"><span style="color:' + th.accent + '">Sang</span>helios · HGM</div>' +
      '<div class="poster-mid">' +
        '<div class="poster-give">DONA</div>' +
        '<div class="poster-type' + (tipo.length > 4 ? ' small' : '') + '" style="color:' + th.accent + '">' + tipo + '</div>' +
        '<div class="poster-tag">' + tagline + '</div>' +
      '</div>' +
      '<div class="poster-foot">' +
        '<div>📍 ' + plan.zona.lugar + '</div>' +
        '<div>🗓 ' + f + ' · ' + plan.horario + '</div>' +
        '<div class="poster-hash">#DonaSangreMedellín</div>' +
      '</div>' +
    '</div>';
  bubble(html, 'bot', true);
}

function renderChatActions() {
  bubble('<div class="chat-actions">' +
    '<button class="chip-btn primary" onclick="deployCampaign()">🚀 Desplegar en el Mapa 3D</button>' +
    '<button class="chip-btn" onclick="regenPoster()">🖼 Otra imagen</button>' +
    '</div>', 'bot', true);
}

function regenPoster() {
  if (!lastPlan) return;
  posterVariant++;
  const t = typingOn();
  setTimeout(() => { t.remove(); renderPoster(lastPlan); renderChatActions(); }, 850);
}

/* ── Entrada libre del chat: intenciones por palabras clave ──
   PUNTO DE INTEGRACIÓN: reemplazar por LLM con tool-calling. */
function sendChat() {
  const inp = document.getElementById('chat-input');
  const txt = inp.value.trim();
  if (!txt) return;
  inp.value = '';
  userText(txt);
  const low = txt.toLowerCase();
  const reply = (fn, d = 850) => { const t = typingOn(); setTimeout(() => { t.remove(); fn(); }, d); };

  if (!lastPlan) {
    reply(() => botText('Primero genera una campaña con el formulario de la izquierda 😉 Luego podré ajustar el tono, la zona o la imagen.'));
    return;
  }
  // Intención: cambiar de zona
  const zonaMatch = Object.entries(ZONAS).find(([k, z]) =>
    low.includes(k) ||
    low.includes(z.nombre.toLowerCase().split('–')[0].trim()) ||
    (k === 'candelaria' && low.includes('centro')));
  if (zonaMatch) {
    reply(() => {
      lastPlan.zonaKey = zonaMatch[0];
      lastPlan.zona = zonaMatch[1];
      botText('📍 Listo, muevo la campaña a <b>' + lastPlan.zona.lugar + '</b> (' + lastPlan.zona.nombre + '). Regenero los materiales…');
      renderChatMessages(lastPlan);
      renderPoster(lastPlan);
      renderChatActions();
    });
    return;
  }
  // Intención: cambiar el tono / público
  if (/juvenil|universitari|joven|formal|corporativ|profesional|empresa|familiar|comunidad|c[aá]lido/.test(low)) {
    lastPlan.publico = /juvenil|universitari|joven/.test(low) ? 'universitarios'
      : /formal|corporativ|profesional|empresa/.test(low) ? 'trabajadores' : 'comunidad';
    const tono = { universitarios: 'juvenil universitario', trabajadores: 'formal corporativo', comunidad: 'cálido comunitario' }[lastPlan.publico];
    reply(() => {
      botText('✍️ Ajusto el tono a <b>' + tono + '</b> y regenero los materiales.');
      renderChatMessages(lastPlan);
      renderPoster(lastPlan);
      renderChatActions();
    });
    return;
  }
  // Intención: otra imagen
  if (/imagen|afiche|p[oó]ster|poster|gr[aá]fica|visual|otra/.test(low)) { regenPoster(); return; }
  // Intención: desplegar
  if (/desplegar|despliega|mapa|lanzar|lanza|publicar/.test(low)) { reply(() => deployCampaign()); return; }
  // Fallback
  reply(() => botText('Puedo cambiar la <b>zona</b> («cambia a Belén»), el <b>tono</b> («más juvenil», «formal», «familiar»), generar <b>otra imagen</b> o <b>desplegar</b> la campaña en el Mapa 3D.'));
}
document.getElementById('chat-input').addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(); });

/* ── Despliegue: la campaña se vuelve zona de recogida viva en el mapa ──
   PUNTO DE INTEGRACIÓN: persistir con POST /api/campanas. */
function deployCampaign() {
  if (!lastPlan) return;
  campaigns.push({
    id: Date.now(),
    zonaKey: lastPlan.zonaKey,
    tipo: lastPlan.tipo === 'TODOS' ? 'Todos' : lastPlan.tipo,
    meta: lastPlan.unidades,
    captadas: 0,
    dia: lastPlan.dia,
    unidad: '#' + ((campaigns.length % 2) + 1)
  });
  botText('🚀 <b>Campaña desplegada.</b> Ya aparece como zona de recogida en el Mapa 3D y su captación se irá actualizando en tiempo real.');
  switchView('mapa');
  renderCampaignMarkers();
  updateCampList();
  const z = ZONAS[lastPlan.zonaKey];
  setTimeout(() => {
    if (map3d) map3d.flyTo({ center: [z.lng, z.lat], zoom: 15.4, pitch: 60, bearing: -10, duration: 2200 });
  }, 600);
}
