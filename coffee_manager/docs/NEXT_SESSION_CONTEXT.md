# Next Session Context

קרא את המסמך הזה ראשון כשחוזרים לעבוד על `coffee_manager`.

## מיקום הפרויקט

```text
/Users/origan/Documents/Projects/coffee_manager
```

הקובץ המרכזי:

```text
/Users/origan/Documents/Projects/coffee_manager/index.html
```

## מה הפרויקט

משחק Canvas single-file בשם:

```text
Coffee Manager: Robot Evolution
```

המשחק הוא טייקון קפה לילדים עם:

- התחברות ושמירה.
- מפת שלבים.
- מצב ניהול דוכן.
- תחרות.
- כוכבים.
- מלאי שמתקלקל.
- שדרוגים.
- רובוט עזר.
- הלוואות.
- AI Autopilot QA.

## הדברים הכי חשובים לא לשבור

1. Stage 1 דורש 15 לקוחות + להגיע פעם אחת ל-₪250.
2. Stage 2 דורש 24 לקוחות + להגיע פעם אחת ל-₪360, באמצעות `peakCash`.
3. `stageObjectives()` חייב לקרוא רק מתוך `stages[stageIndex]`.
4. `stageReadyForTournament()` חייב להתבסס רק על `stageObjectives()`.
5. כפתור התחרות נעול עד 100% משימה.
6. ב-Autopilot, אחרי ניצחון בתחרות, הבוט צריך לעבור ישר לשלב הבא.
7. מלאי פולים וחלב מתקלקל אחרי 20 שניות בדיוק.
8. עלות מלאי נוכחית: beans ₪18, milk ₪12.
9. Hotkeys: Q, E, Space.
10. לא להחזיר את המשחק למראה dashboard סטטי.
11. בלוח ה-Campaign, רק השורה של `Stage Task` היא משימה. Freshness ו-Robot הם Status Only ולא משפיעים על פתיחת תחרות.
12. ב-Stand Mode/אימון אישי מציגים רק את החנות של השחקן. חנויות מתחרות מופיעות רק בתחרות.
13. לשמור על ביצועים: יש תקרות ללקוחות, particles ו-floating texts כדי למנוע לאגים.
14. שני הכוכבים הראשונים מגיעים ממשימות ההכנה. הכוכב האחרון הוא תמיד ניצחון בתחרות.

## שינוי אחרון חשוב

המשתמש התלונן שהמשימות קשות מדי ולא פרופורציונליות לשלבים. האיזון הנוכחי רך יותר:

- Stage 1: Serve 15 customers.
- Stage 1 extra: Reach ₪250 once.
- Stage 2: Serve 24 customers + Reach ₪360 once.
- Stage 3: Earn ₪650 revenue + Reach ₪520 once + Robot total level 2.
- Stage 4: Earn ₪900 revenue + Reach ₪700 once + Robot total level 4.
- Stage 5: Earn ₪1200 revenue + Reach ₪900 once + Robot total level 7.

הכוכב האחרון בכל שלב הוא תחרות. פתיחת שלב הבא דורשת ניצחון בתחרות.

לפני כן המשתמש גם ביקש שמשימת כסף תהיה "להגיע פעם אחת במשחק לסכום היעד".

השינוי הנכון:

- להוסיף/להשתמש ב-`player.peakCash`.
- לעדכן `peakCash` בכל פעם שכסף עולה, כולל מכירה והלוואה.
- לאפס `peakCash` ל-startingCash ב-`resetStage(true)`.
- לשמור `peakCash` ב-localStorage.
- ב-`stageObjectives()` עבור targetType `"cash"` להשתמש ב-`player.peakCash || player.cash`.

ה-UI צריך להציג:

```text
Reach cash once: 166/360
```

ולא:

```text
Build cash: 166/260
```

אם עדיין מופיע `Build cash`, חפש קוד ישן/כפול:

```sh
rg -n "Build cash|servedTargets|cashTargets|stageObjectives|objectiveSummary|ui.board.innerHTML" coffee_manager/index.html
```

אם Freshness או Robot נראים כמו משימות, בדוק את `renderUi()` ואת ה-CSS של `.board-section`, `.rank.objective`, `.rank.info`.

## איך לבדוק מהר

בדיקת syntax ל-JavaScript שבתוך HTML:

```sh
node -e 'const fs=require("fs"); const html=fs.readFileSync("coffee_manager/index.html","utf8"); const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join("\n"); new Function(scripts); console.log("JS syntax OK");'
```

בדיקות טקסט חשובות:

```sh
rg -n "Build cash|servedTargets|cashTargets|peakCash|Reach cash once|STOCK_COSTS|stageObjectives|finishTournament" coffee_manager/index.html
```

## אזורי קוד חשובים

- `const stages`: הגדרת השלבים.
- `const player`: מצב השחקן.
- `stageObjectives()`: משימות השלב.
- `stageReadyForTournament()`: נעילת תחרות.
- `startTournament()`: מעבר לתחרות.
- `finishTournament()`: סיום תחרות, כוכבים, פתיחת שלב הבא.
- `resetStage()`: איפוס שלב.
- `runAutopilot()`: פעולות הבוט.
- `inspectQa()`: בדיקות דיבאג.
- `renderUi()`: עדכון הפאנלים.
- `drawWorld()`, `drawStand()`, `drawPerson()`: ציור Canvas.

## העדפה עיצובית לזכור

המשתמש רוצה "משחק ילדים נחמד" ולא ניאון-דאשבורד. אם עובדים על עיצוב:

- לצייר דוכנים ברורים וחמודים.
- להשתמש בצבעים נעימים.
- להראות סמלי קפה, לאטה, פולים, בריסטה ורובוט.
- לסדר תחרות בצורה מאוזנת יותר, רצוי אזור/ריבוע תחרות.
- בתחרות לא להפריד את דוכן השחקן משלושת המתחרים. כולם צריכים להרגיש באותו שוק מרכזי.
- באימון/שדרוג אישי לא להציג חנויות מתחרות בכלל.
- להסיר פלטפורמות או "במות" שנראות מכוערות.

## אם המשתמש אומר שהשינוי לא נקלט

בדוק לפי הסדר:

1. האם נערך `/Users/origan/Documents/Projects/coffee_manager/index.html`.
2. האם קיימת מחרוזת ישנה עם `rg`.
3. האם `renderUi()` באמת משתמש ב-`objectiveSummary()`.
4. האם יש hardcoded HTML שמציג טקסט ישן.
5. האם הדפדפן צריך hard refresh.
6. האם localStorage ישן מחזיר state מוזר, ואם כן צריך לשמור תאימות או reset ברור.
