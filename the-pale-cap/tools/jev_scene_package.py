"""Compile frozen Jev decisions into a candidate scene package, not a ROM.

Uses the existing vision probe and accepts its creative classifications. Code
owns connectivity, supported action templates, stable IDs and local art jobs.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import json
import os
from pathlib import Path
import re

from PIL import Image

import jev_scene_probe as probe


def digest(data):
    return hashlib.sha256(data).hexdigest()


def neighbors(cell, cols, rows):
    x,y = cell % cols, cell // cols
    return [ny*cols+nx for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))
            if 0 <= nx < cols and 0 <= ny < rows]


def components(cells, cols, rows):
    remaining = set(cells)
    groups = []
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        group, queue = {first}, deque([first])
        while queue:
            for other in neighbors(queue.popleft(), cols, rows):
                if other in remaining:
                    remaining.remove(other); group.add(other); queue.append(other)
        groups.append(sorted(group))
    return sorted(groups, key=lambda g:(-len(g), g[0]))


def compile_package(record, scene_id, cols, rows, visible_height=None):
    width, height = record['sourceSize']
    visible_height = height if visible_height is None else visible_height
    if not 0 < visible_height <= height: raise ValueError('Invalid visible image height')
    if width % cols or height % rows or width//cols % 8 or height//rows % 8:
        raise ValueError('Grid cells must align to native 8x8 tile boundaries')
    cw,ch = width//cols,height//rows
    expected = [f'{chr(65+x)}{y+1}' for y in range(rows) for x in range(cols)]
    if [c['id'] for c in record['cells']] != expected:
        raise ValueError('Scene package requires every grid cell, in row-major order')
    a = record['response']['answers']
    if any('interact_'+label not in a for label in expected):
        raise ValueError('Scene package requires interaction judgments for every cell')
    terrain = [a[c]['choice'] for c in expected]
    interaction = [a['interact_'+c]['choice'] for c in expected]
    # The chosen categories are authoring decisions. Confidence is retained for
    # review but is deliberately NOT an accuracy threshold controlling acceptance.
    interactive = {i for i,k in enumerate(interaction) if k not in ('none','unclear')}
    hidden = {i for i in range(cols*rows) if (i//cols)*ch+ch//2 >= visible_height}
    ground = {i for i,k in enumerate(terrain) if k=='ground'} - interactive - hidden
    groups = components(ground, cols, rows)
    active = set(groups[0]) if groups else set()
    # A deterministic test spawn; a future connected-level brief supplies entry.
    spawn = min(active, key=lambda c:(-(c//cols),abs(c%cols-(cols-1)/2),c)) if active else None
    objects, jobs, regions = [], [], []
    for category in sorted(set(interaction)-{'none','unclear'}):
        for cluster in components({i for i,k in enumerate(interaction) if k==category},cols,rows):
            region_id = f'{scene_id}.region.{cluster[0]:03d}'
            regions.append({'id':region_id,'category':category,'cells':cluster,
                            'identityStatus':'provisional semantic region, not an individual object instance'})
    for region in regions:
        category = region['category']
        # A broad fungal region offers small finite harvesting sites, not one
        # action deleting the entire painted colony. These are template choices,
        # not a claim that cell classification discovered individual mushrooms.
        sites = [[c] for c in region['cells']] if category=='harvest' else [region['cells']]
        for site in sites:
            obj_id = f'{scene_id}.site.{site[0]:03d}'
            approaches = sorted({n for c in site for n in neighbors(c,cols,rows)} & active)
            hidden_site = bool(set(site) & hidden)
            enabled = category=='harvest' and bool(approaches) and not hidden_site
            reason = None if enabled else 'hidden_by_ui' if hidden_site else 'unreachable' if not approaches else 'template_not_implemented'
            obj = {'id':obj_id,'regionId':region['id'],'category':category,'cells':site,
                   'workCells':approaches,'enabledInPrototype':enabled,'disabledReason':reason,
                   'initialState':'intact','persistentStateKey':obj_id+'.state',
                   'interpretation':'Jev-authored visual affordance; frozen for this scene revision'}
            if enabled:
                obj['action'] = {'verb':'harvest','durationTicks':45,
                                 'requiresState':'intact','nextState':'depleted',
                                 'reward':{'itemType':'fungal_material','quantity':1},
                                 'collisionAfter':'unchanged'}
                rects = [[(c%cols)*cw,(c//cols)*ch,cw,ch] for c in site]
                jobs.append({'id':obj_id+'.depleted','objectId':obj_id,'fromState':'intact','toState':'depleted',
                             'sourceImageSHA256':record['sourceSHA256'],
                             'allowedNativeRectsXYWH':rects,
                             'instruction':'Show a small local portion of the fungal growth as harvested. Keep the parent colony intact. Preserve lighting and attachment. Do not alter pixels outside the listed union of rectangles.',
                             'encodingRequirements':['freeze master palette schedule','edit only registered patterns',
                                                     'exact unchanged pixels outside footprint','verify tile roundtrip and upload budget'],
                             'status':'not_generated'})
            objects.append(obj)
    blockers = ['art_state_patches_not_generated','native_runtime_not_integrated',
                'actor_clearance_and_height_not_validated','level_entry_and_exit_not_authored']
    if spawn is None: blockers.append('no_ground_component')
    if not jobs: blockers.append('no_reachable_supported_interaction')
    scene = {'schemaVersion':1,'sceneId':scene_id,'status':'authoring_candidate','runtimeReady':False,
             'source':{'imageSHA256':record['sourceSHA256'],'model':record['response']['model'],
                       'interpretationFingerprint':record['fingerprint'],
                       'dimensions':[width,height],'visibleHeight':visible_height},
             'grid':{'columns':cols,'rows':rows,'cellPixels':[cw,ch],'terrain':terrain,
                     'proposedWalkableCells':sorted(ground),'activeComponentCells':sorted(active),
                     'excludedDisconnectedCells':sorted(ground-active),'uiOccludedFootCells':sorted(hidden)},
             'spawnCell':spawn,'semanticRegions':regions,'objects':objects,'artStateJobs':jobs,
             'validation':{'allEnabledTargetsHaveReachableWorkCells':all(o['workCells'] for o in objects if o['enabledInPrototype']),
                           'connectedGroundComponents':len(groups),'promotionBlockers':blockers},
             'persistence':{'freezeInterpretation':True,'initialObjectStates':{o['id']:'intact' for o in objects},
                            'savePolicy':'Apply the game hideout/extraction save rules; do not save this draft as mid-run progress.'},
             'tuning':{'harvestTicks':45,'harvestYield':1,'note':'Fixed prototype template values; Jev does not set unrestricted stats.'}}
    scene['revision'] = digest(json.dumps(scene,sort_keys=True).encode())
    return scene


def harvest(scene, state, object_id):
    """Pure mechanical test: one yield and one persistent state transition."""
    obj = next(o for o in scene['objects'] if o['id']==object_id)
    if not obj['enabledInPrototype']:
        raise ValueError('Interaction is not enabled')
    action = obj['action']
    if state[object_id] != action['requiresState']:
        return 0
    state[object_id] = action['nextState']
    return action['reward']['quantity']


def fingerprint(payload):
    text = json.dumps(payload)
    for i, name in enumerate(payload['assets']):
        text = text.replace(name, f'IMAGE_{i}')
    return digest(json.dumps(json.loads(text),sort_keys=True).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path,help='Native-resolution decoded art to interpret')
    parser.add_argument('--scene-id',default='heartwood-jev-study')
    parser.add_argument('--out',type=Path,default=Path('the-pale-cap/art-tests/jev-scene-probe/build/package'))
    parser.add_argument('--visible-height',type=int,default=136,help='Current study reserves bottom eight pixels for HUD')
    parser.add_argument('--run',action='store_true',help='Authorize uncached API calls (one per ten cell crops)')
    args = parser.parse_args()
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',args.scene_id):
        parser.error('Use a short lowercase scene ID containing letters, numbers and hyphens')
    cols,rows = 10,9
    if Image.open(args.image).size != (160,144):
        parser.error('This first package harness expects native 160x144 art')
    args.out.mkdir(parents=True,exist_ok=True)
    # Snapshot once so a concurrently edited input cannot mix image revisions
    # across the nine independent requests.
    image_bytes = args.image.read_bytes()
    source_hash = digest(image_bytes)
    snapshot = args.out/f'source-{source_hash}.png'
    snapshot.write_bytes(image_bytes)
    targets = ['the main tree trunk','the largest visible mushroom cluster','the main body of water']
    all_cells, all_answers, requests = [], {}, []
    source = None
    for row in range(rows):
        batch_targets = targets if row==0 else []
        source,clean,grid,cells,payload = probe.prepare(snapshot,cols,rows,'jev-1.14.0',batch_targets)
        selected = [f'{chr(65+x)}{row+1}' for x in range(cols)]
        cells = probe.focus_crops(source,cells,payload,selected)
        probe.add_interactions(cells,payload,True)
        fp = fingerprint(payload)
        folder = args.out/f'row-{row+1}-{fp[:12]}'
        folder.mkdir(exist_ok=True)
        (folder/'request.json').write_text(json.dumps(payload,indent=2)+'\n')
        path = folder/'response.json'
        if path.exists():
            saved = json.loads(path.read_text())
            if saved['fingerprint'] != fp: raise ValueError('Cache identity mismatch')
            response,elapsed = saved['response'],saved['elapsedSeconds']
        else:
            key = os.environ.get('TYPESAFE_API_KEY','')
            if not args.run or not key:
                raise SystemExit('Prepared an uncached row. Use --run with TYPESAFE_API_KEY to evaluate; prior responses remain cached.')
            response,elapsed = probe.evaluate(payload,key)
            path.write_text(json.dumps({'fingerprint':fp,'response':response,'elapsedSeconds':elapsed},indent=2)+'\n')
        probe.validate(response,cells,batch_targets)
        if response.get('model') != 'jev-1.14.0': raise ValueError('Unexpected model version')
        if any('interact_'+c['id'] not in response['answers'] for c in cells): raise ValueError('Missing interaction answer')
        all_cells.extend(cells);all_answers.update(response['answers'])
        requests.append({'fingerprint':fp,'elapsedSeconds':elapsed,'usage':response['usage']})
        print(f'Row {row+1}/{rows}: decisions retained',flush=True)
    record = {'name':args.scene_id+' · native decoded · all close-ups',
              'sourceSHA256':source_hash,'sourceSize':source.size,
              'fingerprint':digest(json.dumps({'requests':[r['fingerprint'] for r in requests],'answers':all_answers},sort_keys=True).encode()),
              'cells':all_cells,'targets':targets,
              'response':{'model':'jev-1.14.0','answers':all_answers,
                          'usage':{'input_tokens':sum(r['usage']['input_tokens'] for r in requests)}},
              'elapsedSeconds':round(sum(r['elapsedSeconds'] for r in requests),3),
              'image':'data:image/png;base64,'+probe.png_data(source),'requests':requests}
    scene = compile_package(record,args.scene_id,cols,rows,args.visible_height)
    # Immutable revision folders preserve previously accepted drafts and state.
    revision_dir = args.out/scene['revision'][:16]
    revision_dir.mkdir(exist_ok=True)
    (revision_dir/'scene.json').write_text(json.dumps(scene,indent=2)+'\n')
    (revision_dir/'interpretation.json').write_text(json.dumps(record,indent=2)+'\n')
    source.save(revision_dir/'source.png')
    page = probe.report_page([record], root_prefix="../../")
    info = f'<p>Scene package: {sum(o["enabledInPrototype"] for o in scene["objects"])} reachable harvest targets; {len(scene["artStateJobs"])} pending art-state jobs. Authoring candidate, not a playable ROM. <a href="scene.json">Scene JSON</a> · <a href="interpretation.json">Frozen Jev decisions</a></p>'
    page = page.replace('<h1>Jev scene probe</h1>','<h1>Jev-authored scene package</h1>'+info)
    (revision_dir/'index.html').write_text(page)
    (args.out/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Scene package</title><p><a href="{revision_dir.name}/">Open the latest movement + interaction package</a></p><p><a href="../inspect/">Heartwood Inspect + overlapping labels</a></p><p><a href="../">All scene probes</a></p>')
    print(json.dumps({'package':str(revision_dir/'scene.json'),'review':str(revision_dir/'index.html'),
                      'objects':len(scene['objects']),'reachableHarvestTargets':len(scene['artStateJobs']),
                      'terrain':dict(Counter(scene['grid']['terrain'])),
                      'inputTokens':record['response']['usage']['input_tokens']}),flush=True)


if __name__=='__main__': main()
