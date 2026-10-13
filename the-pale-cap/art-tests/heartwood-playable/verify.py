"""Verify input-driven gameplay and unchanged background on every frame."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import tempfile
from PIL import ImageChops, ImageDraw
from pyboy import PyBoy

ROOT=Path(__file__).resolve().parent
out=ROOT/'build'; evidence=out/'evidence';evidence.mkdir(exist_ok=True)
rom=out/'heartwood-playable.gbc'
symbols={name:int(addr,16) for addr,name in re.findall(r'\b([0-9A-F]{8})\s+(_\w+)',(out/'heartwood-playable.map').read_text())}
with tempfile.TemporaryDirectory() as temp:
    copy=Path(temp)/'test.gbc';shutil.copy2(rom,copy)
    p=PyBoy(str(copy),window='null',sound_emulated=False);p.set_emulation_speed(0)
    def value(name):return p.memory[symbols['_'+name]]
    def tick(n):p.tick(n,True)
    def press(button,n=2,rest=30):
        p.button_press(button);tick(n);p.button_release(button);tick(rest)
    tick(180);p.screen.image.save(evidence/'00-help.png');press('start',rest=90)
    original=p.screen.image.copy();original.save(evidence/'01-room.png')
    assert len(set(original.getdata()))>100
    # Mask pixels occupied by current and previous hardware objects only.
    def boxes():
        result=[]
        for i in range(40):
            y,x=p.memory[0xFE00+i*4:0xFE02+i*4]
            if y and x:result.append((x-8,y-16,x-1,y-1))
        return result
    prior_boxes=boxes();background_frames=0
    def stable_frame():
        global prior_boxes,background_frames
        tick(1)
        current=p.screen.image.copy()
        diff=ImageChops.difference(original.convert('RGB'),current.convert('RGB'))
        d=ImageDraw.Draw(diff)
        for box in initial_boxes+prior_boxes+boxes()+[(104,80,135,103),(72,64,111,79)]:d.rectangle(box,fill=(0,0,0))
        assert diff.getbbox() is None,('Unexpected scenery change',p.frame_count,diff.getbbox())
        prior_boxes=boxes();background_frames+=1
    initial_boxes=prior_boxes.copy()
    # A one-frame directional input must be sampled within two native frames.
    start_x=value('cursor_x');p.button_press('left');tick(1);p.button_release('left');tick(1)
    assert value('cursor_x')==start_x-1,'Missed short cursor tap'
    press('right');assert value('cursor_x')==start_x
    p.button_press('a')
    for _ in range(2):stable_frame()
    p.button_release('a')
    positions=[]
    for _ in range(900):
        stable_frame();positions.append((value('bram_x'),value('bram_y')))
        if value('loot') and not value('queue_count'):break
    assert value('harvested')==value('loot')==1,'Harvest did not complete'
    for _ in range(45):stable_frame()
    harvested=p.screen.image.copy();harvested.save(evidence/'02-harvested.png')
    # Every walked foot cell must be permitted by the compiled geometry.
    walk_addr=symbols['_walkable']
    for x,y in positions:assert p.memory[walk_addr+(y//8)*20+x//8],('Foot crossed obstacle',x,y)
    assert len(set(positions))>30,'No actual movement'
    p.button_press('b')
    for _ in range(2):stable_frame()
    p.button_release('b')
    for _ in range(90):stable_frame()
    revealed=p.screen.image.copy();revealed.save(evidence/'03-revealed.png')
    assert value('exposure')==1 and value('harvested')==1
    assert revealed.crop((104,80,136,104)).tobytes()==harvested.crop((104,80,136,104)).tobytes(),'Exposure regrew patch'
    assert revealed.crop((72,64,112,80)).tobytes()!=harvested.crop((72,64,112,80)).tobytes(),'Reveal invisible'
    for _ in range(600):stable_frame()
    press('start');assert value('help_open')==1;press('start',rest=90)
    assert p.screen.image.tobytes()==revealed.tobytes(),'Help did not restore persistent scene'
    # Repeated harvest cannot duplicate loot.
    press('a',rest=90);assert value('loot')==1 and value('queue_count')==0
    press('select',rest=90);assert value('loot')==value('harvested')==value('exposure')==0
    assert value('bram_x')==44 and value('bram_y')==100
    p.screen.image.save(evidence/'04-reset.png')
    # Queue a move above the rock, followed by the harvest. Navigation must
    # detour around the blocked cells instead of walking through the painting.
    def aim(x,y):
        while value('cursor_x')!=x:press('right' if value('cursor_x')<x else 'left',rest=2)
        while value('cursor_y')!=y:press('down' if value('cursor_y')<y else 'up',rest=2)
    aim(7,9);press('a',rest=2);aim(14,11);press('a',rest=2)
    assert value('queue_count')==2,'Orders did not queue'
    reached_first=False
    for _ in range(1200):
        tick(1);x=value('bram_x');y=value('bram_y')
        assert p.memory[walk_addr+(y//8)*20+x//8],('Queued route crossed obstacle',x,y)
        reached_first |= (x,y)==(60,76)
        if value('loot') and not value('queue_count'):break
    assert reached_first and value('loot')==1,'FIFO route/harvest failed'
    # Blocked targets give feedback without adding a queued action.
    aim(0,0);press('a',rest=2);assert value('queue_count')==0 and value('rejected')>0
    # Travel under foreground roots, retaining the Hi-Color image around Bram.
    aim(5,9);press('a',rest=400)
    assert (value('bram_x'),value('bram_y'))==(44,76)
    p.screen.image.save(evidence/'05-foreground.png')
    report={'romSHA256':hashlib.sha256(rom.read_bytes()).hexdigest(),'nativeFramesWithUnchangedScenery':background_frames,'harvestFrames':len(positions),'uniqueWalkPositions':len(set(positions)),'shortCursorTap':True,'noBlockedFootCells':True,'exposurePreservesHarvest':True,'helpRestoresScene':True,'duplicateHarvestRejected':True,'resetVerified':True,'queuedDetourThenHarvest':True,'blockedTargetRejected':True,'physicalHardwareTested':False}
    (evidence/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));p.stop(save=False)
