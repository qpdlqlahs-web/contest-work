import librosa, numpy as np
y, sr = librosa.load(r'../audio/yakbang_t2.wav', sr=22050, mono=True)
print(len(y)/sr)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time', start_bpm=126)
print('tempo', tempo)
print('beats', np.round(beats[:12],3), '...', len(beats))
hop=512
rms = librosa.feature.rms(y=y, hop_length=hop)[0]
t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
# per 0.5s rms
for s in np.arange(0, len(y)/sr, 1.0):
    m = (t>=s)&(t<s+1.0)
    print(f'{s:5.1f} rms={rms[m].mean():.3f}', end=' | ')
    if int(s)%5==4: print()
print()
# spectral centroid in vocal band energy (300-3400Hz) ratio
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
vb = S[(f>200)&(f<3500)].sum(0)
print('vocal band per sec:')
for s in np.arange(0, len(y)/sr, 1.0):
    m = (t>=s)&(t<s+1.0)
    print(f'{s:4.0f}:{vb[m].mean():.0f}', end=' ')
print()
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
on = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=hop, units='time')
print('first onsets', np.round(on[:15],3))
