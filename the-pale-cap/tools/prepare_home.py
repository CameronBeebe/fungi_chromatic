"""Reproducible GBC conversion; source concepts are never edited."""
import json,re,itertools
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parents[1]
DMG=[(224,248,207),(134,192,108),(48,104,80),(7,24,33)]
UI=['080819','184252','31C6CE','FFF0C6']
def rgb(h):return tuple(round(round(int(h[i:i+2],16)*31/255)*255/31) for i in (0,2,4))
def comp(a):return ''.join(f'{v:02x}'+('!' if len(list(g))==1 else '') for v,g in []) if False else ''.join(f'{v:02x}'+('!' if (n:=len(list(g)))==1 else f'{n:x}+') for v,g in itertools.groupby(a))
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def save(name,ids,attrs,pals):
 im=Image.new('RGB',(160,144));im.putdata([DMG[i] for i in ids]);im.save(P/f'assets/backgrounds/{name}.png')
 write(P/f'assets/backgrounds/{name}.png.gbsres',dict(_resourceType='background',id=name,name=name,symbol='bg_'+name.replace('-','_'),tileColors=comp(attrs),filename=name+'.png',width=20,height=18,imageWidth=160,imageHeight=144,autoColor=False))
 for k,pal in enumerate(pals):write(P/f'project/palettes/{name}_{k}.gbsres',dict(_resourceType='palette',id=f'{name}-{k}',name=f'{name} {k}',colors=['%02X%02X%02X'%c for c in pal]))
 preview=Image.new('RGB',(160,144));preview.putdata([pals[attrs[(i//160//8)*20+i%160//8]][v] for i,v in enumerate(ids)])
 (P/'art/integrated').mkdir(exist_ok=True);preview.resize((640,576),Image.Resampling.NEAREST).save(P/f'art/integrated/{name}-4x.png')
 tiles={tuple(ids[(ty+y)*160+tx+x] for y in range(8) for x in range(8)) for ty in range(0,144,8) for tx in range(0,160,8)}
 print(name,len(tiles),'tiles, 8 palettes, max 4 colors per tile')
# Warm, cold and floor ramps retain the Root Hearth's compositional contrast.
pals=[[rgb(c) for c in row.split()] for row in [
'100C18 392139 734229 CE8442','180C10 633118 AD5221 FFAD42','211010 844221 CE7B31 FFDE84',
'080819 182139 294A63 5284AD','080819 18394A 317394 73ADCE','180C21 392139 63314A 945263',
'100C18 422921 8C6329 CEAD63',' '.join(UI)]]
im=Image.open(P/'art/source/root-hearth-160x144.png').convert('RGB')
ids=[0]*23040;attrs=[]
for ty in range(18):
 for tx in range(20):
  pix=[im.getpixel((tx*8+x,ty*8+y)) for y in range(8) for x in range(8)]
  options=[]
  for k,pal in enumerate(pals):
   choices=[];err=0
   for c in pix:
    ds=[sum((a-b)**2 for a,b in zip(c,q)) for q in pal];j=min(range(4),key=ds.__getitem__);choices.append(j);err+=ds[j]
   options.append((err,k,choices))
  _,k,choices=min(options);attrs.append(k)
  for j,v in enumerate(choices):ids[(ty*8+j//8)*160+tx*8+j%8]=v
save('root-hearth',ids,attrs,pals)
# Decode exact approved native indices, not a resampled screenshot.
s=(P/'art-tests/gillsong-refinement/art.h').read_text()
def arr(n):return list(map(int,re.search(n+r'\[\] = \{([^}]+)',s)[1].split(',')))
tiles,mp,attrs,ps=map(arr,['art_tiles','art_map','art_attrs','art_palettes'])
ids=[]
for y in range(144):
 for x in range(160):
  o=mp[y//8*20+x//8]*16+y%8*2;ids.append(((tiles[o]>>(7-x%8))&1)|(((tiles[o+1]>>(7-x%8))&1)<<1))
for y in range(120,136):
 for x in range(8,152):ids[y*160+x]=0
font={'B':['110','101','110','101','110'],'A':['010','101','111','101','101'],'C':['011','100','100','100','011'],'K':['101','101','110','101','101'],' ':['000']*5}
for i,c in enumerate('B BACK'):
 for y,row in enumerate(font[c]):
  for x,b in enumerate(row):
   if b=='1':ids[(125+y)*160+67+i*4+x]=3
pals=[[tuple(round(((v>>shift)&31)*255/31) for shift in (0,5,10)) for v in ps[k*4:k*4+4]] for k in range(8)]
save('gillsong-inspect',ids,attrs,pals)
# Shared UI changes appearance through its own palette, not by rewriting frame art.
p=P/'project/palettes/default_ui.gbsres';d=json.loads(p.read_text());d['colors']=['%02X%02X%02X'%rgb(c) for c in UI];write(p,d)
