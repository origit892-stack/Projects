const LOCATIONS = [
  {
    name: "דלת הפלדה הראשית",
    detail: "המתכת משמיעה חריקה ארוכה, כאילו מישהו בוחן מבחוץ כמה כוח נשאר לה."
  },
  {
    name: "חדר מסנני האוויר",
    detail: "אבק אפור רוקד מול פנס החירום והאוויר מרגיש כבד יותר בכל נשימה."
  },
  {
    name: "מחסן השימורים",
    detail: "קופסאות חלודות זזות על המדפים, ואיש לא מוכן להישבע שהן היו שם בבוקר."
  },
  {
    name: "מכלי המים",
    detail: "טפטוף קבוע מהדהד בחדר השירות ונשמע חזק מדי בשביל משהו כל כך קטן."
  },
  {
    name: "חדר הגנרטור",
    detail: "הגנרטור משתעל בפעימות קצרות, והאור בבונקר רועד עם כל נשימה שלו."
  },
  {
    name: "המרפאה המאולתרת",
    detail: "ריח חומר חיטוי ישן מסתיר משהו חמוץ יותר, והאנשים מתחילים לדבר בלחש."
  },
  {
    name: "מנהרת השירות",
    detail: "הבטון מזיע לחות, וסימני גרירה דקים נמשכים אל תוך החושך."
  },
  {
    name: "חדר הקשר",
    detail: "הרדיו קולט קטעי מילים, נשימות, וצליל נמוך שחוזר בכל כמה שניות."
  },
  {
    name: "אזור המגורים",
    detail: "שמיכות, תיקים ועיניים עייפות ממלאים את החלל הצפוף."
  },
  {
    name: "המטבחון",
    detail: "הסירים ריקים, אבל כולם עדיין מסתכלים לשם כאילו משהו יכול להופיע."
  },
  {
    name: "פתח האוורור המזרחי",
    detail: "שריקה חלשה עוברת בתעלה, ואז נפסקת בבת אחת."
  },
  {
    name: "ארון הכלים",
    detail: "מפתח ברגים חסר, והסימן באבק אומר שמישהו לקח אותו לא מזמן."
  },
  {
    name: "מגורי הילדים הישנים",
    detail: "ציור דהוי על הקיר נראה כמעט חדש באור האדום של החירום."
  },
  {
    name: "חדר המפות",
    detail: "סיכות חלודות מסמנות דרכים החוצה, אבל חלק מהקווים נמחקו בלחות."
  },
  {
    name: "פיר המעלית האטום",
    detail: "דפיקה חלשה עולה מלמטה, רחוקה מספיק כדי להישמע כמו זיכרון."
  },
  {
    name: "מקלחות החירום",
    detail: "רצפה קרה, צינורות חשופים וריח מתכתי מזכירים לכולם כמה מעט מים נשארו."
  }
];

const INCIDENTS = [
  {
    title: "סימני פריצה",
    problem: "נמצאו שריטות טריות ומנעול משוחרר.",
    optionA: "לחזק את המקום מיד",
    resultA: "העבודה מחזירה תחושת שליטה, אבל היא גובה אספקה ואנרגיה.",
    effectA: { food: -1, water: -1, morale: 6 },
    optionB: "להשאיר שומר בלבד",
    resultB: "חסכתם משאבים, אך השמועה על הפריצה עוברת בין כולם.",
    effectB: { food: 0, water: 0, morale: -9 }
  },
  {
    title: "תקלה במערכת",
    problem: "לוח הבקרה מהבהב בקצב לא אחיד ומסרב להירגע.",
    optionA: "לבצע תיקון מסוכן",
    resultA: "התיקון מצליח חלקית, אבל המתח מסביב למערכת נשאר באוויר.",
    effectA: { food: -1, water: 2, morale: -4 },
    optionB: "לנתק את המערכת עד הבוקר",
    resultB: "הבונקר שקט יותר, אך המחיר יורגש במדדים.",
    effectB: { food: 0, water: -2, morale: 3 }
  },
  {
    title: "ריב בין ניצולים",
    problem: "שני אנשים מתווכחים בקול והקבוצה מתחילה לבחור צדדים.",
    optionA: "לפשר ביניהם",
    resultA: "הפיוס לא מושלם, אבל כולם רואים שמישהו עדיין מנהל את המקום.",
    effectA: { food: -1, water: 0, morale: 9 },
    optionB: "להעניש את שניהם",
    resultB: "השקט חוזר מהר, יחד עם מבטים קשים יותר.",
    effectB: { food: 1, water: 0, morale: -12 }
  },
  {
    title: "ממצא חשוד",
    problem: "חפץ עטוף בבד נמצא בפינה שאיש לא ניגש אליה שבועות.",
    optionA: "לפתוח בזהירות",
    resultA: "מצאתם משהו שימושי, אבל האווירה סביב הממצא לא נעימה.",
    effectA: { food: 2, water: 0, morale: -5 },
    optionB: "לאטום את האזור",
    resultB: "הסיכון נעלם, אבל גם האפשרות למצוא אספקה.",
    effectB: { food: -1, water: 0, morale: 5 }
  },
  {
    title: "בקשת עזרה מבחוץ",
    problem: "קול מעבר לקיר מתחנן לסיוע ומכיר את שם אחד הניצולים.",
    optionA: "לפתוח חריץ בדלת",
    resultA: "הקשר האנושי מחזק את האנשים, גם אם הוא עולה במשאבים.",
    effectA: { food: -2, water: -1, morale: 14 },
    optionB: "להתעלם מהקול",
    resultB: "הבונקר נשאר סגור, אבל משהו באנשים נסגר יחד איתו.",
    effectB: { food: 1, water: 1, morale: -16 }
  },
  {
    title: "דליפה איטית",
    problem: "קו דק של לחות מתקדם לאורך הרצפה.",
    optionA: "להקצות צוות תיקון",
    resultA: "הדליפה נעצרת, והצוות מתגאה בעבודה הקשה.",
    effectA: { food: -1, water: 3, morale: 4 },
    optionB: "לספוג את המים במטליות",
    resultB: "הפתרון זמני וחוסך מאמץ, אבל לא באמת פותר דבר.",
    effectB: { food: 0, water: -3, morale: -3 }
  },
  {
    title: "מנה מזוהמת",
    problem: "ריח חמוץ עולה מאחת המנות, אבל הרעב כבר מדבר חזק.",
    optionA: "להשליך את המנה",
    resultA: "ההחלטה כואבת, אך היא שומרת על כולם כשירים.",
    effectA: { food: -2, water: 0, morale: 4 },
    optionB: "לחלק אותה אחרי בדיקה",
    resultB: "חלק אכלו ושבעו, אחרים איבדו אמון בהחלטות שלך.",
    effectB: { food: 2, water: -1, morale: -11 }
  },
  {
    title: "שמועה על מחסן נסתר",
    problem: "מישהו נשבע שראה דלת קטנה מאחורי לוח מתכת.",
    optionA: "לפתוח חיפוש מסודר",
    resultA: "החיפוש חושף אספקה קטנה ומעלה את המורל.",
    effectA: { food: 3, water: 1, morale: 6 },
    optionB: "לאסור בזבוז זמן",
    resultB: "המשמעת נשמרת, אבל התחושה היא שוויתרתם על תקווה.",
    effectB: { food: 0, water: 0, morale: -10 }
  },
  {
    title: "איום פנימי",
    problem: "מישהו מחביא ציוד אישי ומסרב להסביר למה.",
    optionA: "לערוך בדיקה לכולם",
    resultA: "נמצאו כמה פריטים, אך הפרטיות בבונקר נשברה.",
    effectA: { food: 2, water: 1, morale: -9 },
    optionB: "לדבר איתו לבד",
    resultB: "השיחה מרגיעה את המצב, גם אם חלק מהציוד לא חוזר.",
    effectB: { food: -1, water: 0, morale: 8 }
  },
  {
    title: "אות רדיו חדש",
    problem: "המכשיר קולט רצף מספרים ושם של עיר רחוקה.",
    optionA: "לפענח את האות",
    resultA: "האות נותן כיוון חדש, אבל הלילה הלך על עבודה מתישה.",
    effectA: { food: -1, water: -1, morale: 13 },
    optionB: "לכבות כדי לחסוך כוח",
    resultB: "המערכות שורדות עוד יום, האנשים קצת פחות.",
    effectB: { food: 0, water: 1, morale: -8 }
  },
  {
    title: "רעידה בבטון",
    problem: "אבק נושר מהתקרה וכולם קופאים במקום.",
    optionA: "לפנות את האזור",
    resultA: "הפינוי מונע פציעות, אבל משבש את חלוקת המנות.",
    effectA: { food: -2, water: 0, morale: 5 },
    optionB: "להמשיך כרגיל",
    resultB: "הסדר נשמר, אך כל רעש קטן מקפיץ את כולם.",
    effectB: { food: 0, water: 0, morale: -13 }
  },
  {
    title: "הזדמנות למסחר",
    problem: "קבוצה מעבר לקשר מציעה החלפה מהירה דרך פתח שירות.",
    optionA: "להחליף מים באוכל",
    resultA: "המחסן נראה טוב יותר, אבל המכלים נראים ריקים מדי.",
    effectA: { food: 4, water: -3, morale: 1 },
    optionB: "להחליף אוכל במים",
    resultB: "המכלים מתמלאים מעט, אך הבטן של כולם מרגישה את העסקה.",
    effectB: { food: -3, water: 4, morale: 1 }
  },
  {
    title: "לילה ללא שינה",
    problem: "רעש מחזורי מונע מהאנשים להירדם.",
    optionA: "לחלק משמרות קצרות",
    resultA: "העייפות מתחלקת בין כולם והקבוצה מחזיקה מעמד.",
    effectA: { food: -1, water: -1, morale: 7 },
    optionB: "לתת רק לחזקים לשמור",
    resultB: "חסכתם בלגן, אבל תחושת חוסר הצדק מתפשטת.",
    effectB: { food: 0, water: 0, morale: -9 }
  },
  {
    title: "מפה קרועה",
    problem: "חלק חסר במפה עשוי להוביל ליציאה או למלכודת.",
    optionA: "לשלוח סיור קצר",
    resultA: "הסיור חוזר עם מידע יקר, אבל גם עם צמא ורעב.",
    effectA: { food: -2, water: -2, morale: 12 },
    optionB: "לשמור את המידע להמשך",
    resultB: "לא סיכנתם איש, אבל החלום לצאת נדחה שוב.",
    effectB: { food: 0, water: 0, morale: -6 }
  },
  {
    title: "שעת זיכרון",
    problem: "אחד הניצולים מבקש לעצור הכול כדי להזכיר את מי שלא שרדו.",
    optionA: "לאפשר טקס קצר",
    resultA: "הכאב מקבל מקום, והאנשים נושמים קצת יותר עמוק.",
    effectA: { food: -1, water: 0, morale: 15 },
    optionB: "להחזיר את כולם לעבודה",
    resultB: "המשימות מתקדמות, אבל הלב של הבונקר נשחק.",
    effectB: { food: 1, water: 0, morale: -14 }
  },
  {
    title: "סדק בחומה",
    problem: "קו שחור מופיע בבטון ומתרחב לאט.",
    optionA: "לאטום אותו בחומרים יקרים",
    resultA: "הסדק נבלם, אבל המחסן מרגיש דל יותר.",
    effectA: { food: -1, water: -2, morale: 8 },
    optionB: "לסמן ולעקוב",
    resultB: "לא בזבזתם משאבים, אך הסדק נשאר בראש של כולם.",
    effectB: { food: 0, water: 0, morale: -7 }
  }
];

const PRESSURES = [
  {
    phrase: "בזמן שהאורות מהבהבים באדום",
    modA: { food: 0, water: 0, morale: 2 },
    modB: { food: 0, water: 0, morale: -2 }
  },
  {
    phrase: "אחרי לילה של רעידות רחוקות",
    modA: { food: -1, water: 0, morale: 1 },
    modB: { food: 0, water: 0, morale: -3 }
  },
  {
    phrase: "כששמועה לא טובה עוברת בין הדרגשים",
    modA: { food: 0, water: 0, morale: 3 },
    modB: { food: 0, water: 0, morale: -4 }
  },
  {
    phrase: "בזמן שמד המים משמיע צפצוף חלש",
    modA: { food: 0, water: -1, morale: 0 },
    modB: { food: 0, water: 1, morale: -2 }
  },
  {
    phrase: "כשמישהו מתחיל לבכות מאחורי הווילון",
    modA: { food: -1, water: 0, morale: 4 },
    modB: { food: 0, water: 0, morale: -5 }
  },
  {
    phrase: "בזמן שהגנרטור עובר לפעימה נמוכה",
    modA: { food: 0, water: -1, morale: 2 },
    modB: { food: 0, water: 0, morale: -3 }
  },
  {
    phrase: "כשבחוץ נשמע פיצוץ עמום",
    modA: { food: -1, water: -1, morale: 3 },
    modB: { food: 1, water: 0, morale: -4 }
  },
  {
    phrase: "אחרי יום ארוך בלי חדשות",
    modA: { food: 0, water: 0, morale: 2 },
    modB: { food: 0, water: 1, morale: -5 }
  }
];

function addEffects(baseEffect, modifier) {
  return {
    food: baseEffect.food + modifier.food,
    water: baseEffect.water + modifier.water,
    morale: baseEffect.morale + modifier.morale
  };
}

function buildEvents() {
  const events = [];

  LOCATIONS.forEach((location) => {
    INCIDENTS.forEach((incident) => {
      PRESSURES.forEach((pressure) => {
        events.push({
          title: `${incident.title} - ${location.name}`,
          story: `${location.detail} ${incident.problem} כל זה קורה ${pressure.phrase}.`,
          choices: [
            {
              text: incident.optionA,
              effect: addEffects(incident.effectA, pressure.modA),
              result: incident.resultA
            },
            {
              text: incident.optionB,
              effect: addEffects(incident.effectB, pressure.modB),
              result: incident.resultB
            }
          ]
        });
      });
    });
  });

  return events;
}

const EVENTS = buildEvents();
