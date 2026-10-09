let appState = {
  activeTab: 'tab-text',
  textOperation: 'encrypt',
  fileOperation: 'encrypt',
  caseMode: 'upper',
  currentCipher: 'vigenere_standard',
  selectedFile: null,
  ciphersMeta: {},
  theme: 'dark'
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNavigation();
  initTextStudio();
  initFileVault();
  initAuditTrail();
  loadCiphersMetadata();
});

// ============================================================================
// THEME SWITCHER (Dark & Light Mode)
// ============================================================================
function initTheme() {
  const savedTheme = localStorage.getItem('tnp_theme') || 'dark';
  setTheme(savedTheme);

  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const nextTheme = (appState.theme === 'dark') ? 'light' : 'dark';
      setTheme(nextTheme);
    });
  }
}

function setTheme(theme) {
  appState.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('tnp_theme', theme);

  const sunIcon = document.getElementById('theme-icon-sun');
  const moonIcon = document.getElementById('theme-icon-moon');
  const label = document.getElementById('theme-label-text');

  if (theme === 'light') {
    if (sunIcon) sunIcon.style.display = 'block';
    if (moonIcon) moonIcon.style.display = 'none';
    if (label) label.textContent = 'Dark Mode';
  } else {
    if (sunIcon) sunIcon.style.display = 'none';
    if (moonIcon) moonIcon.style.display = 'block';
    if (label) label.textContent = 'Light Mode';
  }
}

// ============================================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';

  let iconSvg = '<svg style="width:16px;height:16px;color:var(--accent-amber);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
  if (type === 'success') {
    iconSvg = '<svg style="width:16px;height:16px;color:var(--accent-emerald);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
  } else if (type === 'error') {
    iconSvg = '<svg style="width:16px;height:16px;color:var(--accent-crimson);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
  }

  toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ============================================================================
// NAVIGATION & TABS
// ============================================================================
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      switchTab(targetId);
    });
  });
}

function switchTab(targetId) {
  document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

  const activeBtn = document.querySelector(`.nav-tab-btn[data-tab="${targetId}"]`);
  const activePane = document.getElementById(targetId);

  if (activeBtn) activeBtn.classList.add('active');
  if (activePane) activePane.classList.add('active');

  appState.activeTab = targetId;

  if (targetId === 'tab-audit') {
    fetchAuditLogs();
  }
}

// ============================================================================
// CIPHER METADATA & DYNAMIC PARAMETER GENERATION
// ============================================================================
function loadCiphersMetadata() {
  fetch('/api/ciphers')
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        appState.ciphersMeta = data.ciphers;
        renderCipherParameters(appState.currentCipher);
      }
    })
    .catch(err => console.error("Error fetching cipher metadata:", err));
}

function renderCipherParameters(cipherId) {
  const container = document.getElementById('cipher-params-container');
  const alertText = document.getElementById('cipher-desc-text');
  if (!container) return;

  const meta = appState.ciphersMeta[cipherId];
  if (!meta) return;

  alertText.innerHTML = `<strong>${meta.name}:</strong> ${meta.description}`;

  let html = '';

  if (cipherId === 'vigenere_standard' || cipherId === 'vigenere_autokey') {
    html = `
      <div class="form-group">
        <label class="form-label" for="param-key">Kunci Alfabet (A-Z, Panjang Bebas)</label>
        <input type="text" id="param-key" class="form-control" value="TNPVAULTKEY" placeholder="Masukkan kunci huruf...">
      </div>
    `;
  } else if (cipherId === 'extended_vigenere') {
    html = `
      <div class="form-group">
        <label class="form-label" for="param-key">Kunci Byte / String Bebas (256 ASCII)</label>
        <input type="text" id="param-key" class="form-control" value="TnpSecureVault2026!#" placeholder="Masukkan kunci sembarang...">
      </div>
    `;
  } else if (cipherId === 'playfair') {
    html = `
      <div class="form-group">
        <label class="form-label" for="param-playfair-key">Kunci Matriks 5x5 ('J' digabung ke 'I')</label>
        <input type="text" id="param-playfair-key" class="form-control" value="MONARCHY" placeholder="Kata kunci Playfair...">
        <div style="margin-top: 0.75rem;">
          <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Pratinjau Matriks 5x5 Playfair:</span>
          <div id="playfair-matrix-preview" style="display: grid; grid-template-columns: repeat(5, 36px); gap: 4px; margin-top: 0.4rem;"></div>
        </div>
      </div>
    `;
  } else if (cipherId === 'affine') {
    html = `
      <div class="grid-2">
        <div class="form-group">
          <div class="form-label">
            <label for="param-affine-a">Nilai a (Slope)</label>
            <span id="badge-affine-gcd" class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem;">gcd(7, 26) = 1 (VALID)</span>
          </div>
          <input type="number" id="param-affine-a" class="form-control" value="7" placeholder="Contoh: 7">
          <small style="color: var(--text-muted); font-size: 0.72rem;">Nilai a valid: 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25</small>
        </div>
        <div class="form-group">
          <label class="form-label" for="param-affine-b">Nilai b (Shift / Pergeseran)</label>
          <input type="number" id="param-affine-b" class="form-control" value="10" placeholder="0 - 25">
        </div>
      </div>
    `;
  } else if (cipherId === 'hill') {
    html = `
      <div class="form-group">
        <div class="form-label">
          <label>Dimensi & Matriks Kunci Hill</label>
          <span id="badge-hill-det" class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem;">det mod 26 = 11 (INVERTIBLE)</span>
        </div>
        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
          <button type="button" class="btn btn-secondary btn-sm" id="btn-hill-dim-2" onclick="setHillDimension(2)">Matriks 2x2</button>
          <button type="button" class="btn btn-secondary btn-sm" id="btn-hill-dim-3" onclick="setHillDimension(3)">Matriks 3x3</button>
        </div>
        <div id="hill-matrix-inputs">
          <!-- Injected by setHillDimension -->
        </div>
      </div>
    `;
  } else if (cipherId === 'super_encryption') {
    html = `
      <div class="grid-2">
        <div class="form-group">
          <label class="form-label" for="param-super-vig">Kunci 1: Extended Vigenere (256 ASCII)</label>
          <input type="text" id="param-super-vig" class="form-control" value="TNPKEY2026" placeholder="Kunci substitusi...">
        </div>
        <div class="form-group">
          <label class="form-label" for="param-super-trans">Kunci 2: Transposisi Kolom (Metode Kolom)</label>
          <input type="text" id="param-super-trans" class="form-control" value="TACTICAL" placeholder="Kata kunci permutasi kolom...">
        </div>
      </div>
    `;
  } else if (cipherId === 'enigma') {
    html = `
      <div class="grid-2">
        <div class="form-group">
          <label class="form-label" for="param-enigma-rotors">Susunan 3 Rotor (Pilih dari I s/d V)</label>
          <input type="text" id="param-enigma-rotors" class="form-control" value="I, II, III" placeholder="Contoh: I, II, III">
        </div>
        <div class="form-group">
          <label class="form-label" for="param-enigma-reflector">Reflector UKW</label>
          <select id="param-enigma-reflector" class="form-select">
            <option value="B" selected>Reflector B (Standar Wehrmacht)</option>
            <option value="C">Reflector C</option>
          </select>
        </div>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label class="form-label" for="param-enigma-rings">Ringstellung (1-26)</label>
          <input type="text" id="param-enigma-rings" class="form-control" value="1, 1, 1" placeholder="Contoh: 1, 1, 1">
        </div>
        <div class="form-group">
          <label class="form-label" for="param-enigma-positions">Posisi Awal Rotor (Grundstellung)</label>
          <input type="text" id="param-enigma-positions" class="form-control" value="AAA" maxlength="3" style="text-transform: uppercase;">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label" for="param-enigma-plugboard">Plugboard (Steckerbrett: Pasangan Huruf Ditukar)</label>
        <input type="text" id="param-enigma-plugboard" class="form-control" value="AV BS CG DL FU HZ" placeholder="Contoh: AB CD EF">
      </div>
    `;
  }

  container.innerHTML = html;

  if (cipherId === 'playfair') {
    updatePlayfairPreview();
    const keyInput = document.getElementById('param-playfair-key');
    if (keyInput) keyInput.addEventListener('input', updatePlayfairPreview);
  } else if (cipherId === 'affine') {
    const aInput = document.getElementById('param-affine-a');
    if (aInput) aInput.addEventListener('input', validateAffineGcd);
  } else if (cipherId === 'hill') {
    setHillDimension(2);
  }
}

// ============================================================================
// PLAYFAIR MATRIX PREVIEW
// ============================================================================
function updatePlayfairPreview() {
  const input = document.getElementById('param-playfair-key');
  const preview = document.getElementById('playfair-matrix-preview');
  if (!input || !preview) return;

  const rawKey = input.value.toUpperCase().replace(/[^A-Z]/g, '').replace(/J/g, 'I');
  const alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ";
  const seen = new Set();
  const matrixLetters = [];

  for (let c of rawKey) {
    if (!seen.has(c) && alphabet.includes(c)) {
      seen.add(c);
      matrixLetters.push(c);
    }
  }
  for (let c of alphabet) {
    if (!seen.has(c)) {
      seen.add(c);
      matrixLetters.push(c);
    }
  }

  let html = '';
  matrixLetters.slice(0, 25).forEach(letter => {
    html += `<div style="width: 36px; height: 36px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-weight: 700; color: var(--accent-amber-light);">${letter}</div>`;
  });
  preview.innerHTML = html;
}

// ============================================================================
// AFFINE GCD VALIDATOR
// ============================================================================
function gcd(a, b) {
  return b === 0 ? a : gcd(b, a % b);
}

function validateAffineGcd() {
  const aInput = document.getElementById('param-affine-a');
  const badge = document.getElementById('badge-affine-gcd');
  if (!aInput || !badge) return;

  const aVal = parseInt(aInput.value, 10);
  if (isNaN(aVal)) {
    badge.textContent = "Nilai 'a' kosong";
    badge.style.color = "#f87171";
    return;
  }

  const g = gcd(Math.abs(aVal) % 26, 26);
  if (g === 1) {
    badge.textContent = `gcd(${aVal % 26}, 26) = 1 (VALID RELATIF PRIMA)`;
    badge.style.background = "rgba(16, 185, 129, 0.2)";
    badge.style.color = "#34d399";
  } else {
    badge.textContent = `gcd(${aVal % 26}, 26) = ${g} (TIDAK VALID!)`;
    badge.style.background = "rgba(239, 68, 68, 0.2)";
    badge.style.color = "#f87171";
  }
}

// ============================================================================
// HILL MATRIX DYNAMIC GRID & DETERMINANT
// ============================================================================
let currentHillDim = 2;

function setHillDimension(dim) {
  currentHillDim = dim;
  const container = document.getElementById('hill-matrix-inputs');
  if (!container) return;

  document.getElementById('btn-hill-dim-2')?.classList.toggle('active', dim === 2);
  document.getElementById('btn-hill-dim-3')?.classList.toggle('active', dim === 3);

  let html = `<div style="display: grid; grid-template-columns: repeat(${dim}, 60px); gap: 6px; margin: 0.5rem 0;">`;

  const defaults2x2 = [3, 2, 5, 7];
  const defaults3x3 = [6, 24, 1, 13, 16, 10, 20, 17, 15];
  const defaults = (dim === 2) ? defaults2x2 : defaults3x3;

  for (let i = 0; i < dim * dim; i++) {
    html += `<input type="number" class="form-control hill-cell" id="hill-cell-${i}" value="${defaults[i]}" style="padding: 0.4rem; text-align: center; font-family: var(--font-mono); font-weight: bold;">`;
  }
  html += `</div>`;
  container.innerHTML = html;

  document.querySelectorAll('.hill-cell').forEach(cell => {
    cell.addEventListener('input', checkHillDeterminant);
  });
  checkHillDeterminant();
}

function checkHillDeterminant() {
  const badge = document.getElementById('badge-hill-det');
  if (!badge) return;

  const cells = Array.from(document.querySelectorAll('.hill-cell')).map(c => parseInt(c.value, 10) || 0);
  let det = 0;

  if (currentHillDim === 2 && cells.length === 4) {
    det = (cells[0] * cells[3] - cells[1] * cells[2]);
  } else if (currentHillDim === 3 && cells.length === 9) {
    det = cells[0] * (cells[4] * cells[8] - cells[5] * cells[7])
      - cells[1] * (cells[3] * cells[8] - cells[5] * cells[6])
      + cells[2] * (cells[3] * cells[7] - cells[4] * cells[6]);
  }

  const detMod26 = ((det % 26) + 26) % 26;
  const g = gcd(detMod26, 26);

  if (g === 1 && detMod26 !== 0) {
    badge.textContent = `det mod 26 = ${detMod26} (INVERTIBLE/VALID)`;
    badge.style.background = "rgba(16, 185, 129, 0.2)";
    badge.style.color = "#34d399";
  } else {
    badge.textContent = `det mod 26 = ${detMod26}, gcd=${g} (TIDAK INVERTIBLE!)`;
    badge.style.background = "rgba(239, 68, 68, 0.2)";
    badge.style.color = "#f87171";
  }
}

// ============================================================================
// TEXT STUDIO CONTROLLER
// ============================================================================
function initTextStudio() {
  const cipherSelect = document.getElementById('cipher-select');
  cipherSelect.addEventListener('change', (e) => {
    appState.currentCipher = e.target.value;
    renderCipherParameters(appState.currentCipher);
  });

  // Operation toggle
  const opBtns = document.querySelectorAll('#text-op-toggle .toggle-btn');
  opBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      opBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.textOperation = btn.getAttribute('data-op');
    });
  });

  // Case mode toggle
  const caseBtns = document.querySelectorAll('#case-mode-toggle .toggle-btn');
  caseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      caseBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.caseMode = btn.getAttribute('data-case');
      const b64Out = document.getElementById('b64-output');
      if (b64Out && b64Out.value) {
        b64Out.value = (appState.caseMode === 'upper') ? b64Out.value.toUpperCase() : b64Out.value.toLowerCase();
      }
    });
  });

  // Input character counter
  const textInput = document.getElementById('text-input');
  textInput.addEventListener('input', () => {
    const len = textInput.value.length;
    document.getElementById('char-count-badge').textContent = `${len} karakter`;
  });

  // Action Buttons
  document.getElementById('btn-process-text').addEventListener('click', executeTextCipher);

  document.getElementById('btn-swap-text').addEventListener('click', () => {
    const outVal = document.getElementById('text-output').value;
    if (outVal) {
      document.getElementById('text-input').value = outVal;
      document.getElementById('text-output').value = '';
      document.getElementById('b64-output').value = '';
      const newOp = (appState.textOperation === 'encrypt') ? 'decrypt' : 'encrypt';
      document.querySelector(`#text-op-toggle .toggle-btn[data-op="${newOp}"]`)?.click();
      showToast("Teks ditukar. Mode operasi dibalikkan.");
    }
  });

  // Preset Plaintext Collection
  const SAMPLE_PRESETS = {
    hp_marauder: {
      title: "Harry Potter - Peta Perampok",
      text: "I SOLEMNLY SWEAR THAT I AM UP TO NO GOOD. MISCHIEF MANAGED!"
    },
    hp_chamber: {
      title: "Harry Potter - Kamar Rahasia",
      text: "THE CHAMBER OF SECRETS HAS BEEN OPENED. ENEMIES OF THE HEIR, BEWARE!"
    },
    hp_dumbledore: {
      title: "Harry Potter - Petuah Dumbledore",
      text: "HAPPINESS CAN BE FOUND EVEN IN THE DARKEST OF TIMES, IF ONE ONLY REMEMBERS TO TURN ON THE LIGHT."
    },
    hp_expecto: {
      title: "Harry Potter - Mantra Harapan",
      text: "EXPECTO PATRONUM! THE ONES THAT LOVE US NEVER REALLY LEAVE US. YOU CAN ALWAYS FIND THEM IN HERE."
    },
    crypto_kryptos: {
      title: "Prasasti CIA Kryptos (Jim Sanborn)",
      text: "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION. SLOWLY DESPERATELY DECAYING."
    },
    crypto_turing: {
      title: "Alan Turing & Bletchley Park",
      text: "WE CAN ONLY SEE A SHORT DISTANCE AHEAD, BUT WE CAN SEE PLENTY THERE THAT NEEDS TO BE DONE. MACHINES CAN THINK."
    },
    crypto_caesar: {
      title: "Julius Caesar - Pesan Sandi Romawi",
      text: "ALEA IACTA EST. VENI VIDI VICI. SEPASUKAN LEGION BERGERAK MENYEBERANGI SUNGAI RUBICON SEBELUM FAJAR MENYINGSING."
    },
    crypto_pangram: {
      title: "Pangram Lengkap A-Z",
      text: "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS."
    },
    tactical_intel: {
      title: "Operasi Sandi Garuda Biru (Taktis)",
      text: "OPERASI GARUDA BIRU: KONFIRMASI PERGERAKAN TARGET PADA KOORDINAT APEX GRID SEVEN POINT THREE. AKTIFKAN PROTOKOL ENKRIPSI PENUH."
    },
    tactical_zerotrust: {
      title: "Doktrin Siber Trust No Plaintext",
      text: "ALL CHANNELS ARE COMPROMISED. ENCRYPT EVERY PAYLOAD AT REST AND IN TRANSIT. TRUST NO PLAINTEXT UNDER ANY CIRCUMSTANCES."
    },
    tactical_space: {
      title: "Transmisi Orbit Dalam Apollo",
      text: "GROUND CONTROL TO MAJOR TOM. COMMENCING COUNTDOWN ENGINES ON. CHECK IGNITION AND MAY GOD LOVE BE WITH YOU."
    }
  };

  const presetKeys = Object.keys(SAMPLE_PRESETS);
  let currentPresetIndex = 0;

  const presetSelector = document.getElementById('select-sample-preset');
  if (presetSelector) {
    presetSelector.addEventListener('change', (e) => {
      const selectedKey = e.target.value;
      if (SAMPLE_PRESETS[selectedKey]) {
        const item = SAMPLE_PRESETS[selectedKey];
        document.getElementById('text-input').value = item.text;
        document.getElementById('char-count-badge').textContent = `${item.text.length} karakter`;
        showToast(`Preset Dimuat: ${item.title}`);
      }
    });
  }

  document.getElementById('btn-sample-text').addEventListener('click', () => {
    const nextKey = presetKeys[currentPresetIndex % presetKeys.length];
    currentPresetIndex++;
    const item = SAMPLE_PRESETS[nextKey];

    document.getElementById('text-input').value = item.text;
    document.getElementById('char-count-badge').textContent = `${item.text.length} karakter`;
    if (presetSelector) presetSelector.value = nextKey;
    showToast(`Contoh Dimuat: ${item.title}`);
  });

  document.getElementById('btn-clear-text').addEventListener('click', () => {
    document.getElementById('text-input').value = '';
    document.getElementById('text-output').value = '';
    document.getElementById('b64-output').value = '';
    document.getElementById('char-count-badge').textContent = '0 karakter';
    document.getElementById('stat-duration').textContent = '-';
    document.getElementById('stat-input-size').textContent = '-';
    document.getElementById('stat-output-size').textContent = '-';
    document.getElementById('stat-sha256').textContent = 'Belum ada eksekusi.';
    showToast("Formulir teks dibersihkan.");
  });
}

function collectTextParams() {
  const params = {
    cipher: appState.currentCipher,
    operation: appState.textOperation,
    case_mode: appState.caseMode,
    text: document.getElementById('text-input').value
  };

  const cId = appState.currentCipher;
  if (cId === 'vigenere_standard' || cId === 'vigenere_autokey' || cId === 'extended_vigenere') {
    params.key = document.getElementById('param-key')?.value || '';
  } else if (cId === 'playfair') {
    params.key = document.getElementById('param-playfair-key')?.value || '';
  } else if (cId === 'affine') {
    params.key_a = parseInt(document.getElementById('param-affine-a')?.value, 10);
    params.key_b = parseInt(document.getElementById('param-affine-b')?.value, 10);
  } else if (cId === 'hill') {
    const cells = Array.from(document.querySelectorAll('.hill-cell')).map(c => parseInt(c.value, 10) || 0);
    params.key = cells.join(', ');
  } else if (cId === 'super_encryption') {
    params.vigenere_key = document.getElementById('param-super-vig')?.value || '';
    params.trans_key = document.getElementById('param-super-trans')?.value || '';
  } else if (cId === 'enigma') {
    params.rotors = document.getElementById('param-enigma-rotors')?.value || 'I, II, III';
    params.reflector = document.getElementById('param-enigma-reflector')?.value || 'B';
    params.rings = document.getElementById('param-enigma-rings')?.value || '1, 1, 1';
    params.positions = document.getElementById('param-enigma-positions')?.value || 'AAA';
    params.plugboard = document.getElementById('param-enigma-plugboard')?.value || '';
  }

  return params;
}

function executeTextCipher() {
  const payload = collectTextParams();
  if (!payload.text.trim()) {
    showToast("Silakan masukkan pesan teks terlebih dahulu.", "error");
    return;
  }

  const btn = document.getElementById('btn-process-text');
  btn.disabled = true;
  btn.innerHTML = `<span>Memproses Kriptografi...</span>`;

  fetch('/api/process/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg><span>Eksekusi Kriptografi</span>`;

      if (!data.success) {
        showToast(`Gagal: ${data.error}`, "error");
        return;
      }

      // Populate Results
      document.getElementById('text-output').value = data.output_text;
      document.getElementById('b64-output').value = data.base64_output;

      document.getElementById('stat-duration').textContent = `${data.duration_ms} ms`;
      document.getElementById('stat-input-size').textContent = `${payload.text.length} Byte`;
      document.getElementById('stat-output-size').textContent = `${data.output_text.length} Byte`;
      document.getElementById('stat-sha256').textContent = data.output_sha256;

      // Update Inspector state
      const plainBytes = new TextEncoder().encode(payload.text);
      const cipherBytes = new TextEncoder().encode(data.output_text);
      updateLastExecutionInspector(data.hex_dump_input, data.hex_dump_output, plainBytes, cipherBytes);

      showToast(`Sukses: ${data.cipher_name} (${data.duration_ms} ms)`, "success");
    })
    .catch(err => {
      btn.disabled = false;
      btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg><span>Eksekusi Kriptografi</span>`;
      showToast(`Kesalahan: ${err.message}`, "error");
    });
}

// ============================================================================
// BINARY FILE VAULT CONTROLLER
// ============================================================================
function initFileVault() {
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input-hidden');
  const removeBtn = document.getElementById('btn-remove-file');
  const fileCipherSelect = document.getElementById('file-cipher-select');

  fileCipherSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    document.getElementById('file-key-extended').style.display = (val === 'extended_vigenere') ? 'block' : 'none';
    document.getElementById('file-key-super').style.display = (val === 'super_encryption') ? 'block' : 'none';
  });

  const fileOpBtns = document.querySelectorAll('#file-op-toggle .toggle-btn');
  fileOpBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      fileOpBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      appState.fileOperation = btn.getAttribute('data-op');

      const processBtn = document.getElementById('btn-process-file');
      if (appState.fileOperation === 'encrypt') {
        processBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg><span>Enkripsi & Kemas ke .dat</span>`;
      } else {
        processBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg><span>Dekripsi & Pulihkan Berkas</span>`;
      }
    });
  });

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFileSelection(files[0]);
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFileSelection(e.target.files[0]);
  });

  removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearSelectedFile();
  });

  document.getElementById('btn-process-file').addEventListener('click', executeFileVault);
}

function handleFileSelection(file) {
  appState.selectedFile = file;

  document.getElementById('file-name-label').textContent = file.name;
  document.getElementById('file-size-label').textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
  document.getElementById('selected-file-info').style.display = 'inline-flex';
  document.getElementById('btn-process-file').disabled = false;

  if (file.name.endsWith('.dat')) {
    document.querySelector('#file-op-toggle .toggle-btn[data-op="decrypt"]')?.click();
    showToast("Format kontainer .dat terdeteksi: Mode otomatis beralih ke Dekripsi.");
  } else {
    showToast(`Berkas terpilih: ${file.name}`);
  }
}

function clearSelectedFile() {
  appState.selectedFile = null;
  document.getElementById('file-input-hidden').value = '';
  document.getElementById('selected-file-info').style.display = 'none';
  document.getElementById('btn-process-file').disabled = true;
}

function executeFileVault() {
  if (!appState.selectedFile) {
    showToast("Pilih berkas terlebih dahulu.", "error");
    return;
  }

  const formData = new FormData();
  formData.append('file', appState.selectedFile);
  formData.append('cipher', document.getElementById('file-cipher-select').value);
  formData.append('operation', appState.fileOperation);

  const cipher = document.getElementById('file-cipher-select').value;
  if (cipher === 'extended_vigenere') {
    formData.append('key', document.getElementById('file-key-ext').value);
  } else if (cipher === 'super_encryption') {
    formData.append('vigenere_key', document.getElementById('file-key-vigenere').value);
    formData.append('trans_key', document.getElementById('file-key-trans').value);
  }

  const btn = document.getElementById('btn-process-file');
  btn.disabled = true;
  btn.innerHTML = `<span>Memproses Berkas Biner...</span>`;

  const badge = document.getElementById('file-status-badge');
  badge.textContent = "MEMPROSES ENKRIPSI/DEKRIPSI...";
  badge.style.background = "rgba(245, 158, 11, 0.2)";
  badge.style.color = "var(--accent-amber-light)";

  fetch('/api/process/file', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.innerHTML = (appState.fileOperation === 'encrypt')
        ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg><span>Enkripsi & Kemas ke .dat</span>`
        : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg><span>Dekripsi & Pulihkan Berkas</span>`;

      if (!data.success) {
        showToast(`Gagal: ${data.error}`, "error");
        badge.textContent = "GAGAL";
        badge.style.color = "#f87171";
        return;
      }

      badge.textContent = "SELESAI (SUKSES)";
      badge.style.color = "var(--accent-emerald)";

      document.getElementById('file-result-idle').style.display = 'none';
      document.getElementById('file-result-box').style.display = 'block';

      document.getElementById('res-file-name').textContent = data.download_filename;
      document.getElementById('res-file-meta').textContent = `MIME: ${data.mime_type} | Algoritma: ${data.cipher_name}`;
      document.getElementById('res-file-size').textContent = `${(data.result_size / 1024).toFixed(1)} KB`;

      document.getElementById('res-sha-in').textContent = data.input_sha256;
      document.getElementById('res-sha-out').textContent = data.output_sha256;
      document.getElementById('res-duration').textContent = `${data.duration_ms} ms`;

      const integrityBanner = document.getElementById('res-integrity-banner');
      const integrityText = document.getElementById('res-integrity-text');
      if (data.container_meta && data.container_meta.sha256) {
        if (data.output_sha256 === data.container_meta.sha256) {
          integrityBanner.className = 'alert alert-emerald';
          integrityText.textContent = `Integritas Terverifikasi: SHA-256 Cocok 100% (${data.container_meta.name})`;
        } else {
          integrityBanner.className = 'alert alert-amber';
          integrityText.textContent = `Peringatan: Hash tidak cocok. Kunci mungkin keliru!`;
        }
      } else {
        integrityBanner.className = 'alert alert-cyan';
        integrityText.textContent = `Berkas berhasil dikemas/didekripsi sesuai protokol TNP.`;
      }

      const dlBtn = document.getElementById('btn-download-file');
      dlBtn.href = data.download_url;
      document.getElementById('res-btn-filename').textContent = data.download_filename;

      document.getElementById('file-b64-preview').value = data.base64_preview;

      // Update Inspector
      updateLastExecutionInspector(data.hex_dump_input, data.hex_dump_output, null, null);
      showToast(`Operasi berkas berhasil: ${data.download_filename}`, "success");
    })
    .catch(err => {
      btn.disabled = false;
      badge.textContent = "ERROR SISTEM";
      showToast(`Kesalahan: ${err.message}`, "error");
    });
}

// ============================================================================
// AUDIT TRAIL (SQLITE) CONTROLLER
// ============================================================================
function initAuditTrail() {
  document.getElementById('btn-refresh-logs').addEventListener('click', () => {
    fetchAuditLogs();
    showToast("Riwayat audit diperbarui dari SQLite.");
  });

  document.getElementById('btn-clear-logs').addEventListener('click', () => {
    if (confirm("Bersihkan semua riwayat audit di basis data SQLite?")) {
      fetch('/api/audit-logs/clear', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
          fetchAuditLogs();
          showToast("Basis data riwayat audit berhasil dikosongkan.", "success");
        });
    }
  });
}

function fetchAuditLogs() {
  const tbody = document.getElementById('audit-table-body');
  fetch('/api/audit-logs')
    .then(res => res.json())
    .then(data => {
      if (!data.success) return;

      document.getElementById('stat-total-ops').textContent = data.stats.total_operations;
      document.getElementById('stat-total-bytes').textContent = `${(data.stats.total_bytes_processed / 1024).toFixed(1)} KB`;

      if (data.logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">Belum ada aktivitas tercatat di SQLite.</td></tr>`;
        return;
      }

      let html = '';
      data.logs.forEach(log => {
        const opClass = (log.operation === 'ENCRYPT') ? 'encrypt' : 'decrypt';
        html += `
          <tr>
            <td>#${log.id}</td>
            <td style="color: var(--text-muted); font-size: 0.72rem;">${escapeHtml(log.timestamp)}</td>
            <td><span class="badge-op ${opClass}">${escapeHtml(log.operation)}</span></td>
            <td>${formatTypeBadge(log.input_type)}</td>
            <td style="color: var(--accent-amber-light);">${escapeHtml(log.cipher)}</td>
            <td style="color: var(--text-primary); max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(log.item_name)}</td>
            <td>${log.original_size} → ${log.result_size} B</td>
            <td style="color: var(--accent-orange-light);">${log.duration_ms} ms</td>
            <td style="font-size: 0.7rem; color: var(--text-muted);" title="Input: ${log.input_sha256} | Output: ${log.output_sha256}">
              ${log.input_sha256.substring(0, 8)}... → ${log.output_sha256.substring(0, 8)}...
            </td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    })
    .catch(err => console.error("Error loading audit logs:", err));
}

function formatTypeBadge(typeStr) {
  if (!typeStr) return '<span class="badge-type badge-type-text">BERKAS</span>';
  const upper = typeStr.toUpperCase();

  if (upper.includes('DATABASE') || upper.includes('.DB') || upper.includes('SQLITE')) {
    return `<span class="badge-type badge-type-db">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  if (upper.includes('AUDIO') || upper.includes('WAV') || upper.includes('MP3')) {
    return `<span class="badge-type badge-type-audio">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  if (upper.includes('VIDEO') || upper.includes('MP4') || upper.includes('MKV')) {
    return `<span class="badge-type badge-type-video">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  if (upper.includes('GAMBAR') || upper.includes('IMAGE') || upper.includes('JPG') || upper.includes('PNG')) {
    return `<span class="badge-type badge-type-image">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  if (upper.includes('DOKUMEN') || upper.includes('DOC') || upper.includes('PDF') || upper.includes('TXT')) {
    return `<span class="badge-type badge-type-doc">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  if (upper.includes('CONTAINER') || upper.includes('VAULT') || upper.includes('.DAT')) {
    return `<span class="badge-type badge-type-container">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      <span>${escapeHtml(typeStr)}</span>
    </span>`;
  }
  return `<span class="badge-type badge-type-text">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 7 4 4 20 4 20 7"></polyline><line x1="9" y1="20" x2="15" y2="20"></line><line x1="12" y1="4" x2="12" y2="20"></line></svg>
    <span>${escapeHtml(typeStr)}</span>
  </span>`;
}

// ============================================================================
// UTILITIES
// ============================================================================
function copyToClipboard(elementId) {
  const el = document.getElementById(elementId);
  const text = el ? (el.value !== undefined ? el.value : (el.innerText || el.textContent)) : '';
  if (!text || text.trim() === '') {
    showToast("Tidak ada teks untuk disalin.", "error");
    return;
  }

  navigator.clipboard.writeText(text).then(() => {
    showToast("Berhasil disalin ke papan klip (clipboard)!", "success");
  }).catch(() => {
    if (el && el.select) el.select();
    document.execCommand('copy');
    showToast("Berhasil disalin ke clipboard!", "success");
  });
}
