import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add view-tabs CSS
css_tabs = '''
    /* ------------------------------------------------------------------ */
    /* View Navigation                                                    */
    /* ------------------------------------------------------------------ */
    .view-tabs {
      display: flex; gap: 8px; justify-content: center; margin-bottom: 24px;
      animation: fadeUp .6s ease-out;
    }
    .view-tab {
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 24px;
      color: var(--text-dim);
      font-size: 14px; font-weight: 600; font-family: var(--font);
      cursor: pointer; transition: all .2s;
    }
    .view-tab:hover { color: var(--text); background: rgba(255,255,255,0.08); }
    .view-tab.active {
      background: var(--gold-dim); border-color: var(--border-accent); color: var(--gold);
    }
    
    .view-container { display: none; }
    .view-container.active { display: block; animation: fadeUp .4s ease-out; }

    .search-row {
      margin-bottom: 16px;
    }
    .search-row input {
      width: 100%;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 12px 16px;
      color: var(--text);
      font-size: 14px;
      font-family: var(--font);
      outline: none;
      transition: border-color .2s;
    }
    .search-row input:focus { border-color: var(--border-accent); }

    .ref-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 13px;
    }
    .ref-table th, .ref-table td {
      text-align: left; padding: 12px;
      border-bottom: 1px solid var(--border);
    }
    .ref-table th { color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.1em; }
    .ref-table td { color: #c8d6e8; }
    .ref-table tr:hover { background: rgba(255,255,255,0.02); }
    .ball-name-cell { color: var(--gold); font-weight: 600; }
'''
html = html.replace('/* ------------------------------------------------------------------ */\n    /* Layout                                                             */', css_tabs + '\n    /* ------------------------------------------------------------------ */\n    /* Layout                                                             */')

# Replace layout
layout_start = html.find('<!-- Input Panel -->')
layout_end = html.find('<!-- Datalist for autocomplete -->')
if layout_start != -1 and layout_end != -1:
    new_layout = '''<!-- View Navigation -->
    <div class="view-tabs">
      <button class="view-tab active" onclick="switchView('analyser', this)">Ball Analyser</button>
      <button class="view-tab" onclick="switchView('reference', this)">Ball Reference</button>
    </div>

    <!-- VIEW: Analyser -->
    <div id="view-analyser" class="view-container active">
      <!-- Input Panel -->
      <div class="panel panel--delay1">
        <!-- Current Balls -->
        <div class="section-label">
          <span class="section-label__icon">🎱</span>
          <span class="section-label__text">Your Current Balls</span>
          <button class="btn-clear" style="margin-left: auto;" onclick="clearBalls('current')">Clear All</button>
        </div>
        <div class="input-row">
          <input type="text" id="current-input" list="ball-datalist"
                 placeholder="Type a ball name and press Enter…"
                 onkeydown="if(event.key==='Enter'){addBall('current')}" />
          <button class="btn-add" onclick="addBall('current')">+ Add</button>
        </div>
        <div class="tags" id="current-tags">
          <span class="tags__empty">None added yet</span>
        </div>

        <div class="divider"></div>

        <!-- Level-Up Options -->
        <div class="section-label">
          <span class="section-label__icon">🎯</span>
          <span class="section-label__text">Level-Up Options Offered</span>
          <button class="btn-clear" style="margin-left: auto;" onclick="clearBalls('levelup')">Clear All</button>
        </div>
        <div class="input-row">
          <input type="text" id="levelup-input" list="ball-datalist"
                 placeholder="What balls are being offered?"
                 onkeydown="if(event.key==='Enter'){addBall('levelup')}" />
          <button class="btn-add" onclick="addBall('levelup')">+ Add</button>
        </div>
        <div class="tags" id="levelup-tags">
          <span class="tags__empty">None added yet</span>
        </div>
      </div>

      <div id="error-container"></div>

      <!-- Top Fusions Button -->
      <div style="text-align: right; margin-bottom: 16px;">
        <button class="btn-clear" onclick="toggleTopFusions()" style="font-size: 13px; padding: 8px 16px; border-color: rgba(192, 132, 252, 0.4); color: #c084fc;">🔮 View Top Fusions</button>
      </div>
      <div id="top-fusions-container" style="display: none; margin-bottom: 24px;"></div>

      <button class="cta" id="cta-btn" onclick="getAdvice()">
        ⚡&nbsp; Get Build Advice
      </button>

      <div id="advice-container"></div>
    </div>

    <!-- VIEW: Reference -->
    <div id="view-reference" class="view-container">
      <div class="panel">
        <div class="search-row">
          <input type="text" id="ref-search" placeholder="Search balls by name..." oninput="renderReferenceTable()" />
        </div>
        <div class="ref-tabs" style="margin-bottom: 16px;">
          <button class="ref-tab active" data-ref="top_evo" onclick="switchRefTab('top_evo', this)">⭐ Top Evolutions</button>
          <button class="ref-tab" data-ref="all" onclick="switchRefTab('all', this)">All Balls</button>
        </div>
        <div style="overflow-x: auto;">
          <table class="ref-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Requires</th>
                <th>Description</th>
                <th>Fuses Into</th>
              </tr>
            </thead>
            <tbody id="ref-tbody">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    '''
    html = html[:layout_start] + new_layout + html[layout_end:]

# Update JS script logic
js_add = '''
let currentRefTab = 'top_evo';
let currentSearch = '';

function switchView(viewId, btn) {
  document.querySelectorAll('.view-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.view-container').forEach(c => c.classList.remove('active'));
  document.getElementById('view-' + viewId).classList.add('active');
  if (viewId === 'reference') {
    renderReferenceTable();
  }
}

function switchRefTab(tabId, btn) {
  document.querySelectorAll('.ref-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentRefTab = tabId;
  renderReferenceTable();
}

function renderReferenceTable() {
  currentSearch = document.getElementById('ref-search').value.toLowerCase();
  let list = [];
  
  if (currentRefTab === 'top_evo') {
    list = topEvolutions.map(name => allBalls.find(b => b.name === name)).filter(Boolean);
  } else {
    list = allBalls;
  }

  if (currentSearch) {
    list = list.filter(b => b.name.toLowerCase().includes(currentSearch));
  }

  const tbody = document.getElementById('ref-tbody');
  tbody.innerHTML = list.map(b => {
    let requires = b.combo ? `<div>${escapeHtml(b.combo)}</div>` : '-';
    if (b.base_combo && b.base_combo !== (b.combo || '').toLowerCase() && !(b.combo || '').includes(' OR ')) {
        requires += `<div style="color: var(--text-dim); font-size: 11px; margin-top: 4px;">Steps: ${escapeHtml(b.base_combo)}</div>`;
    }
    let fusesInto = '-';
    if (b.fuses_into && b.fuses_into.length > 0) {
      fusesInto = b.fuses_into.map(f => `<div style="color: var(--cyan); margin-bottom: 2px;">${escapeHtml(f)}</div>`).join('');
    }
    
    return `
      <tr>
        <td class="ball-name-cell">${escapeHtml(b.name)}</td>
        <td>${requires}</td>
        <td style="max-width: 300px; line-height: 1.4;">${escapeHtml(b.desc)}</td>
        <td>${fusesInto}</td>
      </tr>
    `;
  }).join('');
}

function toggleTopFusions() {
  const container = document.getElementById('top-fusions-container');
  if (container.style.display === 'none') {
    container.style.display = 'block';
    
    let fHtml = '<div class="panel" style="border-color: rgba(192, 132, 252, 0.2);"><div class="top-picks-heading top-picks-heading--fusion" style="margin-bottom: 12px;">🔮 Top Fusions</div><div style="display:flex;flex-direction:column;gap:6px;">';
    topFusions.forEach(f => {
      fHtml += `
        <div class="fusion-card">
          <div class="fusion-card__names">
            <span class="fusion-card__ball">${escapeHtml(f.balls[0])}</span>
            <span class="fusion-card__x">×</span>
            <span class="fusion-card__ball">${escapeHtml(f.balls[1])}</span>
          </div>
          ${f.base_combo ? `<div class="fusion-card__tip" style="color: var(--text-dim); margin-top: 4px;">Steps: ${escapeHtml(f.base_combo)}</div>` : ''}
        </div>
      `;
    });
    fHtml += '</div></div>';
    container.innerHTML = fHtml;
  } else {
    container.style.display = 'none';
  }
}
'''

# We need to replace the old renderReference and filterRef functions
old_ref_start = html.find('// ========================================================================\n// Reference Panel')
old_ref_end = html.find('// ========================================================================\n// Error Handling')
if old_ref_start != -1 and old_ref_end != -1:
    html = html[:old_ref_start] + '// ========================================================================\n// Reference Panel\n// ========================================================================\n' + js_add + '\n' + html[old_ref_end:]

# We also need to remove renderReference('top'); from init() and leave it to switchView / or don't render until tab is opened
init_ref = html.find("renderReference('top');")
if init_ref != -1:
    html = html.replace("renderReference('top');", "// Ref rendered on tab switch")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated index.html layout and JS.')
