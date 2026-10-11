#!/bin/bash
# 한방에 담다 Kling 3.0 std, 9:16, 3s x5 = 22.5cr (approved cap 27cr)
cd "$(dirname "$0")"; mkdir -p clips
PRE="Warm stylized 3D clay animation, the mascots keep their exact designs (licorice-slice Gamcho with red paper band and smooth brown clay mitten arms; mugwort-leaf Ssuk; chrysanthemum Gamguk), smooth natural motion."
AV="Avoid: text, letters, logo, watermark, human faces, fingers, extra limbs, duplicated characters, deformed character, morphing, flicker, jitter, photorealistic."
declare -A M S
S[C01]=img/C01Sb_1.png;  M[C01]="The drawer slides open with a snap, Gamcho springs out, lands on the cabinet edge and stares straight into the camera with a surprised face, quick and bouncy."
S[C04]=img/C04S_fix.png; M[C04]="Gamcho walks along the row of drawers and looks around left and right, puzzled, searching; camera tracks sideways slowly."
S[C08]=img/C08Sd_fix.png; M[C08]="Gamcho hops two steps toward the tub edge; Ssuk and Gamguk step left toward it and stretch their leaf arms out to block; Gamcho bounces back to the left. Steam rises gently. No people, no faces."
S[C11]=img/C11S_fix.png; M[C11]="Gamcho does a small hop, lands and strikes a proud pose, the jade robe hem sways; the mirror and its reflection stay still. Static camera."
S[C14]=img/C14Sc_fix.png; M[C14]="Gamcho jumps up in the middle of the group and waves at the camera; the visitors stay completely still, turned away; gentle camera pull-back. No faces, no statues, no signboards."
for k in C01 C04 C08 C11 C14; do
  [ -f "clips/$k.mp4" ] && continue
  url=$(higgsfield.cmd generate create kling3_0 --start-image "${S[$k]}" --prompt "$PRE ${M[$k]} $AV" --duration 3 --mode std --aspect_ratio 9:16 --sound off --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  [ -n "$url" ] && curl -s -o "clips/$k.mp4" "$url" && echo "$k ok $(date -u +%T)" || echo "$k FAIL"
done
