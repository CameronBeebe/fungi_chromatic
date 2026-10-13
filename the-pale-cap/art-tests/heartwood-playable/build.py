"""Native-cell experiment: one Hi-Color master, fixed palettes, local tile updates.

Uses preserved local concept input, never edits or distributes that input.
Requires Pillow and the existing GBDK toolchain. All generated output is ignored.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=PROJECT.parent/'concept-art/heartwood-assets-candidate-v1/source/layout-reference-160x144.png')
parser.add_argument('--gbdk', type=Path, default=Path(os.environ.get('GBDK_PATH', str(Path.home()/'Library/Application Support/modretro-chromatic/toolchain/.local/gbdk'))))
args = parser.parse_args()
out = ROOT/'build'
out.mkdir(exist_ok=True)
base = Image.open(args.source).convert('RGB')
assert base.size == (160, 144)

# New native-cell resource study; source painting is unchanged. Three asymmetric
# ochre fans, a shaded attachment and scattered cut remains, all in one footprint.
full = base.copy()
d = ImageDraw.Draw(full)
for x,y,r in [(109,86,5),(123,89,6),(116,96,4)]:
    d.line((x-3,y+4,x+4,y+4), fill=(51,40,46), width=2)
    d.line((x,y,x,y+4), fill=(148,103,63))
    d.polygon([(x-r,y),(x-r+2,y-3),(x+1,y-4),(x+r,y-1),(x+r-1,y+1),(x-r+1,y+1)], fill=(123,67,36))
    d.line((x-r+2,y-2,x+1,y-3,x+r-1,y-1), fill=(186,116,53))
    d.line((x-r+1,y,x+r-2,y), fill=(221,166,96))
    for q in (-2,1,3):
        d.point((x+q,y-1), fill=(152,88,39))
cut = base.copy()
d = ImageDraw.Draw(cut)
for x,y in [(109,90),(123,93),(116,100)]:
    d.line((x-2,y,x+2,y), fill=(51,40,46))
    d.line((x,y-2,x,y), fill=(138,93,65))
    d.point((x,y-2),fill=(196,148,100))
    d.point((x+3,y-1),fill=(136,98,68))
full.save(out/'master-full.png')

# No dedupe: each screen cell owns a pattern, so patch uploads cannot change
# another tile referencing the same pattern. Sprite storage is bank1:128+.
subprocess.run([str(args.gbdk/'bin/png2hicolorgb'),str(out/'master-full.png'),'--type=3','-L=adaptive-fast','-R=adaptive-fast','--nodedupe','--csource','--bank=2','-o','master.c'],cwd=out,check=True)
tiles = (out/'master.til').read_bytes()
tilemap = (out/'master.map').read_bytes()
attrs = bytearray((out/'master.atr').read_bytes())
pal = (out/'master.pal').read_bytes()
assert len(tiles)==5760 and len(pal)==4640
# Foreground root fringe: actor heads can pass behind it, feet remain outside.
for y in (7,8):
    for x in range(4,8):
        attrs[y*20+x] |= 128
(out/'master.atr').write_bytes(attrs)

def colors_at(x,y):
    slot=attrs[(y//8)*20+x//8]&7
    block=((y+1)//2)*64 if slot<4 else (y//2)*64+32
    colors=struct.unpack_from('<4H',pal,block+(slot%4)*8)
    return [tuple(((v>>s)&31)*255//31 for s in (0,5,10)) for v in colors]

def pattern_id(cell):
    return tilemap[cell]+(256 if attrs[cell]&8 else 0)

def decode(data):
    im=Image.new('RGB',(160,144))
    for y in range(144):
        for x in range(160):
            cell=(y//8)*20+x//8; offset=pattern_id(cell)*16+(y%8)*2
            k=((data[offset]>>(7-x%8))&1)|(((data[offset+1]>>(7-x%8))&1)<<1)
            im.putpixel((x,y),colors_at(x,y)[k])
    return im

decoded=decode(tiles)
decoded.save(out/'master-decoded.png')

def encode_cell(im,cx,cy):
    result=[]
    for y in range(cy*8,cy*8+8):
        lo=hi=0
        for x in range(cx*8,cx*8+8):
            target=im.getpixel((x,y))
            k=min(range(4), key=lambda n:sum((a-b)**2 for a,b in zip(target,colors_at(x,y)[n])))
            lo=(lo<<1)|(k&1);hi=(hi<<1)|(k>>1)
        result.extend((lo,hi))
    return bytes(result)

resource_cells=[y*20+x for y in range(10,13) for x in range(13,17)]
reveal_cells=[y*20+x for y in range(8,10) for x in range(9,14)]
reveal=decoded.copy(); d=ImageDraw.Draw(reveal)
# Deliberate native pixels: fine branching roots. Quantize into the MASTER'S
# palette; no scene-wide recoloring and no independent image conversion.
for points in [[(73,66),(77,68),(79,73),(86,75),(92,75),(98,78),(107,78)],[(83,67),(86,72),(86,75)],[(94,69),(92,73),(92,75)]]:
    d.line(points,fill=(211,191,137))

data=''
def arr(name, values, typ='uint8_t'):
    return f'const {typ} {name}[] = {{'+','.join(str(x) for x in values)+'};\n'
data+=arr('resource_ids',[pattern_id(c) for c in resource_cells],'uint16_t')
data+=arr('resource_full',b''.join(tiles[pattern_id(c)*16:pattern_id(c)*16+16] for c in resource_cells))
data+=arr('resource_cut',b''.join(encode_cell(cut,c%20,c//20) for c in resource_cells))
data+=arr('reveal_ids',[pattern_id(c) for c in reveal_cells],'uint16_t')
data+=arr('reveal_off',b''.join(tiles[pattern_id(c)*16:pattern_id(c)*16+16] for c in reveal_cells))
data+=arr('reveal_on',b''.join(encode_cell(reveal,c%20,c//20) for c in reveal_cells))

# Bram's native 16x16 cells. Two overlaid palette layers provide six opaque
# colors, using four 8x16 objects. Shared plum shadows and warm shelf highlights.
rows=[
'................','......334.......','.....33344......','....3333444.....',
'....2333455.....','....2331555.....','.....221566.....','.....222566.....',
'....2232266.....','...22233222.....','...522333225....','....2233322.....',
'.....22222......','.....22.22......','....11..11......','................']
rgb=[(0,0,0),(50,38,46),(81,54,52),(119,65,44),(169,108,61),(186,151,108),(213,190,144)]
frames=[]
for f in range(8):
    grid=[list(r) for r in rows]
    if f in (2,3): # back, hood covers face
        for y in range(4,9):
            for x in range(8,11):
                if grid[y][x]!='.':grid[y][x]='3' if x<10 else '4'
    if f in (0,1): # front beard centered
        for y in range(6,9):
            grid[y][7]='5';grid[y][8]='6';grid[y][9]='5'
    if f in (1,3,5):
        grid[14][4]='.';grid[14][5]='.';grid[13][4]='1';grid[14][8]='.';grid[14][10]='1'
    if f==7:
        grid[10][11]='.';grid[8][11]='5';grid[7][12]='6';grid[6][13]='4'
    picture=Image.new('RGBA',(16,16))
    for y,row in enumerate(grid):
        for x,c in enumerate(row):
            if c!='.':picture.putpixel((x,y),rgb[int(c)]+(255,))
    picture.save(out/f'bram-{f}.png')
    # 8x16 objects: each half stores upper then lower tile, base then highlights.
    for layer in range(2):
        for half in range(2):
            for y in range(16):
                lo=hi=0
                for x in range(half*8,half*8+8):
                    c=0 if grid[y][x]=='.' else int(grid[y][x])
                    k=c if layer==0 and c<=3 else c-3 if layer==1 and c>=4 else 0
                    lo=lo*2+(k&1);hi=hi*2+(k>>1)
                frames.extend((lo,hi))
data+=arr('bram_tiles',frames)
rgb555=lambda c:sum((v*31//255)<<s for v,s in zip(c,(0,5,10)))
data+=arr('actor_palettes',[rgb555(rgb[i]) for i in (0,1,2,3,0,4,5,6)],'uint16_t')
# Cursor is four small corners; a thin marker avoids covering the target.
marker=[]
for half in range(2):
    for y in range(16):
        lo=hi=0
        for x in range(half*8,half*8+8):
            k=2 if ((y in (0,15) and (x<3 or x>12)) or (x in (0,15) and (y<3 or y>12))) else 0
            lo=lo*2+(k&1);hi=hi*2+(k>>1)
        marker.extend((lo,hi))
data+=arr('cursor_tiles',marker)
data+=arr('cursor_palettes',[rgb555(c) for c in [(0,0,0),(50,38,46),(206,181,131),(150,100,60),(0,0,0),(50,38,46),(173,77,52),(150,100,60)]],'uint16_t')

# Feet positions on an 8px navigation grid. Hand-reviewed clearing only; bridge
# and exits stay scenery in this bounded experiment. Rocks and resource block it.
walk=[]
for y in range(18):
    for x in range(20):
        valid=(9<=y<=15 and 5<=x<=16) or (y==8 and 8<=x<=16)
        if (x in (12,13) and y in (10,11)) or (13<=x<=16 and 10<=y<=12):valid=False
        if x in (6,7) and y==11:valid=False
        walk.append(int(valid))
data+=arr('walkable',walk)
(out/'assets.h').write_text(data)
renderer=ROOT.parent/'hearth-hicolor/src'
rom=out/'heartwood-playable.gbc'
subprocess.run([str(args.gbdk/'bin/lcc'),'-Wm-yC','-Wl-yt0x19','-Wl-m','-Wl-w','-autobank','-Wb-ext=.rel','-I'+str(renderer),'-I.','-o',str(rom),str(ROOT/'src/main.c'),str(renderer/'gbc_hicolor.c'),'master.c'],cwd=out,check=True)
manifest={'source':str(args.source),'sourceSHA256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'romSHA256':hashlib.sha256(rom.read_bytes()).hexdigest(),'romBytes':rom.stat().st_size,'masterBytes':len(tiles)+len(tilemap)+len(attrs)+len(pal),'resourcePatchBytesPerState':len(resource_cells)*16,'revealPatchBytesPerState':len(reveal_cells)*16,'spriteTileBytes':len(frames)+len(marker),'paletteBytes':len(pal),'foregroundPriorityCells':[[x,y] for y in (7,8) for x in range(4,8)]}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
