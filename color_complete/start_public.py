import re
import shutil
import subprocess
import sys
import threading
import time


def pipe_output(process, public_url):
    pattern = re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")
    for line in process.stdout:
        print(line, end="")
        match = pattern.search(line)
        if match and not public_url["value"]:
            public_url["value"] = match.group(0)
            print("\nPublic game link:")
            print(public_url["value"])
            print("\nKeep this window open while people are playing.\n")


def main():
    if not shutil.which("cloudflared"):
        print("cloudflared is not installed.")
        print("Install it first:")
        print("  brew install cloudflared")
        print("\nThen run:")
        print("  python3 start_public.py")
        return 1

    server = subprocess.Popen([sys.executable, "web_server.py"])
    time.sleep(1)

    public_url = {"value": None}
    tunnel = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    threading.Thread(target=pipe_output, args=(tunnel, public_url), daemon=True).start()

    try:
        while tunnel.poll() is None:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        tunnel.terminate()
        server.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
