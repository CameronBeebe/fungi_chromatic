// Exact native-index editing: fork pixels are retained from the approved conversion.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require(process.env.SHARP_MODULE || 'sharp');
const glyph=require('./font.cjs'),out=__dirname;
const source=fs.readFileSync(path.join(out,'reference/baseline-art.h'),'utf8');
const arr=n=>source.match(new RegExp(n+'\\[\\] = \\{([^}]+)'))[1].split(',').map(Number);
const bt=arr('art_tiles'),bm=arr('art_map'),ba=arr('art_attrs'),bp=arr('art_palettes');
const ids=new Uint8Array(23040),attrs=new Uint8Array(360).fill(7);
function put(x,y,v){if(x>=0&&x<160&&y>=0&&y<144)ids[y*160+x]=v;}
function line(x,y,X,Y,v){let dx=Math.abs(X-x),sx=x<X?1:-1,dy=-Math.abs(Y-y),sy=y<Y?1:-1,e=dx+dy;for(;;){put(x,y,v);if(x===X&&y===Y)break;let t=e*2;if(t>=dy){e+=dy;x+=sx}if(t<=dx){e+=dx;y+=sy}}}
function text(s,x,y,v=3){for(const c of s){if(c===' '){x+=4;continue}const g=glyph[c];g.forEach((r,j)=>[...r].forEach((b,i)=>{if(b==='1')put(x+i,y+j,v)}));x+=g[0].length+1}}
// Preserve all fork-bearing tiles, including fine gill indices and original palette assignment.
const retained=[];
for(let ty=2;ty<12;ty++)for(let tx=1;tx<=12;tx++){
 if(ty>=9&&(tx<=3||tx>=11))continue;
 let t=ty*20+tx;attrs[t]=ba[t];retained.push(t);
 for(let y=0;y<8;y++)for(let x=0;x<8;x++){let o=bm[t]*16+y*2;put(tx*8+x,ty*8+y,((bt[o]>>(7-x))&1)|(((bt[o+1]>>(7-x))&1)<<1))}
}
// Architectural rails: jewel corners, broken inner rule, separated specimen labels.
line(1,1,158,1,2);line(1,142,158,142,2);line(1,1,1,142,2);line(158,1,158,142,2);
line(18,13,142,13,1);line(111,16,111,99,1);line(113,45,156,45,1);line(113,74,156,74,1);
line(8,101,151,101,2);line(8,103,151,103,1);
for(const [ox,oy,sx,sy] of [[3,3,1,1],[156,3,-1,1],[3,140,1,-1],[156,140,-1,-1]]){
 const p=(x,y,v)=>put(ox+sx*x,oy+sy*y,v);
 const pattern=['222220000000','200020001000','203020012100','202220001000','200000000000','220001200000','010012210000','001221012000','000100001000'];
 pattern.forEach((r,y)=>[...r].forEach((v,x)=>{if(v!=='0')p(x,y,+v)}));
}
text('GILLSONG',55,4);text('FORK',121,20);text('AMBER',117,49);text('WORN',121,78);
line(126,31,126,37,2);line(134,31,134,37,2);line(126,37,130,41,2);line(134,37,130,41,2);line(130,41,130,43,2);
for(let y=59;y<=70;y++)for(let x=125;x<=135;x++)if(Math.abs(x-130)+Math.abs(y-65)<6)put(x,y,x<129?3:2);
line(126,88,134,88,1);line(125,89,125,92,2);line(135,89,135,92,2);line(126,93,134,93,2);
text('IT HUMS BEFORE RAIN.',9,109);text('A FLOW',17,126,2);text('B STILL',99,126,2);
// Animated corner gardens occupy their own whole tiles, away from fork and text.
for(let ty=9;ty<=11;ty++)for(const tx of [1,2,3,11,12,13])attrs[ty*20+tx]=6;
const paths=[[[9,94],[11,88],[17,84],[19,78],[17,75]],[[11,94],[18,91],[23,85],[27,83],[29,85]],[[16,95],[22,94],[27,90],[29,90]],[[88,94],[94,91],[98,84],[103,81],[106,76]],[[94,95],[102,93],[106,88],[109,87]]];
// Coiled hyphal rosettes, asymmetric stems and stepped leaflets.
paths.push([[9,94],[8,90],[9,86],[12,83],[16,83],[18,85],[18,88],[16,90],[13,90],[11,88],[12,86],[15,86],[15,88]],
 [[20,95],[19,92],[20,89],[23,87],[26,87],[28,89],[27,92],[24,93],[22,91],[24,90]],
 [[30,95],[30,92],[28,90]],[[9,81],[10,78],[13,76],[13,73]],
 [[89,95],[90,92],[93,90],[97,90],[99,92],[98,95],[95,95],[94,93],[96,92]],
 [[102,94],[103,90],[107,88],[110,84],[110,81]],
 [[98,87],[95,85],[96,82],[99,80],[102,80]],[[105,85],[103,84],[104,82],[106,82]]);
const pathPixels=[];
for(const pts of paths){let pixels=[];for(let i=1;i<pts.length;i++){let [x,y]=pts[i-1],[X,Y]=pts[i],n=Math.max(Math.abs(X-x),Math.abs(Y-y));for(let k=0;k<=n;k++)pixels.push([Math.round(x+(X-x)*k/n),Math.round(y+(Y-y)*k/n)])}pixels=[...new Map(pixels.map(p=>[p.join(),p])).values()];pixels.forEach(([x,y],i)=>{let v=1+Math.min(2,Math.floor(i*3/pixels.length));put(x,y,v);pathPixels.push({x,y,index:v})})}
for(const [x,y] of [[13,86],[24,89],[100,89],[104,79]]){put(x-1,y,1);put(x,y-1,2);put(x,y,3);put(x+1,y,2);put(x,y+1,1)}
const rgb=h=>[1,3,5].map(i=>Math.round(parseInt(h.slice(i,i+2),16)*31/255));
const pack=c=>c[0]|c[1]<<5|c[2]<<10;
const themes=[
 {name:'01-vermilion',label:'VERMILION / recommended',colors:['#4a1039','#e74a21','#ffc652','#841831','#ff8421','#fff0b5','#8c1839','#e75a21','#ffbd42','#421831','#a56b42','#efad63','#73314a','#ef9452','#ffe7bd','#391842','#bd5229','#ffc65a'],cyan:['#185263','#2994a5','#73e7de'],ui:['#184252','#31c6ce','#fff0c6']},
 {name:'02-saffron',label:'SAFFRON / warm mineral',colors:['#522131','#ce6321','#ffd673','#733129','#ffa539','#fff0ce','#8c3121','#ef8421','#ffd652','#422139','#947342','#debd73','#63394a','#dea563','#ffefce','#392939','#bd7331','#efce73'],cyan:['#215a63','#42a59c','#94e7ce'],ui:['#295252','#52c6ad','#fff0ce']},
 {name:'03-rose',label:'ROSE / cool lacquer',colors:['#42184a','#ce315a','#ffad84','#731842','#f75a6b','#ffe7ce','#731852','#de4263','#ff9484','#391839','#946373','#deb594','#5a2952','#de7384','#ffdece','#31184a','#a53963','#ef9c84'],cyan:['#294a73','#428cb5','#94d6ef'],ui:['#294263','#63b5e7','#f7e7de']}
];
const palettes=themes.map(t=>{let ps=[];for(let i=0;i<6;i++)ps.push([pack(rgb('#080819')),...t.colors.slice(i*3,i*3+3).map(h=>pack(rgb(h)))]);ps.push([pack(rgb('#080819')),...t.cyan.map(h=>pack(rgb(h)))]);ps.push([pack(rgb('#080819')),...t.ui.map(h=>pack(rgb(h)))]);return ps});
const tiles=[],map=[],keys=new Map();for(let ty=0;ty<18;ty++)for(let tx=0;tx<20;tx++){let bytes=[];for(let y=0;y<8;y++){let a=0,b=0;for(let x=0;x<8;x++){let v=ids[(ty*8+y)*160+tx*8+x];a|=(v&1)<<(7-x);b|=(v>>1)<<(7-x)}bytes.push(a,b)}let key=bytes.join(),id=keys.get(key);if(id===undefined){id=tiles.length;keys.set(key,id);tiles.push(bytes)}map.push(id)}
if(tiles.length>256)throw Error('Single-bank study overflow');
const carray=(n,a,type='uint8_t')=>`const ${type} ${n}[] = {${a.join(',')}};\n`;
fs.writeFileSync(path.join(out,'art.h'),carray('art_tiles',tiles.flat())+carray('art_map',map)+carray('art_attrs',[...attrs])+carray('art_palettes',palettes.flat(2),'uint16_t')+`#define TILE_COUNT ${tiles.length}\n`);
const render=ps=>{let b=Buffer.alloc(23040*3);ids.forEach((v,i)=>{let x=i%160,y=Math.floor(i/160),c=ps[attrs[Math.floor(y/8)*20+Math.floor(x/8)]][v];[c&31,(c>>5)&31,(c>>10)&31].forEach((v,k)=>b[i*3+k]=Math.round(v*255/31))});return b};
(async()=>{for(let i=0;i<3;i++){let b=render(palettes[i]);await sharp(b,{raw:{width:160,height:144,channels:3}}).png().toFile(path.join(out,themes[i].name+'.png'));await sharp(b,{raw:{width:160,height:144,channels:3}}).resize(640,576,{kernel:'nearest'}).png().toFile(path.join(out,themes[i].name+'-4x.png'))}
let inputs=['reference/before.png',...themes.map(t=>t.name+'.png')],labels=['BEFORE / original 186 tiles',...themes.map(t=>t.label)],composite=[];
for(let i=0;i<4;i++){composite.push({input:await sharp(path.join(out,inputs[i])).resize(480,432,{kernel:'nearest'}).toBuffer(),left:16+i*496,top:48});composite.push({input:Buffer.from(`<svg width="480" height="32"><text x="0" y="23" fill="#e3eee6" font-family="sans-serif" font-size="19">${labels[i]}</text></svg>`),left:16+i*496,top:8})}
await sharp({create:{width:2000,height:496,channels:3,background:'#121823'}}).composite(composite).png().toFile(path.join(out,'comparison.png'));
fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify({width:160,height:144,baselineTiles:186,uniqueTiles:tiles.length,tileBytes:tiles.length*16,maxColorsPerTile:4,paletteCount:8,sprites:0,rasterPaletteChanges:false,retainedForkTiles:retained,palettes:themes.map((t,i)=>({name:t.name,rgb555:palettes[i],rgb8:palettes[i].map(p=>p.map(c=>[c&31,c>>5&31,c>>10&31].map(v=>Math.round(v*255/31))))})),animation:{palette:6,pathPixels,description:'Three ordered path bands; brief highlight travels root to tip, then rests. Fork, UI and outer frame are static.'},baselineSourceSHA256:crypto.createHash('sha256').update(source).digest('hex')},null,2));console.log(`${tiles.length} tiles; 8 palettes; fork retained in ${retained.length} tiles`);})();
