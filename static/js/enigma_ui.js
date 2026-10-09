let enigmaState = {
  rotors: ["I", "II", "III"],
  reflector: "B",
  rings: [1, 1, 1],
  positions: { left: "A", middle: "A", right: "A" },
  plugboard: "AV BS CG DL FU HZ",
  soundEnabled: true
};

let audioCtx = null;

function playMechanicalClick() {
  if (!enigmaState.soundEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    // Short metallic impulse
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(320, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(80, audioCtx.currentTime + 0.04);

    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
  } catch (e) {
    // Audio not allowed or unavailable
  }
}

function toggleEnigmaAudio() {
  enigmaState.soundEnabled = !enigmaState.soundEnabled;
  const label = document.getElementById('sound-label');
  if (label) {
    label.textContent = enigmaState.soundEnabled ? "Audio: Nyala" : "Audio: Bisu";
  }
  showToast(enigmaState.soundEnabled ? "Efek suara mekanik Enigma diaktifkan" : "Efek suara dinonaktifkan");
}

function initEnigmaUI() {
  updateRotorDisplays();

  const inputEl = document.getElementById('enigma-interactive-input');
  const outputEl = document.getElementById('enigma-interactive-output');

  if (!inputEl) return;

  let debounceTimer = null;

  inputEl.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    playMechanicalClick();

    debounceTimer = setTimeout(() => {
      const text = inputEl.value;
      if (!text) {
        outputEl.value = '';
        resetSignalPathway();
        return;
      }

      fetch('/api/enigma/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          rotors: enigmaState.rotors.join(','),
          reflector: enigmaState.reflector,
          rings: enigmaState.rings.join(','),
          positions: `${enigmaState.positions.left}${enigmaState.positions.middle}${enigmaState.positions.right}`,
          plugboard: enigmaState.plugboard
        })
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            outputEl.value = data.ciphertext;
            if (data.final_positions) {
              enigmaState.positions = data.final_positions;
              updateRotorDisplays();
            }
            // Light up last cipher character lamp
            if (data.ciphertext.length > 0) {
              const lastCipherChar = data.ciphertext.slice(-1).toUpperCase();
              const lastPlainChar = data.plaintext.slice(-1).toUpperCase();
              lightLamp(lastCipherChar);
              animateSignalPathway(lastPlainChar, lastCipherChar);
            }
          }
        })
        .catch(err => console.error("Enigma step error:", err));
    }, 90);
  });
}

function updateRotorDisplays() {
  const leftEl = document.getElementById('enigma-rotor-left');
  const midEl = document.getElementById('enigma-rotor-middle');
  const rightEl = document.getElementById('enigma-rotor-right');

  if (leftEl) {
    leftEl.textContent = enigmaState.positions.left;
    leftEl.style.transform = "rotateX(20deg)";
    setTimeout(() => { leftEl.style.transform = "rotateX(0deg)"; }, 120);
  }
  if (midEl) {
    midEl.textContent = enigmaState.positions.middle;
    midEl.style.transform = "rotateX(20deg)";
    setTimeout(() => { midEl.style.transform = "rotateX(0deg)"; }, 120);
  }
  if (rightEl) {
    rightEl.textContent = enigmaState.positions.right;
    rightEl.style.transform = "rotateX(20deg)";
    setTimeout(() => { rightEl.style.transform = "rotateX(0deg)"; }, 120);
  }
}

function stepRotorManual(rotorName, direction) {
  playMechanicalClick();
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const current = enigmaState.positions[rotorName];
  const idx = alphabet.indexOf(current);
  let nextIdx = (idx + direction + 26) % 26;
  enigmaState.positions[rotorName] = alphabet[nextIdx];
  updateRotorDisplays();
}

function lightLamp(char) {
  const lamp = document.getElementById(`lamp-${char}`);
  if (!lamp) return;

  // Clear previous
  document.querySelectorAll('.lamp-key').forEach(el => el.classList.remove('active'));

  lamp.classList.add('active');
  setTimeout(() => {
    lamp.classList.remove('active');
  }, 480);
}

function animateSignalPathway(inChar, outChar) {
  const nodes = ['path-key', 'path-plug1', 'path-r3', 'path-r2', 'path-r1', 'path-ref', 'path-lamp'];

  const keyNode = document.getElementById('path-key');
  const lampNode = document.getElementById('path-lamp');
  if (keyNode) keyNode.textContent = `KEY: ${inChar}`;
  if (lampNode) lampNode.textContent = `LAMP: ${outChar}`;

  nodes.forEach((id, idx) => {
    const el = document.getElementById(id);
    if (el) {
      setTimeout(() => {
        el.classList.add('active');
        setTimeout(() => { el.classList.remove('active'); }, 350);
      }, idx * 40);
    }
  });
}

function resetSignalPathway() {
  document.querySelectorAll('.signal-node').forEach(el => el.classList.remove('active'));
}

document.addEventListener('DOMContentLoaded', () => {
  initEnigmaUI();
});
