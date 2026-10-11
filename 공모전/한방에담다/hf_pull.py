"""Higgsfield 작업 목록에서 SINCE(UTC) 이후, 프롬프트에 KEY가 들어간 작업을 찾아 img/NAME_n.png로 저장(읽기 전용, 크레딧 없음).
usage: python hf_pull.py SINCE KEY NAME [--wait N]"""
import json, re, subprocess, sys, time, urllib.request, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SINCE, KEY, NAME = sys.argv[1], sys.argv[2], sys.argv[3]
WAIT = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 0
def hf(*a): return json.loads(subprocess.run(["higgsfield.cmd", *a, "--json"], capture_output=True, text=True, encoding="utf-8").stdout or "null")
t0 = time.time()
while True:
    d = hf("generate", "list"); items = d if isinstance(d, list) else (d or {}).get("items", [])
    rows = []
    for j in items:
        if j.get("created_at", "") <= SINCE: continue
        g = hf("generate", "get", j["id"]); s = json.dumps(g, ensure_ascii=False)
        if KEY not in s: continue
        url = next((u for u in re.findall(r'https://[^"]+?\.png', s) if j["id"] in u), None)
        rows.append((j["created_at"][:19], j.get("status"), url))
    if rows and all(r[1] in ("completed", "failed") for r in rows) or time.time() - t0 > WAIT: break
    time.sleep(20)
rows.sort()
for k, (ts, st, url) in enumerate(rows, 1):
    if st == "completed" and url: urllib.request.urlretrieve(url, f"img/{NAME}_{k}.png")
    print(ts, st, f"{NAME}_{k}" if url else "")
