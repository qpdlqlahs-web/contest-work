"""Save newest completed job whose prompt contains KEY as keyframes_ad/NAME.png.  usage: python save.py "KEY" NAME"""
import json, subprocess, re, sys, urllib.request, os
key, name = sys.argv[1], sys.argv[2]
items = json.loads(subprocess.run("higgsfield generate list --json", shell=True, capture_output=True, text=True, encoding="utf-8").stdout)
items = items if isinstance(items, list) else next(v for v in items.values() if isinstance(v, list))
for j in items[:15]:
    if key in str(j.get("params", {}).get("prompt", "")) and j["status"] == "completed":
        u = j["result_url"]
        urllib.request.urlretrieve(u, os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{name}.png")); print(name, "saved"); break
else: print(name, "NOT FOUND")
