#!/bin/bash
# usage: gen.sh NAME REF PROMPT  -> NAME.png (seedream 4.5 edit, 9:16)
name=$1; ref=$2; prompt=$3
higgsfield generate create seedream_v4_5 --aspect_ratio 9:16 --quality high --image "$ref" --prompt "$prompt" --wait --json 2>&1 \
 | python3 -c "import json,sys;d=json.load(sys.stdin);print(d[0]['status']);print(d[0]['result_url'])" > _$name.url
url=$(tail -1 _$name.url); curl -sSfL -o $name.png "$url" && python3 -c "
from PIL import Image;Image.open('$name.png').convert('RGB').resize((270,480)).save('_${name}_s.jpg',quality=85)" && echo "$name ok"
