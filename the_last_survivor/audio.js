let audioContext = null;

function getAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }

  if (audioContext.state === "suspended") {
    audioContext.resume();
  }

  return audioContext;
}

function playTone(frequency, duration, type, volume, delay = 0) {
  const context = getAudioContext();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const start = context.currentTime + delay;

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, start);
  gain.gain.setValueAtTime(0.0001, start);
  gain.gain.exponentialRampToValueAtTime(volume, start + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);

  oscillator.connect(gain);
  gain.connect(context.destination);
  oscillator.start(start);
  oscillator.stop(start + duration + 0.03);
}

function playMenuBeep() {
  playTone(520, 0.08, "square", 0.035);
}

function playAlarmSound() {
  playTone(170, 0.34, "sawtooth", 0.045);
  playTone(125, 0.34, "sawtooth", 0.035, 0.22);
}

function playSurvivedSound() {
  playTone(420, 0.1, "triangle", 0.035);
  playTone(560, 0.12, "triangle", 0.035, 0.1);
  playTone(740, 0.16, "triangle", 0.035, 0.22);
}

function playCollapseSound() {
  playTone(120, 0.5, "sawtooth", 0.06);
  playTone(72, 0.72, "sine", 0.05, 0.16);
}
