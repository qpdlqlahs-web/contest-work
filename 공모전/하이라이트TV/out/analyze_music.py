import librosa, numpy as np
y,sr=librosa.load('audio/naJuyeon_t2.wav',sr=22050,mono=True)
print('dur',len(y)/sr)
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,units='time',tightness=200)
print('tempo',tempo)
print('beats',np.round(beats,2).tolist())
ib=np.diff(beats); print('median ibi',np.median(ib), 'bpm',60/np.median(ib))
rms=librosa.feature.rms(y=y,hop_length=512)[0]
t=np.arange(len(rms))*512/sr
for s in np.arange(0,80,1.0):
    m=(t>=s)&(t<s+1)
    print(f'{s:4.0f} rms={rms[m].mean():.4f}', '#'*int(rms[m].mean()*300))
oenv=librosa.onset.onset_strength(y=y,sr=sr)
on=librosa.onset.onset_detect(onset_envelope=oenv,sr=sr,units='time')
print('first onsets',np.round(on[:10],2).tolist())
