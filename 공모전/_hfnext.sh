#!/bin/bash
# usage: _hfnext.sh PROJECTDIR SINCE KEY NAME  -> pull result, then wait until slot is free
SINCE="$2"; [ "$SINCE" = "auto" ] && SINCE=$(date -u -d "-3 minutes" +%FT%T)
cd "$1" && python hf_pull.py "$SINCE" "$3" "$4" --wait 560
for i in $(seq 1 40); do n=$(higgsfield.cmd generate list --json 2>/dev/null | python -c "import json,sys;d=json.load(sys.stdin);d=d if isinstance(d,list) else d.get('items',[]);print(sum(j.get('status') in ('waiting','in_progress','queued') for j in d[:10]))"); [ "$n" = "0" ] && { echo "free $(date -u +%FT%T)"; break; }; sleep 12; done
