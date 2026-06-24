/* ════════════════════════════════════════════════════════════
   SANGHELIOS · app.js
   Orquestador de la SPA: navegación por pestañas (vistas) e
   inicialización perezosa de cada módulo, + canvas decorativo
   del hero. Se carga de último.

   Vistas: inicio · dashboard · mapa · publicidad (Campaña) · about
   ════════════════════════════════════════════════════════════ */

let chartsReady = false, mapReady = false;

function switchView(v) {
  document.querySelectorAll('.view').forEach(el => el.classList.toggle('active', el.id === 'view-' + v));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.view === v));
  window.scrollTo({ top: 0 });
  document.body.style.overflow = (v === 'mapa' || v === 'publicidad') ? 'hidden' : '';

  // Inicialización perezosa: las gráficas y el mapa 3D necesitan
  // que su contenedor sea visible para medirse correctamente.
  if (v === 'dashboard' && !chartsReady) { chartsReady = true; initCharts(); }
  if (v === 'mapa') {
    if (!mapReady) { mapReady = true; initMap3D(); }
    else if (map3d) map3d.resize();
  }
  if (v === 'publicidad') bootChat();
  if (v === 'inicio' && previewMap) previewMap.resize();
}

/* ── Canvas decorativo del hero (red de partículas) ── */
(function() {
  const canvas = document.getElementById('hero-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, pts;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  function init() {
    pts = Array.from({ length: 70 }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
      r: Math.random() * 1.8 + 0.8
    }));
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < 110) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(31,41,55,${.55 * (1 - d / 110)})`;
          ctx.lineWidth = .45;
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.stroke();
        }
      }
    }
    pts.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(31,41,55,0.65)';
      ctx.fill();
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });
    requestAnimationFrame(draw);
  }
  resize(); init(); draw();
  window.addEventListener('resize', () => { resize(); init(); });
})();
