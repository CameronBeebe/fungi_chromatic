"""Build a local six-image comparison ROM; no source art is copied or uploaded."""
from pathlib import Path
import argparse, hashlib, json, os, struct, subprocess

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=PROJECT.parent/'concept-art/overworld-study-2026-10-11')
parser.add_argument('--gbdk', type=Path, default=Path(os.environ.get('GBDK_PATH', str(Path.home()/'Library/Application Support/modretro-chromatic/toolchain/.local/gbdk'))))
args = parser.parse_args()
output = ROOT/'build'; generated = output/'generated'
generated.mkdir(parents=True, exist_ok=True)
renderer = ROOT.parent/'hearth-hicolor/src'
images=[]
for direction in ('01-heartwood','02-chalk','03-velvet'):
    for exposure in ('ordinary','elevated'):
        source=args.source/f'{direction}-{exposure}-160x144.png'
        data=source.read_bytes()
        assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(160,144), source
        symbol='gallery_'+direction[3:]+'_'+exposure
        subprocess.run([str(args.gbdk/'bin/png2hicolorgb'),str(source.resolve()),'--type=3','-L=adaptive-fast','-R=adaptive-fast','--csource','--bank=255','-o',f'generated/{symbol}.c'],cwd=output,check=True)
        sizes={ext:(generated/f'{symbol}.{ext}').stat().st_size for ext in ('til','map','atr','pal')}
        assert sizes['til']%16==0 and sizes['til']//16<=360
        assert sizes['map']==sizes['atr']==360 and sizes['pal']==4640
        images.append({'symbol':symbol,'source':source.name,'sourceSHA256':hashlib.sha256(data).hexdigest(),'payloadBytes':sum(sizes.values()),'parts':sizes})
header=''.join(f'#include "{i["symbol"]}.h"\n' for i in images)
header+='static const hicolor_data * const gallery_images[] = {'+','.join('&'+i['symbol']+'_data' for i in images)+'};\n'
header+='static uint8_t gallery_bank(uint8_t index) { switch(index) {\n'
header+=''.join(f'case {n}: return BANK({i["symbol"]});\n' for n,i in enumerate(images))
header+='default: return 0; } }\n'
(generated/'gallery_images.h').write_text(header)
rom=output/'overworld-gallery.gbc'
subprocess.run([str(args.gbdk/'bin/lcc'),'-Wm-yC','-Wl-yt0x19','-autobank','-Wb-ext=.rel','-I'+str(renderer),'-Igenerated','-o',str(rom),str(ROOT/'src/main.c'),str(renderer/'gbc_hicolor.c'),*[f'generated/{i["symbol"]}.c' for i in images]],cwd=output,check=True)
manifest={'kind':'static art comparison; not gameplay','images':images,'imagePayloadBytes':sum(i['payloadBytes'] for i in images),'romBytes':rom.stat().st_size,'romSHA256':hashlib.sha256(rom.read_bytes()).hexdigest()}
(output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
