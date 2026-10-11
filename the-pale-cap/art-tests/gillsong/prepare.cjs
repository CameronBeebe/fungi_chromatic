// Native-screen reconstruction: source illustration sampling + authored UI + tile palettes.
// This is a conversion study, not a claim that downsampling alone authors good pixel art.
const fs=require('fs'),path=require('path');
const sharp=require('/Users/sciphi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const out=__dirname;
const src=path.resolve(out,'../../../concept-art/portfolio-2026-10-11/14-screen-compositions.png');
const hex=s=>[1,3,5].map(i=>parseInt(s.slice(i,i+2),16));
const quant=c=>c.map(v=>Math.round(Math.round(v*31/255)*255/31));
const bg='#081021';
const palettes=[
 [bg,'#522139','#bd4229','#ffbd63'],
 [bg,'#7b2939','#ef7331','#ffe7ad'],
 [bg,'#842139','#ce5229','#ffad42'],
 [bg,'#422131','#946342','#de9c63'],
 [bg,'#6b3942','#de8c52','#ffdeb5'],
 [bg,'#392142','#a54a29','#e7a542'],
 [bg,'#184252','#29849c','#73ced6'],
 [bg,'#215263','#4ab5c6','#f7e7bd']
].map(p=>p.map(s=>quant(hex(s))));
const pix=Array.from({length:160*144},()=>palettes[7][0]);
const put=(x,y,c)=>{if(x>=0&&x<160&&y>=0&&y<144)pix[y*160+x]=c;};
const line=(x0,y0,x1,y1,c)=>{let dx=Math.abs(x1-x0),sx=x0<x1?1:-1,dy=-Math.abs(y1-y0),sy=y0<y1?1:-1,err=dx+dy;for(;;){put(x0,y0,c);if(x0===x1&&y0===y1)break;let e=2*err;if(e>=dy){err+=dy;x0+=sx;}if(e<=dx){err+=dx;y0+=sy;}}};
const glyph={A:['01110','10001','10001','11111','10001','10001','10001'],B:['11110','10001','10001','11110','10001','10001','11110'],C:['01111','10000','10000','10000','10000','10000','01111'],D:['11110','10001','10001','10001','10001','10001','11110'],E:['11111','10000','10000','11110','10000','10000','11111'],F:['11111','10000','10000','11110','10000','10000','10000'],G:['01111','10000','10000','10111','10001','10001','01111'],H:['10001','10001','10001','11111','10001','10001','10001'],I:['111','010','010','010','010','010','111'],K:['10001','10010','10100','11000','10100','10010','10001'],L:['10000','10000','10000','10000','10000','10000','11111'],M:['10001','11011','10101','10101','10001','10001','10001'],N:['10001','11001','11001','10101','10011','10011','10001'],O:['01110','10001','10001','10001','10001','10001','01110'],P:['11110','10001','10001','11110','10000','10000','10000'],R:['11110','10001','10001','11110','10100','10010','10001'],S:['01111','10000','10000','01110','00001','00001','11110'],T:['11111','00100','00100','00100','00100','00100','00100'],U:['10001','10001','10001','10001','10001','10001','01110'],W:['10001','10001','10001','10101','10101','10101','01010'],Y:['10001','10001','01010','00100','00100','00100','00100'],'.':['0','0','0','0','0','0','1']};
function text(s,x,y,c=palettes[7][3]){for(const ch of s){if(ch===' '){x+=4;continue;}let g=glyph[ch];if(!g)throw Error(ch);g.forEach((r,dy)=>[...r].forEach((v,dx)=>{if(v==='1')put(x+dx,y+dy,c)}));x+=g[0].length+1;}}
(async()=>{
 const art=await sharp(src).extract({left:94,top:94,width:545,height:463}).resize(96,80,{fit:'fill',kernel:'lanczos3'}).removeAlpha().raw().toBuffer();
 for(let y=0;y<80;y++)for(let x=0;x<96;x++){let i=(y*96+x)*3;let c=[...art.subarray(i,i+3)];if(Math.max(...c)<45)c=palettes[7][0];put(x+8,y+16,c);}
 // UI is drawn afresh on whole native pixels, never shrunk from mockup text.
 const edge=palettes[7][2],dark=palettes[7][1];
 line(1,1,158,1,edge);line(1,13,158,13,dark);line(1,1,1,142,edge);line(158,1,158,142,edge);line(1,142,158,142,edge);
 text('GILLSONG',55,4);
 line(111,16,111,95,dark);
 text('FORK',121,20);text('AMBER',117,49);text('WORN',121,78);
 line(125,31,125,37,edge);line(135,31,135,37,edge);line(125,37,130,41,edge);line(135,37,130,41,edge);line(130,41,130,45,edge);
 for(let y=60;y<70;y++)for(let x=125;x<136;x++)if(Math.abs(x-130)+Math.abs(y-65)<6)put(x,y,palettes[7][(x+y)%3===0?3:2]);
 line(126,88,134,88,dark);put(125,89,edge);put(135,89,edge);line(126,90,134,90,edge);
 // Isolated three-phase mycelial tracery shares only its own palette.
 for(let y=24;y<89;y++){let x=4+Math.round(2*Math.sin(y/8));put(x,y,palettes[6][1+y%3]);}
 line(1,101,158,101,edge);text('IT HUMS BEFORE RAIN.',9,109);
 text('A CYCLE',9,128,edge);text('B STILL',107,128,edge);
 const indices=[],attrs=[],tiles=[],map=[],keys=new Map();let maxColors=0;
 const rendered=Buffer.alloc(160*144*3);
 const dist=(a,b)=>a.reduce((s,v,i)=>s+[2,3,2][i]*(v-b[i])**2,0);
 for(let ty=0;ty<18;ty++)for(let tx=0;tx<20;tx++){
  let samples=[];for(let y=0;y<8;y++)for(let x=0;x<8;x++)samples.push(pix[(ty*8+y)*160+tx*8+x]);
  const isArt=tx>=1&&tx<=12&&ty>=2&&ty<=11;
  const candidates=isArt?[0,1,2,3,4,5]:(tx===0&&ty>=3&&ty<=10?[6]:[7]);
  let best=null;
  for(const p of candidates){let ids=[],err=0;for(const c of samples){let ds=palettes[p].map(v=>dist(c,v)),min=Math.min(...ds),id=ds.indexOf(min);ids.push(id);err+=min;}if(!best||err<best.err)best={p,ids,err};}
  let bytes=[];for(let y=0;y<8;y++){let lo=0,hi=0;for(let x=0;x<8;x++){let id=best.ids[y*8+x];lo|=(id&1)<<(7-x);hi|=((id>>1)&1)<<(7-x);let off=((ty*8+y)*160+tx*8+x)*3;palettes[best.p][id].forEach((v,k)=>rendered[off+k]=v);}bytes.push(lo,hi);}
  maxColors=Math.max(maxColors,new Set(best.ids).size);
  let key=bytes.join(','),id=keys.get(key);if(id===undefined){id=tiles.length;keys.set(key,id);tiles.push(bytes);}
  map.push(id%256);attrs.push(best.p|(id>=256?8:0));indices.push(best.ids);
 }
 if(tiles.length>384)throw Error('Tile budget');
 await sharp(rendered,{raw:{width:160,height:144,channels:3}}).png().toFile(path.join(out,'screen.png'));
 await sharp(rendered,{raw:{width:160,height:144,channels:3}}).resize(800,720,{kernel:'nearest'}).png().toFile(path.join(out,'screen-5x.png'));
 const arr=(name,data,type='uint8_t')=>`const ${type} ${name}[] = {${data.join(',')}};\n`;
 const colors=palettes.flat().map(c=>c.map(v=>Math.round(v*31/255))).map(c=>c[0]|c[1]<<5|c[2]<<10);
 fs.writeFileSync(path.join(out,'art.h'),arr('art_tiles',tiles.flat())+arr('art_map',map)+arr('art_attrs',attrs)+arr('art_palettes',colors,'uint16_t')+`#define TILE_COUNT ${tiles.length}\n`);
 fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify({width:160,height:144,uniqueTiles:tiles.length,maxColorsPerTile:maxColors,paletteCount:palettes.length,colorsRGB:palettes,method:'Illustration crop converted to native tile palettes; UI rebuilt at native resolution. No hi-color raster changes in this baseline.'},null,2));
 console.log(`160x144; ${tiles.length} unique tiles; ${maxColors} colors/tile; 8 palettes.`);
})();
