let currentType = 'event';

function switchType(type) {
  currentType = type;
  document.querySelectorAll('.toggle-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.type === type)
  );
  document.querySelectorAll('.field-group').forEach(g =>
    g.classList.toggle('active', g.id === 'fields-' + type)
  );
  reset();
}

async function generate() {
  const btn = document.getElementById('btn-gen');

  const body = new FormData();
  body.append('poster_type', currentType);

  if (currentType === 'event') {
    const place = document.getElementById('ev-place').value.trim();
    const time  = document.getElementById('ev-time').value.trim();
    if (!place || !time) { showToast('Completa lugar y fecha antes de generar.'); return; }
    body.append('place', place);
    body.append('time',  time);
  } else {
    const name    = document.getElementById('pe-name').value.trim();
    const idNum   = document.getElementById('pe-id').value.trim();
    const place   = document.getElementById('pe-place').value.trim();
    const message = document.getElementById('pe-message').value.trim();
    if (!name || !idNum || !place) { showToast('Completa nombre, ID y lugar antes de generar.'); return; }
    body.append('name',       name);
    body.append('id_number',  idNum);
    body.append('place',      place);
    body.append('message',    message);
  }

  btn.disabled = true;
  btn.classList.add('loading');

  const res  = await fetch('/generate-image', { method: 'POST', body });
  const data = await res.json();

  btn.disabled = false;
  btn.classList.remove('loading');

  if (!res.ok || data.error) { showToast(data.error ?? 'Error al generar el afiche.'); return; }

  const img     = document.getElementById('result-img');
  const empty   = document.getElementById('empty-state');
  const badge   = document.getElementById('result-badge');
  const actions = document.getElementById('action-row');
  const dl      = document.getElementById('btn-download');

  img.src = data.url + '?t=' + Date.now();
  img.classList.add('visible');
  empty.style.display = 'none';
  badge.classList.add('visible');
  actions.classList.add('visible');
  dl.href     = data.url;
  dl.download = `afiche-${data.type}-sanghelios.png`;
}

function reset() {
  const img   = document.getElementById('result-img');
  const empty = document.getElementById('empty-state');
  img.classList.remove('visible');
  img.src = '';
  empty.style.display = '';
  document.getElementById('result-badge').classList.remove('visible');
  document.getElementById('action-row').classList.remove('visible');
}

let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
}