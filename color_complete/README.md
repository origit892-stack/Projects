# Color Complete

Color Complete is available in two versions:

- `web_server.py` + `web/index.html`: browser multiplayer with one public URL.
- `main.py`: the older local Pygame version.

## Run The Web Version

```bash
python3 -m pip install -r requirements.txt
python3 web_server.py
```

Open:

```text
http://localhost:8080
```

Players use the same URL in their browsers. One player presses `Host`, shares the room code, and the others press `Join`.

## Deploy To The Internet

This game needs a server that supports WebSockets. Static hosts like Netlify/GitHub Pages alone are not enough.

Good options:

- Cloudflare Tunnel from your computer, no GitHub needed
- Railway
- Fly.io
- Heroku
- A VPS with Docker

### No GitHub: Temporary Public Link

Install Cloudflare Tunnel:

```bash
brew install cloudflared
```

Then run:

```bash
python3 start_public.py
```

It will print a public link like:

```text
https://something.trycloudflare.com
```

Send that link to friends. Keep the terminal window open while playing.

### Railway

Railway supports long-running web services and WebSockets, so it fits this game better than Vercel serverless.

With GitHub:

1. Push this folder to GitHub.
2. In Railway, create a new project from the GitHub repo.
3. Railway will detect the `Dockerfile`.
4. It will run:

```bash
python web_server.py
```

Without GitHub:

1. Install the Railway CLI.
2. From this folder, run:

```bash
railway login
railway init
railway up
```

3. In Railway, generate a public domain for the service.
4. Open the public Railway URL.

Test the deployment:

```text
https://your-app.up.railway.app/health
```

It should return:

```json
{"ok": true, "rooms": 0, "websocket_path": "/ws"}
```

### Fly.io / Docker VPS

Build and run:

```text
docker build -t color-complete .
docker run -p 8080:8080 color-complete
```

When deployed publicly, send everyone the public URL. The browser automatically connects to `/ws` on the same domain.

### Netlify Static + Separate WebSocket Server

Netlify static hosting is not enough by itself because this game needs a long-lived WebSocket server at `/ws`.
You can host only the static HTML on Netlify and point it at a separate WebSocket server:

```text
https://your-netlify-site.netlify.app/?ws=wss://your-websocket-server.example.com/ws
```

## Run The Pygame Version

```bash
python3 main.py
```

For Pygame with a hosted relay:

```bash
COLOR_COMPLETE_WS_URL=wss://your-server.example.com python3 main.py
```

## Controls

- Menu: choose player count, round time, number of rounds, then press Start.
- Menu: enter your name, press `Host`, and share the 5-character room code.
- Menu: enter a friend's code and press `Join` to connect through the WebSocket relay.
- Menu: press `New idea` to roll a new drawing prompt.
- Menu: only the host can start the network game.
- Drawing: hold the left mouse button and drag on the canvas.
- Drawing: choose brush color and size from the toolbar.
- Drawing: press the undo arrow, `Z`, or `Backspace` to remove the last stroke from the current turn.
- Drawing: hold `Hint` to peek at the previous drawing in a light onion-skin view.
- Drawing: press `N` to end the current turn early.
- Gallery: use left/right arrow keys to scroll through final drawings and see who contributed to each one.
- Anywhere: press `Esc` to quit.
