import librosa, numpy as np
v,sr=librosa.load('out/_demucs/htdemucs/naJuyeon_t2/vocals.wav',sr=22050,mono=True)
r=librosa.feature.rms(y=v,hop_length=256,frame_length=1024)[0]; t=np.arange(len(r))*256/sr
thr=0.012
act=r>thr
# segments with gap fill 0.35s
segs=[];s=None;last=None
for ti,a in zip(t,act):
    if a:
        if s is None: s=ti
        last=ti
    else:
        if s is not None and ti-last>0.35:
            segs.append((s,last)); s=None
if s is not None: segs.append((s,last))
for a,b in segs:
    if b-a>0.2: print(f'{a:6.2f} - {b:6.2f}  ({b-a:.2f}s)  video(s0=.48): {a-.48:6.2f}-{b-.48:6.2f}')
print('max rms',r.max())
