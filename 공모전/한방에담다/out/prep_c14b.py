# -*- coding: utf-8 -*-
"""v2: C14b(720x1280, 3.04s) -> 1.0 업스케일+샤픈 -> 0.8배속(minterpolate) 3.8s(91f@24) -> prep\clips\C14b.mp4"""
import os, sys
os.environ.setdefault("CLIP_TMP", r"E:\ClaudeWork\temp\E--ClaudeWork--\78455281-bfb1-4500-a2a1-02eb5397fe60\scratchpad\clipwork")
sys.path.insert(0, r"E:\ClaudeWork\일\2026\공모전\한방에담다\prep")
import clips_prep as cp
os.makedirs(cp.TMP, exist_ok=True)
fr = cp.extract("C14b", speed=0.8, method="mci")[:91]
cp.encode(fr, "C14b"); print("C14b", len(fr))
