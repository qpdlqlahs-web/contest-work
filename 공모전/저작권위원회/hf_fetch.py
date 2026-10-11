"""Poll Higgsfield jobs created after a UTC timestamp, download finished panels to img/P{n}.png (by prompt keyword).
Read-only listing (no credits). usage: python hf_fetch.py 2026-10-07T08:40 [--wait N]"""
import json, re, subprocess, sys, time, urllib.request, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SINCE = sys.argv[1]
WAIT = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 0
KEYS = {1: "smugly dragging", 2: "bursts into the cozy bedroom", 3: "points clearly up at a framed", 4: "wagging her index finger",
        5: "kindly shows", 6: "triumphant finale"}

def hf(*a):
    return json.loads(subprocess.run(["higgsfield.cmd", *a, "--json"], capture_output=True, text=True, encoding="utf-8").stdout or "null")

def scan():
    d = hf("generate", "list")
    items = d if isinstance(d, list) else (d or {}).get("items", [])
    rows = []
    for j in items:
        if j.get("created_at", "") <= SINCE: continue
        g = hf("generate", "get", j["id"])
        s = json.dumps(g, ensure_ascii=False)
        n = next((k for k, v in KEYS.items() if v in s), None)
        url = next((u for u in re.findall(r'https://[^"]+?\.png', s) if j["id"] in u), None)
        rows.append((j["created_at"][:19], j.get("status"), n, url))
    return rows

t0 = time.time()
while True:
    rows = scan()
    pending = [r for r in rows if r[1] not in ("completed", "failed")]
    if not pending or time.time() - t0 > WAIT: break
    time.sleep(20)
for ts, st, n, url in rows:
    if st == "completed" and n and url:
        urllib.request.urlretrieve(url, f"img/P{n}.png")
    print(ts, st, f"P{n}", "saved" if st == "completed" and url else "")
