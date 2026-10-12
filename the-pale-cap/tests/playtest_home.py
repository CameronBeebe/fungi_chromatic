"""Cold boot from battery SRAM only; never uses emulator save states."""
from pathlib import Path
from pyboy import PyBoy
import shutil,json,hashlib,tempfile,argparse,re
P=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--rom',type=Path,default=P/'build/rom/the-pale-cap-home-v1.gbc')
parser.add_argument('--output',type=Path,default=P/'artifacts/home-v1-evidence')
parser.add_argument('--hicolor',action='store_true')
args=parser.parse_args()
out=args.output;out.mkdir(parents=True,exist_ok=True)
rom=args.rom
extra={}
with tempfile.TemporaryDirectory() as tmp:
 r=Path(tmp)/'home.gbc';shutil.copy2(rom,r)
 p=PyBoy(str(r),window='null',sound_emulated=args.hicolor);p.set_emulation_speed(0);p.tick(180,True)
 def shot(n):p.screen.image.save(out/(n+'.png'))
 def tick(frames,trace=None):
  if trace is None:p.tick(frames,True)
  else:
   for _ in range(frames):
    p.tick(1,True);trace.append(p.screen.image.convert('RGB').copy())
 def press(k,held=10,rest=20,trace=None):
  p.button_press(k);tick(held,trace);p.button_release(k);tick(rest,trace)
 def check_reveal(frames,name,after_black=False):
  expected=home.convert('RGB').crop((0,0,160,104)).tobytes();started=not after_black
  for i,frame in enumerate(frames):
   top=frame.crop((0,0,160,104));colors=set(top.getdata())
   if colors=={(0,0,0)}:started=True
   if started and len(colors)>4 and top.tobytes()!=expected:
    frame.save(out/(name+'-bad-frame.png'))
    raise AssertionError((name,'intermediate room/palette frame',i))
  assert started,(name,'no black handoff')
 entry=[]
 shot('01-new-game');press('a',trace=entry);shot('02-home');home=p.screen.image.copy()
 if args.hicolor:
  check_reveal(entry,'new-game')
  assert len(set(home.crop((0,0,160,104)).getdata()))>200,'Hi-Color did not start'
  # The final two tiles use palette 7, also used by the menu. An early
  # palette restore previously painted their last row cyan and cream.
  raw=P/'art-tests/hearth-hicolor/generated'
  tiles=(raw/'hearth_menu.til').read_bytes();mapping=(raw/'hearth_menu.map').read_bytes()
  attrs=(raw/'hearth_menu.atr').read_bytes();colors=(raw/'hearth_menu.pal').read_bytes()
  for x in range(144,160):
   i=12*20+x//8;assert attrs[i]&7==7
   tile=mapping[i]+(256 if attrs[i]&8 else 0);bit=7-x%8
   color=((tiles[tile*16+14]>>bit)&1)|(((tiles[tile*16+15]>>bit)&1)<<1)
   offset=103*32+3*8+color*2;rgb555=int.from_bytes(colors[offset:offset+2],'little')
   expected=tuple(((rgb555>>shift)&31)*8 for shift in (0,5,10))
   assert home.convert('RGB').getpixel((x,103))==expected,'Menu palette leaked into room'
  # Two-frame taps must change selection while leaving all room pixels intact.
  press('right',2,2);selected=p.screen.image.copy()
  assert home.crop((0,0,160,104)).tobytes()==selected.crop((0,0,160,104)).tobytes()
  assert home.crop((0,104,160,144)).tobytes()!=selected.crop((0,104,160,144)).tobytes(),'Two-frame direction missed'
  press('left',2,2)
 press('right');press('right');departure=[];press('a',10,90,departure)
 if args.hicolor:
  # Until the outgoing image has been blanked, it must remain the complete
  # Hi-Color room, never its tilemap interpreted with ordinary palettes.
  for i,frame in enumerate(departure):
   top=frame.crop((0,0,160,104))
   if set(top.getdata())=={(0,0,0)}:break
   assert top.tobytes()==home.convert('RGB').crop((0,0,160,104)).tobytes(),('departure snow',i)
  else:raise AssertionError('Departure never blanked before scene load')
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
 press('b',10,90);press('start');press('down');returned=[];press('a',10,1200,returned);shot('05-returned-home')
 if args.hicolor:
  check_reveal(returned,'extraction',after_black=True)
  symbols=Path(str(rom)+'.debug/symbols.noi').read_text()
  counter=int(re.search(r'DEF _music_play_isr_counter (0x[0-9A-Fa-f]+)',symbols)[1],16)
  def clock_ticks():
   total=0;last=p.memory[counter];audio_changes=0
   for _ in range(120):
    p.tick(1,True);now=p.memory[counter];total+=(now-last)&255;last=now
    sound=p.sound.ndarray
    if sound.size and int(sound.max())!=int(sound.min()):audio_changes+=1
   assert audio_changes>100,('Sound output missing',audio_changes)
   return total
  top=p.screen.image.crop((0,0,160,104)).tobytes()
  hi_ticks=clock_ticks()
  assert 513<=hi_ticks<=515,('Hi-Color music clock drift',hi_ticks)
  for _ in range(3600):
   p.tick(1,True)
   if p.screen.image.crop((0,0,160,104)).tobytes()!=top:
    shot('unstable-room')
   assert p.screen.image.crop((0,0,160,104)).tobytes()==top,'Unstable room frame'
  press('right');press('a');normal_ticks=clock_ticks();menu_return=[];press('b',trace=menu_return)
  check_reveal(menu_return,'menu-return')
  assert 513<=normal_ticks<=515,('Menu music clock drift',normal_ticks)
  assert p.screen.image.crop((0,0,160,104)).tobytes()==top,'Room failed after menu'
  extra={'hiColorMusicTicksPer120Frames':hi_ticks,'menuMusicTicksPer120Frames':normal_ticks,
         'consecutiveStableRoomFrames':3600,'twoFrameDirectionTap':True,
         'roomMenuBoundaryMatchesAsset':True,'transitionFramesChecked':len(entry)+len(departure)+len(returned)+len(menu_return)}
 press('right');press('a');press('down');press('a');shot('06-deposit');press('b')
 for _ in range(3):press('down')
 press('a');shot('07-saved');p.stop(save=True)
 ram=Path(str(r)+'.ram');assert ram.exists(),'No battery file generated'
 data=ram.read_bytes();assert data[:4]==b'PCH1' and data[54]==0xa5,'No committed home record'
 assert int.from_bytes(data[46:48],'little')==2,'Fork not in saved stash'
 (out/'saved-home.ram').write_bytes(data)
 p=PyBoy(str(r),window='null',sound_emulated=False);p.set_emulation_speed(0);cold=[];tick(180,cold);shot('08-cold-home')
 if args.hicolor:
  check_reveal(cold,'cold-boot');extra['transitionFramesChecked']+=len(cold)
 # The room is visible immediately, unlike the full-screen startup menu.
 a=home.convert('RGB');b=p.screen.image.convert('RGB')
 assert a.crop((0,0,160,100)).tobytes()==b.crop((0,0,160,100)).tobytes(),'Cold boot did not open home'
 press('right');press('a');press('a');shot('09-restored-stash');press('a',10,90);shot('10-restored-inspection');press('b',10,90)
 if args.hicolor:
  # Engine soft reset must also return to a clean room renderer, not leave a
  # stale LCD handler or duplicate music callback installed.
  for key in ('a','b','start','select'):p.button_press(key)
  p.tick(4,True)
  for key in ('a','b','start','select'):p.button_release(key)
  p.tick(180,True)
  assert p.screen.image.crop((0,0,160,104)).tobytes()==home.crop((0,0,160,104)).tobytes(),'Soft reset corrupted home'
  shot('11-soft-reset-home');extra['softResetRestoresHome']=True
 p.stop(save=False)
report={'romSHA256':hashlib.sha256(rom.read_bytes()).hexdigest(),'checks':['new game starts at illustrated home','Luma gives fork','Bag opens native inspection','B returns to expedition','return enters home scene','stash deposit','home save commits checked record','cold boot from battery SRAM opens home without title','saved ownership is stash','restored stash and illustration inspected'],'saveBytes':len(data),'physicalHardwareTested':False}
report.update(extra)
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
