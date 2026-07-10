import { TrainScene3D } from "./train-3d.js";

const screens = {
  start: document.getElementById("startScreen"),
  briefing: document.getElementById("briefingScreen"),
  game: document.getElementById("gameScreen"),
  ending: document.getElementById("endingScreen"),
};

const trainCar = document.getElementById("trainCar");
const trainViewport = document.getElementById("trainViewport");
const nextDoor = document.getElementById("nextDoor");
const emergencyHandle = document.getElementById("emergencyHandle");
const carNumber = document.getElementById("carNumber");
const progressBar = document.getElementById("progressBar");
const carCaption = document.getElementById("carCaption");
const announcement = document.getElementById("announcement");
const announcementText = document.getElementById("announcementText");
const transitionCurtain = document.getElementById("transitionCurtain");
const transitionText = document.getElementById("transitionText");
const soundButton = document.getElementById("soundButton");
let train3D = null;

const ANOMALIES = [
  {
    id: "face",
    className: "anomaly-face",
    label: "מישהו הביט פנימה מן המנהרה",
    minCar: 2,
    weight: 1.1,
  },
  {
    id: "handprint",
    className: "anomaly-handprint",
    label: "טביעת יד הופיעה על החלון",
    minCar: 1,
    weight: 1.2,
  },
  {
    id: "passenger",
    className: "anomaly-passenger",
    label: "נוסע שלא היה שם קודם",
    minCar: 3,
    weight: 0.9,
  },
  {
    id: "bag",
    className: "anomaly-no-bag",
    label: "התיק החום נעלם",
    minCar: 2,
    weight: 1.25,
  },
  {
    id: "clock",
    className: "anomaly-wrong-clock",
    label: "השעון הציג שעה בלתי אפשרית",
    minCar: 1,
    weight: 1.3,
  },
  {
    id: "route",
    className: "anomaly-route",
    label: "מפת הקו שינתה את התחנה האחרונה",
    minCar: 3,
    weight: 1.2,
  },
  {
    id: "sign",
    className: "anomaly-sign",
    label: "שלט היציאה הזהיר אתכם",
    minCar: 3,
    weight: 1.15,
  },
  {
    id: "number",
    className: "anomaly-number",
    label: "מספר השירות השתנה",
    minCar: 2,
    weight: 1.4,
  },
  {
    id: "lights",
    className: "anomaly-lights",
    label: "אחד מגופי התאורה לא התנהג כרגיל",
    minCar: 1,
    weight: 1.2,
  },
  {
    id: "footprints",
    className: "anomaly-footprints",
    label: "צעדים רטובים הובילו לכיוון הדלת",
    minCar: 4,
    weight: 1,
  },
  {
    id: "poster",
    className: "anomaly-poster",
    label: "הכרזה ידעה שאתם כאן",
    minCar: 4,
    weight: 1.05,
  },
  {
    id: "intercom",
    className: "anomaly-intercom",
    label: "הרמקול פעל ללא הודעה",
    minCar: 4,
    weight: 0.95,
  },
  {
    id: "extra-seat",
    className: "anomaly-extra-seat",
    label: "נוסף מושב לקרון",
    minCar: 5,
    weight: 0.9,
  },
  {
    id: "eyes",
    className: "anomaly-eyes",
    label: "זוג עיניים עקב אחריכם מן הצדדים",
    minCar: 6,
    weight: 0.8,
  },
];

const STORY_MESSAGES = [
  "שירות הלילה פועל כרגיל.",
  "נא לא להשאיר חפצים ללא השגחה.",
  "התחנה הבאה אינה מופיעה בלוח הזמנים.",
  "אם שמעתם את שמכם, אל תענו.",
  "הנהג מבקש להזכיר: בקרון הזה אין נהג.",
  "הנוסעים מתבקשים לא להביט לאחור.",
  "אנו מתנצלים על העיכוב. הזמן אינו בשליטתנו.",
  "התחנה האחרונה מתקרבת. כנראה.",
];

const state = {
  progress: 0,
  mistakes: 0,
  currentAnomaly: null,
  previousAnomalyId: null,
  normalStreak: 0,
  locked: false,
  muted: false,
  startedAt: null,
  timer: null,
  announcementTimer: null,
  ambientTimer: null,
};

let audioContext = null;
let ambientGain = null;
let ambientNodes = [];

function switchScreen(name) {
  Object.entries(screens).forEach(([key, screen]) => {
    screen.classList.toggle("is-visible", key === name);
  });
}

function initAudio() {
  if (audioContext) {
    if (audioContext.state === "suspended") audioContext.resume();
    return;
  }

  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtx) return;
  audioContext = new AudioCtx();
  ambientGain = audioContext.createGain();
  ambientGain.gain.value = 0.11;
  ambientGain.connect(audioContext.destination);

  const hum = audioContext.createOscillator();
  const humFilter = audioContext.createBiquadFilter();
  const humGain = audioContext.createGain();
  hum.type = "sawtooth";
  hum.frequency.value = 46;
  humFilter.type = "lowpass";
  humFilter.frequency.value = 110;
  humGain.gain.value = 0.22;
  hum.connect(humFilter).connect(humGain).connect(ambientGain);
  hum.start();

  const vibration = audioContext.createOscillator();
  const vibrationGain = audioContext.createGain();
  vibration.type = "sine";
  vibration.frequency.value = 83;
  vibrationGain.gain.value = 0.035;
  vibration.connect(vibrationGain).connect(ambientGain);
  vibration.start();

  ambientNodes = [hum, vibration];
  scheduleRailSounds();
}

function scheduleRailSounds() {
  clearInterval(state.ambientTimer);
  state.ambientTimer = setInterval(() => {
    if (!audioContext || state.muted || !screens.game.classList.contains("is-visible")) return;
    playTone(88 + Math.random() * 12, 0.045, "triangle", 0.025, -10);
    setTimeout(() => playTone(74 + Math.random() * 8, 0.04, "triangle", 0.02, -8), 115);
  }, 690);
}

function playTone(frequency, duration, type = "sine", volume = 0.08, slide = 0) {
  if (!audioContext || state.muted) return;
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
  if (slide) {
    oscillator.frequency.exponentialRampToValueAtTime(
      Math.max(20, frequency + slide),
      audioContext.currentTime + duration,
    );
  }
  gain.gain.setValueAtTime(volume, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + duration);
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + duration);
}

function playChime() {
  playTone(659, 0.34, "sine", 0.06, 60);
  setTimeout(() => playTone(880, 0.5, "sine", 0.055, -30), 160);
}

function playDoorSound() {
  playTone(104, 0.55, "sawtooth", 0.07, -62);
  setTimeout(() => playTone(49, 0.32, "triangle", 0.08, -8), 220);
}

function playAlarm() {
  playTone(420, 0.22, "square", 0.06, -100);
  setTimeout(() => playTone(360, 0.3, "square", 0.055, -80), 190);
}

function playWrong() {
  playTone(92, 0.7, "sawtooth", 0.11, -52);
  setTimeout(() => playTone(61, 0.8, "square", 0.07, -28), 130);
}

function toggleSound() {
  state.muted = !state.muted;
  soundButton.classList.toggle("is-muted", state.muted);
  soundButton.setAttribute("aria-label", state.muted ? "הפעלת קול" : "השתקת קול");
  if (ambientGain && audioContext) {
    ambientGain.gain.setTargetAtTime(state.muted ? 0 : 0.11, audioContext.currentTime, 0.08);
  }
}

function startGame() {
  initAudio();
  switchScreen("briefing");
  playChime();
}

function beginJourney() {
  switchScreen("game");
  resetState();
  train3D?.resetPlayer();
  document.getElementById("fpsCapture")?.classList.add("show");
  state.startedAt = Date.now();
  state.timer = setInterval(updateElapsedTime, 1000);
  prepareCar(true);
}

function resetState() {
  state.progress = 0;
  state.mistakes = 0;
  state.currentAnomaly = null;
  state.previousAnomalyId = null;
  state.normalStreak = 0;
  state.locked = false;
  clearInterval(state.timer);
  clearTimeout(state.announcementTimer);
  removeAnomalies();
  updateHud();
}

function removeAnomalies() {
  ANOMALIES.forEach((anomaly) => trainCar.classList.remove(anomaly.className));
  trainCar.classList.remove("train-shudder");
  nextDoor.classList.remove("is-opening");
  emergencyHandle.classList.remove("is-pulled");
  train3D?.resetAnomaly();
  train3D?.resetActions();
}

function chooseWeighted(items) {
  const total = items.reduce((sum, item) => sum + item.weight, 0);
  let roll = Math.random() * total;
  for (const item of items) {
    roll -= item.weight;
    if (roll <= 0) return item;
  }
  return items[items.length - 1];
}

function chooseAnomaly() {
  if (state.progress === 0) {
    state.normalStreak = 1;
    return null;
  }

  const anomalyChance = Math.min(0.5 + state.progress * 0.025, 0.76);
  const mustBeAnomaly = state.normalStreak >= 2;
  if (!mustBeAnomaly && Math.random() > anomalyChance) {
    state.normalStreak += 1;
    return null;
  }

  const available = ANOMALIES.filter(
    (item) => item.minCar <= state.progress && item.id !== state.previousAnomalyId,
  );
  const chosen = chooseWeighted(available.length ? available : ANOMALIES);
  state.normalStreak = 0;
  state.previousAnomalyId = chosen.id;
  return chosen;
}

function prepareCar(firstCar = false) {
  state.locked = false;
  removeAnomalies();
  state.currentAnomaly = chooseAnomaly();
  if (state.currentAnomaly) trainCar.classList.add(state.currentAnomaly.className);
  train3D?.setAnomaly(state.currentAnomaly?.id || null);
  train3D?.setProgress(state.progress);
  train3D?.resetPlayer();
  train3D?.shake(0.08);
  updateHud();

  trainCar.classList.remove("train-shudder");
  void trainCar.offsetWidth;
  trainCar.classList.add("train-shudder");

  if (firstCar) {
    setTimeout(() => {
      showAnnouncement("הקרון הראשון עבר בדיקה. זכרו כל פרט.", "success", 4200);
      playChime();
    }, 800);
  } else if (Math.random() < 0.48 && state.progress > 1) {
    setTimeout(() => {
      const messageIndex = Math.min(
        STORY_MESSAGES.length - 1,
        Math.floor((state.progress / 13) * STORY_MESSAGES.length),
      );
      showAnnouncement(STORY_MESSAGES[messageIndex], "", 3500);
      playChime();
    }, 1000 + Math.random() * 1000);
  }
}

function updateHud() {
  const shownCar = Math.min(13, state.progress + 1);
  carNumber.textContent = String(shownCar).padStart(2, "0");
  carCaption.textContent = `קרון ${String(shownCar).padStart(2, "0")} · שירות לילה`;
  progressBar.style.width = `${(state.progress / 13) * 100}%`;
  train3D?.setProgress(state.progress);
}

function makeDecision(type) {
  if (state.locked) return;
  initAudio();
  state.locked = true;

  const hasAnomaly = Boolean(state.currentAnomaly);
  const isCorrect = (type === "alarm" && hasAnomaly) || (type === "door" && !hasAnomaly);

  if (type === "alarm") {
    emergencyHandle.classList.add("is-pulled");
    train3D?.pullAlarm();
    playAlarm();
  } else {
    nextDoor.classList.add("is-opening");
    train3D?.openDoors();
    playDoorSound();
  }

  if (isCorrect) {
    handleCorrect(type);
  } else {
    handleWrong(type, hasAnomaly);
  }
}

function handleCorrect(type) {
  state.progress += 1;
  updateHud();

  const message = type === "alarm"
    ? "זוהתה חריגה. הקרון נותק מן הקו."
    : "הקרון תקין. הדלת הבאה נפתחה.";
  showAnnouncement(message, "success", 1700);

  setTimeout(() => {
    if (state.progress >= 13) {
      finishGame();
      return;
    }
    runTransition("עוברים לקרון הבא...", () => prepareCar());
  }, 820);
}

function handleWrong(type, hadAnomaly) {
  state.mistakes += 1;
  const missedLabel = hadAnomaly ? state.currentAnomaly.label : "הקרון היה תקין";
  const message = type === "door"
    ? `פספסתם: ${missedLabel}.`
    : "משכתם בידית לשווא. הקרון היה תקין.";

  document.body.classList.add("wrong-answer");
  playWrong();
  showAnnouncement(message, "error", 2400);

  setTimeout(() => {
    document.body.classList.remove("wrong-answer");
    state.progress = Math.max(0, state.progress - 1);
    state.normalStreak = 0;
    runTransition("הרכבת מחזירה אתכם לאחור...", () => prepareCar(state.progress === 0));
  }, 1550);
}

function runTransition(text, callback) {
  transitionText.textContent = text;
  transitionCurtain.classList.add("show");
  setTimeout(() => {
    callback();
    setTimeout(() => transitionCurtain.classList.remove("show"), 350);
  }, 730);
}

function showAnnouncement(text, type = "", duration = 3000) {
  clearTimeout(state.announcementTimer);
  announcementText.textContent = text;
  announcement.className = `announcement show ${type}`.trim();
  state.announcementTimer = setTimeout(() => {
    announcement.classList.remove("show");
  }, duration);
}

function finishGame() {
  clearInterval(state.timer);
  transitionText.textContent = "התחנה האחרונה...";
  transitionCurtain.classList.add("show");
  playChime();
  if (document.pointerLockElement) document.exitPointerLock?.();

  setTimeout(() => {
    updateElapsedTime();
    document.getElementById("mistakeCount").textContent = state.mistakes;
    switchScreen("ending");
    transitionCurtain.classList.remove("show");
    if (ambientGain && audioContext) {
      ambientGain.gain.setTargetAtTime(0.015, audioContext.currentTime, 1.5);
    }
  }, 1500);
}

function updateElapsedTime() {
  if (!state.startedAt) return;
  const totalSeconds = Math.floor((Date.now() - state.startedAt) / 1000);
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  document.getElementById("timeCount").textContent = `${minutes}:${seconds}`;
}

function restartGame() {
  if (ambientGain && audioContext) {
    ambientGain.gain.setTargetAtTime(state.muted ? 0 : 0.11, audioContext.currentTime, 0.2);
  }
  switchScreen("game");
  resetState();
  state.startedAt = Date.now();
  state.timer = setInterval(updateElapsedTime, 1000);
  runTransition("הרכבת יוצאת שוב...", () => prepareCar(true));
}

function updateLook(clientX, clientY) {
  const bounds = trainViewport.getBoundingClientRect();
  const relativeX = (clientX - bounds.left) / bounds.width - 0.5;
  const relativeY = (clientY - bounds.top) / bounds.height - 0.5;
  const lookX = Math.max(-1, Math.min(1, relativeX)) * -2.8;
  const lookY = Math.max(-1, Math.min(1, relativeY)) * 1.7;
  trainCar.style.setProperty("--look-x", `${lookX}deg`);
  trainCar.style.setProperty("--look-y", `${lookY}deg`);
  train3D?.setLook(relativeX * -1.25, relativeY * -1.1);
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.();
  } else {
    document.exitFullscreen?.();
  }
}

document.getElementById("startButton").addEventListener("click", startGame);
document.getElementById("briefingButton").addEventListener("click", beginJourney);
document.getElementById("restartButton").addEventListener("click", restartGame);
document.getElementById("fullscreenButton").addEventListener("click", toggleFullscreen);
soundButton.addEventListener("click", toggleSound);
nextDoor.addEventListener("click", () => makeDecision("door"));
emergencyHandle.addEventListener("click", () => makeDecision("alarm"));
document.getElementById("doorDecision").addEventListener("click", () => makeDecision("door"));
document.getElementById("alarmDecision").addEventListener("click", () => makeDecision("alarm"));

trainViewport.addEventListener("mousemove", (event) => updateLook(event.clientX, event.clientY));
trainViewport.addEventListener("mouseleave", () => {
  trainCar.style.setProperty("--look-x", "0deg");
  trainCar.style.setProperty("--look-y", "0deg");
});
trainViewport.addEventListener(
  "touchmove",
  (event) => {
    const touch = event.touches[0];
    if (touch) updateLook(touch.clientX, touch.clientY);
  },
  { passive: true },
);

document.addEventListener("keydown", (event) => {
  if (!screens.game.classList.contains("is-visible")) return;
  if (train3D) {
    if (event.key.toLowerCase() === "m") toggleSound();
    if (event.key.toLowerCase() === "f") toggleFullscreen();
    return;
  }
  if (["e", "E", "Enter", "ArrowUp"].includes(event.key)) makeDecision("door");
  if (["r", "R", "!"].includes(event.key)) makeDecision("alarm");
  if (event.key.toLowerCase() === "m") toggleSound();
  if (event.key.toLowerCase() === "f") toggleFullscreen();
});

window.addEventListener("beforeunload", () => {
  clearInterval(state.timer);
  clearInterval(state.ambientTimer);
  ambientNodes.forEach((node) => node.stop?.());
});

try {
  train3D = new TrainScene3D(document.getElementById("trainCanvas"));
  train3D.onDecision = (type) => makeDecision(type);
  requestAnimationFrame(() => document.body.classList.add("webgl-mode"));
} catch (error) {
  console.error("WebGL scene could not start; using the CSS fallback.", error);
  window.__train13WebGLError = error?.stack || String(error);
  document.getElementById("webglLoading").hidden = true;
}

window.__train13 = {
  getState: () => ({
    progress: state.progress,
    mistakes: state.mistakes,
    anomaly: state.currentAnomaly?.id || null,
    locked: state.locked,
  }),
  decide: (type) => makeDecision(type),
  start: () => {
    startGame();
    beginJourney();
  },
  hasWebGL: () => Boolean(train3D),
  getFPS: () => train3D?.getPlayerState() || null,
  setTestPosition: (x, z, yaw = 0) => {
    if (!["127.0.0.1", "localhost"].includes(window.location.hostname)) return false;
    train3D?.setTestPosition(x, z, yaw);
    return true;
  },
};
