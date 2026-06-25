# Technical Architecture

## כלל מרכזי

הפרויקט הוא single-file app:

```text
index.html
```

אין ספריות חיצוניות. כל הקוד נמצא באותו קובץ:

- HTML למסכים ולכפתורים.
- CSS לעיצוב, glass panels, login, map, toolbar, modals.
- JavaScript למנוע המשחק, Canvas rendering, שמירה, QA agent, תחרויות ושלבים.

## Canvas

כל המשחק הוויזואלי המרכזי נצבע דרך HTML5 Canvas.

פונקציות ציור מרכזיות:

- `draw()`
- `drawWorld()`
- `drawStand(shop, main)`
- `drawPerson(customer)`
- `drawTournamentPlots()`
- `drawEffects()`
- `drawSteam()`
- `drawCoffeeCup()`
- `drawMachine()`
- `drawSeller()`
- `drawRobot()`

## State Machine

המשתנה המרכזי:

```js
let mode = "login";
```

ערכים עיקריים:

- `login`
- `map`
- `stand`
- `tournament`
- `complete`

הזרימה הרצויה:

```text
login -> map -> stand -> tournament -> complete -> map
```

ב-Autopilot:

```text
stand -> tournament -> next stage stand
```

כלומר הבוט לא אמור להיתקע במסך תוצאות או במפת שלבים.

## נתוני שלבים

השלבים מוגדרים במערך:

```js
const stages = [...]
```

כל שלב כולל:

- `name`
- `target`
- `targetType`
- `targetValue`
- `revenueGoal`
- `tournamentSeconds`
- `standSpawn`
- `tournamentSpawn`
- `rivals`

חשוב: משימות השלב חייבות להגיע רק מהאובייקט הפעיל בתוך `stages`.

אין להחזיר hardcoded targets מתוך `stageObjectives()`.

## פונקציות משימות

פונקציות מרכזיות:

- `stageObjectives()`
- `stageCompletion()`
- `stageReadyForTournament()`
- `objectiveSummary()`

ההתנהגות הרצויה:

- Stage 1 דורש רק `served: 30`.
- Stage 2 דורש רק להגיע פעם אחת ל-500 שקל.
- Stage 2 לא צריך להיכשל אם השחקן הגיע ל-500 ואז בזבז כסף.

לכן יש לשחקן `peakCash`, שמייצג את סכום הכסף הגבוה ביותר שהגיע אליו במהלך אותו שלב.

## נתוני שחקן

אובייקט מרכזי:

```js
const player = {
  name,
  cash,
  peakCash,
  revenue,
  served,
  wasted,
  lost,
  price,
  inventory,
  queue,
  loan,
  upgrades,
  x,
  y
}
```

`peakCash` חשוב למשימות מסוג `cash`.

## מלאי

עלות מלאי:

```js
const STOCK_COSTS = { beans: 18, milk: 12 };
```

כל lot במלאי:

```js
{ type, units, age, bornAt, expectedLife, warned }
```

התפוגה הרצויה:

```text
20 seconds exactly
```

פונקציות קשורות:

- `buyStock(type)`
- `ageInventory(dt)`
- `useInventory(shop)`
- `consume(type)`
- `stockUnits(type)`

## תחרות

פונקציות מרכזיות:

- `startTournament()`
- `finishTournament()`
- `calculateStars(won, topCpu)`
- `updateCompetitorBrains(dt)`

כללים:

- `startTournament()` צריך להחזיר מיד אם `stageReadyForTournament()` שקרי.
- בתחרות אי אפשר לקנות מלאי או שדרוגים.
- בוטים יכולים לשנות מחיר ולהשתדרג כדי להקשות.
- אם השחקן מנצח ומקבל לפחות כוכב אחד, השלב הבא נפתח.

## שמירה

השמירה היא localStorage.

צריך לשמור:

- שם הדוכן.
- שלב נוכחי.
- התקדמות שלבים.
- כוכבים.
- שיאים.
- נתוני שחקן רלוונטיים, כולל `peakCash`.

פונקציות שכדאי לבדוק כשמשנים שמירה:

- `savePayload()`
- `saveGame()`
- `applySave(data)`
- `defaultProgress()`
- `ensureProgress()`

## Hotkeys

המקשים חייבים להמשיך לעבוד:

- `Q`: קניית beans.
- `E`: קניית milk.
- `Space`: שירות לקוח.

ה-Autopilot משתמש באותן פעולות מכניות או בקריאות ישירות מקבילות:

- `qaBuyStock("beans")`
- `qaBuyStock("milk")`
- `qaServe()`
