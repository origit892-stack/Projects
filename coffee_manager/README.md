# Coffee Manager: Robot Evolution

משחק טייקון קפה לילדים, בקובץ HTML אחד, עם Canvas מלא, שמירה ב-localStorage, קמפיין שלבים, תחרויות, מלאי טרי, שדרוגים, רובוט עזר, ובוט QA שבודק את המשחק בזמן אמת.

## איך מריצים

פותחים את הקובץ:

```text
coffee_manager/index.html
```

אין ספריות חיצוניות ואין שרת חובה. המשחק בנוי ב-vanilla HTML, CSS ו-JavaScript בלבד.

## מבנה הפרויקט

```text
coffee_manager/
  index.html
  README.md
  docs/
    GAME_DESIGN.md
    TECHNICAL_ARCHITECTURE.md
    CAMPAIGN_AND_BALANCE.md
    QA_AGENT.md
    USER_PREFERENCES.md
    NEXT_SESSION_CONTEXT.md
```

## מצב המשחק

זרימת המשחק הנוכחית:

```text
Login -> Level Selection Map -> Stand Mode -> Tournament -> Stage Results -> Level Selection Map
```

ב-Autopilot, כשהבוט מנצח בתחרות, הוא אמור לדלג על מסך הסיום ולהמשיך אוטומטית לשלב הבא כדי לבדוק את כל הקמפיין ברצף.

## העיקרון החשוב

המשחק לא אמור להרגיש כמו Dashboard עסקי. הוא צריך להרגיש כמו משחק ילדים חי, צבעוני, נעים, ויזואלי ופעיל:

- דוכן שחקן ברור.
- לקוחות שנראים כמו בני אדם קטנים, לא נקודות מופשטות.
- תנועה ברחוב.
- שדרוגים שמשנים גם את הגרפיקה, לא רק מספרים.
- תחרות שמרגישה כמו אירוע נפרד.

## מסמכי המשך

לפני שינוי משמעותי בפרויקט, כדאי לקרוא קודם:

1. `docs/NEXT_SESSION_CONTEXT.md`
2. `docs/USER_PREFERENCES.md`
3. `docs/TECHNICAL_ARCHITECTURE.md`
