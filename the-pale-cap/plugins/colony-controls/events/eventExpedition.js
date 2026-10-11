const FIELD='12f07015-0a42-504a-8d39-3f689e13ad3a';
// Version 1 home save schema. Semantic values only, never VM execution contexts.
const saveIds=[0,1,3,5,7,9,10,11,17,21,22,23,24,25,26,27,28,49,50,53];
module.exports={
 id:'EVENT_EXPEDITION',name:'Expedition: home, bag and inspection',groups:['EVENT_GROUP_SCREEN'],
 fields:[{key:'mode',label:'Mode',type:'select',defaultValue:'menu',options:[['menu','Bag menu'],['home','Home'],['arrive','Return home'],['inspect','Illustrated inspection'],['pickup','Receive item']]}],
 compile(input,h){
  const v=id=>h.getVariableAlias(String(id)),set=(id,n)=>h._setConst(v(id),n),next=()=>h.getNextLabel(),label=l=>h._label(l),jump=l=>h._jump(l),eq=(id,n,l)=>h._ifConst('.EQ',v(id),n,l,0);
  const num=value=>({type:'number',value}),sv=value=>({type:'variable',value:String(value)});
  const travel=(scene,x=0,y=0)=>{h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');h.sceneSwitchUsingScriptValues(scene,typeof x==='object'?x:num(x),typeof y==='object'?y:num(y),'down',1);};
  const save=op=>{for(const id of [...saveIds].reverse())h._stackPushConst(v(id));h._stackPushConst(v(54));h._stackPushConst(op);h._callNative('ff_home_save');h._stackPop(saveIds.length+2);};
  const mutate=op=>{for(const id of [0,53,49,50])h._stackPushConst(v(id));h._stackPushConst(op);h._callNative('ff_inventory');h._stackPop(5);};
  if(input.mode==='pickup'){const done=next();eq(49,1,done);eq(49,2,done);set(49,1);label(done);return;}
  // Returning home is a real scene transition, after the final order was removed.
  if(input.mode==='arrive') {set(48,1);travel('root-hearth');return;}
  if(input.mode==='inspect'){
   h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');
   const flow=op=>{h._stackPushConst(op);h._callNative('ff_gillsong');h._stackPop(1);};
   const animate=next(),back=next();flow(0);label(animate);
   h._idle();h.ifInput(['b'],()=>jump(back));flow(1);jump(animate);label(back);
   const home=next();eq(48,1,home);set(56,1);travel(FIELD,sv(59),sv(60));label(home);travel('root-hearth');return;
  }
  h.lock();
  const draw=(lines,compact=false)=>{
   const height=compact?5:18;h._overlayClear(0,0,20,height,'.UI_COLOR_WHITE',true,false);h._overlayMoveTo(0,compact?13:0,'.OVERLAY_SPEED_INSTANT');h._overlaySetScroll(0,0,20,height,'.UI_COLOR_WHITE');h._setTextLayer('.TEXT_LAYER_WIN');
   const rows=Array(compact?4:17).fill('');for(const [y,t]of lines)rows[y]=' '+t;h.textDraw(rows.join('\n'),1,0,'overlay');h._overlayWait(true,['.UI_WAIT_WINDOW','.UI_WAIT_TEXT']);
  };
  const choose=ys=>{set(51,1);h._choice(v(51),['.UI_MENU_CANCEL_B','.UI_MENU_SET_START'],ys.length);ys.forEach((y,i)=>h._menuItem(1,y,i+1,i+1,i?i:ys.length,i===ys.length-1?1:i+2));};
  const note=lines=>{draw([[1,'THE PALE CAP'],...lines,[16,'A/B Back']]);h.inputAwait(['a','b']);};
  const root=next(),home=next(),bag=next(),stash=next(),ret=next(),depart=next(),equip=next(),deposit=next(),withdraw=next(),close=next(),take=next(),inspect=next(),saving=next(),homeOptions=next();
  if(input.mode==='home'){
   const ready=next(),loaded=next(),fresh=next();eq(55,1,ready);save(0);eq(54,1,loaded);eq(54,0,fresh);
   note([[4,'Save unavailable'],[6,'Damaged or older'],[7,'save preserved.'],[10,'New Game will not'],[11,'write until Save.']]);
   label(fresh);const title=next(),begin=next();label(title);
   draw([[2,'THE PALE CAP'],[5,'A living language'],[9,'New Game'],[12,'Controls'],[16,'A Choose']]);choose([9,12]);eq(51,1,begin);
   note([[3,'D-pad: cursor'],[5,'A: order / talk'],[7,'B: spell'],[9,'START: bag'],[11,'SELECT: spells']]);jump(title);label(begin);set(17,50);jump(ready);
   label(loaded);save(1);
   label(ready);set(55,1);set(48,1);set(29,0);set(42,0);
   // Fresh or loaded home never contains an active native queue.
   for(const id of [36,37,38,39,40,41,42])h._stackPushConst(v(id));h._stackPushConst(0);h._stackPushConst(0);h._stackPushConst(0);h._callNative('ff_controls');h._stackPop(10);
  }
  label(root);eq(48,1,home);
  draw([[1,'EXPEDITION'],[3,'Fungi: $00$'],[6,'Bag'],[9,'Return home'],[13,'Seek Luma'],[16,'A Choose  B Back']]);choose([6,9]);eq(51,1,bag);eq(51,2,ret);jump(close);
  label(home);draw([[1,'ROOT HEARTH'],[3,'Bag   Home   Exit']],true);set(51,1);h._choice(v(51),['.UI_MENU_SET_START'],3);h._menuItem(1,3,3,2,1,1);h._menuItem(7,3,1,3,2,2);h._menuItem(14,3,2,1,3,3);eq(51,1,bag);eq(51,2,homeOptions);jump(depart);
  label(homeOptions);draw([[1,'ROOT HEARTH'],[4,'Stash'],[6,'Store all'],[8,'Take supplies'],[10,'Save'],[12,'Back'],[16,'A Choose  B Back']]);choose([4,6,8,10,12]);eq(51,1,stash);eq(51,2,deposit);eq(51,3,take);eq(51,4,saving);jump(home);
  label(saving);save(2);const saved=next();eq(54,1,saved);note([[5,'Could not save'],[8,'Previous record'],[9,'kept intact.']]);jump(homeOptions);label(saved);note([[5,'Hideout saved'],[8,'Next boot starts'],[9,'here at home.']]);jump(homeOptions);
  label(take);mutate(3);note([[5,'Supplies taken'],[8,'Bag fungi: $00$'],[10,'Stored: $53$']]);jump(homeOptions);
  label(depart);set(48,0);set(56,0);travel(FIELD,15,22);
  label(ret);set(43,25);set(44,13);for(const id of [43,44,38,39,40,41,42])h._stackPushConst(v(id));h._stackPushConst(0);h._stackPushConst(5);h._stackPushConst(2);h._callNative('ff_controls');h._stackPop(10);
  const queued=next();eq(41,1,queued);note([[5,'Order unavailable'],[8,'Let earlier work'],[9,'finish first.']]);jump(root);label(queued);h.variableInc('29');jump(close);
  label(bag);const has=next(),on=next(),bagDraw=next();eq(49,1,has);note([[4,'No fork carried'],[7,'Fungi: $00$']]);jump(root);
  label(has);eq(50,1,on);draw([[1,'GILLSONG'],[3,'Carried'],[6,'Inspect'],[9,'Equip'],[12,'Back'],[16,'A Choose  B Back']]);jump(bagDraw);
  label(on);draw([[1,'GILLSONG'],[3,'Equipped'],[6,'Inspect'],[9,'Unequip'],[12,'Back'],[16,'A Choose  B Back']]);label(bagDraw);choose([6,9,12]);eq(51,1,inspect);eq(51,2,equip);jump(root);
  label(equip);mutate(2);jump(bag);
  label(inspect);const inspectReady=next();eq(48,1,inspectReady);eq(29,0,inspectReady);note([[5,'Let orders finish'],[8,'before inspecting']]);jump(bag);
  label(inspectReady);if(input.mode!=='home'){h.actorSetById('bram');h.actorGetPosition('57','58','tiles');h.actorSetById('player');h.actorGetPosition('59','60','tiles');}travel('gillsong-inspect');
  label(stash);const stored=next();eq(49,2,stored);draw([[1,'HOME STASH'],[3,'Fungi: $53$'],[5,'No fork stored'],[9,'Store all'],[12,'Back'],[16,'A Choose  B Back']]);choose([9,12]);eq(51,1,deposit);jump(homeOptions);
  label(stored);draw([[1,'HOME STASH'],[3,'Fungi: $53$'],[5,'Gillsong'],[8,'Inspect'],[10,'Withdraw fork'],[12,'Back'],[16,'A Choose  B Back']]);choose([8,10,12]);eq(51,1,inspect);eq(51,2,withdraw);jump(homeOptions);
  label(deposit);mutate(0);note([[4,'Stored: $53$'],[6,'Bag fungi: $00$'],[9,'Carried fork'],[10,'stored unequipped']]);jump(homeOptions);
  label(withdraw);mutate(1);jump(stash);
  label(close);h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');h._overlayWait(true,['.UI_WAIT_WINDOW']);h.unlock();
 }
};
