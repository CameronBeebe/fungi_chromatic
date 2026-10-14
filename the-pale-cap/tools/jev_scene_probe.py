"""Small, offline Jev vision experiment. Never writes game assets or collision.

Requires Pillow; credentials come only from TYPESAFE_API_KEY. --run explicitly
sends the selected pictures and questions to TypeSafe; otherwise prepares them.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid

from PIL import Image, ImageDraw

ENDPOINT = 'https://api.typesafe.ai/v1/systemone'
CRITERIA = {
    'ground': 'Open floor, earth, path or steps that visually support an ordinary walking character at ground level.',
    'solid': 'Solid obstacle at the point: trunk, rock, wall, furniture or dense impassable growth.',
    'water': 'Water, a chasm, or an unsupported drop. Not ordinary walking ground.',
    'raised': 'A visible raised surface such as a mushroom cap, roof or overhead bridge, with no evident ground-level access here.',
    'unclear': 'Ambiguous, hidden or mixed enough that the foot position cannot be judged confidently.',
}
INTERACTIONS = {
    'harvest': 'A recognizable collectable biological resource, such as a mushroom cluster, fruit or herb.',
    'mine': 'A recognizable mineral deposit or exposed stone suitable as a mining candidate.',
    'container': 'A recognizable chest, crate, storage vessel or similar object that could be opened.',
    'entrance': 'A doorway, portal, cave mouth, ladder or path exit that could connect to another space.',
    'talk': 'A recognizable character or creature that could be addressed.',
    'none': 'Ordinary scenery or terrain, with no visible cue for a deliberate interaction target.',
    'unclear': 'There may be an interaction target, but the visual evidence is ambiguous or does not fit the categories.',
}


def add_interactions(cells, payload, closeups):
    for c in cells:
        location = f"the center of `crops.{c['id']}`" if closeups else f"the center of cell {c['id']} in `grid`"
        payload['questions']['interact_'+c['id']] = {
            'type':'choice',
            'instructions': f'At {location}, what is the strongest visually suggested interaction category? Use `clean` for scene context. This is an art annotation proposal, not a claim about implemented game mechanics. Judge the object under the center, not unrelated nearby objects. Plain rocks and trees are not automatically resources; prefer none without a recognizable interaction cue. Return unclear for ambiguity.',
            'criteria': INTERACTIONS,
        }


def png_data(im):
    buffer = io.BytesIO()
    im.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


def prepare(path, cols, rows, model, targets):
    source = Image.open(path).convert('RGB')
    # Integer nearest-neighbor scaling retains native pixels; API minima include
    # 78,400 total pixels, so a native 160x144 frame needs at least 3x.
    w, h = source.size
    scale = max(1, math.ceil(256/w), math.ceil(256/h), math.ceil(math.sqrt(78400/(w*h))))
    if max(w*scale, h*scale) > 1568:
        raise ValueError('Use a smaller source image: scaled image exceeds API limits')
    clean = source.resize((w*scale, h*scale), Image.Resampling.NEAREST)
    marked = clean.copy()
    pen = ImageDraw.Draw(marked)
    cells = []
    for y in range(rows):
        for x in range(cols):
            bounds = [x/cols, y/rows, (x+1)/cols, (y+1)/rows]
            label = f'{chr(65+x)}{y+1}'
            left, top, right, bottom = [bounds[i] * (clean.width if i%2==0 else clean.height) for i in range(4)]
            pen.rectangle((left, top, right-1, bottom-1), outline=(180,180,180))
            pen.rectangle((left+1,top+1,left+21,top+11), fill=(12,16,24))
            pen.text((left+2,top+1),label,fill=(255,255,255))
            cells.append({'id': label, 'bounds': bounds})
    clean_id, grid_id = str(uuid.uuid4()), str(uuid.uuid4())
    questions = {}
    for cell in cells:
        questions[cell['id']] = {
            'type': 'choice',
            'instructions': f"Classify the terrain at the CENTER of grid cell {cell['id']} in `grid`. Use `clean` for unobscured detail. Judge where the character's feet would stand, not whether its head overlaps art. Ignore grid lines and labels. Return raised rather than assuming an overhead surface is connected to the ground. Do not infer hidden passageways.",
            'criteria': CRITERIA,
        }
    for i, target in enumerate(targets):
        questions[f'present_{i}'] = {'type': 'noul', 'instructions': f'Is {target} visibly identifiable in `clean`?'}
        # Independent speculative questions; the presence result gates display.
        questions[f'box_{i}'] = {'type': 'box', 'instructions': f'In `clean`, locate {target}. Return its tight bounds. If multiple exist, use the largest matching instance.'}
    payload = {
        'model': model,
        'state': {'clean': clean_id, 'grid': grid_id,
                  'context': 'A painted overhead/isometric fantasy game environment. Infer visual terrain only; no authored collision map is supplied. The grid has labeled columns left to right and rows top to bottom.'},
        'assets': {clean_id: {'type':'image','format':'png','data_base64':png_data(clean)},
                   grid_id: {'type':'image','format':'png','data_base64':png_data(marked)}},
        'questions': questions,
    }
    return source, clean, marked, cells, payload


def focus_crops(source, cells, payload, selected):
    """An alternate spatial prompt: explicit center crops, same terrain rubric."""
    cells = [c for c in cells if c['id'] in selected]
    if {c['id'] for c in cells} != set(selected):
        raise ValueError('A requested cell is outside the grid')
    for key in list(payload['questions']):
        if key not in selected and not key.startswith(('present_', 'box_')):
            del payload['questions'][key]
    payload['state']['crops'] = {}
    for c in cells:
        l,t,r,b = c['bounds']
        cx,cy = (l+r)*source.width/2, (t+b)*source.height/2
        # Three cells across: target occupies the center third. Padding at the
        # scene edge is explicit and must never be treated as walkable terrain.
        cw,ch = (r-l)*source.width, (b-t)*source.height
        crop = source.crop((round(cx-cw*1.5),round(cy-ch*1.5),round(cx+cw*1.5),round(cy+ch*1.5)))
        crop = crop.resize((384,384),Image.Resampling.NEAREST)
        asset_id = str(uuid.uuid4())
        payload['assets'][asset_id] = {'type':'image','format':'png','data_base64':png_data(crop)}
        payload['state']['crops'][c['id']] = asset_id
        payload['questions'][c['id']]['instructions'] = (
            f"Classify the terrain at the EXACT CENTER of `crops.{c['id']}`. "
            "The crop shows three cells across and down, with the target in the center third. "
            "Use `clean` to interpret context. Judge where feet would stand, not head overlap. "
            "Black padding outside the source is unknown, never ground. Do not assume elevated surfaces are reachable."
        )
    return cells


def validate(response, cells, targets):
    answers = response.get('answers', {})
    for cell in cells:
        answer = answers.get(cell['id'], {})
        probabilities = answer.get('probabilities', {})
        if answer.get('choice') not in CRITERIA or set(probabilities) != set(CRITERIA):
            raise ValueError(f'Missing or invalid terrain answer: {cell["id"]}')
        for v in [answer.get('confidence'), *probabilities.values()]:
            if not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1:
                raise ValueError('Invalid probability/confidence')
        if abs(sum(probabilities.values())-1) > .02:
            raise ValueError('Probability distribution does not sum to one')
        interaction = answers.get('interact_'+cell['id'])
        if interaction is not None:
            probs = interaction.get('probabilities', {})
            if interaction.get('choice') not in INTERACTIONS or set(probs) != set(INTERACTIONS):
                raise ValueError('Invalid interaction answer')
            for v in [interaction.get('confidence'), *probs.values()]:
                if not isinstance(v, (int,float)) or not math.isfinite(v) or not 0 <= v <= 1:
                    raise ValueError('Invalid interaction probability/confidence')
            if abs(sum(probs.values())-1) > .02:
                raise ValueError('Interaction distribution does not sum to one')
    for i, _ in enumerate(targets):
        p = answers.get(f'present_{i}', {}).get('noul')
        if not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError('Missing or invalid presence answer')
        box = answers.get(f'box_{i}', {}).get('box', {})
        values = [box.get(k) for k in ('left','top','right','bottom')]
        if any(not isinstance(v, (int,float)) or not math.isfinite(v) or not 0 <= v <= 1 for v in values):
            raise ValueError('Invalid normalized object bounds')
        if not values[0] <= values[2] or not values[1] <= values[3]:
            raise ValueError('Reversed object bounds')


def evaluate(payload, key):
    request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method='POST', headers={
        'Authorization': 'Bearer '+key, 'Content-Type':'application/json',
        'TypeSafe-Danger-Zone-Images':'true',
    })
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        # Keep provider body out of logs; it might echo submitted content.
        raise RuntimeError(f'TypeSafe HTTP {error.code}; no automatic retry or model fallback') from None
    except urllib.error.URLError:
        raise RuntimeError('TypeSafe connection failed; no automatic retry') from None
    return result, round(time.monotonic()-started, 3)


def report_page(records, root_prefix=""):
    """Review page; root_prefix links sibling studies under the report server."""
    # Inputs and raw answers stay JSON data, never executable HTML.
    data = json.dumps(records).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page = '''<!doctype html><html><head><meta charset="utf-8"><title>Jev scene probe</title>
<style>body{background:#111820;color:#e6e5df;font:16px system-ui;margin:24px;max-width:1100px}h1{font-size:26px}p{max-width:850px;color:#bfcbd0}button,select,input{font:inherit}button,select{background:#26343c;color:#eee;padding:8px;border:1px solid #61767f}button{margin-right:6px}#stage{position:relative;width:min(800px,100%);margin-top:18px}#scene{width:100%;display:block;image-rendering:pixelated}svg{position:absolute;inset:0;width:100%;height:100%}.cell{cursor:crosshair}.cell:hover{stroke:white;stroke-width:.5}.legend{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0}.dot{display:inline-block;width:12px;height:12px;margin-right:6px}#detail{min-height:65px;white-space:pre-wrap}label{margin-right:14px}#meta{font-size:13px}a{color:#98dadd}</style></head><body>
<h1>Jev scene probe</h1><p>Experimental visual labels, not a collision map. Green means plausible ground at the cell center. Disconnected raised surfaces, narrow passages and character clearance still need validation. Hover a cell for the full distribution.</p>
<select id="pick" aria-label="Scene"></select> <button id="terrain">Terrain</button><button id="mask">Candidate ground</button><button id="interactions">Interactions</button><button id="original">Original</button>
<div class="legend" id="legend"></div>
<label>Minimum ground probability <input id="threshold" type="range" min="50" max="99" value="75"><span id="cutoff">75%</span></label><label><input id="boxes" type="checkbox" checked>Object boxes (presence ≥75%)</label>
<div id="stage"><img id="scene" alt="Selected game scene"><svg id="overlay" viewBox="0 0 100 100" preserveAspectRatio="none"></svg></div>
<p id="detail">Hover a cell to inspect its prediction.</p><p id="meta"></p><p id="objects"></p>
<p>Source: TypeSafe Jev vision API, explicit model recorded per scene. Threshold is an experimental review control, not calibrated walkability accuracy. No game files were changed.</p>
<script>const records='''+data+''';
const $=id=>document.getElementById(id),ns='http://www.w3.org/2000/svg';
const colors={ground:'#61c790',solid:'#e48d72',water:'#669ee0',raised:'#b4a2e3',unclear:'#d8c27a'};const interactionColors={harvest:'#61c790',mine:'#d8c27a',container:'#e48d72',entrance:'#669ee0',talk:'#b4a2e3',none:'#53636b',unclear:'#b8b8ac'};let mode='terrain';
records.forEach((r,i)=>{let o=document.createElement('option');o.value=i;o.textContent=r.name;$('pick').append(o)});
function legend(){ $('legend').replaceChildren();Object.entries(mode==='interactions'?interactionColors:colors).forEach(([k,c])=>{let s=document.createElement('span');let d=document.createElement('i');d.className='dot';d.style.background=c;s.append(d,document.createTextNode(k));$('legend').append(s)});}
function rect(b,color,fill,tip){let r=document.createElementNS(ns,'rect');r.setAttribute('x',100*b[0]);r.setAttribute('y',100*b[1]);r.setAttribute('width',100*(b[2]-b[0]));r.setAttribute('height',100*(b[3]-b[1]));r.setAttribute('fill',fill?color:'none');r.setAttribute('fill-opacity','.38');r.setAttribute('stroke',color);r.setAttribute('stroke-width',fill?'.12':'.45');r.classList.add('cell');r.onmouseenter=()=>{$('detail').textContent=tip};$('overlay').append(r)}
function draw(){legend();const r=records[+$('pick').value],a=r.response.answers,t=+$('threshold').value/100;$('cutoff').textContent=Math.round(t*100)+'%';$('scene').src=r.image;$('overlay').replaceChildren();let ground=0;
r.cells.forEach(c=>{const terrain=a[c.id],v=mode==='interactions'?a['interact_'+c.id]:terrain,p=terrain.probabilities.ground;ground+=p>=t?1:0;if(mode==='original'||!v)return;let color=mode==='mask'?(p>=t?colors.ground:colors.unclear):(mode==='interactions'?interactionColors:colors)[v.choice];rect(c.bounds,color,true,c.id+' · '+v.choice+' · confidence '+v.confidence.toFixed(2)+'\\n'+Object.entries(v.probabilities).map(([k,p])=>k+' '+(p*100).toFixed(1)+'%').join(' | '))});
let descriptions=[];r.targets.forEach((target,i)=>{const p=a['present_'+i].noul,b=a['box_'+i].box;descriptions.push(target+': presence '+(p*100).toFixed(0)+'%');if($('boxes').checked&&p>=.75)rect([b.left,b.top,b.right,b.bottom],'#fff',false,target+' · presence '+(p*100).toFixed(1)+'%')});
$('objects').textContent=descriptions.join(' · ');if(mode==='interactions')$('detail').textContent=r.cells.some(c=>a['interact_'+c.id])?'Visual interaction candidates only; not implemented mechanics. Hover a cell.':'This earlier run did not ask interaction questions. Select the close-ups + interactions run.';$('meta').textContent=r.response.model+' · '+r.elapsedSeconds+(r.requests?' s total / '+r.requests.length+' requests · ':' s request · ')+r.response.usage.input_tokens+' input tokens · '+ground+'/'+r.cells.length+' cells above ground threshold · '+r.sourceSHA256.slice(0,12);}
['terrain','mask','original','interactions'].forEach(k=>$(k).onclick=()=>{mode=k;draw()});$('pick').onchange=draw;$('threshold').oninput=draw;$('boxes').onchange=draw;draw();</script></body></html>'''

    nav = ('<nav><a href="'+root_prefix+'index.html">All scene probes</a> · '
           '<a href="'+root_prefix+'package/index.html">Movement + interaction package</a> · '
           '<a href="'+root_prefix+'inspect/index.html">Heartwood Inspect + overlapping labels</a></nav>')
    return page.replace('<body>', '<body>'+nav)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('images', nargs='+', type=Path)
    parser.add_argument('--out', type=Path, default=Path('the-pale-cap/art-tests/jev-scene-probe/build'))
    parser.add_argument('--model', default='jev-1.14.0')
    parser.add_argument('--cols', type=int, default=10)
    parser.add_argument('--rows', type=int, default=9)
    parser.add_argument('--target', action='append', default=[])
    parser.add_argument('--focus-cells', help='Comma-separated cells to inspect using explicit close-ups, e.g. H3,I4,C2,E7,D4')
    parser.add_argument('--interactions', action='store_true', help='Ask independent visual interaction categories for each selected cell')
    parser.add_argument('--run', action='store_true', help='Send the prepared images to TypeSafe; incurs API usage')
    parser.add_argument('--resume', action='store_true', help='Reuse matching saved responses instead of billing again')
    args = parser.parse_args()
    if not 1 <= args.cols <= 20 or not 1 <= args.rows <= 18:
        parser.error('Grid bounds: 1–20 columns, 1–18 rows')
    key = os.environ.get('TYPESAFE_API_KEY', '')
    if args.run and not key:
        parser.error('Set TYPESAFE_API_KEY in the environment; never pass it as a CLI argument')
    targets = args.target or ['the main tree trunk', 'the largest visible mushroom cluster', 'the main body of water']
    args.out.mkdir(parents=True, exist_ok=True)
    records = []
    for path in args.images:
        source, clean, grid, cells, payload = prepare(path, args.cols, args.rows, args.model, targets)
        if args.focus_cells:
            cells = focus_crops(source, cells, payload, args.focus_cells.split(','))
        if args.interactions:
            add_interactions(cells, payload, bool(args.focus_cells))
        # Stable fingerprint excludes random asset placeholders but includes all
        # image bytes, questions and model, preventing reuse after prompt edits.
        canonical = json.dumps(payload, sort_keys=True)
        for i, asset_id in enumerate(payload['assets']):
            canonical = canonical.replace(asset_id, f'IMAGE_{i}')
        canonical = json.dumps(json.loads(canonical), sort_keys=True)
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        folder = args.out / f'{path.stem}-{fingerprint[:12]}'
        folder.mkdir(exist_ok=True)
        clean.save(folder/'clean.png');grid.save(folder/'grid.png')
        (folder/'request.json').write_text(json.dumps(payload, indent=2)+'\n')
        saved = folder/'result.json'
        if args.resume and saved.exists():
            record = json.loads(saved.read_text())
            if record.get('fingerprint') != fingerprint:
                raise ValueError('Response fingerprint mismatch')
            validate(record['response'], cells, targets)
        elif args.run:
            response, elapsed = evaluate(payload, key)
            (folder/'raw-response.json').write_text(json.dumps(response, indent=2)+'\n')
            validate(response, cells, targets)
            if args.interactions and any('interact_'+c['id'] not in response['answers'] for c in cells):
                raise ValueError('Missing requested interaction answer')
            record = {'name':path.stem+(' · close-ups' if args.focus_cells else ' · grid')+(' + interactions' if args.interactions else ''), 'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),
                      'fingerprint':fingerprint, 'sourceSize':source.size, 'cells':cells, 'targets':targets,
                      'response':response, 'elapsedSeconds':elapsed, 'image':'data:image/png;base64,'+png_data(source)}
            saved.write_text(json.dumps(record, indent=2)+'\n')
        else:
            print(f'Prepared {folder}: {len(cells)} cells + {len(targets)*2} object questions; no API call')
            continue
        records.append(record)
        print(json.dumps({'scene':path.stem,'model':record['response'].get('model'),'seconds':record['elapsedSeconds'],
                          'usage':record['response'].get('usage'),'result':str(saved)}),flush=True)
        # Retain partial successes if a later image fails.
        # Include previous runs so alternate spatial prompts can be compared.
        retained = [json.loads(p.read_text()) for p in sorted(args.out.glob('*/result.json'))]
        (args.out/'index.html').write_text(report_page(retained))
    if records:
        print(f'Review: {args.out / "index.html"}')


if __name__ == '__main__':
    main()
