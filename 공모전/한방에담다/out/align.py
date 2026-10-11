import stable_whisper, json, soundfile as sf, numpy as np
voc='_work/demucs/htdemucs/yakbang_t2/vocals.wav'
v,sr=sf.read(voc); v=v.mean(1)
# crop 8.0..70.0 for alignment
a=int(8.0*sr); b=int(70.5*sr)
sf.write('_work/voc_crop.wav', v[a:b], sr)
lines=["제기동 한옥 지붕 아래","약재만 약 삼백팔십","서랍 서랍 다 열어 봐도","내 자리는 어디 있지","빼꼼 여기도 감초 빼꼼 저기도 감초","안 끼는 데가 없다지",
"군도 아냐 신도 아냐","그럼 나는 뭐지","감초 감초 약방에 감초","어디든 끼는 약방에 감초","머리는 시원 발은 뜨끈","서울한방진흥센터로 가자",
"널리 구제한다 보제원 옛터","나는 감초","다 어울리게 하지","감초 감초 약방에 감초","약방엔 감초","약령시엔 쉼 한 첩"]
m=stable_whisper.load_faster_whisper('large-v3', device='cpu', compute_type='int8')
res=m.align('_work/voc_crop.wav','\n'.join(lines),language='ko')
out=[]
for s in res.segments:
    ws=[(round(w.start+8.0,2),round(w.end+8.0,2),w.word.strip()) for w in s.words]
    out.append(dict(text=s.text,start=round(s.start+8,2),end=round(s.end+8,2),words=ws))
    print(f'{s.start+8:6.2f}-{s.end+8:6.2f} {s.text}')
json.dump(out,open('_work/align.json','w'),ensure_ascii=False,indent=1)
