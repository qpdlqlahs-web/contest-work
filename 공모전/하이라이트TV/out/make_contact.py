import subprocess,os
from PIL import Image, ImageDraw
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def sheet(video,prefix,tw,th,cols,per):
    os.makedirs('out/_work/cs',exist_ok=True)
    for f in os.listdir('out/_work/cs'): os.remove('out/_work/cs/'+f)
    subprocess.run(['ffmpeg','-v','error','-y','-i',video,'-vf','fps=1,scale=%d:%d'%(tw,th),'out/_work/cs/%03d.png'],check=True)
    fs=sorted(os.listdir('out/_work/cs'))
    for p in range(0,len(fs),per):
        sub=fs[p:p+per]; rows=(len(sub)+cols-1)//cols
        sh=Image.new('RGB',(cols*tw,rows*th))
        for i,f in enumerate(sub):
            im=Image.open('out/_work/cs/'+f).convert('RGB'); d=ImageDraw.Draw(im)
            d.rectangle([0,0,44,16],fill=(0,0,0)); d.text((3,3),'%ds'%(p+i),fill=(255,255,0))
            sh.paste(im,((i%cols)*tw,(i//cols)*th))
        sh.save('out/_check/%s_%d.jpg'%(prefix,p//per+1),quality=88)
import sys
v=sys.argv[1] if len(sys.argv)>1 else 'v1'
sfx='' if v=='v1' else '_'+v
sheet('out/naJuyeon_main_%s.mp4'%v,'main_contact'+sfx,480,270,5,20)
sheet('out/naJuyeon_shorts_%s.mp4'%v,'shorts_contact'+sfx,270,480,10,20)
