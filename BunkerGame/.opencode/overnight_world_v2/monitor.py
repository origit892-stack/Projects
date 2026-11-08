import os
import re
import time
import json
from datetime import datetime

ROOT="/Users/Ori/Documents/Projects/BunkerGame"
R=os.path.join(ROOT,".opencode","overnight_world_v2")

ORDER=[
("CP01_SAFETY","Safety / inventory"),
("CP02_WORLD_PLAN","World topology"),
("CP03_TERRAIN","Terrain / hills"),
("CP04_FOREST","Forest"),
("CP05_ROCKS_LANDMARKS","Rocks / landmarks"),
("CP06_WILDLIFE","Wildlife"),
("CP07_GAMEPLAY","Gameplay"),
("CP08_PRESENTATION","Presentation"),
("CP09_TECH_QA","Technical QA"),
("CP10_PLAY_QA","Play QA"),
("CP11_VISUAL_QA","Visual QA"),
("CP12_FINAL","Final integration"),
]

def read(path, default=""):
    try:
        with open(path,"r",errors="replace") as f:
            return f.read()
    except:
        return default

def tail(path,n=18):
    try:
        with open(path,"r",errors="replace") as f:
            x=f.readlines()
        return [z.rstrip() for z in x[-n:]]
    except:
        return []

def parse_events():
    events=[]
    for line in tail(os.path.join(R,"events.log"),200):
        p=line.split("|",3)
        if len(p)==4:
            events.append(p)
    return events

def newest_run():
    p=read(os.path.join(R,"current_run_file.txt")).strip()
    return p if p and os.path.isfile(p) else ""

def clean_event(line):
    line=line.strip()
    if len(line)>220:
        line=line[:217]+"..."
    return line

while True:
    os.system("clear")

    state=read(os.path.join(R,"state.txt"),"UNKNOWN").strip()
    cp=read(os.path.join(R,"current_checkpoint.txt"),"NONE").strip()
    activity=read(os.path.join(R,"current_activity.txt"),"Waiting for first event").strip()
    attempt=read(os.path.join(R,"attempt.txt"),"0").strip()
    pid=read(os.path.join(R,"active_run.pid"),"").strip()

    events=parse_events()
    passed={e[1] for e in events if e[2]=="PASS"}
    failed=[e for e in events if e[2]=="FAIL"]

    run=newest_run()
    run_size=0
    age=None
    run_lines=[]

    if run:
        try:
            st=os.stat(run)
            run_size=st.st_size
            age=int(time.time()-st.st_mtime)
            run_lines=tail(run,80)
        except:
            pass

    last_live=""
    last_tool=""
    error_count=0

    for line in run_lines:
        if "LIVE|" in line:
            m=re.search(r'LIVE\|[^"\\]*',line)
            if m:
                last_live=m.group(0)
        if '"tool":"' in line:
            m=re.search(r'"tool":"([^"]+)"',line)
            if m:
                last_tool=m.group(1)
        low=line.lower()
        if '"status":"error"' in low or '"status":"failed"' in low:
            error_count+=1

    total=len(ORDER)
    pc=sum(1 for x,_ in ORDER if x in passed)
    percentage=int(pc/total*100)
    bars=round(percentage/4)
    bar="█"*bars+"░"*(25-bars)

    print("="*72)
    print(" BUNKERGAME — LIVE WORLD BUILD V2")
    print(" "+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*72)
    print()
    print(f"STATE        : {state}")
    print(f"ATTEMPT      : {attempt}")
    print(f"RUN PID      : {pid or 'NONE'}")
    print(f"CHECKPOINT   : {cp}")
    print(f"ACTIVITY     : {activity[:150]}")
    print(f"LAST TOOL    : {last_tool or 'waiting'}")
    print(f"RUN LOG      : {run if run else 'not created yet'}")
    print(f"LOG SIZE     : {run_size:,} bytes")
    print(f"LAST OUTPUT  : {str(age)+' sec ago' if age is not None else 'N/A'}")
    print(f"ERROR EVENTS : {error_count}")
    print()
    print(f"PROGRESS     : [{bar}] {percentage}%  ({pc}/{total})")
    print()
    print("CHECKPOINTS")
    print("-"*72)

    for key,label in ORDER:
        if key in passed:
            icon="✓"
        elif key==cp:
            icon="●"
        else:
            icon="○"
        print(f" {icon} {key:<24} {label}")

    print()
    print("LAST LIVE AGENT EVENT")
    print("-"*72)
    print(last_live if last_live else "waiting for LIVE event...")
    print()
    print("RECENT PHYSICAL CHECKPOINT EVENTS")
    print("-"*72)

    if events:
        for e in events[-8:]:
            print(f"{e[0]} | {e[1]} | {e[2]} | {e[3][:100]}")
    else:
        print("No checkpoint events yet.")

    print()
    print("WATCHDOG")
    print("-"*72)

    wd=tail(os.path.join(R,"watchdog.log"),6)
    for line in wd:
        print(clean_event(line))

    print()
    print("="*72)
    print("Dashboard refreshes every 3 seconds.")
    print("Ctrl+C stops ONLY this dashboard — the overnight build keeps running.")
    print("="*72)

    time.sleep(3)
