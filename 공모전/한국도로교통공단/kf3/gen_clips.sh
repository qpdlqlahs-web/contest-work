#!/bin/bash
# v5 clips (Kling 3.0 pro, 5s, no sound)
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing, no new characters appear. Pedestrian signal (if visible) keeps only the bottom green lamp lit the whole time."
run(){ out=$1; shift
  ( url=$("$@" --duration 5 --mode pro --sound off --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
    [ -n "$url" ] && curl -s -o "$out" "$url" && echo "$out ok" || echo "$out FAIL" ) & }
K="higgsfield generate create kling3_0"
run clips_ad/V1.mp4 $K --start-image kf3/V1.png --aspect_ratio 16:9 --prompt "$PRE Static camera. The small boy stands beside the tall hedge, looking around a little unsure; in the background the turtle-car drives slowly toward the crosswalk and comes to a complete stop behind the white stop line."
run clips_ad/V2.mp4 $K --start-image kf3/V2.png --aspect_ratio 16:9 --prompt "$PRE Static camera. The boy raises his hand high and waves it so he is easy to see; the turtle-car stays completely still behind the stop line, blinks and nods at him kindly."
run clips_ad/V3.mp4 $K --start-image kf3/V3.png --aspect_ratio 16:9 --prompt "$PRE Static camera. The boy, seen from behind, watches the stopped turtle-car; the turtle-car stays still behind the stop line, smiles and nods to show it has stopped. The car does not move."
run clips_ad/V4.mp4 $K --start-image kf3/V4s2.png --aspect_ratio 16:9 --prompt "$PRE Static camera. The boy, standing at the start of the crosswalk, turns his head to look one way down the road, then turns to look the other way, then smiles and steps forward onto the zebra crosswalk. No cars move."
run clips_ad/V5.mp4 $K --start-image kf3/V5.png --aspect_ratio 16:9 --prompt "$PRE Static camera. The grandmother and the boy, holding hands, walk slowly and carefully forward across the zebra crosswalk; grandma takes small gentle steps and smiles. The background never moves."
run clips_ad/V6.mp4 $K --start-image kf3/V6.png --aspect_ratio 16:9 --prompt "$PRE The camera tracks slowly sideways with them. Grandma's hand gently holds the boy's hand as they walk slowly across the zebra stripes; her thumb softly squeezes his hand."
run clips_ad/N1.mp4 $K --start-image kf3/N1_start.png --end-image kf3/N1_end.png --aspect_ratio 16:9 --prompt "$PRE The camera tracks sideways with the cars. Both cars drive toward screen-left. The red rabbit-car speeds up from behind and overtakes the calm turtle-car, laughing smugly with a clay dust puff. Cars only move forward."
run clips_ad/N2.mp4 $K --start-image kf3/N2.png --aspect_ratio 16:9 --prompt "$PRE The camera slowly tracks backward in front of the car. The turtle-car drives slowly and proudly forward along the red school-zone road, its shell gleaming, confident smile."
run clips_ad/N3.mp4 $K --start-image kf3/N3.png --aspect_ratio 16:9 --prompt "$PRE The camera tracks slowly sideways. The turtle-car cruises slowly forward along the red road; on the sidewalk the grandmother and the boy give it a big thumbs up and smile; the turtle-car winks back."
run clips_ad/A14.mp4 $K --start-image kf3/A14f.png --aspect_ratio 16:9 --prompt "$PRE The camera slowly tracks backward in front of her. The young woman, stopped in the bicycle lane, taps her yellow helmet proudly, then holds the handlebar with both hands and rides slowly forward inside the bicycle lane. Signboards stay blank."
run clips/S09.mp4 $K --start-image kf3/S09f.png --aspect_ratio 9:16 --prompt "$PRE The camera slowly tracks backward in front of her. The young woman, stopped in the blue bicycle lane, taps her yellow helmet proudly, then holds the handlebar with both hands and rides slowly forward inside the bicycle lane. Signboards stay blank."
wait
