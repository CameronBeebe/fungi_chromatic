"""Read-only compiled-layout audit. Writes evidence only beside this script."""
from pathlib import Path
import struct, hashlib, json
ROOT = Path('/Users/sciphi/src/fungi_chromatic')
OUT = Path(__file__).resolve().parent
GBS = Path('/Users/sciphi/Library/Application Support/modretro-chromatic/toolchain/.local/vendor/gb-studio')
results = []
for name in ('the-pale-cap-controls.gbc', 'the-pale-cap-atmosphere-v2.gbc'):
    rom = ROOT/'the-pale-cap/build/rom'/name
    data = rom.read_bytes()
    symbols = {s[1]: int(s[2], 16) for line in Path(str(rom)+'.debug/symbols.noi').read_text().splitlines()
               if len(s := line.split()) == 3 and s[0] == 'DEF'}
    def offset(address):
        bank, address = address >> 16, address & 0xffff
        return bank*0x4000 + (address-0x4000 if bank else address)
    start = offset(symbols['_save_points'])
    points = []
    for index in range(24):
        address, size, ident = struct.unpack_from('<HHB', data, start+index*5)
        if address == 0:
            break
        assert ident == index and size > 0
        points.append(dict(id=ident, address=hex(address), size=size))
    assert len(points) == 23
    blob_size = 6 + sum(p['size']+3 for p in points)
    assert blob_size <= 8192
    results.append(dict(rom=str(rom), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                        header={hex(i):hex(data[i]) for i in (0x143,0x147,0x148,0x149)},
                        save_points_rom_offset=hex(start), blocks=points, save_blob_size=blob_size,
                        signature=hex(struct.unpack_from('<I',data,offset(symbols['_save_signature']))[0]),
                        globals=Path(str(rom)+'.debug/globals.i').read_text()))
(OUT/'compiled-evidence.json').write_text(json.dumps(results, indent=2)+'\n')
paths = [ROOT/'the-pale-cap'/n for n in ('DESIGN.md','TODO.md','EXPEDITION-SLICE.md','PLAYTEST.md','project.gbsproj','project/settings.gbsres','project/variables.gbsres','plugins/colony-controls/engine/src/ff_controls.c')]
paths += [GBS/n for n in ('package.json','appData/engine/engine.json','appData/engine/gbvm/src/core/load_save.c','appData/engine/gbvm/include/load_save.h','appData/engine/gbvm/src/core/core.c','appData/engine/gbvm/src/core/data_manager.c','src/lib/compiler/scriptBuilder/scriptBuilder.ts','src/lib/compiler/compileData.ts','src/lib/compiler/generateGBVMData.ts')]
(OUT/'source-fingerprints.json').write_text(json.dumps([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),lines=len(p.read_text().splitlines())) for p in paths],indent=2)+'\n')
for r in results:
    print(r['rom'], r['sha256'], 'blob', r['save_blob_size'], 'signature',r['signature'])
    print(r['header']);print([l for l in r['globals'].splitlines() if 'MAX_GLOBAL' in l])
