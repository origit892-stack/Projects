import base64
import json
import os
import re
import shutil
import subprocess
import threading
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus

import requests
from flask import Flask, Response, jsonify, render_template, request
from PIL import Image, ImageStat

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from pywebpush import WebPushException, webpush
except ImportError:
    WebPushException = Exception
    webpush = None


load_dotenv()

app = Flask(__name__)

DATA_PATH = Path("user_schedule.json")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if GEMINI_API_KEY in {"your_key_here", "your_gemini_api_key_here"}:
    GEMINI_API_KEY = ""
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
VISION_MODEL = os.getenv("VISION_MODEL", MODEL_NAME).strip()
VISION_PROVIDER = os.getenv("VISION_PROVIDER", "local").strip().lower()
AI_PROVIDER = os.getenv("AI_PROVIDER", "opencode").strip().lower()
OPENCODE_BIN = os.getenv("OPENCODE_BIN", "/usr/local/bin/opencode")
OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "").strip()
OPENCODE_AGENT = os.getenv("OPENCODE_AGENT", "compaction").strip()
OPENCODE_TIMEOUT = int(os.getenv("OPENCODE_TIMEOUT", "45"))
OPENCODE_WEB_TIMEOUT = min(OPENCODE_TIMEOUT, int(os.getenv("OPENCODE_WEB_TIMEOUT", "25")))
BIGPICKLE_BIN = os.getenv("BIGPICKLE_BIN", "bigpickle")
BIGPICKLE_TIMEOUT = int(os.getenv("BIGPICKLE_TIMEOUT", "25"))
NOMINATIM_URL = "https://nominatim.openstreetmap.org"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_FALLBACK_URL = "https://overpass.kumi.systems/api/interpreter"
HTTP_HEADERS = {"User-Agent": "MemoryLane-AI/1.0 (local prototype)"}
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PRIVATE_KEY_PATH = os.getenv("VAPID_PRIVATE_KEY_PATH", "")
VAPID_CLAIMS_SUB = os.getenv("VAPID_CLAIMS_SUB", "mailto:memorylane@example.com")
PUSH_PRIVATE_KEY = VAPID_PRIVATE_KEY_PATH or VAPID_PRIVATE_KEY

client = genai.Client(api_key=GEMINI_API_KEY) if genai and GEMINI_API_KEY else None
chat_sessions = {}
LAST_AI_STATUS = {
    "provider": AI_PROVIDER,
    "ok": False,
    "source": "startup",
    "message": "עוד לא נשלחה בקשת AI.",
    "elapsed_ms": 0,
    "updated_at": "",
}

SYSTEM_INSTRUCTION = (
    "אתה עוזר דיגיטלי חם בשם MemoryLane המשמש כבן שיח טיפולי בסגנון Reminiscence Therapy. "
    "בתחילת השיחה, שאל בנימוס מה שם המשתמש כדי לפנות אליו בשמו, וזכור את השם רק להמשך השיחה הנוכחית. "
    "אסור לנחש שם ואסור להשתמש בשם שלא נאמר במפורש בשיחה הנוכחית. "
    "אם המשתמש אומר רק שלום, היי, או משפט כללי בלי שם, אל תפנה אליו בשם. "
    "אם המשתמש מציג את עצמו במשפט כמו 'קוראים לי שמחה' או 'שמי...', הכר בשם קודם, פנה אליו בשם, "
    "ואל תתייחס לזה כאל זיכרון שכבר צריך לנתח. "
    "אם המשתמש אומר שהוא רוצה לדבר על עצמו, שאל שאלה פתוחה ועדינה על חייו, משפחתו, ביתו, עבודתו או מה שמעסיק אותו היום. "
    "נהל שיחה קולחת בעברית טבעית, חמה וסבלנית. נתח לעומק את מה שהמשתמש משתף על עברו, "
    "חזק אותו רגשית, ושאל שאלות המשך ממוקדות כדי לעורר זיכרונות. "
    "אם המשתמש משתף כתובת, מיקום, או מבקש חוגים ופעילויות, התייחס לאזור שנמסר והצע רעיונות רלוונטיים. "
    "אל תציג את עצמך כרופא או כתחליף לטיפול רפואי."
)


def get_chat_history(session_id):
    session_id = (session_id or "default").strip()[:80] or "default"
    chat_sessions.setdefault(session_id, [])
    if len(chat_sessions) > 200:
        for old_key in list(chat_sessions.keys())[:50]:
            chat_sessions.pop(old_key, None)
    return chat_sessions[session_id]


def update_ai_status(ok, source, message, elapsed_ms=0):
    LAST_AI_STATUS.update(
        {
            "provider": AI_PROVIDER,
            "ok": bool(ok),
            "source": source,
            "message": str(message or "")[:500],
            "elapsed_ms": int(elapsed_ms or 0),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


def last_user_text(history):
    for message in reversed(history):
        if message.get("role") == "user":
            parts = message.get("parts") or []
            if parts:
                text = parts[-1]
                if not text.startswith("[מערכת:"):
                    return text.strip()
    return ""


def extract_name_from_history(history):
    patterns = [
        r"(?:קוראים לי|שמי|השם שלי)\s+([א-תA-Za-z][א-תA-Za-z'\- ]{1,24})",
        r"אני\s+([א-תA-Za-z][א-תA-Za-z'\- ]{1,24})",
    ]
    for message in history:
        if message.get("role") != "user":
            continue
        for part in message.get("parts") or []:
            for pattern in patterns:
                match = re.search(pattern, part)
                if match:
                    name = re.split(r"[,.!?;:،\n]", match.group(1).strip())[0].strip()
                    name = " ".join(name.split()[:2])
                    if name.split()[0] in {"רוצה", "צריך", "צריכה", "כאן", "לא", "כן", "הייתי"}:
                        continue
                    return name
    return ""


def warm_fallback_reply(history):
    text = last_user_text(history)
    clean = re.sub(r"[!?.،,;:\s]+", "", text)
    name = extract_name_from_history(history)

    if name and any(phrase in text for phrase in ["קוראים לי", "שמי", "השם שלי"]):
        return f"שלום {name}, נעים מאוד. אני כאן איתך. מה היית רוצה לספר לי היום?"
    if clean in {"שלום", "היי", "הי", "בוקרשלום", "ערבטוב", "צהרייםטובים"}:
        return f"שלום {name}, אני כאן איתך. על מה תרצה לדבר היום?" if name else "שלום, נעים שאתה כאן. איך קוראים לך?"
    if any(phrase in text for phrase in ["רוצה לדבר עלי", "רוצה לדבר עליי", "לדבר עלי", "לדבר עליי"]):
        prefix = f"{name}, " if name else ""
        return f"{prefix}אני מקשיב. במה היית רוצה להתחיל: במשפחה, בבית שגדלת בו, בעבודה, או במשהו שמעסיק אותך היום?"
    daughter_match = re.search(r"(?:בתי|ביתי|הבת שלי|ילדה שלי|הקטנה שלי|בת\s+שלי)\s+(?:הקטנה\s+)?([א-תA-Za-z][א-תA-Za-z'\-]*)?", text)
    if daughter_match or any(word in text for word in ["בתי", "ביתי", "הבת שלי", "רחלי"]):
        daughter_name = (daughter_match.group(1) if daughter_match and daughter_match.group(1) else "").strip()
        subject = daughter_name or "הבת שלך"
        prefix = f"{name}, " if name else ""
        return f"{prefix}ספר לי על {subject}. איזה זיכרון קטן ממנה עולה לך ראשון כשאתה חושב עליה?"
    son_match = re.search(r"(?:בני|הבן שלי|ילד שלי)\s+([א-תA-Za-z][א-תA-Za-z'\-]*)?", text)
    if son_match or any(word in text for word in ["בני", "הבן שלי"]):
        son_name = (son_match.group(1) if son_match and son_match.group(1) else "").strip()
        subject = son_name or "הבן שלך"
        prefix = f"{name}, " if name else ""
        return f"{prefix}ספר לי על {subject}. מה הדבר שאתה הכי אוהב לזכור עליו?"
    if any(word in text for word in ["אשתי", "בעלי", "משפחה", "אמא", "אבא", "נכד", "נכדה"]):
        prefix = f"{name}, " if name else ""
        return f"{prefix}זה נשמע זיכרון משפחתי חשוב. מי היה שם איתך, ומה אתה זוכר מהאווירה באותו זמן?"
    if any(word in text for word in ["בית", "שכונה", "רחוב", "חצר", "מטבח"]):
        prefix = f"{name}, " if name else ""
        return f"{prefix}ספר לי על המקום הזה. איך הוא נראה, ואיזה ריח או קול אתה זוכר ממנו?"
    if any(word in text for word in ["עצוב", "קשה", "בודד", "לבד", "מפחד"]):
        return "אני שומע שזה לא פשוט. אני כאן איתך. מה הדבר שהכי מכביד עליך עכשיו?"
    if text:
        prefix = f"{name}, " if name else ""
        return f"{prefix}אני מקשיב לך. מה הפרט הקטן שהכי נשאר איתך מזה?"
    return "אני כאן איתך. אפשר לכתוב לי כל דבר שעולה עכשיו."


def should_use_local_chat_reply(text):
    clean = re.sub(r"[!?.،,;:\s]+", "", text or "")
    if clean in {"שלום", "היי", "הי", "בוקרשלום", "ערבטוב", "צהרייםטובים"}:
        return True
    local_phrases = [
        "קוראים לי",
        "שמי",
        "השם שלי",
        "רוצה לדבר עלי",
        "רוצה לדבר עליי",
        "לדבר עלי",
        "לדבר עליי",
    ]
    memory_words = [
        "בתי", "ביתי", "הבת שלי", "בני", "הבן שלי", "רחלי", "ילדה", "ילד",
        "אשתי", "בעלי", "אמא", "אבא", "נכד", "נכדה", "משפחה",
        "בית", "שכונה", "רחוב", "חצר", "מטבח", "עבודה", "צבא", "חתונה",
        "ילדות", "זוכר", "זוכרת", "מתגעגע", "מתגעגעת",
    ]
    return any(phrase in (text or "") for phrase in local_phrases + memory_words)


def local_image_reply(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return "קיבלתי את התמונה, אבל לא הצלחתי לקרוא אותה. אפשר לנסות תמונה אחרת או לספר לי מה רואים בה?"

    width, height = image.size
    stat = ImageStat.Stat(image.resize((1, 1)))
    red, green, blue = stat.mean
    brightness = (red + green + blue) / 3
    orientation = "לאורך" if height > width else "לרוחב" if width > height else "מרובעת"
    light_text = "בהירה מאוד" if brightness > 210 else "כהה יחסית" if brightness < 70 else "בבהירות רגילה"

    return (
        f"קיבלתי את התמונה. כרגע ניתוח ה-AI לתמונות לא זמין, אבל אני רואה שהתמונה {orientation}, "
        f"בגודל {width} על {height} פיקסלים, והיא {light_text}. "
        "מה מופיע בתמונה, ואיזה זיכרון היא מחזירה אליך?"
    )


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def load_saved_data():
    if not DATA_PATH.exists():
        return {
            "registered_classes": [],
            "medications": [],
            "address": "",
            "latitude": None,
            "longitude": None,
            "push_subscriptions": [],
            "last_push_alerts": {},
            "activity_cache": {},
        }

    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        data = {}

    data.setdefault("registered_classes", [])
    data.setdefault("medications", [])
    data.setdefault("address", "")
    data.setdefault("latitude", None)
    data.setdefault("longitude", None)
    data.setdefault("push_subscriptions", [])
    data.setdefault("last_push_alerts", {})
    data.setdefault("activity_cache", {})
    return data


def save_data(data):
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def geocode_address(address):
    if not address:
        return None

    base_params = {
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "dedupe": 1,
        "countrycodes": "il",
        "accept-language": "he",
    }
    searches = [
        {
            **base_params,
            "q": address,
            "viewbox": "34.17,33.35,35.90,29.45",
            "bounded": 1,
        },
        {**base_params, "q": f"{address}, ישראל"},
        {**base_params, "q": address},
    ]

    results = []
    for params in searches:
        try:
            response = requests.get(
                f"{NOMINATIM_URL}/search",
                params=params,
                headers=HTTP_HEADERS,
                timeout=12,
            )
            response.raise_for_status()
            results = response.json()
        except (requests.RequestException, ValueError):
            results = []
        if results:
            break

    if not results:
        return None

    def importance(place):
        return float(place.get("importance") or 0)

    place = sorted(results, key=importance, reverse=True)[0]
    details = place.get("address", {})
    return {
        "address": place.get("display_name", address),
        "city": city_from_address_details(details),
        "latitude": float(place["lat"]),
        "longitude": float(place["lon"]),
    }


def city_from_address_details(details):
    city = (
        details.get("city")
        or details.get("town")
        or details.get("village")
        or details.get("municipality")
        or details.get("city_district")
    )
    if city:
        return re.sub(r"^(עיריית|מועצה מקומית|מועצה אזורית)\s+", "", city).strip()
    return ""


def city_from_geocode_result(location):
    if not location:
        return ""
    if location.get("city"):
        return location["city"]
    return reverse_geocode(location["latitude"], location["longitude"])


def reverse_geocode(latitude, longitude):
    try:
        response = requests.get(
            f"{NOMINATIM_URL}/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1,
                "zoom": 18,
                "accept-language": "he",
            },
            headers=HTTP_HEADERS,
            timeout=12,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError, TypeError):
        return f"{latitude}, {longitude}"

    details = result.get("address", {})
    city = city_from_address_details(details)
    state = details.get("state")
    county = details.get("county")

    if city:
        return city

    region = county or state
    if region:
        region = re.sub(r"^(נפת|מחוז)\s+", "", region).strip()
        return f"אזור {region}"

    return "אזור כללי בישראל"


def contact_url(tags, latitude, longitude):
    for key in ("contact:website", "website", "url", "contact:facebook"):
        value = tags.get(key)
        if value:
            return value if value.startswith(("http://", "https://")) else f"https://{value}"

    email = tags.get("contact:email") or tags.get("email")
    if email:
        return f"mailto:{email}"

    phone = tags.get("contact:phone") or tags.get("phone")
    if phone:
        return f"tel:{phone}"

    return ""


def describe_activity(name, tags=None):
    tags = tags or {}
    text = " ".join(
        [
            name or "",
            tags.get("amenity", ""),
            tags.get("leisure", ""),
            tags.get("club", ""),
            tags.get("sport", ""),
        ]
    ).lower()

    if any(word in text for word in ["community_centre", "מרכז תרבות", "מרכז קהילתי"]):
        return "מרכז קהילתי או תרבותי עם פעילויות קהילה, מפגשים, הרצאות וחוגים. כדאי לבדוק באתר או בטלפון מה מתאים לגיל השלישי."
    if any(word in text for word in ["theatre", "תיאטרון", "תאטרון", "קאמרי", "גשר", "אופרה"]):
        return "צפייה בהצגות, מופעים ופעילות תרבותית. כדאי לבדוק באתר זמני מופעים ונגישות."
    if any(word in text for word in ["library", "ספרייה", "ספריה"]):
        return "מפגש שקט סביב ספרים, הרצאות, קריאה ופעילות קהילתית."
    if any(word in text for word in ["arts", "אומנות", "אמנות", "ציור"]):
        return "פעילות יצירה, אומנות, סדנאות ומפגש חברתי רגוע."
    if any(word in text for word in ["fitness", "sports", "יוגה", "ספורט", "התעמלות"]):
        return "פעילות גופנית קלה או חוג תנועה. מומלץ לברר התאמה ונגישות לפני ההגעה."
    if any(word in text for word in ["community", "social", "קהילתי", "חברה"]):
        return "פעילות חברתית וקהילתית, מפגשים, הרצאות וחוגים באזור."
    return "מקום קרוב שיכול להתאים לפעילות תרבותית או חברתית. כדאי לפתוח קישור ולבדוק פרטים."


def clean_search_location(location):
    location = (location or "").strip()
    blocked_phrases = [
        "אין כתובת מלאה",
        "כתובת לא זמינה",
        "מיקום במפה",
        "באזור הכתובת שהוזנה",
        "מומלץ ליצור קשר",
    ]
    if not location or any(phrase in location for phrase in blocked_phrases):
        return ""
    return location


def build_search_url(name, location=""):
    clean_location = clean_search_location(location)
    query = " ".join(part for part in [name, clean_location, "יצירת קשר אתר רשמי"] if part).strip()
    return f"https://www.google.com/search?q={quote_plus(query)}"


def format_activity(element):
    tags = element.get("tags", {})
    latitude = element.get("lat") or element.get("center", {}).get("lat")
    longitude = element.get("lon") or element.get("center", {}).get("lon")
    name = tags.get("name:he") or tags.get("name") or "מקום פעילות קרוב"
    street = tags.get("addr:street", "")
    house = tags.get("addr:housenumber", "")
    city = tags.get("addr:city", "")
    address_parts = [part for part in [street, house, city] if part]
    location = " ".join(address_parts) if address_parts else tags.get("addr:full", "")

    contact = contact_url(tags, latitude, longitude)
    map_url = (
        f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=18/{latitude}/{longitude}"
        if latitude and longitude
        else ""
    )
    search_url = build_search_url(name, location)
    return {
        "id": f"osm-{element.get('type')}-{element.get('id')}",
        "name": name,
        "location": location or "",
        "time": tags.get("opening_hours") or "",
        "contact_url": contact,
        "has_direct_contact": contact.startswith(("http://", "https://", "mailto:", "tel:")),
        "phone": tags.get("contact:phone") or tags.get("phone") or "",
        "map_url": map_url,
        "search_url": search_url,
        "description": describe_activity(name, tags),
    }


def search_nearby_activities(latitude, longitude):
    if latitude is None or longitude is None:
        return []

    elements = []
    started = time.monotonic()
    filters = [
        ('node', 'amenity', 'library'),
        ('node', 'amenity', 'community_centre'),
        ('node', 'amenity', 'social_facility'),
        ('node', 'amenity', 'arts_centre'),
        ('node', 'amenity', 'theatre'),
        ('node', 'leisure', 'sports_centre'),
        ('node', 'leisure', 'fitness_centre'),
        ('node', 'club', 'social'),
        ('way', 'amenity', 'library'),
        ('way', 'amenity', 'community_centre'),
        ('way', 'leisure', 'sports_centre'),
    ]

    for element_type, key, value in filters:
        if time.monotonic() - started > 4 or len(elements) >= 6:
            break
        query = (
            f'[out:json][timeout:4];'
            f'{element_type}(around:12000,{latitude},{longitude})["{key}"="{value}"];'
            'out center tags 8;'
        )
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, headers=HTTP_HEADERS, timeout=3)
            response.raise_for_status()
            elements.extend(response.json().get("elements", []))
        except (requests.RequestException, ValueError):
            continue

    activities = []
    seen = set()
    for element in elements:
        activity = format_activity(element)
        if activity["name"] in seen:
            continue
        seen.add(activity["name"])
        activities.append(activity)
        if len(activities) >= 8:
            break

    return activities


def search_city_activities(city):
    city = (city or "").strip()
    if not city or city.startswith("אזור "):
        return []

    queries = [
        f"ספריה {city}",
        f"ספריית {city}",
        f"מרכז תרבות {city}",
        f"מרכז קהילתי {city}",
        f"קאנטרי {city}",
        f"ספורט {city}",
        f"מרכז יום לקשיש {city}",
    ]
    activities = []
    seen = set()
    for query in queries:
        if len(activities) >= 6:
            break
        try:
            response = requests.get(
                f"{NOMINATIM_URL}/search",
                params={
                    "q": query,
                    "format": "json",
                    "addressdetails": 1,
                    "namedetails": 1,
                    "limit": 4,
                    "countrycodes": "il",
                    "accept-language": "he",
                },
                headers=HTTP_HEADERS,
                timeout=4,
            )
            response.raise_for_status()
            results = response.json()
        except (requests.RequestException, ValueError):
            continue

        for place in results:
            display = place.get("display_name", "")
            if city not in display:
                continue
            name = (
                place.get("namedetails", {}).get("name:he")
                or place.get("namedetails", {}).get("name")
                or display.split(",", 1)[0].strip()
            )
            if not name or name in seen:
                continue
            seen.add(name)
            latitude = place.get("lat")
            longitude = place.get("lon")
            tags = {
                "amenity": place.get("type") if place.get("class") == "amenity" else "",
                "leisure": place.get("type") if place.get("class") == "leisure" else "",
            }
            activities.append(
                {
                    "id": f"nominatim-{place.get('osm_type')}-{place.get('osm_id')}",
                    "name": name,
                    "location": city,
                    "time": "",
                    "contact_url": "",
                    "has_direct_contact": False,
                    "phone": "",
                    "map_url": (
                        f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=18/{latitude}/{longitude}"
                        if latitude and longitude
                        else f"https://www.openstreetmap.org/search?query={quote_plus(f'{name} {city}')}"
                    ),
                    "search_url": build_search_url(name, city),
                    "description": describe_activity(name, tags),
                }
            )
    return activities


def make_activity_accessible(activity):
    contact = activity.get("contact_url", "")
    phone = activity.get("phone", "")
    if contact.startswith("tel:") and not phone:
        phone = contact.removeprefix("tel:")
    name = activity.get("name", "מקום פעילות")
    location = activity.get("location") or "באזור הכתובת שהוזנה"

    return {
        "id": activity.get("id", ""),
        "name": name,
        "location": location,
        "time": activity.get("time") or "מומלץ ליצור קשר לפני ההגעה",
        "contact_url": contact,
        "phone": phone,
        "map_url": activity.get("map_url")
        or f"https://www.openstreetmap.org/search?query={quote_plus(f'{name} {location}')}",
        "search_url": activity.get("search_url")
        or build_search_url(name, location),
        "description": activity.get("description") or describe_activity(name),
        "note": "אפשר לפתוח מיקום במפה או לחפש פרטי קשר של המקום.",
    }


def extract_json_array(text):
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        parsed = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def polish_activities_with_gemini(address, raw_activities):
    actionable = [
        make_activity_accessible(item)
        for item in raw_activities
        if item.get("name") and item.get("name") != "מקום פעילות קרוב"
    ]
    if not actionable:
        return []

    if not client:
        return actionable

    prompt = (
        "החזר JSON בלבד, ללא טקסט נוסף. "
        "קבל רשימת מקומות פעילות שנמצאו ליד כתובת של משתמש קשיש. "
        "המטרה: להפוך את הרשימה לנגישה, רגועה ושימושית בעברית. "
        "אסור להמציא כתובות, טלפונים, שעות או קישורים. השתמש רק בפרטים שמופיעים בקלט. "
        "אם אין שעה, כתוב בדיוק: מומלץ ליצור קשר לפני ההגעה. "
        "אם אין כתובת, כתוב: באזור הכתובת שהוזנה. "
        "החזר עד 6 פריטים בפורמט: "
        "[{\"id\":\"...\",\"name\":\"...\",\"location\":\"...\",\"time\":\"...\",\"contact_url\":\"...\",\"phone\":\"...\",\"map_url\":\"...\",\"search_url\":\"...\",\"description\":\"...\",\"note\":\"...\"}]. "
        f"כתובת המשתמש: {address}\n"
        f"מקומות מהמקור: {json.dumps(actionable, ensure_ascii=False)}"
    )

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=[prompt])
    except Exception:
        return actionable

    polished = extract_json_array(response.text or "")
    if not polished:
        return actionable

    allowed_by_id = {item["id"]: item for item in actionable}
    safe_items = []
    for item in polished:
        source = allowed_by_id.get(item.get("id"))
        if not source:
            continue
        safe_items.append(
            {
                "id": source["id"],
                "name": item.get("name") or source["name"],
                "location": item.get("location") or source["location"],
                "time": item.get("time") or source["time"],
                "contact_url": source["contact_url"],
                "phone": source["phone"],
                "map_url": source["map_url"],
                "search_url": source["search_url"],
                "description": item.get("description") or source["description"],
                "note": item.get("note") or source["note"],
            }
        )
    return safe_items or actionable


def generate_activity_fallback_with_gemini(address):
    if not client or not address:
        return []

    prompt = (
        "החזר JSON בלבד, ללא טקסט נוסף. "
        "מצא או הרכב רשימת פעילויות וחוגים רלוונטיים לקשיש לפי הכתובת. "
        "המטרה היא טבלה שימושית, רגועה ונגישה. "
        "אל תכתוב 'אין כתובת מלאה', 'שעות פתיחה לא זמינות' או 'צריך לגשת למקום'. "
        "אם אין לך ודאות לגבי טלפון או אתר, השאר contact_url ריק. "
        "תמיד מלא search_url כקישור חיפוש Google לפי שם המקום + כתובת + יצירת קשר. "
        "אל תמציא מספרי טלפון. החזר עד 5 פריטים בפורמט JSON: "
        "[{\"id\":\"gemini-1\",\"name\":\"...\",\"location\":\"...\",\"time\":\"מומלץ ליצור קשר לפני ההגעה\",\"contact_url\":\"...\",\"phone\":\"\",\"map_url\":\"...\",\"search_url\":\"...\",\"description\":\"...\",\"note\":\"...\"}]. "
        f"כתובת: {address}"
    )

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=[prompt])
    except Exception:
        return []

    items = extract_json_array(response.text or "")
    clean_items = []
    for index, item in enumerate(items[:5], start=1):
        name = item.get("name") or "פעילות באזור"
        location = item.get("location") or "באזור הכתובת שהוזנה"
        clean_items.append(
            {
                "id": item.get("id") or f"gemini-{index}",
                "name": name,
                "location": location,
                "time": item.get("time") or "מומלץ ליצור קשר לפני ההגעה",
                "contact_url": item.get("contact_url") or "",
                "phone": item.get("phone") or "",
                "map_url": item.get("map_url")
                or f"https://www.openstreetmap.org/search?query={quote_plus(f'{name} {location}')}",
                "search_url": item.get("search_url")
                or build_search_url(name, location),
                "description": item.get("description") or describe_activity(name),
                "note": item.get("note") or "אפשר לפתוח מיקום במפה או לחפש פרטי קשר של המקום.",
            }
        )
    return clean_items


def get_nearby_classes(data):
    cache_key = (data.get("address") or "").strip()
    cache = data.get("activity_cache", {})
    cached = cache.get(cache_key) if cache_key else None
    if cached and cached.get("items"):
        return cached["items"]

    raw_activities = search_city_activities(cache_key)
    if len(raw_activities) < 3:
        raw_activities.extend(search_nearby_activities(data.get("latitude"), data.get("longitude")))
    items = [
        make_activity_accessible(item)
        for item in raw_activities
        if item.get("name") and item.get("name") != "מקום פעילות קרוב"
    ][:6]
    if cache_key and items:
        data.setdefault("activity_cache", {})[cache_key] = {
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
        }
        save_data(data)
    return items


def strip_terminal_codes(text):
    text = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)
    text = re.sub(r"<summary>.*?</summary>", "", text, flags=re.DOTALL)
    text = re.sub(r"^> .*$", "", text, flags=re.MULTILINE)
    return text.strip()


def build_chat_prompt(history, user_text=None):
    lines = [
        SYSTEM_INSTRUCTION,
        "אתה משוחח עכשיו עם קשיש/ה בתוך אפליקציית MemoryLane.",
        "ענה בעברית בלבד, חם, קצר יחסית, סבלני ואישי. אל תכתוב שאתה כלי קוד או סוכן פיתוח.",
        "אל תציע קוד, טרמינל או פעולות טכניות. התמקד בשיחה אנושית, זיכרונות, הקשבה ושאלת המשך אחת.",
        "אם אין שם ברור בהיסטוריית השיחה הנוכחית, אל תשתמש בשם פרטי בתשובה.",
        "",
        "היסטוריית השיחה:",
    ]
    for message in history[-10:]:
        role = "משתמש" if message["role"] == "user" else "MemoryLane"
        for part in message["parts"]:
            lines.append(f"{role}: {part}")
    if user_text:
        lines.append(f"משתמש: {user_text}")
    lines.append("MemoryLane:")
    return "\n".join(lines)


def generate_with_opencode(history, user_text=None, image_part=None):
    if image_part:
        return "OpenCode מחובר לשיחה, אבל ניתוח תמונות עדיין לא מחובר במנוע הזה.", False

    opencode_path = OPENCODE_BIN if Path(OPENCODE_BIN).exists() else shutil.which("opencode")
    if not opencode_path:
        return "OpenCode לא מותקן או לא נמצא על השרת. צריך להתקין ולהגדיר opencode כדי שאוכל לענות בשיחה אמיתית.", False

    command = [opencode_path, "run"]
    if OPENCODE_AGENT:
        command.extend(["--agent", OPENCODE_AGENT])
    if OPENCODE_MODEL:
        command.extend(["--model", OPENCODE_MODEL])
    command.append(build_chat_prompt(history, user_text))

    env = {**os.environ, "NO_COLOR": "1"}

    last_reply = ""
    for _attempt in range(2):
        started = time.monotonic()
        try:
            result = subprocess.run(
                command,
                cwd=Path(__file__).resolve().parent,
                env=env,
                capture_output=True,
                text=True,
                timeout=OPENCODE_WEB_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            update_ai_status(False, "opencode", "OpenCode timeout", OPENCODE_WEB_TIMEOUT * 1000)
            return "", False
        except OSError as exc:
            update_ai_status(False, "opencode", exc)
            return f"OpenCode לא הצליח לפעול על השרת: {exc}", False

        elapsed_ms = (time.monotonic() - started) * 1000
        reply = strip_terminal_codes(result.stdout or "") or strip_terminal_codes(result.stderr or "")
        last_reply = reply
        if result.returncode != 0:
            update_ai_status(False, "opencode", reply or f"return code {result.returncode}", elapsed_ms)
            return f"OpenCode לא הצליח לענות כרגע: {reply or 'שגיאה לא ידועה'}", False
        if len(reply.strip()) >= 8:
            update_ai_status(True, "opencode", "OpenCode returned a usable reply", elapsed_ms)
            return reply, True

    update_ai_status(False, "opencode", f"Reply too short: {last_reply!r}")
    return last_reply, bool(last_reply)


def generate_with_bigpickle(history, user_text=None):
    bigpickle_path = BIGPICKLE_BIN if Path(BIGPICKLE_BIN).exists() else shutil.which(BIGPICKLE_BIN)
    if not bigpickle_path:
        update_ai_status(False, "bigpickle", "Bigpickle is not installed or not in PATH")
        return "", False

    command = [bigpickle_path, build_chat_prompt(history, user_text)]
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parent,
            env={**os.environ, "NO_COLOR": "1"},
            capture_output=True,
            text=True,
            timeout=BIGPICKLE_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        update_ai_status(False, "bigpickle", "Bigpickle timeout", BIGPICKLE_TIMEOUT * 1000)
        return "", False
    except OSError as exc:
        update_ai_status(False, "bigpickle", exc)
        return "", False

    elapsed_ms = (time.monotonic() - started) * 1000
    reply = strip_terminal_codes(result.stdout or "") or strip_terminal_codes(result.stderr or "")
    if result.returncode != 0:
        update_ai_status(False, "bigpickle", reply or f"return code {result.returncode}", elapsed_ms)
        return "", False
    update_ai_status(bool(reply), "bigpickle", "Bigpickle returned a reply" if reply else "Bigpickle returned an empty reply", elapsed_ms)
    return reply, bool(reply)

def generate_local_chat_reply(history):
    update_ai_status(False, "local", "Using local conversation fallback; external AI unavailable or disabled")
    return warm_fallback_reply(history), False


def generate_reply(user_text=None, image_part=None, session_id=None):
    history = get_chat_history(session_id)
    if AI_PROVIDER == "opencode":
        reply, ok = generate_with_opencode(history, user_text=user_text, image_part=image_part)
        if ok and reply:
            return reply, True
        return generate_local_chat_reply(history)

    if AI_PROVIDER == "bigpickle":
        reply, ok = generate_with_bigpickle(history, user_text=user_text)
        if ok and reply:
            return reply, True
        return generate_local_chat_reply(history)

    update_ai_status(False, AI_PROVIDER, "Unsupported AI_PROVIDER. Use opencode or bigpickle.")
    return generate_local_chat_reply(history)


def generate_image_reply(image_bytes, mime_type, session_id=None):
    if VISION_PROVIDER != "gemini":
        reply = local_image_reply(image_bytes)
        history = get_chat_history(session_id)
        history.append({"role": "user", "parts": ["[המשתמש העלה תמונה לניתוח]"]})
        history.append({"role": "model", "parts": [reply]})
        update_ai_status(False, f"vision:{VISION_PROVIDER}", "Vision provider is local/basic; no Gemini direct call")
        return reply, False

    if not client or not types:
        reply = local_image_reply(image_bytes)
        history = get_chat_history(session_id)
        history.append({"role": "user", "parts": ["[המשתמש העלה תמונה לניתוח]"]})
        history.append({"role": "model", "parts": [reply]})
        update_ai_status(False, "vision:gemini", "Gemini vision requested but client is not configured")
        return reply, False

    prompt = (
        "אתה MemoryLane. נתח בעדינות תמונה שהעלה משתמש קשיש. "
        "כתוב בעברית בלבד ואל תציג את עצמך מחדש. "
        "אל תזהה אנשים בשמות ואל תנחש פרטים רגישים, תאריך, מקום או קשר משפחתי אם הם לא ברורים. "
        "אם התמונה ריקה, מטושטשת או לא ברורה, אמור בעדינות שאין מספיק פרטים נראים. "
        "אם היא ברורה, תאר בקצרה 2-3 דברים שנראים בתמונה, ואז שאל שאלה אחת חמה שעוזרת להיזכר בסיפור שמאחוריה."
    )

    model_names = []
    for model in [VISION_MODEL, MODEL_NAME, "gemini-2.0-flash-lite", "gemini-2.0-flash"]:
        if model and model not in model_names:
            model_names.append(model)

    last_error = None
    response = None
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    for model in model_names:
        started = time.monotonic()
        try:
            response = client.models.generate_content(model=model, contents=[prompt, image_part])
            update_ai_status(True, f"vision:{model}", "Vision model returned a reply", (time.monotonic() - started) * 1000)
            break
        except Exception as exc:
            last_error = exc
            update_ai_status(False, f"vision:{model}", exc, (time.monotonic() - started) * 1000)

    if response is None:
        reply = local_image_reply(image_bytes)
        history = get_chat_history(session_id)
        history.append({"role": "user", "parts": ["[המשתמש העלה תמונה לניתוח]"]})
        history.append({"role": "model", "parts": [reply]})
        return reply, False

    reply = (response.text or "").strip()
    if not reply:
        return "קיבלתי את התמונה. מה הסיפור הקטן שהיא מחזירה אליך?", False

    history = get_chat_history(session_id)
    history.append({"role": "user", "parts": ["[המשתמש העלה תמונה לניתוח]"]})
    history.append({"role": "model", "parts": [reply]})
    return reply, True


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sw.js")
def service_worker():
    script = """
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'MemoryLane AI';
  const options = {
    body: data.body || '',
    icon: '/static/icon.png',
    badge: '/static/icon.png',
    requireInteraction: true,
    silent: false,
    vibrate: [240, 120, 240, 120, 360],
    data: { url: data.url || '/' }
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url || '/'));
});
"""
    return Response(script, mimetype="application/javascript")


@app.route("/api/get_address", methods=["GET"])
def get_address():
    data = load_saved_data()
    address = data.get("address", "")
    return jsonify(
        {
            "address": address,
            "classes": get_nearby_classes(data),
            "registered": data["registered_classes"],
        }
    )


@app.route("/api/address", methods=["POST"])
def address_endpoint():
    payload = request.get_json(silent=True) or {}
    address = payload.get("address", "").strip()
    if not address:
        return jsonify({"reply": "כדי למצוא פעילויות צריך לכתוב כתובת או אזור.", "ai_connected": False, "address": "", "classes": [], "registered": []}), 400
    location = geocode_address(address)
    data = load_saved_data()
    if location:
        data["address"] = city_from_geocode_result(location) or address
        data["latitude"] = location["latitude"]
        data["longitude"] = location["longitude"]
    else:
        data["address"] = address
        data["latitude"] = None
        data["longitude"] = None
    save_data(data)

    session_id = payload.get("session_id", "")
    if session_id:
        history = get_chat_history(session_id)
        history.append({"role": "user", "parts": [f"[מערכת: העיר או האזור הכללי של המשתמש עודכנו ל-{data['address']}]"]})
    reply = "עדכנתי את העיר או האזור הכללי וחיפשתי פעילויות קרובות לפי מקורות פתוחים."
    ai_connected = False

    return jsonify(
        {
            "reply": reply,
            "ai_connected": ai_connected,
            "address": data["address"],
            "classes": get_nearby_classes(data),
            "registered": data["registered_classes"],
        }
    )


@app.route("/api/location", methods=["POST"])
def location_endpoint():
    payload = request.get_json(silent=True) or {}
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    if latitude is None or longitude is None:
        return jsonify({"reply": "לא התקבל מיקום תקין. אפשר להזין כתובת ידנית.", "ai_connected": False, "classes": []}), 400
    address = reverse_geocode(latitude, longitude)

    data = load_saved_data()
    data["address"] = address
    data["latitude"] = float(latitude)
    data["longitude"] = float(longitude)
    save_data(data)

    session_id = payload.get("session_id", "")
    if session_id:
        history = get_chat_history(session_id)
        history.append({"role": "user", "parts": [f"[מערכת: מיקום GPS שותף. מוצג למשתמש רק כעיר או אזור כללי: {address}]"]})
    reply = "עדכנתי את העיר או האזור הכללי וחיפשתי פעילויות קרובות לפי מקורות פתוחים."
    ai_connected = False

    return jsonify(
        {
            "reply": reply,
            "ai_connected": ai_connected,
            "address": address,
            "classes": get_nearby_classes(data),
            "registered": data["registered_classes"],
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat_io():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()
    session_id = payload.get("session_id", "")
    if not message:
        return jsonify({"reply": "אני כאן. אפשר לכתוב לי כל זיכרון שעולה עכשיו."})

    history = get_chat_history(session_id)
    history.append({"role": "user", "parts": [message]})
    if should_use_local_chat_reply(message):
        reply = warm_fallback_reply(history)
        update_ai_status(False, "local", "Answered locally for simple conversational turn")
        history.append({"role": "model", "parts": [reply]})
        return jsonify({"reply": reply, "ai_connected": False})

    reply, ai_connected = generate_reply(session_id=session_id)
    if ai_connected:
        history.append({"role": "model", "parts": [reply]})

    return jsonify({"reply": reply, "ai_connected": ai_connected})


@app.route("/api/classes/register", methods=["POST"])
def register_class():
    payload = request.get_json(silent=True) or {}
    class_id = payload.get("class_id")
    data = load_saved_data()

    if class_id in data["registered_classes"]:
        data["registered_classes"].remove(class_id)
    else:
        data["registered_classes"].append(class_id)

    save_data(data)
    return jsonify(
        {
            "classes": get_nearby_classes(data),
            "registered": data["registered_classes"],
        }
    )


@app.route("/api/medications", methods=["GET"])
def get_medications():
    return jsonify(load_saved_data()["medications"])


@app.route("/api/medications/add", methods=["POST"])
def add_medication():
    data = load_saved_data()
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    time = payload.get("time", "").strip()

    if name and time:
        data["medications"].append({"name": name, "time": time})
        save_data(data)

    return jsonify({"status": "success", "medications": data["medications"]})


@app.route("/api/medications/delete", methods=["POST"])
def delete_medication():
    payload = request.get_json(silent=True) or {}
    index = payload.get("index")
    data = load_saved_data()

    if isinstance(index, int) and 0 <= index < len(data["medications"]):
        data["medications"].pop(index)
        save_data(data)

    return jsonify({"status": "success", "medications": data["medications"]})


@app.route("/api/push/public-key", methods=["GET"])
def push_public_key():
    return jsonify(
        {
            "publicKey": VAPID_PUBLIC_KEY,
            "enabled": bool(webpush and VAPID_PUBLIC_KEY and PUSH_PRIVATE_KEY),
        }
    )


@app.route("/api/push/subscribe", methods=["POST"])
def subscribe_push():
    subscription = request.get_json(silent=True) or {}
    data = load_saved_data()
    endpoint = subscription.get("endpoint")
    if endpoint and all(item.get("endpoint") != endpoint for item in data["push_subscriptions"]):
        data["push_subscriptions"].append(subscription)
        save_data(data)
    return jsonify({"status": "success", "enabled": bool(webpush and PUSH_PRIVATE_KEY)})


def send_push(subscription, title, body):
    if not webpush or not PUSH_PRIVATE_KEY:
        return False

    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps({"title": title, "body": body, "url": "/"}),
            vapid_private_key=PUSH_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_CLAIMS_SUB},
        )
        return True
    except WebPushException:
        return False


@app.route("/api/push/test", methods=["POST"])
def test_push():
    data = load_saved_data()
    sent = 0
    for subscription in data["push_subscriptions"]:
        if send_push(subscription, "בדיקת התרעה - MemoryLane AI", "אם קיבלת את זה, התרעות Push מחוברות."):
            sent += 1
    return jsonify({"status": "success", "sent": sent})


def medication_push_loop():
    while True:
        data = load_saved_data()
        current_time = time.strftime("%H:%M")
        today = time.strftime("%Y-%m-%d")
        changed = False

        for medication in data["medications"]:
            if medication.get("time") != current_time:
                continue
            alert_key = f"{today}-{current_time}-{medication.get('name', '')}"
            if data["last_push_alerts"].get(alert_key):
                continue

            for subscription in data["push_subscriptions"]:
                send_push(
                    subscription,
                    "תזכורת תרופה - MemoryLane AI",
                    f"הגיע הזמן לקחת {medication.get('name', 'את התרופה')}.",
                )
            data["last_push_alerts"][alert_key] = True
            changed = True

        if changed:
            save_data(data)

        time.sleep(5)


threading.Thread(target=medication_push_loop, daemon=True).start()


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
