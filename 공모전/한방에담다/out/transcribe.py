import sys, json, subprocess, os
from pathlib import Path
wav = r'..\audio\yakbang_t2.wav'
# demucs vocals
out = Path('_work/demucs')
if not (out/'htdemucs'/'yakbang_t2'/'vocals.wav').exists():
    subprocess.run([sys.executable,'-m','demucs','--two-stems','vocals','-o',str(out),wav],check=True)
voc = str(out/'htdemucs'/'yakbang_t2'/'vocals.wav')
from faster_whisper import WhisperModel
try:
    m = WhisperModel('large-v3', device='cpu', compute_type='int8')
except Exception as e:
    print('cuda fail', e); m = WhisperModel('large-v3', device='cpu', compute_type='int8')
segs, info = m.transcribe(voc, language='ko', word_timestamps=True, vad_filter=False, condition_on_previous_text=False, beam_size=5)
res=[]
for s in segs:
    print(f'{s.start:6.2f}-{s.end:6.2f} {s.text}')
    res.append(dict(start=s.start,end=s.end,text=s.text,words=[(w.start,w.end,w.word) for w in s.words]))
json.dump(res, open('_work/whisper.json','w'), ensure_ascii=False, indent=1)
