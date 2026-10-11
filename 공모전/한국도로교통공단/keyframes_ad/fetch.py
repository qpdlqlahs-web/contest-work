"""Download the newest N completed image jobs (web generations show up here too).
usage: python fetch.py N name  -> saves name_1.png, name_2.png ... into keyframes_ad/"""
import json, subprocess, sys, os, re, urllib.request
n, name = int(sys.argv[1]), sys.argv[2]
out = subprocess.run("higgsfield generate list --json", shell=True, capture_output=True, text=True, encoding="utf-8").stdout
items = json.loads(out); items = items if isinstance(items, list) else next(v for v in items.values() if isinstance(v, list))
imgs = [j for j in items if j.get("status") == "completed" and re.search(r"https://\S+\.(png|jpg|webp)", json.dumps(j))][:n]
for i, j in enumerate(imgs, 1):
    url = [u for u in re.findall(r"https://[^\"\s]+", json.dumps(j)) if "/hf_" in u and not u.endswith("_min.webp")][0]
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{name}_{i}.png")
    urllib.request.urlretrieve(url, dst); print(dst, url[-50:])
