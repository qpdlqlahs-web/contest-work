#!/bin/bash
# HighlightTV Kling 3.0 std, 16:9, no sound. K1-K3 5s (7.5cr), K4 3s (4.5cr) = 27cr (approved budget)
cd "$(dirname "$0")"; mkdir -p clips
PRE="Photorealistic Korean TV drama footage, the woman keeps her exact face, grey permed bob, gold glasses and mustard cardigan; no text appearing."
AV="Avoid: extra fingers, deformed hands, face morphing, identity change, extra people, text, logos, camera shake."
declare -A M D
M[K1]="Slow motion. Water arcs from the man's paper cup toward the woman on the right. She snaps the black umbrella open in front of her in one smooth motion; the water hits the umbrella canopy and bursts into sparkling backlit droplets. She stays completely dry and expressionless. Locked camera height, slow push-in. Water never passes through the umbrella."; D[K1]=5
M[K2]="Slow motion. The kimchi flies in an arc toward the woman on the right. She lifts the red tub with both hands up to eye level, tilting the red lid like a shield; the kimchi slaps onto the lid with a small spray of red seasoning droplets. She lowers the tub slightly and blinks calmly. The angry woman on the left freezes, mouth open. Locked camera, slight push-in. Kimchi never passes through the lid, no red splatter on faces."; D[K2]=5
M[K3]="Slow-motion confident walk toward the camera, papers drift and flutter through the air around her, hair and cardigan move gently, coworkers turn their heads to watch, camera dollies back slowly keeping her centered, soft lens flare from the windows. Natural walking steps, no sliding feet, no leg distortion."; D[K3]=5
M[K4]="She looks up toward the top-right corner of the frame, raises her left hand up and out of the frame at the top right as if picking something off the screen, then brings her closed hand down and presses it gently on the left side of her chest, then looks into the camera with a small proud smile. Static locked camera, no zoom."; D[K4]=3
declare -A S=([K1]=img/K1Sb_1.png [K2]=img/K2Se_1.png [K3]=img/K3Sb_1.png [K4]=img/K4Sb_1.png)
for k in K1 K2 K3 K4; do
  [ -f "clips/$k.mp4" ] && continue
  url=$(higgsfield.cmd generate create kling3_0 --start-image "${S[$k]}" --prompt "$PRE ${M[$k]} $AV" --duration ${D[$k]} --mode std --aspect_ratio 16:9 --sound off --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  [ -n "$url" ] && curl -s -o "clips/$k.mp4" "$url" && echo "$k ok $(date -u +%T)" || echo "$k FAIL"
done
