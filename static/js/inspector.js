let lastExecutionState = {
  plainBytes: null,
  cipherBytes: null,
  plainHexDump: [],
  cipherHexDump: []
};

document.addEventListener('DOMContentLoaded', () => {
  initInteractiveInspector();
});

function initInteractiveInspector() {
  const textInput = document.getElementById('inspector-interactive-text');
  const b64Input = document.getElementById('inspector-interactive-b64');
  const cipherSelect = document.getElementById('inspector-cipher-select');
  const keyInput = document.getElementById('inspector-key-input');
  const loadLastBtn = document.getElementById('btn-inspector-load-last');
  const clearBtn = document.getElementById('btn-inspector-clear');

  if (textInput) {
    textInput.addEventListener('input', performLiveCipherInspection);
  }

  if (b64Input) {
    b64Input.addEventListener('input', () => {
      const b64Str = b64Input.value.trim().replace(/\s+/g, '');
      try {
        const rawBytes = base64ToBytes(b64Str);
        const decodedText = new TextDecoder('utf-8', { fatal: false }).decode(rawBytes);
        if (textInput) {
          textInput.value = decodedText;
        }
        performLiveCipherInspection();
      } catch (e) {
        // Still typing base64 or invalid padding, do nothing yet
      }
    });
  }

  if (cipherSelect) {
    cipherSelect.addEventListener('change', performLiveCipherInspection);
  }

  if (keyInput) {
    keyInput.addEventListener('input', performLiveCipherInspection);
  }

  if (loadLastBtn) {
    loadLastBtn.addEventListener('click', () => {
      if (lastExecutionState.plainHexDump.length === 0 && lastExecutionState.cipherHexDump.length === 0) {
        showToast("Belum ada data eksekusi kriptografi terakhir. Jalankan enkripsi di Text Studio atau File Vault terlebih dahulu!");
        return;
      }

      renderInteractiveHexDump('inspector-plain-hex', lastExecutionState.plainHexDump);
      renderInteractiveHexDump('inspector-cipher-hex', lastExecutionState.cipherHexDump);

      if (lastExecutionState.plainBytes && textInput) {
        textInput.value = new TextDecoder('utf-8', { fatal: false }).decode(lastExecutionState.plainBytes);
        const badge = document.getElementById('inspector-text-bytes-badge');
        if (badge) badge.textContent = `${lastExecutionState.plainBytes.length} Bytes`;
      }
      if (lastExecutionState.cipherBytes && b64Input) {
        b64Input.value = bytesToBase64(lastExecutionState.cipherBytes);
      }

      showToast("Data eksekusi kriptografi terakhir berhasil dimuat ke Inspector!");
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (textInput) textInput.value = '';
      if (b64Input) b64Input.value = '';
      const badge = document.getElementById('inspector-text-bytes-badge');
      if (badge) badge.textContent = `0 Bytes`;

      document.getElementById('inspector-plain-hex').innerHTML =
        '<div style="color: var(--text-muted); text-align: center; padding: 2.5rem 0;">Ketik teks di atas atau muat data eksekusi untuk melihat dump.</div>';
      document.getElementById('inspector-cipher-hex').innerHTML =
        '<div style="color: var(--text-muted); text-align: center; padding: 2.5rem 0;">Hasil cipherteks terenkripsi akan diinspeksi di sini.</div>';
      showToast("Inspector dibersihkan.");
    });
  }

  // Stream View Filter Toggle (Semua / Plainteks / Cipherteks)
  const filterBtns = document.querySelectorAll('#inspector-stream-filter .toggle-btn');
  const panelPlain = document.getElementById('panel-plain-hex');
  const panelCipher = document.getElementById('panel-cipher-hex');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.getAttribute('data-filter');

      if (mode === 'both') {
        if (panelPlain) panelPlain.style.display = 'block';
        if (panelCipher) panelCipher.style.display = 'block';
      } else if (mode === 'plain') {
        if (panelPlain) panelPlain.style.display = 'block';
        if (panelCipher) panelCipher.style.display = 'none';
      } else if (mode === 'cipher') {
        if (panelPlain) panelPlain.style.display = 'none';
        if (panelCipher) panelCipher.style.display = 'block';
      }
    });
  });
}

function updateLastExecutionInspector(plainDump, cipherDump, plainBytes, cipherBytes) {
  lastExecutionState.plainHexDump = plainDump || [];
  lastExecutionState.cipherHexDump = cipherDump || [];
  lastExecutionState.plainBytes = plainBytes || null;
  lastExecutionState.cipherBytes = cipherBytes || null;

  renderInteractiveHexDump('inspector-plain-hex', lastExecutionState.plainHexDump);
  renderInteractiveHexDump('inspector-cipher-hex', lastExecutionState.cipherHexDump);
}

function generateHexDumpFromBytes(bytes, maxBytes = 256) {
  const lines = [];
  const sample = bytes.slice(0, maxBytes);
  for (let i = 0; i < sample.length; i += 16) {
    const chunk = sample.slice(i, i + 16);
    const offset = i.toString(16).padStart(8, '0');
    const hexParts = [];
    for (let b of chunk) {
      hexParts.push(b.toString(16).padStart(2, '0'));
    }
    let hexStr = hexParts.join(' ');
    let asciiStr = '';
    for (let b of chunk) {
      asciiStr += (b >= 32 && b <= 126) ? String.fromCharCode(b) : '.';
    }
    lines.push({ offset: offset, hex: hexStr, ascii: asciiStr, rawChunk: Array.from(chunk) });
  }
  return lines;
}

function renderInteractiveHexDump(targetElementId, hexLines) {
  const container = document.getElementById(targetElementId);
  if (!container) return;

  if (!hexLines || hexLines.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2.5rem 0;">Data stream kosong atau belum dieksekusi.</div>';
    return;
  }

  let html = '';
  hexLines.forEach((line, lineIdx) => {
    const hexBytesArray = line.hex.trim().split(/\s+/).filter(Boolean);
    let interactiveHex = '';

    // Render exactly 16 byte slots for bulletproof alignment
    for (let byteIdx = 0; byteIdx < 16; byteIdx++) {
      if (byteIdx < hexBytesArray.length) {
        const bStr = hexBytesArray[byteIdx];
        const decVal = parseInt(bStr, 16);
        const asciiChar = (decVal >= 32 && decVal <= 126) ? String.fromCharCode(decVal) : '.';
        interactiveHex += `<span class="hex-byte-item" id="${targetElementId}-b-${lineIdx}-${byteIdx}" data-line="${lineIdx}" data-byte="${byteIdx}" title="Offset: +0x${byteIdx.toString(16).toUpperCase()} | Hex: 0x${bStr.toUpperCase()} | Dec: ${decVal} | ASCII: ${asciiChar}" onclick="inspectByte('${targetElementId}', ${lineIdx}, ${byteIdx}, '${bStr}')">${bStr}</span>`;
      } else {
        interactiveHex += `<span class="hex-byte-item hex-byte-empty">&nbsp;&nbsp;</span>`;
      }
      if (byteIdx === 7) {
        interactiveHex += `<span class="hex-byte-gap"></span>`;
      }
    }

    // Render corresponding ASCII chars
    let interactiveAscii = '';
    const asciiChars = line.ascii.split('');
    asciiChars.forEach((ch, charIdx) => {
      const bStr = hexBytesArray[charIdx] || '';
      interactiveAscii += `<span class="hex-ascii-char" id="${targetElementId}-a-${lineIdx}-${charIdx}" data-line="${lineIdx}" data-byte="${charIdx}" title="Hex: 0x${bStr.toUpperCase()} | Char: '${ch}'" onclick="inspectByte('${targetElementId}', ${lineIdx}, ${charIdx}, '${bStr}')">${escapeHtml(ch)}</span>`;
    });

    html += `
      <div class="hex-line">
        <span class="hex-offset">${escapeHtml(line.offset)}</span>
        <div class="hex-bytes">${interactiveHex}</div>
        <div class="hex-ascii" id="${targetElementId}-ascii-row-${lineIdx}">${interactiveAscii}</div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function inspectByte(containerId, lineIdx, byteIdx, hexVal) {
  if (!hexVal) return;
  // Clear other active highlights in this container
  document.querySelectorAll(`#${containerId} .hex-byte-item`).forEach(b => b.classList.remove('active'));
  document.querySelectorAll(`#${containerId} .hex-ascii-char`).forEach(a => a.classList.remove('active'));

  const byteEl = document.getElementById(`${containerId}-b-${lineIdx}-${byteIdx}`);
  const asciiEl = document.getElementById(`${containerId}-a-${lineIdx}-${byteIdx}`);

  if (byteEl) byteEl.classList.add('active');
  if (asciiEl) asciiEl.classList.add('active');

  const decVal = parseInt(hexVal, 16);
  const binVal = decVal.toString(2).padStart(8, '0');
  const asciiChar = (decVal >= 32 && decVal <= 126) ? `'${String.fromCharCode(decVal)}'` : '(Non-printable)';

  showToast(`[BYTE 0x${hexVal.toUpperCase()}] Dec: ${decVal} | Bin: ${binVal} | Char: ${asciiChar}`);
}

function bytesToBase64(bytes) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

function base64ToBytes(b64) {
  const binary = window.atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

let inspectorDebounceTimer = null;

function performLiveCipherInspection() {
  const textInput = document.getElementById('inspector-interactive-text');
  const b64Input = document.getElementById('inspector-interactive-b64');
  const cipherSelect = document.getElementById('inspector-cipher-select');
  const keyInput = document.getElementById('inspector-key-input');
  const syncIndicator = document.getElementById('inspector-sync-indicator');

  const text = textInput ? textInput.value : '';
  if (!text || text.length === 0) {
    renderInteractiveHexDump('inspector-plain-hex', []);
    renderInteractiveHexDump('inspector-cipher-hex', []);
    if (b64Input && document.activeElement !== b64Input) {
      b64Input.value = '';
    }
    const badge = document.getElementById('inspector-text-bytes-badge');
    if (badge) badge.textContent = `0 Bytes`;
    return;
  }

  const cipherId = cipherSelect ? cipherSelect.value : 'extended_vigenere';
  const key = keyInput ? (keyInput.value || 'SENTINEL') : 'SENTINEL';
  const utf8Bytes = new TextEncoder().encode(text);

  // Update live byte count badge
  const badge = document.getElementById('inspector-text-bytes-badge');
  if (badge) badge.textContent = `${utf8Bytes.length} Bytes`;

  // Update base64 input if user is not actively typing in base64
  if (b64Input && document.activeElement !== b64Input) {
    b64Input.value = bytesToBase64(utf8Bytes);
  }

  // 1. INSTANT Plaintext Hex Dump render (0ms)
  renderInteractiveHexDump('inspector-plain-hex', generateHexDumpFromBytes(utf8Bytes));

  // 2. INSTANT Client-Side Cipher Hex Dump calculation (0ms, 60fps responsive!)
  // Computes instant Extended Vigenere byte transformation so output stream is NEVER blank or lagging
  const keyBytes = new TextEncoder().encode(key || 'K');
  const instantCipherBytes = new Uint8Array(utf8Bytes.length);
  for (let i = 0; i < utf8Bytes.length; i++) {
    instantCipherBytes[i] = (utf8Bytes[i] + keyBytes[i % keyBytes.length]) % 256;
  }
  renderInteractiveHexDump('inspector-cipher-hex', generateHexDumpFromBytes(instantCipherBytes));

  // 3. Debounced backend sync (60ms) for 100% cryptographic parity across all algorithms
  if (syncIndicator) {
    syncIndicator.innerHTML = '<span style="width: 7px; height: 7px; background: #f59e0b; border-radius: 50%; box-shadow: 0 0 8px #f59e0b;"></span><span>MENYELARASKAN...</span>';
  }

  clearTimeout(inspectorDebounceTimer);
  inspectorDebounceTimer = setTimeout(() => {
    fetch('/api/process/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cipher: cipherId,
        operation: 'encrypt',
        case_mode: 'upper',
        text: text,
        key: key,
        key_a: 7,
        key_b: 10,
        vigenere_key: key,
        trans_key: 'TACTICAL'
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (data.hex_dump_output && data.hex_dump_output.length > 0) {
            renderInteractiveHexDump('inspector-cipher-hex', data.hex_dump_output);
          }
          if (data.hex_dump_input && data.hex_dump_input.length > 0) {
            renderInteractiveHexDump('inspector-plain-hex', data.hex_dump_input);
          }
        }
        if (syncIndicator) {
          syncIndicator.innerHTML = '<span style="width: 7px; height: 7px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span><span>LIVE SYNC AKTIF</span>';
        }
      })
      .catch(err => {
        console.warn("Inspector sync fallback to client stream:", err);
        if (syncIndicator) {
          syncIndicator.innerHTML = '<span style="width: 7px; height: 7px; background: #10b981; border-radius: 50%;"></span><span>CLIENT STREAM AKTIF</span>';
        }
      });
  }, 60);
}
