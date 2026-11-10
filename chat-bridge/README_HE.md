# Chat Bridge 0.1 — תוסף Chrome וגשר MCP מקומי

Chat Bridge מחבר בין שיחת ChatGPT שפתוחה בדפדפן לבין Agents מקומיים כמו Hermes ו-OpenCode. התוסף קורא טקסט שמוצג בשיחה, שומר אותו במסד SQLite מקומי, ומעמיד כלי MCP לחיפוש, קריאה ושליחת הודעות לאותה שיחה פתוחה.

## מה כבר נכלל ב-MVP

- תוסף Chrome מסוג Manifest V3.
- זיהוי הודעות משתמש ו-ChatGPT שמוצגות ב-DOM של השיחה הפתוחה.
- שמירה מקומית בקובץ `~/.chat-bridge/chat-bridge.sqlite3`.
- שרת MCP עם הכלים:
  - `chatbridge_status`
  - `chatbridge_list_conversations`
  - `chatbridge_search_messages`
  - `chatbridge_read_conversation`
  - `chatbridge_send_message`
- אותו מאגר משותף ל-Hermes ול-OpenCode. כל Agent מריץ תהליך MCP מקומי נפרד, ושניהם קוראים את אותו SQLite.
- שליחת הודעות כבויה כברירת מחדל. יש להפעיל את `Allow Agent to send messages` בחלונית התוסף.

## התקנה ב-macOS

1. חלץ את התיקייה למיקום קבוע, לדוגמה `~/Projects/chat-bridge`.
2. פתח Terminal והריץ:

   ```bash
   cd ~/Projects/chat-bridge
   ./install_mac.sh
   ```

   הסקריפט ייצור סביבת Python, יתקין את ספריית MCP, ייצור מפתח מקומי אקראי וישמור את נתיב מסד הנתונים. בסוף הוא יציג Token.

3. פתח `chrome://extensions` ב-Chrome, הפעל **Developer mode**, לחץ **Load unpacked**, ובחר את התיקייה `extension` שבתוך הפרויקט.
4. לחץ על סמל Chat Bridge בסרגל Chrome, היכנס ל-**Settings**, הדבק את ה-Token שהסקריפט הציג ולחץ **Save settings**.
5. לחץ פעמיים על `start.command` שבתיקיית הפרויקט. ייפתח Terminal עם השירות המקומי. השאר את החלון פתוח בזמן השימוש.
6. פתח או רענן שיחה ב-ChatGPT. בחלונית התוסף אמור להופיע `Local bridge connected`.

## חיבור ל-Hermes

פתח `~/.hermes/config.yaml` והוסף את הערך הבא תחת `mcp_servers`. החלף את הנתיב לנתיב המלא של הקובץ `run_mcp.command` אצלך:

```yaml
mcp_servers:
  chat-bridge:
    command: "/Users/USER/Projects/chat-bridge/run_mcp.command"
    args: []
    enabled: true
    timeout: 150
    connect_timeout: 30
```

אם כבר קיים `mcp_servers:`, הוסף רק את המפתח `chat-bridge:` מתחתיו. אל תיצור מפתח `mcp_servers` כפול. אתחל את Hermes.

## חיבור ל-OpenCode

הוסף את הפריט הבא לתוך אובייקט `mcp` בקובץ ההגדרות של OpenCode. החלף לנתיב המלא אצלך:

```jsonc
"mcp": {
  "chat-bridge": {
    "type": "local",
    "command": ["/Users/USER/Projects/chat-bridge/run_mcp.command"],
    "enabled": true,
    "timeout": 150000
  }
}
```

אם כבר קיים `mcp`, הוסף רק את הפריט `chat-bridge`. שמור והפעל מחדש או טען מחדש את OpenCode.

## איך משתמשים

1. פתח ב-Chrome את שיחת ChatGPT שברצונך לשמור.
2. התוסף שומר את ההודעות שהדפדפן מציג.
3. ה-Agent מפעיל `chatbridge_list_conversations` כדי למצוא את השיחה.
4. ה-Agent מפעיל `chatbridge_read_conversation` כדי לקרוא אותה, או `chatbridge_search_messages` כדי למצוא החלטה/נושא בשיחות שמורות.
5. כדי לדבר עם ChatGPT, השאר את השיחה הרלוונטית פתוחה, הפעל בחלונית התוסף את `Allow Agent to send messages`, ואז ה-Agent יכול להפעיל `chatbridge_send_message` עם מזהה השיחה וההודעה.

## מגבלות חשובות

- זהו אוטומציה של ממשק האתר, לא API רשמי של ChatGPT. שינוי במבנה האתר עלול לחייב עדכון של בוררי ה-DOM.
- נשמר רק טקסט שהדפדפן טען והציג. אם יש הודעות ישנות שלא נטענו, גלול למעלה כדי לטעון אותן. המאגר עלול להכיל רק חלק מהשיחה.
- קבצים מצורפים, תמונות, אודיו ותוכן לא-טקסטואלי אינם נשמרים בגרסה זו.
- שליחה פועלת רק בשיחה שכבר פתוחה ומתאימה ב-ChatGPT. ה-MVP אינו פותח שיחה חדשה או מחליף טאבים.
- אם תיבת ההודעה כבר מכילה טיוטה שלא נשלחה, התוסף מסרב לשלוח כדי לא למחוק את הטקסט שלך.
- מסד הנתונים המקומי אינו מוצפן על ידי התוכנה. שמור על הרשאות המשתמש ב-macOS ואל תשתף את ה-Token.

## בדיקות

מתוך תיקיית הפרויקט:

```bash
python3 -m unittest discover -s host/tests -v
python3 -m py_compile host/db.py host/bridge_daemon.py host/mcp_server.py
```

## אבטחה

- השירות המקומי מאזין רק על `127.0.0.1:8765`.
- בקשות מהתוסף דורשות Token אקראי ו-Origin מסוג `chrome-extension://`.
- התוסף מבקש גישה רק לארבעת אתרי הספקים (ChatGPT, Claude, Gemini, Grok) ולשירות המקומי.
- אין סנכרון ענן ואין כתובת ציבורית.
- שליחת הודעות על ידי Agent כבויה כברירת מחדל ודורשת הפעלה מפורשת בחלונית התוסף.

## גרסה 2.0 — תמיכה במספר ספקים (2026-11)

- **ספקים נתמכים:** ChatGPT, Claude, Gemini, Grok. כל ספק מקבל אדפטר DOM נפרד (`extension/adapter-*.js`) שמשתף תעבורה משותפת (`extension/shared.js`).
- **מאגר:** נוסף עמודת `provider` לכל השורות. מאגר v1 קיים ימוגר אוטומטית בהפעלת הדמון (כל השורות הקיימות מקבלות `provider='chatgpt'`).
- **ממשק חדש:** לכל כלי MCP אפשר להעביר פרמטר `provider` (ריק = כל הספקים). כלי חדש: `chatbridge_provider_status` — מראה כמה שיחות/הודעות לכל ספק, מתי נכנתה האחרונה, והאם יש כשל בצילום (עם סיבה).
- **חלון התוסף:** במקום `Failed to fetch` כשהדמון כבוי — מסך **Daemon offline** מסודר עם הוראות הפעלה, ורשימת סטטוס לכל ספק.
- **מצב אימות:** אדפטר ה-ChatGPT נבנה מהבוררים שנבדקו ב-2026-11-10. אדפטרי Claude/Gemini/Grok הם בדיקה-בטוחה (best-effort) — אם בחלון התוסף או ב-`chatbridge_provider_status` מופיע `capture failed`, צריך לעדכן את `extension/adapter-<provider>.js` לפי מה שנראה ב-DevTools.
- **תאימות:** התוסף v1 ממשיך לעבוד מול דמון v2 (אותו token, אותו מאגר), ולהפוך לחלקית.
