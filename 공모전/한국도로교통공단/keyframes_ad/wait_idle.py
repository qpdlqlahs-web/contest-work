"""Block until no Higgsfield job is pending (free Unlimited runs one at a time)."""
import json, subprocess, time
time.sleep(6)
for _ in range(80):
    items = json.loads(subprocess.run("higgsfield generate list --json", shell=True, capture_output=True, text=True, encoding="utf-8").stdout)
    items = items if isinstance(items, list) else next(v for v in items.values() if isinstance(v, list))
    pend = [j for j in items[:10] if j.get("status") not in ("completed", "failed", "nsfw", "canceled", "cancelled")]
    if not pend: print("idle"); break
    time.sleep(10)
else: print("timeout")
