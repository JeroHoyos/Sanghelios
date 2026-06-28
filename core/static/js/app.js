/* ════════════════════════════════════════════════════════════
   SANGHELIOS · app.js
   Controlador raíz: navegación entre vistas y bootstrap.

   CAMBIO RESPECTO A LA VERSIÓN ANTERIOR:
   - switchView('mapa') ahora llama a onMapViewActivated()
     (definida en mapa.js) para inicializar o redimensionar
     el mapa de forma lazy (sólo cuando el usuario lo abre).
   ════════════════════════════════════════════════════════════ */

/* ── switchView: activa la pestaña y la vista correcta ── */
function switchView(name) {
  /* Ocultar todas las vistas */
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

  /* Desactivar todos los tab-btn */
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

  /* Mostrar la vista seleccionada */
  const view = document.getElementById(`view-${name}`);
  if (view) view.classList.add('active');

  /* Marcar el tab correspondiente */
  const tab = document.querySelector(`.tab-btn[data-view="${name}"]`);
  if (tab) tab.classList.add('active');

  /* ── Inicialización lazy del mapa ── */
  if (name === 'mapa') {
    setTimeout(() => {
      if (!map3d && typeof initMap3D === 'function') {
        initMap3D();
      } else if (map3d) {
        map3d.resize();
      }
    }, 50);
  }

  /* ── Refrescar gráficas del dashboard al abrir la pestaña ── */
  if (name === 'dashboard' && typeof initCharts === 'function') {
    setTimeout(initCharts, 100);
  }
}

/* ── Bootstrap ── */
document.addEventListener('DOMContentLoaded', () => {
  /* Fecha de hoy en el dashboard */
  const label = document.getElementById('today-label');
  if (label) {
    const now = new Date();
    label.textContent = now.toLocaleDateString('es-CO', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  /* Inicializar módulos que no dependen del mapa */
  if (typeof initDashboard === 'function') initDashboard();
  if (typeof initCampana   === 'function') initCampana();
});