import librosa, numpy as np
y,sr=librosa.load('audio/naJuyeon_t2.wav',sr=22050,mono=True)
hop=256
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
fps=sr/hop
# fit period/phase
best=None
for bpm in np.arange(100,115,0.05):
    P=60/bpm
    for ph in np.arange(0.3,0.9,0.005):
        ts=np.arange(ph,76,P)
        idx=(ts*fps).astype(int)
        # take max within +-2 frames
        v=sum(oenv[max(0,i-2):i+3].max() for i in idx)
        if best is None or v>best[0]: best=(v,bpm,ph)
print(best)
v,bpm,ph=best
P=60/bpm
ts=np.arange(ph,76,P)
# per-beat strength & low-freq energy
S=np.abs(librosa.stft(y,n_fft=2048,hop_length=hop))
fr=librosa.fft_frequencies(sr=sr,n_fft=2048)
low=S[fr<150].sum(0)
st=[]
for i,t in enumerate(ts):
    j=int(t*fps); st.append((oenv[max(0,j-2):j+3].max(), low[max(0,j-2):j+3].max()))
st=np.array(st)
for ph4 in range(4):
    print('phase',ph4, st[ph4::4,0].mean(), st[ph4::4,1].mean())
# drift check: location of onset peak near each beat
offs=[]
for t in ts:
    j=int(t*fps); w=oenv[max(0,j-4):j+5]; offs.append((np.argmax(w)-4)/fps)
offs=np.array(offs)
for k in range(0,len(offs),12): print(round(ts[k],2), np.round(offs[k:k+12].mean()*1000), 'ms')
np.save('out/_grid.npy',np.array([bpm,ph]))
# fine rms 55-62 & 74-78
rms=librosa.feature.rms(y=y,hop_length=512,frame_length=2048)[0]; t=np.arange(len(rms))*512/sr
for s in np.arange(56,62,0.25):
    m=(t>=s)&(t<s+0.25); print(f'{s:5.2f} {rms[m].mean():.4f}')
for s in np.arange(0,1.0,0.1):
    m=(t>=s)&(t<s+0.1); print(f'{s:5.2f} {rms[m].mean():.4f}')
for s in np.arange(74,77.5,0.25):
    m=(t>=s)&(t<s+0.25); print(f'{s:5.2f} {rms[m].mean():.4f}')
