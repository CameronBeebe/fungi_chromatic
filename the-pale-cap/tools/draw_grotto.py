"""Authored, tile-aligned GBC scenery. Outputs a new asset, never the old room."""
from pathlib import Path
import json, random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
W,H=32,28
INK=['#071821','#306850','#86c06c','#e0f8cf']
PAL=[['17182f','343455','626084','aaa0b0'],
     ['172c37','28504f','438072','91b58a'],
     ['10283e','185374','299ca4','86e0cd'],
     ['302139','84475b','e88078','ffe0ab'],
     ['29233d','605178','b8abc6','fff0cc'],
     ['2c2038','734448','d88951','ffdf8a'],
     ['152d3b','2d6670','62bfad','c0ffd3']]
im=Image.new('RGB',(W*8,H*8),INK[0]); d=ImageDraw.Draw(im)
slots=[[1]*W for _ in range(H)]; solid=set()
def rect(box,c): d.rectangle(box,fill=INK[c])
def line(points,c,width=1): d.line(points,fill=INK[c],width=width)
def region(x,y,w,h,p,block=False):
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            slots[yy][xx]=p
            if block: solid.add((xx,yy))
def tile(x,y,kind):
    a,b=x*8,y*8
    if kind=='floor':
        rect((a,b,a+7,b+7),0)
        if (x*7+y*11)%5==0: line([(a+2,b+4),(a+4,b+4)],1)
        if (x+y*3)%7==0: d.point((a+6,b+1),fill=INK[1])
    elif kind=='wall':
        rect((a,b,a+7,b+7),0); rect((a,b,a+6,b+5),1)
        line([(a+1,b),(a+5,b)],2); line([(a,b+1),(a,b+4)],2)
        line([(a+2,b+6),(a+7,b+6)],0)
    elif kind=='water':
        rect((a,b,a+7,b+7),1)
        line([(a+((y%2)*2),b+2),(a+4,b+2)],2)
        if (x+y)%3==0: line([(a+3,b+5),(a+6,b+5)],3)
    elif kind=='path':
        rect((a,b,a+7,b+7),1); line([(a,b+7),(a+7,b+7)],0)
        line([(a,b),(a+5,b)],2); d.point((a+6,b+4),fill=INK[0])
    elif kind=='moss':
        rect((a,b,a+7,b+7),0)
        line([(a,b+6),(a+2,b+3),(a+3,b+6),(a+5,b+2),(a+6,b+6)],1)
        d.point((a+5,b+2),fill=INK[2])
for y in range(H):
    for x in range(W):
        tile(x,y,'floor')
        if x<2 or x>=30 or y<2 or y>=26:
            tile(x,y,'wall');region(x,y,1,1,0,True)
        elif (x*3+y*7)%11==0: tile(x,y,'moss')
# Irregular cliff alcoves, with clear negative space for walking.
for x,y,w,h in [(2,2,7,3),(23,2,7,3),(2,5,3,4),(27,5,3,2),(2,23,5,3),(26,23,4,3)]:
    region(x,y,w,h,0,True)
    for yy in range(y,y+h):
        for xx in range(x,x+w): tile(xx,yy,'wall')
# Pool and stone rim.
for y in range(13,23):
    for x in range(2,9):
        if (x==8 and y in (13,22)) or (x==2 and y==13):continue
        tile(x,y,'water'); region(x,y,1,1,2,True)
for y in range(14,22):
    line([(71,y*8),(71,y*8+5)],2)
# Paths lead from the entrance to the sanctuary and forge.
for y in range(9,26):
    for x in (15,16):tile(x,y,'path');region(x,y,1,1,0)
for x in range(10,27):
    for y in (16,17):tile(x,y,'path');region(x,y,1,1,0)
# Raised pale cap shrine: a large stepped silhouette and gill fan.
region(10,2,12,7,4,True)
rect((80,16,175,71),0)
d.ellipse((89,19,166,56),fill=INK[1])
d.polygon([(84,45),(90,34),(102,26),(114,22),(141,22),(155,28),(166,38),(171,47),(165,52),(90,52)],fill=INK[2])
line([(91,36),(103,29),(116,25),(139,25),(150,29)],3,2)
for x,y in [(104,36),(123,30),(143,37),(155,44),(93,44)]:
    rect((x,y,x+4,y+2),3)
d.polygon([(92,53),(162,53),(138,62),(117,62)],fill=INK[1])
for x in range(96,162,8):line([(x,54),(128,64)],2)
rect((119,56,136,69),2);line([(123,58),(123,68)],3)
line([(105,70),(118,66),(137,66),(151,70)],2,2)
# Small copper forge, coals and chimney.
region(24,7,5,6,5,True)
rect((192,56,231,103),0)
rect((208,56,222,74),1)
for y in range(57,74,5):line([(209,y),(220,y)],2)
d.polygon([(193,83),(200,73),(225,73),(230,83),(230,101),(193,101)],fill=INK[1])
line([(195,82),(228,82)],2,2);rect((201,85,221,98),0)
for x in (204,210,217):
    d.polygon([(x,96),(x-2,91),(x+1,86),(x+3,92),(x+4,96)],fill=INK[2]);d.point((x+1,93),fill=INK[3])
line([(193,102),(231,102)],3)
# Decorative coral mushrooms (background scenery, distinct from pickups).
for x,y in [(5,7),(25,4),(27,21),(3,24),(22,22)]:
    region(x,y,3,3,3,True);a,b=x*8,y*8
    rect((a,b,a+23,b+23),0)
    rect((a+10,b+10,a+13,b+22),2)
    d.polygon([(a+1,b+12),(a+4,b+5),(a+9,b+2),(a+16,b+2),(a+21,b+7),(a+22,b+12)],fill=INK[2])
    line([(a+2,b+13),(a+21,b+13)],1,2)
    rect((a+7,b+5,a+10,b+7),3);rect((a+15,b+7,a+17,b+9),3)
# Lamps flank the entrance and sanctuary.
for x,y in [(12,22),(19,22),(10,10),(21,10)]:
    region(x,y,1,2,5,True);a,b=x*8,y*8
    rect((a,b,a+7,b+15),0);rect((a+3,b+7,a+4,b+14),1)
    rect((a+1,b+2,a+6,b+7),2);rect((a+2,b+3,a+5,b+6),3)
    line([(a+1,b+1),(a+6,b+1)],1)
# Mycelium filaments form a restrained trail across dark moss.
for x,y in [(10,19),(11,14),(20,14),(23,18),(9,11)]:
    region(x,y,2,2,6);a,b=x*8,y*8
    line([(a,b+15),(a+5,b+10),(a+5,b+5),(a+11,b+1)],1)
    line([(a+5,b+9),(a+11,b+8),(a+15,b+3)],1)
    d.point((a+11,b+1),fill=INK[2])
im.save(ROOT/'assets/backgrounds/grotto-v2.png')
# Human-viewable design proof; cartridge uses indexed source and tile palettes.
proof=im.copy()
for y in range(H*8):
    for x in range(W*8):
        i=INK.index('#%02x%02x%02x'%im.getpixel((x,y)))
        proof.putpixel((x,y),tuple(bytes.fromhex(PAL[slots[y//8][x//8]][i])))
proof.resize((768,672),Image.Resampling.NEAREST).save(ROOT/'art/grotto-color-proof.png')
(ROOT/'art/grotto-layout.json').write_text(json.dumps({'palettes':PAL,'slots':slots,'solid':sorted(solid),'width':W,'height':H},indent=2)+'\n')
print('Authored 256 x 224 grotto, seven background palettes.')
