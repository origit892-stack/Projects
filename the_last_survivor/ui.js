const UI = {
  dayNumber: document.getElementById("dayNumber"),
  foodValue: document.getElementById("foodValue"),
  waterValue: document.getElementById("waterValue"),
  moraleValue: document.getElementById("moraleValue"),
  foodFill: document.getElementById("foodFill"),
  waterFill: document.getElementById("waterFill"),
  moraleFill: document.getElementById("moraleFill"),
  eventLabel: document.getElementById("eventLabel"),
  eventBankCount: document.getElementById("eventBankCount"),
  eventTitle: document.getElementById("eventTitle"),
  eventStory: document.getElementById("eventStory"),
  choices: document.getElementById("choices"),
  result: document.getElementById("result"),
  inventorySlots: document.getElementById("inventorySlots"),
  managementActions: document.getElementById("managementActions"),
  routineStatus: document.getElementById("routineStatus"),
  nextButton: document.getElementById("nextButton"),
  restartButton: document.getElementById("restartButton"),
  dayFlash: document.getElementById("dayFlash"),
  bunkerVisual: document.querySelector(".bunker-visual"),
  hatch: document.querySelector(".hatch"),
  gameShell: document.getElementById("gameShell"),
  gameOverScreen: document.getElementById("gameOverScreen"),
  survivedText: document.getElementById("survivedText"),
  deathReason: document.getElementById("deathReason"),
  tryAgainButton: document.getElementById("tryAgainButton")
};

const roomElements = {
  bunks: document.querySelector('[data-room="bunks"]'),
  food: document.querySelector('[data-room="food"]'),
  machines: document.querySelector('[data-room="machines"]')
};

const survivorElements = {
  noa: document.querySelector('[data-survivor="noa"]'),
  amir: document.querySelector('[data-survivor="amir"]'),
  dana: document.querySelector('[data-survivor="dana"]')
};

function renderEventBankCount(totalEvents) {
  UI.eventBankCount.textContent = `מאגר אירועים: ${totalEvents.toLocaleString("he-IL")} מקרים שונים`;
}

function renderStats(state, maxStats) {
  UI.dayNumber.textContent = state.day;
  UI.foodValue.textContent = `${state.food}/${maxStats.food}`;
  UI.waterValue.textContent = `${state.water}/${maxStats.water}`;
  UI.moraleValue.textContent = `${state.morale}/${maxStats.morale}`;

  updateProgress(UI.foodFill, state.food, maxStats.food);
  updateProgress(UI.waterFill, state.water, maxStats.water);
  updateProgress(UI.moraleFill, state.morale, maxStats.morale);
  updateValveAlert(state, maxStats);
  updateBunkerMood(state, maxStats);
}

function updateProgress(fill, value, max) {
  const percent = (value / max) * 100;
  const track = fill.parentElement;

  fill.style.width = `${percent}%`;
  fill.classList.toggle("warning", percent < 30);
  track.setAttribute("aria-valuenow", value);
}

function updateValveAlert(state, maxStats) {
  const hasLowStat = Object.keys(maxStats).some((key) => {
    return (state[key] / maxStats[key]) * 100 < 30;
  });

  UI.bunkerVisual.classList.toggle("alert", hasLowStat);
}

function spinValve() {
  UI.hatch.classList.remove("spinning");
  void UI.hatch.offsetWidth;
  UI.hatch.classList.add("spinning");
}

function renderInventory(inventory, items) {
  UI.inventorySlots.innerHTML = "";

  for (let index = 0; index < 3; index += 1) {
    const itemId = inventory[index];
    const slot = document.createElement("div");
    slot.className = `inventory-slot${itemId ? "" : " empty"}`;
    slot.textContent = itemId ? items[itemId].label : "ריק";
    UI.inventorySlots.appendChild(slot);
  }
}

function flashInventorySlot(index) {
  const slot = UI.inventorySlots.children[index];

  if (!slot) return;

  slot.classList.remove("gained");
  void slot.offsetWidth;
  slot.classList.add("gained");
}

function renderManagementPanel(state, upgrades, handlers) {
  UI.managementActions.innerHTML = "";

  const expeditionButton = createManagementButton("שלח משלחת אל פני השטח", handlers.onOpenExpedition);
  expeditionButton.disabled = Boolean(state.expedition) || !state.survivors.some((survivor) => survivor.status === "active");
  UI.managementActions.appendChild(expeditionButton);

  const foodUpgradeButton = createManagementButton(
    `שדרג חדר אוכל (${upgrades.dining ? "בוצע" : "10 אוכל"})`,
    handlers.onUpgradeDining
  );
  foodUpgradeButton.disabled = upgrades.dining || state.food < 10;
  UI.managementActions.appendChild(foodUpgradeButton);

  const machineUpgradeButton = createManagementButton(
    `שדרג מכונות (${upgrades.machines ? "בוצע" : "8 מים"})`,
    handlers.onUpgradeMachines
  );
  machineUpgradeButton.disabled = upgrades.machines || state.water < 8;
  UI.managementActions.appendChild(machineUpgradeButton);

  const note = document.createElement("span");
  note.className = "management-note";
  note.textContent = state.expedition
    ? `${state.expedition.name} במשלחת, חוזר בעוד ${state.expedition.daysLeft} ימים`
    : "אין משלחת פעילה";
  UI.managementActions.appendChild(note);
}

function renderExpeditionChoices(survivors, onSelect, onCancel) {
  UI.managementActions.innerHTML = "";

  survivors
    .filter((survivor) => survivor.status === "active")
    .forEach((survivor) => {
      const button = createManagementButton(`שלח את ${survivor.name}`, () => onSelect(survivor.id));
      button.classList.add("small-choice-button");
      UI.managementActions.appendChild(button);
    });

  UI.managementActions.appendChild(createManagementButton("בטל", onCancel));
}

function createManagementButton(text, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "management-button";
  button.textContent = text;
  button.addEventListener("click", onClick);

  return button;
}

function renderSurvivors(survivors) {
  survivors.forEach((survivor) => {
    const element = survivorElements[survivor.id];
    const room = roomElements[survivor.room];

    if (!element || !room) return;

    if (element.parentElement !== room) {
      room.appendChild(element);
    }

    element.classList.toggle("injured", survivor.status === "injured");
    element.classList.toggle("away", survivor.status === "away");
    element.classList.toggle("lost", survivor.status === "lost");
  });
}

function moveSurvivor(survivor) {
  const element = survivorElements[survivor.id];
  const room = roomElements[survivor.room];

  if (!element || !room || survivor.status === "away" || survivor.status === "lost") return;

  if (element.parentElement !== room) {
    room.appendChild(element);
  }

  element.style.right = `${18 + Math.floor(Math.random() * 42)}%`;
  element.style.bottom = `${48 + Math.floor(Math.random() * 44)}px`;
}

function showSurvivorSpeech(survivor, text) {
  const element = survivorElements[survivor.id];
  const bubble = element?.querySelector(".speech-bubble");

  if (!bubble || survivor.status === "away" || survivor.status === "lost") return;

  bubble.textContent = text;
  bubble.classList.remove("show");
  void bubble.offsetWidth;
  bubble.classList.add("show");
}

function updateBunkerMood(state, maxStats) {
  const lowFood = (state.food / maxStats.food) * 100 < 30;
  const lowWater = (state.water / maxStats.water) * 100 < 30;
  const highMorale = (state.morale / maxStats.morale) * 100 >= 70;

  UI.bunkerVisual.classList.toggle("mood-good", highMorale && !lowFood && !lowWater);
  UI.bunkerVisual.classList.toggle("mood-strained", lowFood || lowWater);
  UI.bunkerVisual.classList.toggle("mood-neutral", !highMorale && !lowFood && !lowWater);
}

function showRoutineMode(message) {
  UI.gameShell.classList.add("phase-routine");
  UI.gameShell.classList.remove("phase-event");
  UI.routineStatus.textContent = message;
  UI.nextButton.classList.add("hidden");
  UI.restartButton.classList.add("hidden");
}

function showEventMode() {
  UI.gameShell.classList.add("phase-event");
  UI.gameShell.classList.remove("phase-routine");
}

function playBunkerAlarm() {
  UI.bunkerVisual.classList.remove("alarm");
  void UI.bunkerVisual.offsetWidth;
  UI.bunkerVisual.classList.add("alarm");
  window.setTimeout(() => UI.bunkerVisual.classList.remove("alarm"), 1120);
}

function renderEventLoading(day) {
  showEventMode();
  UI.eventLabel.textContent = `אירוע יומי | יום ${day}`;
  UI.eventTitle.textContent = "בודק את מערכות הבונקר...";
  UI.eventStory.textContent = "הבונקר מאזין לרעש שבחוץ ומכין אירוע חדש.";
  UI.result.textContent = "";
  UI.result.classList.remove("game-over");
  UI.nextButton.classList.add("hidden");
  UI.restartButton.classList.add("hidden");
  UI.choices.innerHTML = "";
}

function renderEvent(event, day, onChoice) {
  showEventMode();
  UI.eventLabel.textContent = `אירוע יומי | יום ${day}`;
  UI.eventTitle.textContent = event.title;
  UI.eventStory.textContent = event.story;
  UI.result.textContent = "";
  UI.result.classList.remove("game-over");
  UI.nextButton.classList.add("hidden");
  UI.restartButton.classList.add("hidden");

  UI.choices.innerHTML = "";
  event.choices.forEach((choice) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `choice-button${choice.special ? " special-choice" : ""}${choice.healing ? " healing-choice" : ""}`;
    button.textContent = choice.text;
    button.addEventListener("click", () => onChoice(choice));
    UI.choices.appendChild(button);
  });
}

function lockChoices() {
  UI.choices.querySelectorAll("button").forEach((button) => {
    button.disabled = true;
  });
}

function renderChoiceResult(choice, effectText) {
  UI.result.innerHTML = `<strong>${choice.result}</strong>${effectText ? `<br>${effectText}` : ""}`;
  UI.nextButton.classList.add("hidden");
}

function renderGameOver(survivedDays, reason) {
  UI.choices.innerHTML = "";
  UI.nextButton.classList.add("hidden");
  UI.restartButton.classList.remove("hidden");
  UI.gameShell.classList.add("hidden");
  UI.gameOverScreen.classList.remove("hidden");
  UI.survivedText.textContent = `שרדת ${survivedDays} ימים`;
  UI.deathReason.textContent = reason;
  UI.tryAgainButton.focus();
}

function showGameShell() {
  UI.gameShell.classList.remove("hidden");
  UI.gameOverScreen.classList.add("hidden");
}

function playDayFlash(callback) {
  UI.dayFlash.classList.remove("active");
  void UI.dayFlash.offsetWidth;
  UI.dayFlash.classList.add("active");
  window.setTimeout(callback, 260);
  window.setTimeout(() => UI.dayFlash.classList.remove("active"), 680);
}
