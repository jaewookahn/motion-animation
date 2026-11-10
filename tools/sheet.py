import sys,pathlib
from PIL import Image, ImageDraw
d=pathlib.Path(sys.argv[1]); files=sorted(d.glob('*.png')); per=int(sys.argv[3]) if len(sys.argv)>3 else 12
for si in range(0,len(files),per):
    chunk=files[si:si+per]; cols=3; rows=(len(chunk)+cols-1)//cols
    sheet=Image.new('RGB',(cols*640,rows*360),'gray'); dr=ImageDraw.Draw(sheet)
    for i,fp in enumerate(chunk):
        im=Image.open(fp).convert('RGB').resize((640,360)); x,y=(i%cols)*640,(i//cols)*360
        sheet.paste(im,(x,y)); dr.rectangle([x,y,x+70,y+18],fill='black'); dr.text((x+4,y+3),fp.stem,fill='yellow')
    sheet.save(f'{sys.argv[2]}_{si//per}.png')
