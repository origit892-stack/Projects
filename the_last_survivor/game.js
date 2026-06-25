const maxStats = {
  food: 20,
  water: 20,
  morale: 100
};

const ITEMS = {
  wrench: {
    label: "מפתח שוודי",
    matches: ["תקלה", "דליפה", "פתח אוורור", "סדק", "מכונות"],
    choiceText: "להשתמש במפתח השוודי",
    result: "המפתח השוודי עושה את ההבדל. התיקון נקי, מהיר וכמעט בלי מחיר.",
    effect: { food: 0, water: 2, morale: 6 }
  },
  radio: {
    label: "רדיו",
    matches: ["רדיו", "קשר", "אות", "בקשת עזרה"],
    choiceText: "להפעיל את הרדיו",
    result: "הרדיו מסנן את הרעש ומחזיר תשובה ברורה יותר. האנשים נזכרים שהם לא לבד.",
    effect: { food: 0, water: 0, morale: 14 }
  },
  medkit: {
    label: "ערכת עזרה ראשונה",
    matches: ["פציעה", "פצוע", "פציעות", "מרפאה", "מנה מזוהמת", "לילה ללא שינה"],
    choiceText: "השתמש בערכת עזרה ראשונה כדי להציל אותו",
    result: "ערכת העזרה נפתחת על הרצפה. תחבושות, חיטוי ונשימה עמוקה אחת מחזירים אדם אחד לעמוד על הרגליים.",
    effect: { food: 0, water: 0, morale: 12 }
  }
};

const ROUTINE_DURATION = 5000;
const ROOMS = ["bunks", "food", "machines"];
const SPEECH = {
  good: ["אולי נצא מזה.", "מי תיקן את האור?", "יש פה קצב טוב."],
  hungry: ["אני רעב.", "מישהו ספר את הקופסאות?", "המדף הזה מסתכל עליי."],
  thirsty: ["נגמר לי הרוק.", "שומעים את הטפטוף?", "מים. רק מים."],
  injured: ["אני בסדר. בערך.", "צריך תחבושת.", "אל תתנו לי להירדם."],
  neutral: ["משעמם פה...", "שמעתם את הרעש הזה?", "עוד יום מתחת לאדמה."]
};

let routineTimer = null;
let routineLifeTimer = null;

const state = {
  day: 1,
  food: 20,
  water: 20,
  morale: 100,
  inventory: [],
  upgrades: {
    dining: false,
    machines: false
  },
  survivors: [
    { id: "noa", name: "נועה", room: "bunks", status: "active" },
    { id: "amir", name: "אמיר", room: "food", status: "active" },
    { id: "dana", name: "דנה", room: "machines", status: "active" }
  ],
  expedition: null,
  currentEvent: null,
  choiceMade: false,
  gameOver: false,
  lastRoutineMessage: ""
};

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function updateStats(effect) {
  state.food = clamp(state.food + (effect.food || 0), 0, maxStats.food);
  state.water = clamp(state.water + (effect.water || 0), 0, maxStats.water);
  state.morale = clamp(state.morale + (effect.morale || 0), 0, maxStats.morale);
}

function describeEffect(effect) {
  const labels = {
    food: "אוכל",
    water: "מים",
    morale: "מורל"
  };

  return Object.entries(effect)
    .filter(([, value]) => value !== 0)
    .map(([key, value]) => `${labels[key]} ${value > 0 ? "+" : ""}${value}`)
    .join(" | ");
}

async function getRandomEvent() {
  const aiEvent = await getAiGeneratedEvent(state, maxStats);

  return aiEvent || EVENTS[Math.floor(Math.random() * EVENTS.length)];
}

function hasLost() {
  return state.food === 0 || state.water === 0 || state.morale === 0;
}

function getCollapseReason() {
  if (state.morale === 0) {
    return "התושבים איבדו תקווה. בלי אמון ובלי רצון להמשיך, הדממה ניצחה את הבונקר מבפנים.";
  }

  if (state.water === 0) {
    return "היובש הכריע אתכם. המכלים התרוקנו, והבונקר הפך למלכודת מתכת חמה ושקטה.";
  }

  if (state.food === 0) {
    return "הרעב שבר את השגרה. המדפים התרוקנו, וההישרדות הפכה למאבק שאי אפשר לנצח.";
  }

  return "מערכות הבונקר קרסו, והמקלט האחרון הפסיק להחזיק את מי שנשאר בפנים.";
}

function getSpecialChoice(event) {
  const injuredSurvivor = state.survivors.find((survivor) => survivor.status === "injured");
  const eventText = `${event.title || ""} ${event.story || ""}`;

  if (state.inventory.includes("medkit") && (injuredSurvivor || hasInjuryText(eventText))) {
    return {
      text: ITEMS.medkit.choiceText,
      effect: ITEMS.medkit.effect,
      result: injuredSurvivor
        ? `${ITEMS.medkit.result} ${injuredSurvivor.name} חוזר לתפקוד.`
        : ITEMS.medkit.result,
      special: true,
      healing: true,
      itemId: "medkit"
    };
  }

  const itemId = state.inventory.find((id) => {
    if (id === "medkit") return false;
    return ITEMS[id].matches.some((match) => eventText.includes(match));
  });

  if (!itemId) return null;

  const item = ITEMS[itemId];

  return {
    text: item.choiceText,
    effect: item.effect,
    result: item.result,
    special: true,
    itemId
  };
}

function hasInjuryText(text) {
  return ["פציעה", "פצוע", "פציעות", "נפצע", "מרפאה"].some((word) => text.includes(word));
}

function getChoicesForCurrentEvent() {
  const specialChoice = getSpecialChoice(state.currentEvent);

  return specialChoice
    ? [...state.currentEvent.choices, specialChoice]
    : state.currentEvent.choices;
}

function maybeGainItem(choice) {
  if (choice.special || state.inventory.length >= 3) {
    return "";
  }

  const eventText = `${state.currentEvent.title} ${choice.text}`;
  let itemId = null;

  if (eventText.includes("ממצא חשוד") && eventText.includes("לפתוח")) {
    itemId = getMissingItem(["wrench", "radio", "medkit"]);
  } else if (eventText.includes("שמועה על מחסן") && eventText.includes("חיפוש")) {
    itemId = getMissingItem(["wrench", "medkit", "radio"]);
  } else if (eventText.includes("אות רדיו") && eventText.includes("לפענח")) {
    itemId = getMissingItem(["radio"]);
  } else if (isUsefulChoice(choice) && Math.random() < 0.2) {
    itemId = getMissingItem(["medkit", "wrench", "radio"]);
  }

  if (!itemId) return "";

  addItem(itemId);
  return `מצאתם ציוד חדש: ${ITEMS[itemId].label}`;
}

function isUsefulChoice(choice) {
  return choice.effect.food > 0 || choice.effect.water > 0 || choice.effect.morale > 6;
}

function getMissingItem(preferredItems) {
  return preferredItems.find((itemId) => !state.inventory.includes(itemId)) || null;
}

function addItem(itemId) {
  if (!itemId || state.inventory.includes(itemId) || state.inventory.length >= 3) return false;

  state.inventory.push(itemId);
  renderInventory(state.inventory, ITEMS);
  flashInventorySlot(state.inventory.length - 1);
  return true;
}

function removeItem(itemId) {
  const index = state.inventory.indexOf(itemId);

  if (index === -1) return;

  state.inventory.splice(index, 1);
  renderInventory(state.inventory, ITEMS);
}

function healFirstInjuredSurvivor() {
  const survivor = state.survivors.find((current) => current.status === "injured");

  if (survivor) {
    survivor.status = "active";
    survivor.room = "bunks";
  }
}

function chooseOption(choice) {
  if (state.choiceMade || state.gameOver) return;

  state.choiceMade = true;
  playMenuBeep();
  updateStats(choice.effect);

  if (choice.healing) {
    healFirstInjuredSurvivor();
    removeItem("medkit");
  }

  renderStats(state, maxStats);
  renderSurvivors(state.survivors);
  spinValve();
  lockChoices();

  const itemText = maybeGainItem(choice);
  const effectText = [describeEffect(choice.effect), itemText].filter(Boolean).join(" | ");
  renderChoiceResult(choice, effectText);

  if (hasLost()) {
    endGame();
    return;
  }

  window.setTimeout(() => {
    if (!state.gameOver) {
      playSurvivedSound();
      beginRoutineAfterChoice();
    }
  }, 850);
}

function beginRoutineAfterChoice() {
  startRoutine(`יום ${state.day} - התוצאות מורגשות בבונקר...`);
}

function advanceToNextDay() {
  if (state.gameOver) return;

  state.day += 1;
  updateStats({
    food: state.upgrades.dining ? -1 : -2,
    water: -2,
    morale: state.upgrades.machines ? 2 : 0
  });
  processExpeditionDay();
  renderStats(state, maxStats);
  renderSurvivors(state.survivors);
  renderManagementPanel(state, state.upgrades, managementHandlers);

  if (hasLost()) {
    endGame();
    return;
  }

  startRoutine(state.lastRoutineMessage || `יום ${state.day} - השגרה נמשכת...`);
  state.lastRoutineMessage = "";
}

function startRoutine(message = `יום ${state.day} - השגרה נמשכת...`) {
  showRoutineMode(message);
  renderStats(state, maxStats);
  renderInventory(state.inventory, ITEMS);
  renderSurvivors(state.survivors);
  renderManagementPanel(state, state.upgrades, managementHandlers);
  startRoutineLife();

  clearTimeout(routineTimer);
  routineTimer = window.setTimeout(openDailyEvent, ROUTINE_DURATION);
}

async function openDailyEvent() {
  if (state.gameOver) return;

  stopRoutineLife();
  playAlarmSound();
  playBunkerAlarm();
  spinValve();
  renderEventLoading(state.day);
  playDayFlash(async () => {
    state.currentEvent = await getRandomEvent();
    state.choiceMade = false;
    renderStats(state, maxStats);
    renderEvent(
      { ...state.currentEvent, choices: getChoicesForCurrentEvent() },
      state.day,
      chooseOption
    );
  });
}

function startRoutineLife() {
  stopRoutineLife();
  runRoutineLifeTick();
  routineLifeTimer = window.setInterval(runRoutineLifeTick, 1350);
}

function stopRoutineLife() {
  clearInterval(routineLifeTimer);
}

function runRoutineLifeTick() {
  const activeSurvivors = state.survivors.filter((survivor) => survivor.status === "active" || survivor.status === "injured");

  activeSurvivors.forEach((survivor) => {
    if (Math.random() < 0.58) {
      survivor.room = ROOMS[Math.floor(Math.random() * ROOMS.length)];
    }

    moveSurvivor(survivor);
  });

  const speaker = activeSurvivors[Math.floor(Math.random() * activeSurvivors.length)];

  if (speaker) {
    showSurvivorSpeech(speaker, getSpeechLine(speaker));
  }
}

function getSpeechLine(survivor) {
  if (survivor.status === "injured") return pick(SPEECH.injured);
  if (state.food <= 6) return pick(SPEECH.hungry);
  if (state.water <= 6) return pick(SPEECH.thirsty);
  if (state.morale >= 70) return pick(SPEECH.good);
  return pick(SPEECH.neutral);
}

function pick(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function openExpeditionPicker() {
  playMenuBeep();
  clearTimeout(routineTimer);
  renderExpeditionChoices(state.survivors, sendExpedition, () => startRoutine("בחירת משלחת בוטלה. השגרה נמשכת..."));
}

function sendExpedition(survivorId) {
  const survivor = state.survivors.find((current) => current.id === survivorId);

  if (!survivor || survivor.status !== "active" || state.expedition) return;

  playMenuBeep();
  survivor.status = "away";
  state.expedition = {
    survivorId,
    name: survivor.name,
    daysLeft: 2
  };
  state.lastRoutineMessage = `${survivor.name} יצא אל פני השטח. הבונקר מחכה לסימן חיים.`;
  renderSurvivors(state.survivors);
  startRoutine(state.lastRoutineMessage);
  state.lastRoutineMessage = "";
}

function processExpeditionDay() {
  if (!state.expedition) return;

  state.expedition.daysLeft -= 1;

  if (state.expedition.daysLeft > 0) {
    state.lastRoutineMessage = `${state.expedition.name} עדיין בחוץ. נשאר עוד יום אחד לחכות.`;
    return;
  }

  resolveExpedition();
}

function resolveExpedition() {
  const expedition = state.expedition;
  const survivor = state.survivors.find((current) => current.id === expedition.survivorId);
  const roll = Math.random();

  state.expedition = null;

  if (!survivor) return;

  if (roll < 0.5) {
    survivor.status = "active";
    survivor.room = "food";
    updateStats({ food: 6, water: 5, morale: 8 });
    state.lastRoutineMessage = `${survivor.name} חזר עם אוכל, מים וסיפור שאף אחד לא מאמין לו לגמרי.`;
  } else if (roll < 0.72) {
    survivor.status = "active";
    survivor.room = "machines";
    const itemId = getMissingItem(["medkit", "wrench", "radio"]);
    if (itemId) addItem(itemId);
    updateStats({ food: 1, water: 1, morale: 6 });
    state.lastRoutineMessage = `${survivor.name} חזר עם ציוד שימושי מהחורבות.`;
  } else if (roll < 0.92) {
    survivor.status = "injured";
    survivor.room = "bunks";
    updateStats({ food: 1, water: 0, morale: -8 });
    state.lastRoutineMessage = `${survivor.name} חזר פצוע. ערכת עזרה ראשונה יכולה לשנות את הסיפור.`;
  } else {
    survivor.status = "lost";
    updateStats({ food: 0, water: 0, morale: -25 });
    state.lastRoutineMessage = `${survivor.name} לא חזר. אף אחד לא מדבר בזמן חלוקת המנות.`;
  }
}

function upgradeDining() {
  if (state.upgrades.dining || state.food < 10) return;

  playMenuBeep();
  state.food -= 10;
  state.upgrades.dining = true;
  startRoutine("חדר האוכל שודרג. מעכשיו הבונקר צורך פחות אוכל בכל יום.");
}

function upgradeMachines() {
  if (state.upgrades.machines || state.water < 8) return;

  playMenuBeep();
  state.water -= 8;
  state.upgrades.machines = true;
  startRoutine("חדר המכונות שודרג. המערכות יציבות יותר והמורל מקבל חיזוק יומי.");
}

function startNextDay() {
  if (!state.gameOver) {
    advanceToNextDay();
  }
}

function endGame() {
  state.gameOver = true;
  clearTimeout(routineTimer);
  stopRoutineLife();
  playCollapseSound();
  renderStats(state, maxStats);
  renderGameOver(state.day, getCollapseReason());
}

function restartGame() {
  clearTimeout(routineTimer);
  stopRoutineLife();
  showGameShell();
  state.day = 1;
  state.food = 20;
  state.water = 20;
  state.morale = 100;
  state.inventory = [];
  state.upgrades = { dining: false, machines: false };
  state.survivors = [
    { id: "noa", name: "נועה", room: "bunks", status: "active" },
    { id: "amir", name: "אמיר", room: "food", status: "active" },
    { id: "dana", name: "דנה", room: "machines", status: "active" }
  ];
  state.expedition = null;
  state.gameOver = false;
  state.choiceMade = false;
  state.lastRoutineMessage = "";
  renderInventory(state.inventory, ITEMS);
  renderSurvivors(state.survivors);
  startRoutine();
}

const managementHandlers = {
  onOpenExpedition: openExpeditionPicker,
  onUpgradeDining: upgradeDining,
  onUpgradeMachines: upgradeMachines
};

UI.nextButton.addEventListener("click", startNextDay);
UI.restartButton.addEventListener("click", restartGame);
UI.tryAgainButton.addEventListener("click", restartGame);

renderEventBankCount(EVENTS.length);
renderInventory(state.inventory, ITEMS);
renderSurvivors(state.survivors);
startRoutine();
