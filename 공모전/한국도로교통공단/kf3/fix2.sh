#!/bin/bash
cd "$(dirname "$0")/.."
ed(){ out=$1; src=$2; shift 2
  ( url=$(higgsfield generate create nano_banana_flash --prompt "Edit this image. Keep the claymation style, the exact same camera angle, framing, background, lighting and character designs. $*  No text, no letters, no logos anywhere." --image-references $src --aspect_ratio 16:9 --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "kf3/$out.png" "$url" && echo "$out ok" || echo "$out FAIL" ) & }
ed V4e kf3/V4s.png "Only change the boy's pose: he has turned his head to look toward screen-LEFT, and is taking his first confident step forward onto the zebra crosswalk, smiling."
ed N1e kf3/N1s.png "Only change the car positions: the red rabbit-car has overtaken and is now clearly AHEAD on the right side of the frame, ears flapping, with a small clay dust puff behind it; the green turtle-car is now behind it on the left, still calm and smiling. Both cars still face screen-right."
wait
