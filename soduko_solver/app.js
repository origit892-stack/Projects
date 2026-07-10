const boardElement = document.getElementById("sudokuBoard");
const solveButton = document.getElementById("solveButton");
const clearButton = document.getElementById("clearButton");
const undoButton = document.getElementById("undoButton");
const exampleButton = document.getElementById("exampleButton");
const filledCount = document.getElementById("filledCount");
const toast = document.getElementById("toast");
const toastIcon = document.getElementById("toastIcon");
const toastTitle = document.getElementById("toastTitle");
const toastMessage = document.getElementById("toastMessage");
const celebration = document.getElementById("celebration");

const EXAMPLE = [
  [5, 3, 0, 0, 7, 0, 0, 0, 0],
  [6, 0, 0, 1, 9, 5, 0, 0, 0],
  [0, 9, 8, 0, 0, 0, 0, 6, 0],
  [8, 0, 0, 0, 6, 0, 0, 0, 3],
  [4, 0, 0, 8, 0, 3, 0, 0, 1],
  [7, 0, 0, 0, 2, 0, 0, 0, 6],
  [0, 6, 0, 0, 0, 0, 2, 8, 0],
  [0, 0, 0, 4, 1, 9, 0, 0, 5],
  [0, 0, 0, 0, 8, 0, 0, 7, 9],
];

const cells = [];
let history = [];
let selectedIndex = null;
let toastTimer = null;
let isSolving = false;

function createBoard() {
  for (let index = 0; index < 81; index += 1) {
    const cell = document.createElement("input");
    const row = Math.floor(index / 9);
    const column = index % 9;

    cell.className = "cell";
    cell.type = "text";
    cell.inputMode = "numeric";
    cell.maxLength = 1;
    cell.autocomplete = "off";
    cell.spellcheck = false;
    cell.dataset.index = index;
    cell.dataset.row = row;
    cell.dataset.column = column;
    cell.setAttribute("role", "gridcell");
    cell.setAttribute("aria-label", `שורה ${row + 1}, עמודה ${column + 1}`);

    cell.addEventListener("focus", () => selectCell(index));
    cell.addEventListener("click", () => selectCell(index));
    cell.addEventListener("input", handleInput);
    cell.addEventListener("keydown", handleKeydown);
    cell.addEventListener("paste", handlePaste);

    boardElement.appendChild(cell);
    cells.push(cell);
  }
}

function selectCell(index) {
  selectedIndex = index;
  const selected = cells[index];
  const row = Number(selected.dataset.row);
  const column = Number(selected.dataset.column);
  const boxRow = Math.floor(row / 3);
  const boxColumn = Math.floor(column / 3);
  const value = selected.value;

  cells.forEach((cell) => {
    const cellRow = Number(cell.dataset.row);
    const cellColumn = Number(cell.dataset.column);
    const sameBox =
      Math.floor(cellRow / 3) === boxRow && Math.floor(cellColumn / 3) === boxColumn;

    cell.classList.toggle("selected", cell === selected);
    cell.classList.toggle(
      "related",
      cell !== selected && (cellRow === row || cellColumn === column || sameBox),
    );
    cell.classList.toggle("same-value", Boolean(value) && cell !== selected && cell.value === value);
  });
}

function handleInput(event) {
  if (isSolving) return;
  const cell = event.target;
  const nextValue = cell.value.replace(/[^1-9]/g, "").slice(-1);
  const previousValue = cell.dataset.previousValue || "";

  if (previousValue !== nextValue) {
    history.push({ index: Number(cell.dataset.index), value: previousValue });
    undoButton.disabled = false;
  }

  cell.value = nextValue;
  cell.dataset.previousValue = nextValue;
  cell.classList.remove("solved", "given");
  validateBoard();
  updateCount();
  selectCell(Number(cell.dataset.index));
}

function handleKeydown(event) {
  const index = Number(event.target.dataset.index);
  const row = Math.floor(index / 9);
  const column = index % 9;
  let target = null;

  if (event.key === "ArrowUp") target = Math.max(0, row - 1) * 9 + column;
  if (event.key === "ArrowDown") target = Math.min(8, row + 1) * 9 + column;
  if (event.key === "ArrowLeft") target = row * 9 + Math.max(0, column - 1);
  if (event.key === "ArrowRight") target = row * 9 + Math.min(8, column + 1);

  if (target !== null) {
    event.preventDefault();
    cells[target].focus();
    return;
  }

  if (["Backspace", "Delete", "0", " "].includes(event.key)) {
    event.preventDefault();
    setCellValue(index, "", true);
  }
}

function handlePaste(event) {
  const raw = event.clipboardData.getData("text");
  const normalized = raw.replace(/[^0-9.]/g, "");
  if (normalized.length !== 81) return;

  event.preventDefault();
  saveSnapshot();
  normalized.split("").forEach((character, index) => {
    const value = character === "0" || character === "." ? "" : character;
    setCellValue(index, value, false);
  });
  validateBoard();
  updateCount();
  showToast("הלוח הודבק", "81 המשבצות נטענו בהצלחה.", "success");
}

function setCellValue(index, value, remember = false) {
  const cell = cells[index];
  if (remember && cell.value !== value) {
    history.push({ index, value: cell.value });
    undoButton.disabled = false;
  }
  cell.value = value;
  cell.dataset.previousValue = value;
  cell.classList.remove("solved", "given");
  validateBoard();
  updateCount();
  if (selectedIndex !== null) selectCell(selectedIndex);
}

function saveSnapshot() {
  history.push({ snapshot: cells.map((cell) => cell.value) });
  undoButton.disabled = false;
}

function undo() {
  const action = history.pop();
  if (!action) return;

  if (action.snapshot) {
    action.snapshot.forEach((value, index) => {
      cells[index].value = value;
      cells[index].dataset.previousValue = value;
      cells[index].classList.remove("solved", "given");
    });
  } else {
    cells[action.index].value = action.value;
    cells[action.index].dataset.previousValue = action.value;
    cells[action.index].classList.remove("solved", "given");
    cells[action.index].focus();
  }

  undoButton.disabled = history.length === 0;
  validateBoard();
  updateCount();
}

function getBoard() {
  return Array.from({ length: 9 }, (_, row) =>
    Array.from({ length: 9 }, (_, column) => Number(cells[row * 9 + column].value) || 0),
  );
}

function validateBoard() {
  const board = getBoard();
  const invalidIndexes = new Set();

  for (let row = 0; row < 9; row += 1) {
    for (let column = 0; column < 9; column += 1) {
      const value = board[row][column];
      if (!value) continue;

      board[row][column] = 0;
      if (!isSafe(board, row, column, value)) invalidIndexes.add(row * 9 + column);
      board[row][column] = value;
    }
  }

  cells.forEach((cell, index) => cell.classList.toggle("invalid", invalidIndexes.has(index)));
  return invalidIndexes.size === 0;
}

function isSafe(board, row, column, number) {
  for (let i = 0; i < 9; i += 1) {
    if (board[row][i] === number || board[i][column] === number) return false;
  }

  const startRow = Math.floor(row / 3) * 3;
  const startColumn = Math.floor(column / 3) * 3;
  for (let r = startRow; r < startRow + 3; r += 1) {
    for (let c = startColumn; c < startColumn + 3; c += 1) {
      if (board[r][c] === number) return false;
    }
  }
  return true;
}

function solveSudoku(board) {
  let bestCell = null;
  let bestCandidates = null;

  for (let row = 0; row < 9; row += 1) {
    for (let column = 0; column < 9; column += 1) {
      if (board[row][column] !== 0) continue;
      const candidates = [];
      for (let number = 1; number <= 9; number += 1) {
        if (isSafe(board, row, column, number)) candidates.push(number);
      }
      if (candidates.length === 0) return false;
      if (!bestCandidates || candidates.length < bestCandidates.length) {
        bestCell = [row, column];
        bestCandidates = candidates;
      }
    }
  }

  if (!bestCell) return true;
  const [row, column] = bestCell;
  for (const number of bestCandidates) {
    board[row][column] = number;
    if (solveSudoku(board)) return true;
    board[row][column] = 0;
  }
  return false;
}

async function solve() {
  if (isSolving) return;
  const board = getBoard();
  const startingValues = cells.map((cell) => cell.value);
  const enteredCount = startingValues.filter(Boolean).length;

  if (enteredCount === 0) {
    showToast("הלוח עדיין ריק", "הזינו כמה מספרים או נסו את החידה לדוגמה.");
    cells[0].focus();
    return;
  }

  if (!validateBoard()) {
    showToast("יש התנגשות בלוח", "המשבצות המסומנות מכילות מספר שחוזר בשורה, בעמודה או בריבוע.");
    return;
  }

  isSolving = true;
  solveButton.disabled = true;
  solveButton.querySelector("strong").textContent = "חושבים...";

  await new Promise((resolve) => setTimeout(resolve, 340));
  const hasSolution = solveSudoku(board);

  if (!hasSolution) {
    isSolving = false;
    solveButton.disabled = false;
    solveButton.querySelector("strong").textContent = "פתרו את הלוח";
    showToast("לא נמצא פתרון", "המספרים תקינים בנפרד, אבל אינם מובילים ללוח פתיר.");
    return;
  }

  saveSnapshot();
  cells.forEach((cell, index) => {
    if (startingValues[index]) cell.classList.add("given");
  });

  const emptyIndexes = startingValues
    .map((value, index) => (value ? null : index))
    .filter((index) => index !== null);

  emptyIndexes.forEach((index, order) => {
    setTimeout(() => {
      const row = Math.floor(index / 9);
      const column = index % 9;
      cells[index].value = board[row][column];
      cells[index].dataset.previousValue = String(board[row][column]);
      cells[index].classList.add("solved");
      cells[index].style.animationDelay = `${Math.min(order * 7, 180)}ms`;
      updateCount();
    }, Math.min(order * 7, 180));
  });

  setTimeout(() => {
    isSolving = false;
    solveButton.disabled = false;
    solveButton.querySelector("strong").textContent = "פתרו את הלוח";
    validateBoard();
    launchConfetti();
    showToast("החידה נפתרה!", "כל 81 המשבצות הושלמו בהצלחה.", "success");
  }, 650);
}

function clearBoard() {
  if (isSolving) return;
  const hasValues = cells.some((cell) => cell.value);
  if (!hasValues) return;
  saveSnapshot();
  cells.forEach((cell) => {
    cell.value = "";
    cell.dataset.previousValue = "";
    cell.classList.remove("invalid", "solved", "given", "same-value");
  });
  updateCount();
  cells[0].focus();
  showToast("הלוח נקי", "אפשר להתחיל חידה חדשה.", "success");
}

function loadExample() {
  if (isSolving) return;
  if (cells.some((cell) => cell.value)) saveSnapshot();
  EXAMPLE.flat().forEach((value, index) => {
    cells[index].value = value || "";
    cells[index].dataset.previousValue = value ? String(value) : "";
    cells[index].classList.remove("invalid", "solved", "given");
  });
  updateCount();
  validateBoard();
  cells[2].focus();
  showToast("החידה מוכנה", "עכשיו אפשר לנסות לפתור לבד — או לתת לנו לעבוד.", "success");
}

function updateCount() {
  filledCount.textContent = cells.filter((cell) => cell.value).length;
}

function showToast(title, message, type = "error") {
  clearTimeout(toastTimer);
  toastTitle.textContent = title;
  toastMessage.textContent = message;
  toastIcon.textContent = type === "success" ? "✓" : "!";
  toast.classList.toggle("success", type === "success");
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 4200);
}

function launchConfetti() {
  celebration.innerHTML = "";
  const colors = ["#b85638", "#87917c", "#d6a758", "#1f2522", "#e1c9ae"];
  for (let index = 0; index < 58; index += 1) {
    const piece = document.createElement("i");
    piece.className = "confetti";
    piece.style.left = `${Math.random() * 100}%`;
    piece.style.background = colors[index % colors.length];
    piece.style.setProperty("--drift", `${Math.random() * 220 - 110}px`);
    piece.style.animationDelay = `${Math.random() * 0.7}s`;
    piece.style.animationDuration = `${2.2 + Math.random() * 1.4}s`;
    celebration.appendChild(piece);
  }
  setTimeout(() => { celebration.innerHTML = ""; }, 4300);
}

solveButton.addEventListener("click", solve);
clearButton.addEventListener("click", clearBoard);
undoButton.addEventListener("click", undo);
exampleButton.addEventListener("click", loadExample);
document.getElementById("toastClose").addEventListener("click", () => toast.classList.remove("show"));

createBoard();
updateCount();
