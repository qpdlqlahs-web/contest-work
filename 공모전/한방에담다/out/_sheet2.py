import sys
from PIL import Image
fl=[int(x) for x in sys.argv[2].split(',')]
d=sys.argv[3] if len(sys.argv)>3 else '_test2'
ims=[Image.open(f'_check/{d}/f{f:04d}.png').resize((400,711)) for f in fl]
cols=5; rows=(len(ims)+cols-1)//cols
S=Image.new('RGB',(400*cols,711*rows))
for i,im in enumerate(ims): S.paste(im,((i%cols)*400,(i//cols)*711))
S.save(f'_check/{sys.argv[1]}.jpg',quality=88)
