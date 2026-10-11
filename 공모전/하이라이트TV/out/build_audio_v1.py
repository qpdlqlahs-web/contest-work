"""본편/숏폼 오디오: 곡의 연속 구간 하나 + 페이드 + 효과음(곡 타악기 조각, 합성 띠링) -> 믹스 wav
사용: python out/build_audio.py main|short
"""
import sys, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from ed_timeline import *
ROOT=os.path.dirname(HERE)
mode=sys.argv[1]; short=(mode=='short')
dur=SHORT_DUR if short else MAIN_DUR
song,sr=sf.read(os.path.join(ROOT,'audio','naJuyeon_t2.wav'),dtype='float32')
drums,_=sf.read(os.path.join(HERE,'_demucs','htdemucs','naJuyeon_t2','drums.wav'),dtype='float32')
n=int(round(dur*sr)); a=int(round(S0*sr))
mus=song[a:a+n].copy()
fo=1.4 if short else 1.2
fi=int(0.02*sr); mus[:fi]*=np.linspace(0,1,fi)[:,None]
nfo=int(fo*sr); t=np.linspace(0,1,nfo); mus[-nfo:]*=np.cos(t*np.pi/2)[:,None]**1.5
def lp(x,fc): return sosfilt(butter(4,fc,'low',fs=sr,output='sos'),x,axis=0)
def hp(x,fc): return sosfilt(butter(4,fc,'high',fs=sr,output='sos'),x,axis=0)
# 두둥: 곡 시작 팀파니 스팅 조각 (저역 강조)
st=song[int(0.46*sr):int(0.86*sr)].copy()
hit=lp(st,420)*1.0+st*0.25
hit*=np.exp(-np.linspace(0,5,len(hit)))[:,None]
hit/=np.abs(hit).max()
# 착: 드럼 스템에서 14초~50초 사이 고역 타격이 가장 큰 지점의 0.16초
seg=drums[int(14*sr):int(50*sr)]
h=hp(seg,2500); env=np.abs(h).mean(1)
w=int(0.01*sr); sm=np.convolve(env,np.ones(w)/w,'same')
d=np.diff(sm); pk=int(np.argmax(d))
chak=drums[int(14*sr)+pk-int(0.005*sr):int(14*sr)+pk+int(0.16*sr)].copy()
chak=hp(chak,600); chak*=np.exp(-np.linspace(0,6,len(chak)))[:,None]; chak/=np.abs(chak).max()
print('chak at song %.2f s'%(14+pk/sr))
# 띠링: 1568Hz + 2093Hz 0.35초 감쇠
L=int(0.35*sr); tt=np.arange(L)/sr
d1=np.sin(2*np.pi*1568*tt)*np.exp(-tt*9)
d2=np.zeros(L); k0=int(0.08*sr); d2[k0:]=np.sin(2*np.pi*2093*tt[:L-k0])*np.exp(-tt[:L-k0]*9)
ding=(d1*0.6+d2*0.6); ding/=np.abs(ding).max(); ding=np.stack([ding,ding],1).astype(np.float32)
bank={'hit':hit,'chak':chak,'ding':ding}
mix=mus.copy()
for kind,tm,g in sfx_events(short):
    x=bank[kind]*g*0.6
    i=int(round(tm*sr)); j=min(len(mix),i+len(x))
    mix[i:j]+=x[:j-i]
print(len(sfx_events(short)),'sfx')
sf.write(os.path.join(HERE,'_work',mode+'_mix.wav'),mix,sr,subtype='FLOAT')
print('mix peak',np.abs(mix).max())
