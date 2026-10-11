"""Cold boot from battery SRAM only; never uses emulator save states."""
from pathlib import Path
from pyboy import PyBoy
import shutil,json,hashlib,tempfile
P=Path(__file__).resolve().parents[1]
out=P/'artifacts/home-v1-evidence';out.mkdir(exist_ok=True)
rom=P/'build/rom/the-pale-cap-home-v1.gbc'
with tempfile.TemporaryDirectory() as tmp:
 r=Path(tmp)/'home.gbc';shutil.copy2(rom,r)
 p=PyBoy(str(r),window='null',sound_emulated=False);p.set_emulation_speed(0);p.tick(180,True)
 def shot(n):p.screen.image.save(out/(n+'.png'))
 def press(k,held=10,rest=20):p.button_press(k);p.tick(held,True);p.button_release(k);p.tick(rest,True)
 shot('01-new-game');press('a');shot('02-home');home=p.screen.image.copy()
 press('right');press('right');press('a',10,90)
 for _ in range(4):press('up',4,4)
 press('a',4,1200);shot('03-luma-gift')
 for _ in range(6):press('a',10,180)
 press('start');press('a');press('a',10,90);shot('04-inspect')
 frames=[]
 for _ in range(192):
  p.tick(1,True);frames.append(p.screen.image.convert('RGB').copy())
 baseline=list(frames[0].getdata());changed=set()
 cyan={(8,8,24),(24,80,96),(40,144,160),(112,224,216)}
 for frame in frames[1:]:
  for i,(a,b) in enumerate(zip(baseline,frame.getdata())):
   if a!=b:
    assert a in cyan and b in cyan,'Animation escaped cyan ornament palette'
    changed.add(i)
 assert len(changed)>0,'Gillsong inspection is static'
 frames[0].save(out/'gillsong-flow.gif',save_all=True,append_images=frames[1:],duration=17,loop=0)
 print('Animated ornament pixels:',len(changed))
 press('b',10,90);press('start');press('down');press('a',10,1200);shot('05-returned-home')
 press('right');press('a');press('down');press('a');shot('06-deposit');press('b')
 for _ in range(3):press('down')
 press('a');shot('07-saved');p.stop(save=True)
 ram=Path(str(r)+'.ram');assert ram.exists(),'No battery file generated'
 data=ram.read_bytes();assert data[:4]==b'PCH1' and data[54]==0xa5,'No committed home record'
 assert int.from_bytes(data[46:48],'little')==2,'Fork not in saved stash'
 (out/'saved-home.ram').write_bytes(data)
 p=PyBoy(str(r),window='null',sound_emulated=False);p.set_emulation_speed(0);p.tick(180,True);shot('08-cold-home')
 # The room is visible immediately, unlike the full-screen startup menu.
 a=home.convert('RGB');b=p.screen.image.convert('RGB')
 assert a.crop((0,0,160,100)).tobytes()==b.crop((0,0,160,100)).tobytes(),'Cold boot did not open home'
 press('right');press('a');press('a');shot('09-restored-stash');press('a',10,90);shot('10-restored-inspection');press('b',10,90)
 p.stop(save=False)
report={'romSHA256':hashlib.sha256(rom.read_bytes()).hexdigest(),'checks':['new game starts at illustrated home','Luma gives fork','Bag opens native inspection','B returns to expedition','return enters home scene','stash deposit','home save commits checked record','cold boot from battery SRAM opens home without title','saved ownership is stash','restored stash and illustration inspected'],'saveBytes':len(data),'physicalHardwareTested':False}
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
