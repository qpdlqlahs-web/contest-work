import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
for name in sys.argv[1:]:
    segs, _ = m.transcribe(f"stems/htdemucs/{name}/vocals.wav", language="ko", word_timestamps=True,
                           vad_filter=False, beam_size=5, initial_prompt="퓨리얼, 직수, 필터, 꿀꺽, 콸콸, 뚝딱, Pure, Real")
    out = []
    print(f"===== {name}")
    for s in segs:
        print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [[w.start, w.end, w.word] for w in s.words]})
    json.dump(out, open(f"stems/{name}_words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
