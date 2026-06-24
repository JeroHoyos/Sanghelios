/* ════════════════════════════════════════════════════════════
   SANGHELIOS · config.js
   Constantes de configuración: geografía de Medellín, canales
   de comunicación y temas de las piezas gráficas.

   PUNTO DE INTEGRACIÓN:
   - ZONAS e INGRESOS deberían venir de la base de datos / API GIS.
   ════════════════════════════════════════════════════════════ */

/* RNG con semilla (reproducible) — usado por data.js y campana.js */
function mulberry32(seed) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(20250610);

/* Hospital General de Medellín (nodo central) */
const HGM = { lng: -75.5733, lat: 6.2295 };

/* Zonas candidatas de captación (comunas + lugar concreto + perfil dominante) */
const ZONAS = {
  laureles:    { lng: -75.5917, lat: 6.2447, nombre: 'Laureles–Estadio', lugar: 'Primer Parque de Laureles',        perfil: 'universitarios', don: 64 },
  poblado:     { lng: -75.5658, lat: 6.2087, nombre: 'El Poblado',       lugar: 'Parque de El Poblado',             perfil: 'trabajadores',   don: 52 },
  candelaria:  { lng: -75.5680, lat: 6.2476, nombre: 'La Candelaria',    lugar: 'Plaza Botero — Carabobo',          perfil: 'trabajadores',   don: 71 },
  belen:       { lng: -75.6037, lat: 6.2326, nombre: 'Belén',            lugar: 'Parque Principal de Belén',        perfil: 'comunidad',      don: 43 },
  robledo:     { lng: -75.5993, lat: 6.2769, nombre: 'Robledo',          lugar: 'Campus ITM Robledo',               perfil: 'universitarios', don: 57 },
  castilla:    { lng: -75.5765, lat: 6.2762, nombre: 'Castilla',         lugar: 'Parque Juanes de la Paz',          perfil: 'comunidad',      don: 38 },
  buenosaires: { lng: -75.5510, lat: 6.2391, nombre: 'Buenos Aires',     lugar: 'Av. Ayacucho — Est. Bicentenario', perfil: 'comunidad',      don: 31 },
  manrique:    { lng: -75.5557, lat: 6.2735, nombre: 'Manrique',         lugar: 'Parque Gaitán',                    perfil: 'comunidad',      don: 27 }
};

/* Puntos de ingreso de hospitalizados (urgencias y focos de accidentalidad) */
const INGRESOS = [
  { lng: -75.5733, lat: 6.2289, n: 'Urgencias HGM',            s: 'Puerta principal de ingreso hospitalario', v: 96 },
  { lng: -75.5658, lat: 6.2638, n: 'H. San Vicente Fundación', s: 'Remisiones de alta complejidad',           v: 74 },
  { lng: -75.5762, lat: 6.2306, n: 'Glorieta Industriales',    s: 'Foco de accidentalidad vial',              v: 41 },
  { lng: -75.5662, lat: 6.2354, n: 'Av. 33 × Av. El Poblado',  s: 'Foco de accidentalidad vial',              v: 35 },
  { lng: -75.5840, lat: 6.2180, n: 'Autopista Sur — Guayabal', s: 'Foco de accidentalidad vial',              v: 47 },
  { lng: -75.5757, lat: 6.2472, n: 'Av. Regional × Calle 50',  s: 'Foco de accidentalidad vial',              v: 38 },
  { lng: -75.6030, lat: 6.2519, n: 'San Juan × Carrera 80',    s: 'Foco de accidentalidad vial',              v: 29 },
  { lng: -75.5640, lat: 6.2470, n: 'Av. Oriental — Centro',    s: 'Traslados en ambulancia al HGM',           v: 33 },
  { lng: -75.5550, lat: 6.2150, n: 'Vía Las Palmas (km 2)',    s: 'Foco de accidentalidad vial',              v: 26 }
];

/* Canales de convocatoria disponibles en el formulario de campaña */
const CHANNEL_META = {
  redes:  { label: '📱 Redes Sociales' },
  correo: { label: '✉️ Correo Institucional' },
  sms:    { label: '💬 SMS · 1 vía' }
};

/* Temas visuales de la pieza gráfica generada (rotan con "otra imagen") */
const POSTER_THEMES = [
  { bg: 'linear-gradient(160deg, #BF1212 0%, #7A0C0C 100%)', fg: '#FFFFFF', accent: '#FFD9D9' },
  { bg: 'linear-gradient(160deg, #1F2937 0%, #0B0F16 100%)', fg: '#FFFFFF', accent: '#F87171' },
  { bg: 'linear-gradient(160deg, #FFF5F5 0%, #FFDCDC 100%)', fg: '#7A0C0C', accent: '#BF1212' }
];

/* Estilo de mapa (OpenFreeMap, sin API key). Cambiar aquí para usar otro proveedor. */
const MAP_STYLE_URL = 'https://tiles.openfreemap.org/styles/liberty';
