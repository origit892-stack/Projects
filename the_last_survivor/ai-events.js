async function getAiGeneratedEvent(state, maxStats) {
  const config = window.BUNKER_AI_CONFIG || {};

  if (!config.enabled || !config.apiKey) {
    return null;
  }

  try {
    const response = await fetch(buildGeminiUrl(config), {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(buildGeminiRequest(state, maxStats))
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
    const event = parseAiEvent(text);

    return isValidAiEvent(event) ? event : null;
  } catch (error) {
    return null;
  }
}

function buildGeminiUrl(config) {
  const model = encodeURIComponent(config.model || "gemini-2.5-flash");
  const apiKey = encodeURIComponent(config.apiKey);

  return `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
}

function buildGeminiRequest(state, maxStats) {
  return {
    contents: [
      {
        parts: [
          {
            text: [
              "צור אירוע אקראי למשחק דפדפן בעברית בשם הניצול האחרון.",
              "המשחק עוסק בניהול בונקר הישרדות פוסט-אפוקליפטי.",
              "החזר JSON בלבד, בלי Markdown ובלי הסברים.",
              "מבנה חובה:",
              "{",
              "  \"title\": \"כותרת קצרה\",",
              "  \"story\": \"סיפור קצר של 1-2 משפטים\",",
              "  \"choices\": [",
              "    { \"text\": \"בחירה ראשונה\", \"effect\": { \"food\": 0, \"water\": 0, \"morale\": 0 }, \"result\": \"תוצאה קצרה\" },",
              "    { \"text\": \"בחירה שניה\", \"effect\": { \"food\": 0, \"water\": 0, \"morale\": 0 }, \"result\": \"תוצאה קצרה\" }",
              "  ]",
              "}",
              `מצב נוכחי: יום ${state.day}, אוכל ${state.food}/${maxStats.food}, מים ${state.water}/${maxStats.water}, מורל ${state.morale}/${maxStats.morale}.`,
              "כל השפעה חייבת להיות מספר שלם בטווח -4 עד 4 לאוכל/מים ובטווח -18 עד 18 למורל.",
              "לפחות בחירה אחת צריכה לכלול מחיר אמיתי, ולפחות בחירה אחת צריכה לכלול יתרון כלשהו."
            ].join("\n")
          }
        ]
      }
    ],
    generationConfig: {
      temperature: 0.95,
      responseMimeType: "application/json"
    }
  };
}

function parseAiEvent(text) {
  if (!text) return null;

  const cleanText = text
    .replace(/^```json\s*/i, "")
    .replace(/^```\s*/i, "")
    .replace(/```$/i, "")
    .trim();

  try {
    return JSON.parse(cleanText);
  } catch (error) {
    return null;
  }
}

function isValidAiEvent(event) {
  if (!event || typeof event.title !== "string" || typeof event.story !== "string") {
    return false;
  }

  if (!Array.isArray(event.choices) || event.choices.length !== 2) {
    return false;
  }

  return event.choices.every((choice) => {
    return typeof choice.text === "string" &&
      typeof choice.result === "string" &&
      choice.effect &&
      Number.isFinite(choice.effect.food) &&
      Number.isFinite(choice.effect.water) &&
      Number.isFinite(choice.effect.morale);
  });
}
