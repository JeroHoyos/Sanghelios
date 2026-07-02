/* ════════════════════════════════════════════════════════════
   SANGHELIOS · questions.js
   Datos de las 15 preguntas del flujo de aptitud para donación.
   Cada pregunta define qué outcome produce cada respuesta.

   Outcomes posibles:
     'next'        → continuar a la siguiente pregunta
     'eligible'    → APTO PARA DONAR
     'deferred'    → DIFERIDO (temporalmente no puede donar)
     'ineligible'  → NO APTO (permanente o largo plazo)
     'sub'         → mostrar sub-pregunta condicional
   ════════════════════════════════════════════════════════════ */

const QUESTIONS = [
  {
    id: 1,
    icon: '🎂',
    text: '¿Tienes entre 18 y 65 años?',
    hint: 'La mayoría de bancos de sangre aceptan donantes en este rango de edad.',
    yes: { action: 'next' },
    no:  { action: 'ineligible', reason: 'Edad fuera del rango permitido', detail: 'Los bancos de sangre requieren que los donantes tengan <strong>entre 18 y 65 años</strong>. Fuera de este rango no está permitida la donación por razones de seguridad para el donante.' }
  },
  {
    id: 2,
    icon: '⚖️',
    text: '¿Pesas al menos 50 kg (110 lb)?',
    hint: 'El peso mínimo garantiza que la extracción sea segura para ti.',
    yes: { action: 'next' },
    no:  { action: 'ineligible', reason: 'Peso por debajo del mínimo requerido', detail: 'Se necesita un peso mínimo de <strong>50 kg</strong> para donar sangre. Esto protege tu salud y asegura que el volumen extraído sea seguro.' }
  },
  {
    id: 3,
    icon: '😊',
    text: '¿Te sientes bien de salud hoy?',
    hint: 'Considera tu estado general: energía, ánimo y bienestar físico.',
    yes: { action: 'next' },
    no:  { action: 'deferred', reason: 'Malestar general el día de la donación', detail: 'Es importante sentirse bien el día de la donación. <strong>Puedes volver otro día</strong> cuando te encuentres en óptimas condiciones.' }
  },
  {
    id: 4,
    icon: '🤒',
    text: '¿Tienes fiebre, gripe o alguna infección activa?',
    hint: 'Incluye resfriado, infección urinaria, infección cutánea, etc.',
    yes: { action: 'deferred', reason: 'Enfermedad o infección activa', detail: 'No se puede donar mientras hay una <strong>enfermedad activa</strong> como fiebre, gripe o infección. Debes esperar hasta estar completamente recuperado.' },
    no:  { action: 'next' }
  },
  {
    id: 5,
    icon: '😴',
    text: '¿Has comido bien y dormido suficiente antes de donar?',
    hint: 'Se recomienda haber dormido al menos 6-7 horas y haber comido 2-3 horas antes.',
    yes: { action: 'next' },
    no:  { action: 'deferred', reason: 'Ayuno o descanso insuficiente', detail: 'Para donar de forma segura, es necesario haber <strong>comido y descansado bien</strong>. Vuelve otro día cuando estés bien alimentado y descansado.' }
  },
  {
    id: 6,
    icon: '🩸',
    text: '¿Tienes la hemoglobina en un nivel normal?',
    hint: 'Mujeres: ≥12.5 g/dL · Hombres: ≥13.5 g/dL. Si no lo sabes, el banco de sangre lo mide al llegar.',
    yes: { action: 'next' },
    no:  { action: 'ineligible', reason: 'Nivel de hemoglobina fuera del rango normal', detail: 'Si tienes <strong>anemia u hemoglobina baja</strong>, no es posible donar en este momento. Consulta con tu médico para tratamiento y posible donación futura.' }
  },
  {
    id: 7,
    icon: '🤰',
    text: '¿Estás embarazada, has dado a luz recientemente o estás amamantando?',
    hint: 'El período de espera tras el parto o la lactancia varía según el banco de sangre.',
    yes: { action: 'deferred', reason: 'Embarazo, posparto o lactancia activa', detail: 'No se puede donar durante el <strong>embarazo, el período de posparto inmediato ni durante la lactancia materna</strong>. Espera hasta finalizar estos períodos.' },
    no:  { action: 'next' }
  },
  {
    id: 8,
    icon: '💉',
    text: '¿Has donado sangre recientemente?',
    hint: 'El período mínimo entre donaciones es generalmente 56 días (8 semanas).',
    yes: {
      action: 'sub',
      subText: '¿Ya transcurrieron al menos 8 semanas (56 días) desde tu última donación?',
      subYes: { action: 'next' },
      subNo:  { action: 'deferred', reason: 'Período de espera entre donaciones no cumplido', detail: 'Es necesario esperar <strong>al menos 8 semanas (56 días)</strong> entre donaciones de sangre completa. Esto permite que tu cuerpo recupere los glóbulos rojos.' }
    },
    no: { action: 'next' }
  },
  {
    id: 9,
    icon: '🏥',
    text: '¿Has tenido cirugía, transfusión, endoscopía o colonoscopía recientemente?',
    hint: 'Incluye cualquier procedimiento que haya requerido anestesia o instrumentos internos.',
    yes: { action: 'deferred', reason: 'Procedimiento médico o quirúrgico reciente', detail: 'Tras una <strong>cirugía, transfusión, endoscopía o colonoscopía</strong> se requiere un período de espera variable. Consulta con el banco de sangre sobre tu caso específico.' },
    no:  { action: 'next' }
  },
  {
    id: 10,
    icon: '🎨',
    text: '¿Te has hecho un tatuaje o piercing recientemente?',
    hint: 'Por lo general se exige esperar entre 4 y 12 meses, dependiendo de la normativa local.',
    yes: { action: 'deferred', reason: 'Tatuaje o piercing reciente', detail: 'Los <strong>tatuajes y piercings</strong> requieren un período de espera (habitualmente 4-12 meses) para descartar riesgo de infecciones transmisibles por sangre.' },
    no:  { action: 'next' }
  },
  {
    id: 11,
    icon: '💊',
    text: '¿Has recibido alguna vacuna recientemente?',
    hint: 'Algunas vacunas requieren un período de espera antes de donar.',
    yes: {
      action: 'sub',
      subText: '¿Ha transcurrido el período de espera recomendado para la vacuna que recibiste? (Vacunas inactivas: sin espera · Vacunas vivas: 4 semanas)',
      subYes: { action: 'next' },
      subNo:  { action: 'deferred', reason: 'Vacunación reciente con período de espera pendiente', detail: 'Algunas <strong>vacunas de virus o bacterias vivos</strong> requieren esperar hasta 4 semanas antes de donar. Verifica con el banco de sangre qué vacuna recibiste.' }
    },
    no: { action: 'next' }
  },
  {
    id: 12,
    icon: '💊',
    text: '¿Estás tomando medicamentos que sean incompatibles con la donación?',
    hint: 'Anticoagulantes, isotretinoína, finasterida o algunos antibióticos pueden ser motivo de diferimiento.',
    yes: { action: 'ineligible', reason: 'Medicación incompatible con la donación', detail: 'Ciertos <strong>medicamentos</strong> pueden descalificar temporal o permanentemente. El personal del banco de sangre evaluará tu medicación actual de forma personalizada.' },
    no:  { action: 'next' }
  },
  {
    id: 13,
    icon: '🫀',
    text: '¿Tienes alguna condición médica permanente que impida la donación?',
    hint: 'Ejemplos: VIH, Hepatitis B o C, enfermedad de Chagas, ciertos trastornos sanguíneos.',
    yes: { action: 'ineligible', reason: 'Condición médica permanente incompatible', detail: 'Algunas condiciones como <strong>VIH, Hepatitis B/C o ciertos trastornos sanguíneos</strong> impiden la donación de forma permanente para proteger a los receptores.' },
    no:  { action: 'next' }
  },
  {
    id: 14,
    icon: '⚠️',
    text: '¿Has tenido comportamientos de alto riesgo para enfermedades de transmisión sanguínea recientemente?',
    hint: 'El banco de sangre evaluará esto de forma confidencial y sin juicio.',
    yes: { action: 'deferred', reason: 'Comportamientos de riesgo para enfermedades transmisibles', detail: 'Ciertos <strong>comportamientos de riesgo</strong> requieren un período de espera para garantizar la seguridad de los receptores. El banco de sangre puede orientarte de forma confidencial.' },
    no:  { action: 'next' }
  },
  {
    id: 15,
    icon: '🩺',
    text: '¿Tienes los signos vitales dentro de rangos normales?',
    hint: 'Presión arterial: 90-160/50-100 mmHg · Pulso: 50-100 ppm · Temperatura normal. El banco de sangre los mide al llegar.',
    yes: { action: 'eligible', reason: '¡Cumples todos los requisitos!', detail: 'Has respondido favorablemente a todas las preguntas de aptitud. <strong>Estás listo para donar sangre</strong> y ayudar a salvar vidas.' },
    no:  { action: 'deferred', reason: 'Signos vitales fuera del rango normal', detail: 'Si tu <strong>presión arterial, pulso o temperatura</strong> están fuera del rango normal, el personal médico te evaluará y determinará si puedes donar en otro momento.' }
  }
];