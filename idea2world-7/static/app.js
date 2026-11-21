/* Idea2World 7.0 studio front-end. Vanilla JS, no build step. */
'use strict';

const state = {
  status: null,
  projects: [],
  project: null,
  artifacts: {},
  job: null,
  jobCursor: 0,
  screen: 'dashboard',
  file: null,
  pollTimer: null,
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[c]));

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function toast(message, bad = false) {
  const el = $('#toast');
  el.textContent = message;
  el.classList.toggle('bad', bad);
  el.classList.remove('hidden');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add('hidden'), bad ? 9000 : 4200);
}

const titles = {
  dashboard: ['Dashboard', 'Projects, versions and where each world stands.'],
  create: ['Create', 'Describe a world in your own words. The crew plans, builds and reviews it.'],
  thinking: ['AI Thinking', 'What the crew understood, decided and why.'],
  art: ['Art Direction', 'The visual language every later stage is judged against.'],
  plan: ['World Plan', 'Districts, routes, landmarks and the terrain that carries them.'],
  assets: ['Asset Library', 'What gets modelled, how it is obtained, and what is rejected.'],
  luau: ['Luau Workspace', 'The modular build system generated for this world.'],
  studio: ['Live Studio', 'Build, capture and playtest through Roblox Studio MCP.'],
  review: ['Visual Review', 'Screenshots and the 100-point visual rubric.'],
  qa: ['QA Report', 'Structural, gameplay, performance and visual gates.'],
  export: ['Export', 'Acceptance checklist, versions and the shippable archive.'],
};

const nav = {
  dashboard: renderDashboard,
  create: renderCreate,
  thinking: renderThinking,
  art: renderArt,
  plan: renderPlan,
  assets: renderAssets,
  luau: renderLuau,
  studio: renderStudio,
  review: renderReview,
  qa: renderQa,
  export: renderExport,
};

async function init() {
  wireChrome();
  await refreshStatus();
  await refreshProjects();
  show('dashboard');
}

function wireChrome() {
  $('#nav').addEventListener('click', (event) => {
    const button = event.target.closest('button[data-screen]');
    if (button) show(button.dataset.screen);
  });
  $('#project-select').addEventListener('change', async (event) => {
    await selectProject(event.target.value || null);
    renderCurrent();
  });
  $('#refresh').addEventListener('click', async () => {
    await refreshStatus();
    await refreshProjects();
    if (state.project) await selectProject(state.project.id);
    renderCurrent();
    toast('Refreshed');
  });
  $('#new-project').addEventListener('click', () => show('create'));
}

function show(screen) {
  state.screen = screen;
  $$('#nav button').forEach((b) => b.classList.toggle('active', b.dataset.screen === screen));
  $$('.screen').forEach((s) => s.classList.toggle('active', s.id === `screen-${screen}`));
  const [title, sub] = titles[screen] || ['', ''];
  $('#screen-title').textContent = title;
  $('#screen-sub').textContent = sub;
  renderCurrent();
}

async function refreshStatus() {
  try {
    state.status = await api('/api/status');
  } catch (error) {
    toast(`Server unreachable: ${error.message}`, true);
    return;
  }
  const brain = state.status.brain || {};
  const brainChip = $('#brain-chip');
  brainChip.textContent = brain.available ? `brain: ${brain.provider}:${brain.model}` : 'brain: offline planner';
  brainChip.className = `chip ${brain.available ? 'ok' : 'warn'}`;
  const studio = state.status.studio || {};
  const studioChip = $('#studio-chip');
  studioChip.textContent = studio.available ? 'studio: MCP found' : 'studio: MCP not found';
  studioChip.className = `chip ${studio.available ? 'ok' : 'warn'}`;
}

async function refreshProjects() {
  const data = await api('/api/projects');
  state.projects = data.projects || [];
  const select = $('#project-select');
  select.innerHTML = state.projects.length
    ? state.projects.map((p) => `<option value="${esc(p.id)}">${esc(p.title || p.id)}</option>`).join('')
    : '<option value="">no projects yet</option>';
  if (state.project && state.projects.some((p) => p.id === state.project.id)) {
    select.value = state.project.id;
  } else if (state.projects.length) {
    await selectProject(state.projects[0].id);
    select.value = state.projects[0].id;
  }
  updateBadge();
}

async function selectProject(id) {
  state.artifacts = {};
  state.file = null;
  if (!id) { state.project = null; updateBadge(); return; }
  state.project = await api(`/api/projects/${encodeURIComponent(id)}`);
  updateBadge();
}

function updateBadge() {
  const badge = $('#quality-badge');
  const scores = state.project?.scores || {};
  if (scores.visual === undefined || scores.visual === null) {
    badge.textContent = state.project ? 'not scored' : '—';
    badge.className = 'badge';
    return;
  }
  const value = Number(scores.visual);
  badge.textContent = `${value.toFixed(1)} / 100 · target ${scores.threshold || 85}`;
  badge.className = `badge ${value >= (scores.threshold || 85) ? 'ok' : value >= 65 ? 'warn' : 'bad'}`;
}

async function artifact(name) {
  if (!state.project) return null;
  if (name in state.artifacts) return state.artifacts[name];
  try {
    const data = await api(`/api/projects/${encodeURIComponent(state.project.id)}/artifact/${name}`);
    state.artifacts[name] = data;
    return data;
  } catch {
    state.artifacts[name] = null;
    return null;
  }
}

function renderCurrent() {
  const fn = nav[state.screen] || renderDashboard;
  const root = $(`#screen-${state.screen}`);
  fn(root).catch((error) => {
    root.innerHTML = `<div class="empty">${esc(error.message)}</div>`;
  });
}

/* ------------------------------------------------------------------ dashboard */
async function renderDashboard(root) {
  const cards = state.projects.map((p) => {
    const score = p.scores?.visual;
    const badge = score === undefined ? '<span class="pill">unscored</span>'
      : `<span class="pill ${score >= 85 ? 'ok' : score >= 65 ? 'warn' : 'bad'}">${Number(score).toFixed(1)}</span>`;
    return `<div class="card">
      <div class="row"><h3>${esc(p.title || p.id)}</h3>${badge}</div>
      <p class="small">${esc((p.idea || '').slice(0, 120))}</p>
      <div class="row small muted" style="margin-top:10px">
        <span>${esc(p.stage || 'created')} · ${esc((p.updated_at || '').slice(0, 16).replace('T', ' '))}</span>
        <span>${p.versions || 0} versions</span>
      </div>
      <div class="actions" style="margin-top:12px">
        <button data-open="${esc(p.id)}">Open</button>
        <button class="ghost" data-export="${esc(p.id)}">Export</button>
      </div>
    </div>`;
  }).join('');
  root.innerHTML = `
    <div class="grid four" style="margin-bottom:16px">
      <div class="card"><h3>Projects</h3><div class="big">${state.projects.length}</div><p>worlds in the library</p></div>
      <div class="card"><h3>Brain</h3><div class="big">${state.status?.brain?.available ? 'LLM' : 'Offline'}</div>
        <p>${state.status?.brain?.available ? esc(state.status.brain.model) : 'deterministic planner'}</p></div>
      <div class="card"><h3>Studio</h3><div class="big">${state.status?.studio?.available ? 'Ready' : 'Off'}</div>
        <p>${state.status?.studio?.available ? 'Roblox Studio MCP detected' : 'enable Studio as MCP server'}</p></div>
      <div class="card"><h3>Quality bar</h3><div class="big">${state.status?.quality_threshold || 85}</div><p>project threshold, no critical defects</p></div>
    </div>
    ${state.projects.length ? `<div class="grid three">${cards}</div>` : `
      <div class="empty">
        <p>No worlds yet.</p>
        <p class="small">Start with an idea like “a floating crystal archipelago with windy bridges and a sunken observatory”.</p>
        <button class="primary" data-screen="create">Create the first world</button>
      </div>`}`;
  $$('[data-open]', root).forEach((b) => b.addEventListener('click', async () => {
    await selectProject(b.dataset.open);
    $('#project-select').value = b.dataset.open;
    show('thinking');
  }));
  $$('[data-export]', root).forEach((b) => b.addEventListener('click', async () => {
    try {
      const archive = await api(`/api/projects/${encodeURIComponent(b.dataset.export)}/export`, { method: 'POST', body: {} });
      toast(`Exported ${archive.file_count} files (${Math.round(archive.bytes / 1024)} KB)`);
    } catch (error) { toast(error.message, true); }
  }));
  $$('[data-screen]', root).forEach((b) => b.addEventListener('click', () => show(b.dataset.screen)));
}

/* --------------------------------------------------------------------- create */
const DEFAULTS = { size: 2200, seed: 42, region_count: 7, detail_budget: 1100, terrain_cells: 100,
  visual_theme: 'auto', style: 'auto', studio_mode: 'none', repair_iterations: 2, vfx_density: 65 };

function renderCreate(root) {
  const d = { ...DEFAULTS, ...(state.status?.defaults || {}) };
  root.innerHTML = `
    <div class="split">
      <div class="card">
        <h3>The idea</h3>
        <p class="small">Free-form. No template is applied; the crew derives genre, art direction, districts and landmarks.</p>
        <textarea id="idea" placeholder="A cozy floating-island observatory where players collect star fragments, repair a broken telescope and reveal constellations above a crystal sea."></textarea>
        <div class="form" style="margin-top:14px">
          <div class="row-2">
            <div class="field"><label>World size (studs) <span id="v-size" class="mono">${d.size}</span></label>
              <input id="size" type="range" min="900" max="4000" step="100" value="${d.size}" /></div>
            <div class="field"><label>Districts <span id="v-region" class="mono">${d.region_count}</span></label>
              <input id="region_count" type="range" min="4" max="9" step="1" value="${d.region_count}" /></div>
          </div>
          <div class="row-2">
            <div class="field"><label>Detail budget <span id="v-detail" class="mono">${d.detail_budget}</span></label>
              <input id="detail_budget" type="range" min="150" max="3000" step="50" value="${d.detail_budget}" /></div>
            <div class="field"><label>Seed</label><input id="seed" type="number" value="${d.seed}" /></div>
          </div>
          <div class="row-2">
            <div class="field"><label>Art style</label>
              <select id="style">
                ${['auto', 'stylized_low_poly', 'fantasy_cinematic', 'cosmic_art', 'sci_fi_clean', 'stud', 'natural_realism']
                  .map((s) => `<option value="${s}" ${s === d.style ? 'selected' : ''}>${s.replace(/_/g, ' ')}</option>`).join('')}
              </select></div>
            <div class="field"><label>Theme accent</label>
              <select id="visual_theme">
                ${['auto', 'natural', 'cosmic', 'sci_fi', 'fantasy', 'crystal', 'steampunk']
                  .map((s) => `<option value="${s}" ${s === d.visual_theme ? 'selected' : ''}>${s.replace('_', ' ')}</option>`).join('')}
              </select></div>
          </div>
          <div class="row-2">
            <div class="field"><label>Verification</label>
              <select id="studio_mode">
                <option value="none">Plan only (no build)</option>
                <option value="simulate">Build in the Luau simulator</option>
                <option value="auto" selected>Build in Roblox Studio (fallback: none)</option>
              </select></div>
            <div class="field"><label>Repair passes</label>
              <select id="repair_iterations">
                ${[0, 1, 2, 3].map((n) => `<option value="${n}" ${n === d.repair_iterations ? 'selected' : ''}>${n}</option>`).join('')}
              </select></div>
          </div>
          <label class="small muted"><input id="mesh_generation" type="checkbox" /> Ask Studio to generate meshes for hero assets</label>
          <div class="actions"><button class="primary" id="start">Create world</button>
            <span class="small muted">Runs in the background; you can watch each stage.</span></div>
        </div>
      </div>
      <div class="card" id="job-panel">
        <h3>Generation</h3>
        <p class="small">Nothing is optimistically reported: every gate is marked met, failed or unverified.</p>
        <div id="job-body"><div class="empty">No job running.</div></div>
      </div>
    </div>`;
  const bind = (id, out, suffix = '') => {
    const input = $(`#${id}`, root);
    input.addEventListener('input', () => { $(out, root).textContent = input.value + suffix; });
  };
  bind('size', '#v-size'); bind('region_count', '#v-region'); bind('detail_budget', '#v-detail');
  $('#start', root).addEventListener('click', () => startJob(root));
  if (state.job && ['queued', 'running'].includes(state.job.status)) attachJob(state.job.id, root);
}

async function startJob(root) {
  const idea = $('#idea', root).value.trim();
  if (idea.length < 3) { toast('Write an idea first', true); return; }
  const settings = {
    size: Number($('#size', root).value),
    seed: Number($('#seed', root).value) || 42,
    region_count: Number($('#region_count', root).value),
    detail_budget: Number($('#detail_budget', root).value),
    style: $('#style', root).value,
    visual_theme: $('#visual_theme', root).value,
    studio_mode: $('#studio_mode', root).value,
    repair_iterations: Number($('#repair_iterations', root).value),
    mesh_generation: $('#mesh_generation', root).checked,
  };
  try {
    const { job } = await api('/api/create', { method: 'POST', body: { idea, settings } });
    toast('World creation started');
    attachJob(job.id, root);
  } catch (error) { toast(error.message, true); }
}

function attachJob(jobId, root) {
  const body = $('#job-body', root);
  body.innerHTML = `
    <div class="row"><span class="mono small" id="job-status">queued</span><span class="mono small" id="job-pct">0%</span></div>
    <div class="progress" style="margin:8px 0"><div id="job-bar"></div></div>
    <div class="stage-list" id="job-stages"></div>
    <div class="log" id="job-log" style="margin-top:12px"></div>`;
  let cursor = 0;
  const stages = new Map();
  const log = $('#job-log', root);
  const poll = async () => {
    try {
      const job = await api(`/api/jobs/${jobId}?cursor=${cursor}`);
      cursor = job.event_count;
      state.job = job;
      $('#job-status', root).textContent = `${job.status} · ${job.seconds}s`;
      $('#job-pct', root).textContent = `${Math.round(job.progress * 100)}%`;
      $('#job-bar', root).style.width = `${Math.round(job.progress * 100)}%`;
      for (const event of job.events || []) {
        const line = document.createElement('div');
        line.textContent = describeEvent(event);
        if (event.type.includes('fail') || event.error) line.className = 'err';
        log.appendChild(line);
        if (event.type === 'stage_start') stages.set(event.stage, 'running');
        if (event.type === 'stage_done') stages.set(event.stage, 'done');
        if (event.type === 'stage_failed') stages.set(event.stage, 'failed');
        if (event.type === 'stage_skipped') stages.set(event.stage, 'failed');
      }
      log.scrollTop = log.scrollHeight;
      $('#job-stages', root).innerHTML = [...stages.entries()]
        .map(([name, status]) => `<span class="stage ${status}">${esc(name)}</span>`).join('');
      if (['done', 'failed', 'cancelled'].includes(job.status)) {
        clearTimeout(state.pollTimer);
        if (job.status === 'done') {
          await refreshProjects();
          const id = job.result?.project?.id || job.meta?.project;
          if (id) {
            await selectProject(id);
            $('#project-select').value = id;
            updateBadge();
          }
          toast('World created. Review the plan, then build it.', false);
        } else {
          toast(job.error || 'Job failed', true);
        }
        return;
      }
      state.pollTimer = setTimeout(poll, 900);
    } catch (error) {
      toast(error.message, true);
    }
  };
  poll();
}

function describeEvent(event) {
  switch (event.type) {
    case 'pipeline_start': return '▶ pipeline started';
    case 'stage_start': return `▶ ${event.stage}${event.detail ? ` — ${event.detail}` : ''}`;
    case 'stage_done': return `✓ ${event.stage} (${event.seconds}s)`;
    case 'stage_failed': return `✗ ${event.stage}: ${event.error}`;
    case 'stage_timeout': return `✗ ${event.stage}: ${event.error}`;
    case 'stage_skipped': return `– ${event.stage} skipped (dependency failed)`;
    case 'agent': return `  ${event.agent}: ${event.detail}`;
    case 'repair_start': return `↻ repair pass ${event.iteration}: ${(event.actions || []).join(', ')}`;
    case 'repair_done': return `↻ repair pass ${event.iteration} → score ${event.score}`;
    case 'build_done': return `${event.ok ? '✓' : '✗'} studio build: ${event.instances} instances`;
    case 'capture_done': return `✓ captured ${event.captured} views, visual ${event.score}`;
    case 'playtest_done': return `${event.passed ? '✓' : '✗'} playtest`;
    case 'job_failed': return `✗ job failed: ${event.error}`;
    default: return event.type;
  }
}

/* -------------------------------------------------------------------- thinking */
async function renderThinking(root) {
  if (!state.project) return emptyState(root, 'Create a world to see the crew thinking.');
  const thinking = await artifact('thinking');
  const decisions = await artifact('decision_log');
  const design = await artifact('game_design');
  const events = (thinking?.events || []).slice(-90);
  root.innerHTML = `
    <div class="split">
      <div class="card">
        <h3>Timeline</h3>
        <p class="small">${events.length ? `${events.length} recorded steps` : 'No run recorded yet.'}</p>
        <div class="log" style="height:420px">${events.map((e) => `<div>${esc(describeEvent(e))}</div>`).join('') || '—'}</div>
      </div>
      <div class="card">
        <h3>Decisions</h3>
        <p class="small">Each choice lists alternatives and the reason it won.</p>
        <div class="list" style="margin-top:10px">
          ${(decisions?.decisions || []).slice(-10).reverse().map((d) => `
            <div class="item">
              <div class="t"><strong>${esc(d.topic)}</strong><span class="pill">${esc(d.domain)} · ${esc(d.confidence)}</span></div>
              <small>${esc(typeof d.chosen === 'string' ? d.chosen : JSON.stringify(d.chosen))}</small>
              <div class="small muted" style="margin-top:4px">${esc(d.rationale)}</div>
            </div>`).join('') || '<div class="small muted">no decisions logged</div>'}
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <h3>What the designer understood</h3>
      <div class="grid two" style="margin-top:10px">
        <dl class="kv">
          <dt>Genre</dt><dd>${esc(design?.genre || '—')}</dd>
          <dt>Audience</dt><dd>${esc(design?.target_audience || '—')}</dd>
          <dt>Session</dt><dd>${esc(design?.session_design || '—')}</dd>
          <dt>Hook</dt><dd>${esc(design?.hook || '—')}</dd>
          <dt>Brain</dt><dd>${esc((design?.brain || {}).brain || 'offline')}</dd>
        </dl>
        <div>
          <h4 style="margin-top:0">Core loop</h4>
          <ol class="small muted" style="margin:0; padding-left:18px">${(design?.core_loop || []).map((s) => `<li>${esc(s)}</li>`).join('')}</ol>
          <h4>Progression</h4>
          <div class="actions">${(design?.progression_beats || []).map((b, i) => `<span class="pill accent">${i + 1}. ${esc(b)}</span>`).join('')}</div>
        </div>
      </div>
    </div>`;
}

/* ------------------------------------------------------------------- art */
async function renderArt(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const art = await artifact('art_direction');
  if (!art) return emptyState(root, 'No art direction yet — run creation.');
  const palette = art.palette || {};
  root.innerHTML = `
    <div class="grid two">
      <div class="card">
        <h3>${esc(art.style_label)} / ${esc(art.theme)}</h3>
        <p>${esc(art.mood)}</p>
        <h4>Geometry language</h4><p class="small">${esc(art.geometry_language)}</p>
        <h4>Lighting</h4><p class="small">${esc(art.lighting_note || JSON.stringify(art.lighting))}</p>
        <h4>Signature detail</h4><p class="small">${esc(art.signature_detail || art.detail_bias || '—')}</p>
        <h4>Avoid</h4><div class="actions">${(art.avoid || []).map((a) => `<span class="pill bad">${esc(a)}</span>`).join('')}</div>
      </div>
      <div class="card">
        <h3>Palette</h3>
        <p class="small">Six named roles; builders and the critic read the same values.</p>
        <div class="swatches" style="margin-top:12px">
          ${Object.entries(palette).map(([role, hex]) => `
            <div class="swatch"><div class="c" style="background:${esc(hex)}"></div>
              <div class="n"><span>${esc(role)}</span><span class="mono">${esc(hex)}</span></div></div>`).join('')}
        </div>
        <h4>Materials</h4>
        <div class="actions">${Object.entries(art.materials || {}).map(([k, v]) => `<span class="pill">${esc(k)} → ${esc(v)}</span>`).join('')}</div>
      </div>
    </div>
    <div class="grid two" style="margin-top:14px">
      <div class="card">
        <h3>Reference principles</h3>
        <p class="small">${esc(art.references?.[0]?.label || '')}</p>
        <div class="list" style="margin-top:10px">
          ${(art.references || []).map((r) => `<div class="item"><div class="t"><strong>${esc(r.label)}</strong>
            <span class="pill">${esc(r.id)}</span></div><small>${esc(r.composition)}</small></div>`).join('')}
        </div>
      </div>
      <div class="card">
        <h3>Design principles applied</h3>
        <ol class="small muted" style="margin:10px 0 0; padding-left:18px">
          ${(art.design_principles || []).map((p) => `<li>${esc(p)}</li>`).join('')}
        </ol>
      </div>
    </div>`;
}

/* --------------------------------------------------------------------- plan */
async function renderPlan(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const world = state.project;
  const spec = await artifact('world_spec');
  if (!spec) return emptyState(root, 'No WorldSpec yet — run creation.');
  const nav = spec.navigation_report || {};
  const metrics = nav.metrics || {};
  const composition = spec.composition || {};
  root.innerHTML = `
    <div class="split">
      <div class="card" style="padding:10px">
        <img class="preview" src="/api/projects/${encodeURIComponent(world.id)}/preview.svg?t=${Date.now()}" alt="World plan" />
        <p class="small muted" style="margin:8px 4px 2px">${esc(spec.title)} · seed ${esc(spec.world?.seed)} · ${esc(spec.world?.size)} studs · water ${esc(spec.world?.water_level)}</p>
      </div>
      <div>
        <div class="grid three">
          <div class="card"><h3>Districts</h3><div class="big">${(spec.regions || []).length}</div><p>${esc(new Set((spec.regions || []).map((r) => r.kind)).size)} kinds</p></div>
          <div class="card"><h3>Landmarks</h3><div class="big">${(spec.pois || []).length}</div><p>${esc(new Set((spec.pois || []).map((p) => p.kind)).size)} kinds</p></div>
          <div class="card"><h3>Routes</h3><div class="big">${(spec.paths || []).length}</div><p>${Math.round(metrics.path_length_total || 0)} studs</p></div>
        </div>
        <div class="card" style="margin-top:14px">
          <h3>Composition</h3>
          <dl class="kv">
            <dt>Focal point</dt><dd>${esc(composition.focal_point?.name || '—')} (${esc(composition.focal_point?.kind || '—')})</dd>
            <dt>Layout</dt><dd>${esc(composition.layout || '—')}</dd>
            <dt>Loop</dt><dd>${composition.traversal_loop ? 'yes — routes form a cycle' : 'no'}</dd>
            <dt>Walkable</dt><dd>${metrics.walkable_ratio !== undefined ? `${Math.round(metrics.walkable_ratio * 100)}%` : '—'}</dd>
            <dt>Reachable</dt><dd>${metrics.reachable_pois ?? '—'}/${metrics.poi_count ?? '—'} landmarks</dd>
            <dt>Clearance</dt><dd>${metrics.min_clearance ?? '—'} studs</dd>
            <dt>Validation</dt><dd>${nav.critical_count ? `<span class="pill bad">${nav.critical_count} critical</span>` : '<span class="pill ok">passed</span>'}</dd>
          </dl>
        </div>
      </div>
    </div>
    <div class="grid two" style="margin-top:14px">
      <div class="card">
        <h3>Landmarks</h3>
        <table><thead><tr><th>Name</th><th>Kind</th><th>District</th><th>Interaction</th></tr></thead><tbody>
          ${(spec.pois || []).map((p) => `<tr><td>${esc(p.name)}</td><td>${esc(p.kind)}</td>
            <td>${esc((spec.regions || []).find((r) => r.id === p.region)?.name || p.region)}</td>
            <td>${esc(p.interaction || '—')}</td></tr>`).join('')}
        </tbody></table>
      </div>
      <div class="card">
        <h3>Districts</h3>
        <table><thead><tr><th>Name</th><th>Kind</th><th>Radius</th><th>POIs</th></tr></thead><tbody>
          ${(spec.regions || []).map((r) => `<tr><td>${esc(r.name)}</td><td>${esc(r.kind)}</td>
            <td>${Math.round(r.radius)}</td><td>${(spec.pois || []).filter((p) => p.region === r.id).length}</td></tr>`).join('')}
        </tbody></table>
      </div>
    </div>
    ${(nav.issues || []).length ? `<div class="card" style="margin-top:14px"><h3>Navigation issues</h3>
      <div class="list" style="margin-top:8px">${nav.issues.slice(0, 12).map((i) => `<div class="item">
        <div class="t"><strong>${esc(i.code)}</strong><span class="pill ${i.severity === 'critical' ? 'bad' : 'warn'}">${esc(i.severity)}</span></div>
        <small>${esc(i.message)}</small><div class="small muted">Fix: ${esc(i.fix)}</div></div>`).join('')}</div></div>` : ''}`;
}

/* ------------------------------------------------------------------- assets */
async function renderAssets(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const spec = await artifact('world_spec');
  if (!spec) return emptyState(root, 'No assets yet.');
  const manifest = spec.asset_manifest || { assets: [] };
  const validation = spec.asset_validation || {};
  const materials = spec.material_plan || {};
  const stats = validation.stats || {};
  root.innerHTML = `
    <div class="grid four">
      <div class="card"><h3>Definitions</h3><div class="big">${manifest.assets.length}</div><p>unique assets</p></div>
      <div class="card"><h3>Placements</h3><div class="big">${(spec.placements || []).length}</div><p>instances in world</p></div>
      <div class="card"><h3>Shaped parts</h3><div class="big">${Math.round((stats.shaped_share || 0) * 100)}%</div><p>non-box geometry</p></div>
      <div class="card"><h3>Mesh-ready</h3><div class="big">${stats.mesh_assets || 0}</div><p>with a Studio mesh prompt</p></div>
    </div>
    <div class="card" style="margin-top:14px">
      <div class="row"><h3>Manifest</h3>
        <span class="pill ${validation.passed ? 'ok' : 'bad'}">${validation.passed ? 'validated' : `${validation.critical_count || 0} critical`}</span></div>
      <table><thead><tr><th>Asset</th><th>Kind</th><th>Category</th><th>Method</th><th>Parts</th><th>Footprint</th><th>Triangles</th></tr></thead><tbody>
        ${manifest.assets.map((a) => `<tr><td>${esc(a.id)}</td><td>${esc(a.kind)}</td><td>${esc(a.category)}</td>
          <td><span class="pill ${a.method === 'mesh' ? 'accent' : ''}">${a.method === 'mesh' ? 'mesh (recipe fallback)' : esc(a.method)}</span></td>
          <td>${(a.recipe || []).length}</td><td>${Math.round(a.footprint || 0)}</td><td>${a.triangles || 0}</td></tr>`).join('')}
      </tbody></table>
    </div>
    <div class="grid two" style="margin-top:14px">
      <div class="card">
        <h3>Material plan</h3>
        <table><thead><tr><th>Material</th><th>Roughness</th><th>Metalness</th><th>Role</th><th>Parts</th></tr></thead><tbody>
          ${(materials.materials || []).slice(0, 14).map((m) => `<tr><td>${esc(m.name)}</td><td>${m.roughness}</td>
            <td>${m.metalness}</td><td>${esc(m.targetColor)}</td><td>${m.partCount}</td></tr>`).join('')}
        </tbody></table>
      </div>
      <div class="card">
        <h3>Validation</h3>
        ${(validation.issues || []).length ? `<div class="list" style="margin-top:8px">${validation.issues.slice(0, 10).map((i) => `
          <div class="item"><div class="t"><strong>${esc(i.code)}</strong>
            <span class="pill ${i.severity === 'critical' ? 'bad' : 'warn'}">${esc(i.severity)}</span></div>
            <small>${esc(i.message)}</small></div>`).join('')}</div>`
          : '<p class="small" style="margin-top:8px">No asset issues: every structure has a shaped silhouette beyond primitives.</p>'}
      </div>
    </div>`;
}

/* --------------------------------------------------------------------- luau */
async function renderLuau(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const listing = await api(`/api/projects/${encodeURIComponent(state.project.id)}/luau`);
  const validation = (await artifact('luau_project'))?.validation;
  const files = listing.files || [];
  if (!files.length) return emptyState(root, 'No generated Luau yet.');
  if (!state.file) state.file = files.find((f) => f.name === 'MapConfig.lua')?.name || files[0].name;
  const source = await fetch(`/api/projects/${encodeURIComponent(state.project.id)}/luau/${encodeURIComponent(state.file)}`).then((r) => r.text());
  root.innerHTML = `
    <div class="split">
      <div class="card">
        <div class="row"><h3>Modules</h3><span class="pill">${files.length} files</span></div>
        <p class="small">Data lives in MapConfig; the rest is the build system.</p>
        <div class="file-list" style="margin-top:10px">
          ${files.map((f) => `<button data-file="${esc(f.name)}" class="${f.name === state.file ? 'active' : ''}">
            <span>${esc(f.name)}</span><span class="muted small">${f.lines}</span></button>`).join('')}
        </div>
        <h4>Static validation</h4>
        ${validation ? `<p class="small">${validation.passed ? '<span class="pill ok">passed</span>' : '<span class="pill bad">failed</span>'}
          ${esc(Object.entries(validation.tools || {}).map(([k, v]) => `${k}: ${v}`).join(' · '))}</p>` : '<p class="small muted">not run</p>'}
      </div>
      <div class="card">
        <div class="row"><h3 class="mono">${esc(state.file)}</h3><span class="pill">${Math.round(source.length / 1024)} KB</span></div>
        <div class="code" id="code">${esc(source.slice(0, 40000))}</div>
      </div>
    </div>`;
  $$('[data-file]', root).forEach((b) => b.addEventListener('click', () => {
    state.file = b.dataset.file;
    renderCurrent();
  }));
}

/* ------------------------------------------------------------------- studio */
async function renderStudio(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const build = await artifact('build_report');
  const studio = state.status?.studio || {};
  root.innerHTML = `
    <div class="grid two">
      <div class="card">
        <h3>Connection</h3>
        <p class="small">${studio.available ? `StudioMCP found at <span class="mono">${esc(studio.binary)}</span>` : 'StudioMCP binary not found.'}</p>
        <p class="small muted" style="margin-top:6px">${esc(studio.hint || '')}</p>
        <div class="actions" style="margin-top:10px">
          <button id="probe">Probe Studio</button>
          <span id="probe-out" class="small muted"></span>
        </div>
        <h4>Build</h4>
        <div class="actions">
          <select id="build-mode">
            <option value="auto">Roblox Studio (auto)</option>
            <option value="simulate">Luau simulator</option>
          </select>
          <button class="primary" id="build">Build world</button>
          <button id="capture">Capture</button>
          <button id="playtest">Playtest</button>
          <button id="validate">Static validation</button>
        </div>
        <p class="small muted" style="margin-top:8px">A simulated build is labelled as such everywhere: it never counts as a Studio verification.</p>
      </div>
      <div class="card">
        <h3>Last build</h3>
        ${build ? `<dl class="kv">
          <dt>Result</dt><dd>${build.ok ? '<span class="pill ok">ok</span>' : '<span class="pill bad">failed</span>'}
            <span class="pill ${build.mode === 'simulated' ? 'warn' : 'accent'}">${esc(build.mode || 'studio')}</span></dd>
          <dt>Parts</dt><dd>${esc(build.report?.stats?.partsCreated ?? build.instances ?? '—')}</dd>
          <dt>Models</dt><dd>${esc(build.report?.stats?.modelsCreated ?? '—')}</dd>
          <dt>Landmarks</dt><dd>${esc(build.report?.stats?.pois ?? '—')}</dd>
          <dt>Placements</dt><dd>${esc(build.report?.stats?.placements ?? '—')}</dd>
          <dt>Seconds</dt><dd>${esc(build.report?.stats?.seconds ?? build.total_seconds ?? '—')}</dd>
          <dt>Validation</dt><dd>${build.validation?.passed ? '<span class="pill ok">passed</span>' : `<span class="pill bad">${esc((build.validation?.failures || []).join(', ') || 'not run')}</span>`}</dd>
        </dl>` : '<p class="small muted">No build recorded yet.</p>'}
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <h3>Console</h3>
      <div class="log" id="studio-log">${esc(build?.console || build?.error || 'No console output recorded.')}</div>
    </div>`;
  $('#probe', root).addEventListener('click', async () => {
    $('#probe-out', root).textContent = 'probing…';
    try {
      const result = await api('/api/studio/probe', { method: 'POST', body: {} });
      $('#probe-out', root).textContent = result.connected
        ? `connected · ${result.tools?.length || 0} tools`
        : `not connected: ${result.error || 'no binary'}`;
    } catch (error) { $('#probe-out', root).textContent = error.message; }
  });
  $('#build', root).addEventListener('click', () => studioJob(root, 'build', { mode: $('#build-mode', root).value }));
  $('#capture', root).addEventListener('click', () => studioJob(root, 'capture', {}));
  $('#playtest', root).addEventListener('click', () => studioJob(root, 'playtest', { seconds: 20 }));
  $('#validate', root).addEventListener('click', async () => {
    try {
      const report = await api(`/api/projects/${encodeURIComponent(state.project.id)}/validate`, { method: 'POST', body: {} });
      toast(report.luau?.passed ? 'Static validation passed' : 'Validation found critical issues', !report.luau?.passed);
      state.artifacts = {};
      renderCurrent();
    } catch (error) { toast(error.message, true); }
  });
}

async function studioJob(root, action, body) {
  try {
    const { job } = await api(`/api/projects/${encodeURIComponent(state.project.id)}/${action}`,
      { method: 'POST', body });
    const log = $('#studio-log', root);
    log.textContent = '';
    let cursor = 0;
    const poll = async () => {
      const data = await api(`/api/jobs/${job.id}?cursor=${cursor}`);
      cursor = data.event_count;
      for (const event of data.events || []) {
        const line = document.createElement('div');
        line.textContent = describeEvent(event);
        log.appendChild(line);
      }
      log.scrollTop = log.scrollHeight;
      if (['done', 'failed', 'cancelled'].includes(data.status)) {
        state.artifacts = {};
        if (data.status === 'failed') toast(data.error || 'job failed', true);
        else toast(action === 'build' ? 'Build finished' : 'Playtest finished');
        renderCurrent();
        return;
      }
      setTimeout(poll, 900);
    };
    poll();
  } catch (error) { toast(error.message, true); }
}

/* ------------------------------------------------------------------- review */
async function renderReview(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const visual = await artifact('visual_qa');
  if (!visual) return emptyState(root, 'No visual review yet — build and capture first.');
  const breakdown = visual.heuristic?.breakdown || {};
  const max = visual.heuristic?.max || {};
  const shots = state.project.screenshots || [];
  root.innerHTML = `
    <div class="grid two">
      <div class="card">
        <div class="row"><h3>Visual score</h3>
          <span class="pill ${visual.passed ? 'ok' : 'bad'}">${visual.total} / 100</span></div>
        <p class="small">${esc(visual.mode)} · threshold ${visual.threshold} · ${visual.criticalFindings?.length || 0} critical</p>
        <div style="margin-top:12px">
          ${Object.entries(breakdown).map(([key, value]) => `
            <div style="margin-bottom:8px">
              <div class="row small"><span>${esc(key.replace(/_/g, ' '))}</span><span class="mono">${value} / ${max[key] || '—'}</span></div>
              <div class="progress"><div style="width:${Math.round((value / (max[key] || 1)) * 100)}%"></div></div>
            </div>`).join('')}
        </div>
        ${visual.vision ? `<h4>Vision review</h4><p class="small">${esc(visual.vision.verdict || visual.vision.error || 'no verdict')}</p>` : ''}
      </div>
      <div class="card">
        <h3>Findings</h3>
        <div class="list" style="margin-top:8px">
          ${(visual.findings || []).slice(0, 12).map((f) => `<div class="item">
            <div class="t"><strong>${esc(f.code)}</strong>
              <span class="pill ${f.severity === 'critical' ? 'bad' : f.severity === 'major' ? 'warn' : ''}">${esc(f.severity)}</span></div>
            <small>${esc(f.message)}</small><div class="small muted">Fix: ${esc(f.fix)}</div></div>`).join('')
            || '<div class="small muted">No findings.</div>'}
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:14px">
      <div class="row"><h3>Screenshots</h3><span class="pill">${shots.length}</span></div>
      ${shots.length ? `<div class="shots" style="margin-top:10px">${shots.map((s) => `
        <figure><img src="/api/projects/${encodeURIComponent(state.project.id)}/screenshot/${encodeURIComponent(s.file)}" alt="${esc(s.view)}" />
        <figcaption>${esc(s.view || s.file)}</figcaption></figure>`).join('')}</div>`
      : `<p class="small muted" style="margin-top:8px">No screenshots. Capture runs only in a real Studio session; a simulated build cannot render.</p>`}
    </div>`;
}

/* ----------------------------------------------------------------------- qa */
async function renderQa(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const qa = await artifact('qa');
  if (!qa) return emptyState(root, 'No QA report yet.');
  const gateRow = (g) => `<div class="gate"><div class="l"><strong>${esc(g.gate.replace(/_/g, ' '))}</strong>
    <small>${esc(g.detail)}</small></div><span class="pill ${g.ok ? 'ok' : 'bad'}">${g.ok ? 'pass' : 'fail'}</span></div>`;
  const checkTable = (title, checks, detailKey = 'detail') => `
    <div class="card"><h3>${esc(title)}</h3>
      <table><thead><tr><th>Check</th><th>Result</th><th>Detail</th></tr></thead><tbody>
        ${(checks || []).map((c) => `<tr><td>${esc(c.name)}</td>
          <td><span class="pill ${c.ok ? 'ok' : 'bad'}">${c.ok ? 'pass' : 'fail'}</span></td>
          <td class="small">${esc(c[detailKey] || c.detail || '')}</td></tr>`).join('')}
      </tbody></table></div>`;
  root.innerHTML = `
    <div class="grid two">
      <div class="card">
        <div class="row"><h3>Gates</h3><span class="pill ${qa.passed ? 'ok' : 'bad'}">${qa.gate_counts?.passed}/${qa.gate_counts?.total}</span></div>
        <div class="gates" style="margin-top:10px">${(qa.gates || []).map(gateRow).join('')}</div>
        <p class="small" style="margin-top:10px"><strong>${esc(qa.verdict || '')}</strong></p>
        ${qa.unverified?.length ? `<p class="small muted" style="margin-top:10px">Unverified: ${esc(qa.unverified.join(', '))} — this run did not touch a real Studio session.</p>` : ''}
      </div>
      <div class="card">
        <h3>Performance budget</h3>
        <dl class="kv">
          ${(qa.performance?.checks || []).map((c) => `<dt>${esc(c.name)}</dt>
            <dd>${c.value}${c.unit ? ` ${esc(c.unit)}` : ''}${c.limit ? ` / ${c.limit}` : ''}
            <span class="pill ${c.ok ? 'ok' : 'bad'}">${c.ok ? 'ok' : 'over'}</span></dd>`).join('')}
          <dt>Estimated memory</dt><dd>${qa.performance?.stats?.estimated_memory_mb ?? '—'} MB</dd>
          <dt>Unique assets</dt><dd>${qa.performance?.stats?.unique_assets ?? '—'}</dd>
        </dl>
        ${(qa.performance?.warnings || []).length ? `<h4>Warnings</h4>
          <ul class="small muted" style="margin:0; padding-left:18px">${qa.performance.warnings.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>` : ''}
      </div>
    </div>
    <div class="grid two" style="margin-top:14px">
      ${checkTable('Structural', qa.structural?.checks)}
      ${checkTable('Gameplay', qa.gameplay?.checks)}
    </div>`;
}

/* ------------------------------------------------------------------- export */
async function renderExport(root) {
  if (!state.project) return emptyState(root, 'No project selected.');
  const approval = await artifact('approval');
  const project = state.project;
  root.innerHTML = `
    <div class="grid two">
      <div class="card">
        <div class="row"><h3>Acceptance</h3>
          <span class="pill ${approval?.approved ? 'ok' : 'warn'}">${approval ? `${approval.criteria_met}/${approval.criteria_total}` : '—'}</span></div>
        <p class="small">${esc(approval?.statement || 'No sign-off recorded yet.')}</p>
        <div class="checklist" style="margin-top:12px">
          ${(approval?.items || []).map((item) => `
            <div class="check ${item.ok ? 'ok' : 'bad'}">
              <div class="box">${item.ok ? '✓' : ''}</div>
              <div><strong class="small">${esc(item.label)}</strong><small>${esc(item.evidence || '')}</small></div>
            </div>`).join('') || '<div class="small muted">No checklist yet.</div>'}
        </div>
      </div>
      <div>
        <div class="card">
          <h3>Archive</h3>
          <p class="small">WorldSpec, modular Luau, one-paste installer, reports, map preview and the README.</p>
          <div class="actions" style="margin-top:10px">
            <button class="primary" id="export">Build export</button>
            <a class="btn" href="/api/projects/${encodeURIComponent(project.id)}/download"><button id="download">Download zip</button></a>
            <button id="approve">Re-run sign-off</button>
          </div>
          <div id="export-out" class="small muted" style="margin-top:8px"></div>
        </div>
        <div class="card" style="margin-top:14px">
          <h3>Versions</h3>
          <div class="list" style="margin-top:8px">
            ${(project.versions || []).slice().reverse().map((v) => `<div class="item">
              <div class="t"><strong class="mono">${esc(v.version)}</strong><span class="small muted">${esc(v.label)}</span></div>
              <div class="row" style="margin-top:6px"><small>${esc((v.created_at || '').replace('T', ' '))}</small>
                <button class="ghost small" data-restore="${esc(v.version)}">Restore</button></div>
            </div>`).join('') || '<div class="small muted">no checkpoints yet</div>'}
          </div>
        </div>
      </div>
    </div>`;
  $('#export', root).addEventListener('click', async () => {
    try {
      const archive = await api(`/api/projects/${encodeURIComponent(project.id)}/export`, { method: 'POST', body: {} });
      $('#export-out', root).textContent = `${archive.file_count} files · ${Math.round(archive.bytes / 1024)} KB · ${archive.zip}`;
      toast('Export created');
    } catch (error) { toast(error.message, true); }
  });
  $('#approve', root).addEventListener('click', async () => {
    try {
      await api(`/api/projects/${encodeURIComponent(project.id)}/approve`, { method: 'POST', body: {} });
      state.artifacts = {};
      renderCurrent();
      toast('Sign-off updated');
    } catch (error) { toast(error.message, true); }
  });
  $$('[data-restore]', root).forEach((b) => b.addEventListener('click', async () => {
    if (!confirm(`Restore ${b.dataset.restore}? Current files will be replaced.`)) return;
    try {
      await api(`/api/projects/${encodeURIComponent(project.id)}/restore`, { method: 'POST', body: { version: b.dataset.restore } });
      await selectProject(project.id);
      renderCurrent();
      toast(`Restored ${b.dataset.restore}`);
    } catch (error) { toast(error.message, true); }
  }));
}

function emptyState(root, message) {
  root.innerHTML = `<div class="empty"><p>${esc(message)}</p>
    <button class="primary" data-goto="create">Create a world</button></div>`;
  $$('[data-goto]', root).forEach((b) => b.addEventListener('click', () => show(b.dataset.goto)));
}

init();
