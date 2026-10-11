#!/bin/bash
cd "$(dirname "$0")/.."
ed(){ out=$1; src=$2; ar=$3; shift 3
  ( url=$(higgsfield generate create nano_banana_flash --prompt "Edit this image. Keep the claymation style, camera angle, framing, lighting and the characters exactly the same. $*  No text, no letters, no logos anywhere." --image-references $src --aspect_ratio $ar --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "kf3/$out.png" "$url" && echo "$out ok" || echo "$out FAIL" ) & }
ed V4s kf3/V4s.png 16:9 "Remove the beige car on the road completely (empty red road there). Keep the boy at the crosswalk start looking toward screen-right."
ed V5 kf3/V5.png 16:9 "Remove the red car in the background completely (empty road). The grandmother and the boy now hold hands, both stepping slowly onto the zebra crosswalk together. Keep the pedestrian signal with only the bottom green lamp lit."
ed N1s kf3/N1s.png 16:9 "Remove the pedestrian traffic signal and any crosswalk stripes; keep both cars, the red school-zone road and the buildings."
ed N2 kf3/N2.png 16:9 "Remove the pedestrian traffic signal and all zebra-crosswalk stripes on the road; keep the turtle-car, the school fence, the red road and the blank triangle sign."
ed N3 kf3/N3.png 16:9 "Remove the pedestrian traffic signal and all zebra-crosswalk stripes; keep the turtle-car on the red road and the grandmother and boy on the sidewalk giving a thumbs up."
ed A14f kf3/A14f.png 16:9 "Remove the blue car on the left side of the image (the one near the red bicycle lane) completely; keep the blue car on the right, the young woman on the scooter in the bicycle lane, and everything else."
wait
