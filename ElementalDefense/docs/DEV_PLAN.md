ניתוח מקדים של האפיון (GDD v3.0) לקראת תכנון הפיתוח:

⚬ ה-Vertical Slice המינימלי: ייצור מפה (גריד 13×13, מסלול רציף של מינימום 40 אריחים) → הצבת תושבת Turret בעלות 100 זהב → שיבוץ אבן אש וגל ראשון של אויבי Runt → בניית אבן חומצה וביצוע מיזוג (Napalm Launcher) → סיום הריצה בניצחון או בנפילת הליבה מתחת ל-20 HP.
⚬ תוכן ל-Post-Launch: מנגנון ה-Co-op (1–4 שחקנים), גילדות (חוזים, מצודה, Cyber Cores), ואירועי Live-Ops / Battle Pass. אלו אינם קריטיים ללופ הליבה.
⚬ נקודות אינטגרציה קריטיות בין מסלולים: Remotes כמו PlaceTower, MergeGem, ChooseCard, וסכמות נתונים מרכזיות כמו TowerConfig ו-PlayerProfile.
⚬ החלטות אנושיות דחופות לפני Stage 0: אישור סופי של מנוע המשחק (Roblox מול Unity/Godot), שפת ברירת מחדל (עברית מול אנגלית), וטון הדיבור של A.R.I.A.

1. מפת שלבים 0–8

Stage	שם	מטרה	משך (ימים)	תלות	שער יציאה מדיד	מה לא נכלל
0	Infra & Schemas	הקמת שלד פרויקט, Git, DataStores, וסכמות JSON/Luau	1	none	Mocks מחזירים נתונים תקינים דרך Remotes	לוגיקת קרב, UI, אלגוריתם מפה
1	Core Slice	לופ בסיסי: יצירת מסלול, תושבת Turret, אבן אש, וגל Runt	3	Stage 0	אפשר לשחק 5 דקות: הריגת אויב או דליפה לליבה (20 HP)	קלפים, מיזוגים, כלכלה (N), אויבים מתקדמים
2	Merge & Econ	שילוב חוקי כלכלה (עלות 100×1.15^N), ושאר היסודות למיזוג כפול	4	Stage 1	בנייה + 2 מיזוגים בזמן ריצה; זהב מתעדכן בצד שרת	מיזוגים משולשים (T3/T4), בוסים
3	Drafting	חפיסת 20 הקלפים, לוגיקת דראפט (3 הצעות, Reroll)	4	Stage 2	סיום גל פותח UI דראפט שמשפיע על סטטים	עץ התדר, שמירת מטא
4	Act I (1–20)	בוס Hive Queen / Goliath Prime, אקטיבים (Overclock)	5	Stage 3	השלמת 20 גלים ללא קריסות שרת	מערכות 2-3 (גלים 21-50)
5	Meta Progression	עץ תדר (5 ענפים), שרדס, שמירת DataStore	4	Stage 4	שרדס מריצה קודמת משמשים לשדרוג Node בפרופיל	Mutators, מצבי משחק שונים
6	Acts II & III	גלים 21–50, מיזוגי T3/T4, מכניקות בוסים מתקדמות	5	Stage 5	ריצה חלקה של 50 גלים (כ-35 דקות) בסימולציה	מצב Endless
7	UX, Audio, FTUE	טוטוריאל (6 פרקים של A.R.I.A), חלקיקים, נגישות	4	Stage 6	80% אחוזי הצלחה במעבר טוטוריאל במכשירי יעד	לוקליזציה לשפות P1/P2
8	Co-op & Social	שרת עד 4 שחקנים, רפליקציה מלאה, גילדות בסיסיות	7	Stage 7	4 שחקנים באותו חדר, זהב נפרד, בנייה ללא חפיפות	Battle Pass, חוזים מורכבים

2. לוח משימות

ID	Stage	Track	Owner	קבצים	blocked_by	שעות	DoD	בדיקה אוטומטית / שער
T1	0	A	OpenCode-1	WaveDirector.lua, CombatService.lua	none	4	מחלקות שרת בסיסיות קיימות, Authority נאכף	TestService:Run("CombatAuth")
T2	0	B	OpenCode-2	EconomyService.lua, TowerConfig.json	none	4	נתוני קונפיגורציה נטענים בשרת בזמן ריצה	TestService:Run("ConfigLoad")
T3	0	C	OpenCode-3	HUDController.lua, Remotes.lua	none	4	חוזים (Remotes) מוגדרים במדויק ומחוברים ל-UI ריק	TestService:Run("RemotesExist")
T4	1	A	OpenCode-1	MapGenerator.lua	T1	4	אלגוריתם מייצר 40 אריחים רציפים ללא לולאות	TestService:Run("PathValidation")
T5	1	B	OpenCode-2	EconomyService.lua	T2	3	חוקי הצבת Turret בעלות 100 ומערכת N ממומשים בשרת	TestService:Run("ServerEcon")
T6	1	C	OpenCode-3	BuildMenu.lua	T3	4	תפריט מאפשר גרירה, נבדק RTL ומובייל (Touch)	TestService:Run("BuildUI_RTL")

tasks:
  - id: T1
    stage: 0
    track: A (Gameplay)
    owner: OpenCode-1
    files: [ "Server/WaveDirector.lua", "Server/CombatService.lua" ]
    blocked_by: none
    estimation_hours: 4
    dod: "Classes instantiated, basic Server Authority rules applied."
    test_command: "rojo build && run_tests --suite CombatAuth"
  - id: T2
    stage: 0
    track: B (Systems)
    owner: OpenCode-2
    files: [ "Shared/Configs/TowerConfig.json", "Server/EconomyService.lua" ]
    blocked_by: none
    estimation_hours: 4
    dod: "JSON Configs load successfully at runtime."
    test_command: "run_tests --suite ConfigLoad"
  - id: T3
    stage: 0
    track: C (Client)
    owner: OpenCode-3
    files: [ "Client/HUDController.lua", "Shared/Remotes.lua" ]
    blocked_by: none
    estimation_hours: 4
    dod: "RemoteEvents created, validated inputs defined."
    test_command: "run_tests --suite RemotesExist"
  - id: T4
    stage: 1
    track: A (Gameplay)
    owner: OpenCode-1
    files: [ "Server/MapGenerator.lua" ]
    blocked_by: [ "T1" ]
    estimation_hours: 4
    dod: "Generates 13x13 grid with 40 min continuous tiles."
    test_command: "run_tests --suite PathValidation"
  - id: T5
    stage: 1
    track: B (Systems)
    owner: OpenCode-2
    files: [ "Server/EconomyService.lua" ]
    blocked_by: [ "T2" ]
    estimation_hours: 3
    dod: "Turret placement deducts 100 gold, strictly on server."
    test_command: "run_tests --suite ServerEcon"
  - id: T6
    stage: 1
    track: C (Client)
    owner: OpenCode-3
    files: [ "Client/BuildMenu.lua" ]
    blocked_by: [ "T3" ]
    estimation_hours: 4
    dod: "Drag-and-drop build UI works. Supports RTL and Mobile Touch."
    test_command: "run_tests --suite BuildUI_RTL"


3. גרף תלויות (Mermaid)

graph TD
    %% Stage 0
    T1[T1: Track A - Server Architecture]
    T2[T2: Track B - Schemas & Configs]
    T3[T3: Track C - Remotes & Basic UI]
    Gate0((Gate 0: Schemas Ready))
    
    T1 --> Gate0
    T2 --> Gate0
    T3 --> Gate0

    %% Stage 1
    Gate0 --> T4[T4: Track A - Map Gen]
    Gate0 --> T5[T5: Track B - Econ N-Scaling]
    Gate0 --> T6[T6: Track C - Build HUD]
    Gate1((Gate 1: MVS Core Loop))

    T4 --> Gate1
    T5 --> Gate1
    T6 --> Gate1
    
    %% Stage 2
    Gate1 --> S2A[S2A: Elements & Status]
    Gate1 --> S2B[S2B: Merge Logic Server]
    Gate1 --> S2C[S2C: Merge VFX & UI]
    Gate2((Gate 2: Merging Complete))

    S2A --> Gate2
    S2B --> Gate2
    S2C --> Gate2


4. תוכנית השבוע הראשון (Stage 0–1)

יום	Track A (OpenCode-1 / Gameplay)	Track B (OpenCode-2 / Systems)	Track C (OpenCode-3 / Client)	נקודות סינכרון / אימות
1	הקמת שלד WaveDirector ו-CombatService.	כתיבת TowerConfig, EnemyConfig JSONs.	הקמת Remotes וזרימת HUD ריק.	סוף יום 1: אישור חוזי Remotes משותפים בין כל הטרמינלים.
2	מערכת ייצור מפה (BFS Validation).	לוגיקת כלכלה (עלות תושבת, תקרת זהב).	תפריט גרירת תושבת למסך.	אמצע יום 2: Handoff Task – Track B מזין כלכלה ל-Remotes של Track C.
3	מערכת Pathfinding של אויבים על המסלול.	חישוב נזק (Server Authority) מול Core HP.	עיצוב אינדיקציה ויזואלית לאזור בנייה (Pads).	סוף יום 3: Stage 0 Exit Gate (CI עבר).
4	שילוב אויב (Runt) ב-1.2 Tiles/sec.	חיבור מחירי גל (הכנסת גל 150+35w).	אינדיקציית דליפת אויב ומד ה-Core HP.	אמצע יום 4: אינטגרציה מקצה לקצה. לקוח מזמן גל.
5	לוגיקת נזק Hitscan עבור Turret.	הוספת שלל אויב (Bounty) לשרת.	ליטוש Mobile Touch וכיול RTL.	סוף יום 5: Stage 1 Exit Gate - הדגמה חיה של ה-Vertical Slice.

5. אסטרטגיית Git ועבודה מקבילה

1. מבנה ענפים:
  ⚬ main (מוגן, נעול לדחיפה ישירה).
  ⚬ stage/0, stage/1 (ענפי אינטגרציה לכל שלב).
  ⚬ ענפי עבודה: feature/A-map-gen, feature/B-econ-rules, feature/C-hud.
2. חוקי Handoff: מכיוון שלכל קובץ יש בעלים אחד, אם Track C צריך לחשוף פונקציה מ-WaveDirector.lua (השייך ל-A), C פותח Handoff Task ל-A. A מממש את הפונקציה (Getter), דוחף ל-stage/X, ורק אז C מושך (Pull) ומשתמש.
3. פתרון קונפליקטים: Hermes (Technical Producer) מקצה קונפליקטים למי שכתב את התשתית של אותו קובץ (Ownership). המיזוג מתבצע באמצעות Rebase כדי לשמור על היסטוריה שטוחה ונקייה.
4. Merge: לתוך main רק בסיום מלא של Stage ולאחר מעבר CI/CD מלא וקבלת חתימת ה-Tech Lead.

6. שערי אימות (Validation Gates)

Stage	בדיקה אוטומטית (CI)	בדיקה ידנית (QA)	מדד הצלחה	חותם (Sign-off)
0	Run All Unit Tests, Lint (Luau)	עבודה עם Console לאימות פקודות.	100% כיסוי Remotes	Hermes
1	סקריפט מריץ ריצה עיוורת (Bot) שמפסיד בכוונה בגל 1	שחקן אנושי מציב מגדל במובייל.	הצלחה ב-100% של טסט חסימת רמאות (ניסיון הצבה ללא זהב).	Tech Lead
2	סימולציית N: בניית 20 מגדלים מוודאת שהזהב מסתנכרן.	ביצוע מיזוג T2 ואימות ויזואלי של פיצוץ.	ירידה צפויה של 180 זהב + אימות שרת.	Tech Lead
3	DraftProbabilitiesTest: בדיקת התפלגות של 10,000 קלפים.	חזרה ללחיצת Reroll ובדיקת עלויות.	Fallback ל-Rarity עובד כראוי.	Tech Lead

7. קבצי ניהול מטא (תוכן מלא להקמה)

AGENTS.md

# סוכני פיתוח (Terminals)
* **Hermes (Tech Lead/Producer):** תזמור, ניהול תלויות (blocked_by), בדיקת שערי יציאה, הקצאת Pull Requests ועדכון DECISIONS.md.
* **OpenCode-1 (Track A):** מומחה Gameplay שרת. אחראי על: `WaveDirector`, אויבים, בוסים, יכולות ליבה.
* **OpenCode-2 (Track B):** מומחה Systems/Data. אחראי על: כלכלה, DataStores (ProfileService), עץ תדר, קונפיגורציות[span_50](start_span)[span_50](end_span).
* **OpenCode-3 (Track C):** מומחה Client/UI/UX. אחראי על: HUD, מובייל, נגישות, לוקליזציה (RTL), מערכת חלקיקים.


TASKS.md
מכיל את טבלת לוח המשימות ובלוק ה-YAML מסעיף 2.

OWNERSHIP.md

# בעלות קבצים (נאכף כדי למנוע התנגשויות)
* **Track A (Server Gameplay):** `Server/WaveDirector.lua`, `Server/MapGenerator.lua`, `Server/CombatService.lua`.
* **Track B (Server Systems):** `Server/EconomyService.lua`, `Server/ProfileManager.lua`, `Shared/Configs/*`.
* **Track C (Client UI/VFX):** `Client/HUDController.lua`, `Client/BuildMenu.lua`, `Client/VFXManager.lua`.
* **Handoff:** שינוי בקובץ שלא בבעלותך דורש משימת העברה לבעלים.


DECISIONS.md

# יומן החלטות ארכיטקטורה
* **09/11/2026 (Hermes):** חלוקת הפיתוח ל-3 Tracks נפרדים לחלוטין.
* **09/11/2026 (Hermes):** סמכות שרת מוחלטת (Server Authority) - לקוח שולח אך ורק כוונות (Intent) כגון `PlaceTower`[span_51](start_span)[span_51](end_span).
* **09/11/2026 (Hermes):** כל קבצי הכלכלה נוצרים כ-Hot Configs ב-JSON לטעינה בזמן אמת ב-ReplicatedStorage[span_52](start_span)[span_52](end_span).


8. עשרה סיכונים תפעוליים של עבודה מקבילה + מיטיגציה

1. סיכון: Track C בונה UI ללא Remotes מוכנים מ-Track A. מיטיגציה: Stage 0 כופה הגדרת חוזים (Mocks) לפני לוגיקה.
2. סיכון: קונפליקטים במיזוג קבצי DataStore. מיטיגציה: בעלות קבצים מוחלטת (OWNERSHIP.md).
3. סיכון: צוואר בקבוק במשימות Handoff. מיטיגציה: משימות Handoff מקבלות עדיפות P0 ב-Sprints.
4. סיכון: שינוי נוסחת הכלכלה (N) שובר את הדראפט של Track B. מיטיגציה: שום מספר כלכלי לא משתנה ללא אישור והרצת סקריפט הסימולציה.
5. סיכון: Client מיישם לוגיקת נזק פנימית. מיטיגציה: Code Review אוטומטי שחוסם פונקציות מתמטיות של אויבים בצד Client.
6. סיכון: RTL דופק את פריסת ה-HUD לאחר אינטגרציה. מיטיגציה: כל רכיב UI נבדק אוטומטית במצב מראה (RTL flag) ב-Stage 1.
7. סיכון: העמסת אירועי רשת (Remotes Spam). מיטיגציה: מערכת Rate Limiting כחלק מ-Stage 0 בצד שרת.
8. סיכון: חריגה משמעותית מתקציב הזיכרון (120MB לקוח). מיטיגציה: Memory snapshot בסוף כל Stage שחוסם מעבר אם יש דליפה.
9. סיכון: Track B (מטא) לא מסתנכרן עם Track A (גל משחק). מיטיגציה: יצירת Event Bus מרכזי (OnWaveEnd) כבר ב-Stage 1.
10. סיכון: חוסר יישור קו טכני. מיטיגציה: Vertical slice (Stage 1) מחייב את כולם לייצר מוצר עובד תוך שבוע לפני שממשיכים לרוחב.

9. החלטות פתוחות (Human input before Stage 0)

על פי סעיף 27.3 ב-GDD, נדרשות ההחלטות האנושיות הבאות לפני תחילת קידוד Stage 0:

1. מנוע משחק: האם מאשרים סופית פיתוח ב-Roblox (Luau/DataStores)? (הארכיטקטורה במסמך נגזרה מכך).
2. לוקליזציה ראשית: האם לפתח את ממשק הבסיס בעברית ב-RTL או באנגלית עם כיווניות שמאל-לימין כברירת מחדל?
3. היקף כמותי ל-Launch: האם מתחייבים לריצה של 50 גלים (כ-30–38 דק') כבר בשחרור, או מקצצים ל-40 כ-MVP?
4. מצב Co-op: האם להכניס את ארכיטקטורת ה-Multiplayer (Stage 8 בתוכנית שלי) לגרסת ה-Launch או שזה מיועד ל-Post-Launch מוחלט?
5. טון A.R.I.A: אישור הטון ("מודאגת"/דרמטית או טכנית נטו) כדי להתחיל את הקלטות האודיו (Track C).