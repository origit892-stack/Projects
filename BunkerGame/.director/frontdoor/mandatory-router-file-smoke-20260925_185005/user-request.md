בצע עבורי implementation מלא בתוך הספרייה הזאת בלבד:

/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/mandatory-router-file-smoke-20260925_185005/work

אני צריך ארבעה artifacts:

1. backend.txt עם התוכן המדויק BACKEND=READY
2. frontend.txt עם התוכן המדויק FRONTEND=READY
3. tests.txt עם התוכן המדויק TESTS=PASS
4. release.txt עם התוכן המדויק RELEASE=READY

backend ו-frontend הם workstreams בלתי תלויים ויכולים להתבצע במקביל.

tests חייב להתבצע רק אחרי ששניהם הושלמו.
הוא חייב לקרוא את backend.txt ואת frontend.txt ולאמת את התוכן המדויק שלהם
לפני יצירת tests.txt.

release חייב להתבצע רק אחרי ש-tests עבר בהצלחה.
לפני יצירת release.txt יש לקרוא ולאמת את שלושת ה-artifacts הקודמים.

אל תשנה שום דבר מחוץ ל-sandbox הזה.

בצע את העבודה בפועל באופן אוטונומי עד להשלמה מאומתת.
