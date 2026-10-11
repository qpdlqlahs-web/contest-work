from faster_whisper import WhisperModel
import sys
m=WhisperModel('medium',device='cpu',compute_type='int8')
segs,info=m.transcribe('audio/naJuyeon_t2.wav',language='ko',word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
for s in segs:
    print(f'{s.start:6.2f}-{s.end:6.2f} {s.text}')
