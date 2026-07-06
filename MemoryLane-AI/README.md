# MemoryLane AI

MemoryLane AI is a warm Hebrew-first reminiscence companion for older adults.
It helps users tell life stories, reflect on memories, upload meaningful photos,
and optionally connect their location to nearby social activities.

## Product Idea

MemoryLane is designed as a gentle daily companion, not a medical system.
It supports reminiscence therapy-style conversations by asking patient,
specific follow-up questions about the user's past and by validating emotional
details in a calm voice.

Core flows:

- Personal conversation in natural Hebrew.
- First-name memory for the current chat session.
- Photo upload that turns an image into a warm memory prompt.
- Address or GPS-based search for nearby activity places using OpenStreetMap.
- Medication reminder list stored locally.
- Browser notification permission and optional Web Push reminders.

## Suggested MVP

1. Chat screen with Hebrew conversation.
2. Photo upload prompt generator.
3. Real nearby activity search by address or GPS.
4. Medication list with add/delete actions.
5. Local JSON storage for prototype data.

## Run Locally

```bash
cd /Users/origan/Documents/Projects/MemoryLane-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then edit `.env` and add your Gemini API key:

```bash
GEMINI_API_KEY=your_key_here
```

For medication reminders that can arrive after the tab is closed, also add VAPID
Web Push keys. Generate them outside git, then copy the public key into `.env`:

```bash
python -m py_vapid --gen
python -m py_vapid --applicationServerKey --private-key private_key.pem
```

Use the `applicationServerKey` output as `VAPID_PUBLIC_KEY`, and set
`VAPID_PRIVATE_KEY_PATH=private_key.pem`. Keep `private_key.pem` secret. Without
VAPID keys, the app can still request browser notification permission, but
closed-tab push reminders will not be active.

Closed-tab reminders require all of these:

- The Flask server is running at the reminder time.
- The user clicked "אפשר התרעות גם כשהאתר סגור" and approved notifications.
- The site is opened from `localhost`, `127.0.0.1`, or HTTPS.
- VAPID keys are configured in `.env`.

Start the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Notes

- Do not commit real API keys.
- This prototype stores user data in `user_schedule.json`.
- Nearby places come from public OpenStreetMap/Nominatim/Overpass data, so some
  places may be missing contact details.
- For a real product, add authentication, consent screens, privacy controls,
  encrypted storage, and clear medical disclaimers.
