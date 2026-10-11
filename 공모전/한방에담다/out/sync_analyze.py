# -*- coding: utf-8 -*-
import numpy as np, soundfile as sf, librosa, json
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d
v,sr=sf.read('_work/demucs/htdemucs/yakbang_t2/vocals.wav'); v=v.mean(1).astype(np.float32)
sr2=22050; v22=librosa.resample(v,orig_sr=sr,target_sr=sr2); hop=110   # 5ms
S=np.abs(librosa.stft(v22,n_fft=1024,hop_length=hop)); f=librosa.fft_frequencies(sr=sr2,n_fft=1024)
B=S[(f>200)&(f<5000)]
env=B.sum(0); env=env/env.max()
t=np.arange(len(env))*hop/sr2
L=np.log1p(B*30)
flux=np.maximum(0,np.diff(L,axis=1)).sum(0); flux=np.concatenate([[0],flux])
fl=uniform_filter1d(flux,3)
thr=np.percentile(fl,85)
pk,pr=find_peaks(fl,height=thr,distance=int(0.06*sr2/hop))
ons=[(round(float(t[p]),3),float(fl[p])) for p in pk]
# blobs
e=uniform_filter1d(env,int(0.05*sr2/hop))
act=e>0.06
blobs=[];s=None
for i,a in enumerate(act):
    if a and s is None: s=i
    if (not a) and s is not None:
        if blobs and t[s]-blobs[-1][1]<0.22: blobs[-1][1]=t[i]
        else: blobs.append([t[s],t[i]])
        s=None
blobs=[b for b in blobs if b[1]-b[0]>0.3]
json.dump(dict(onsets=ons,blobs=[[round(a,3),round(b,3)] for a,b in blobs],env_t=list(map(float,t[::2])),env=list(map(float,e[::2]))),open('_work/sync_data.json','w'))
w1=json.load(open('_work/whisper.json',encoding='utf8')); w2=json.load(open('_work/align.json',encoding='utf8'))
for a,b in blobs:
    if a<8.5 or a>70: continue
    cands=[o for o in ons if a-0.05<=o[0]<=b+0.05]
    ws=[(round(x[0],2),x[2].strip()) for s in w1 for x in s['words'] if a-0.3<=x[0]<=b+0.3]
    print(f'blob {a:6.2f}-{b:6.2f} ({b-a:4.1f}s) onsets={len(cands)} whisper={ws}')
