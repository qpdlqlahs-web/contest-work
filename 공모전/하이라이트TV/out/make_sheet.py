import sys,glob,os
from PIL import Image, ImageDraw
d=sys.argv[1]; out=sys.argv[2]; cols=int(sys.argv[3]); tw=int(sys.argv[4]) if len(sys.argv)>4 else 640
fs=sorted(glob.glob(os.path.join(d,'*.png')))
ims=[Image.open(f).convert('RGB') for f in fs]
th=int(tw*ims[0].height/ims[0].width)
rows=(len(ims)+cols-1)//cols
sh=Image.new('RGB',(cols*tw,rows*th))
for i,(f,im) in enumerate(zip(fs,ims)):
    im=im.resize((tw,th)); dr=ImageDraw.Draw(im)
    n=int(os.path.basename(f).split('_')[-1].split('.')[0])
    dr.rectangle([0,0,110,20],fill=(0,0,0)); dr.text((4,4),'f%d t=%.2f'%(n,n/30),fill=(255,255,0))
    sh.paste(im,((i%cols)*tw,(i//cols)*th))
sh.save(out,quality=90)
