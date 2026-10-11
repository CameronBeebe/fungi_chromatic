// One authored item instance. Location: 0 world, 1 bag, 2 home stash.
module.exports = {
 id:'EVENT_EXPEDITION', name:'Expedition: bag and hideout', groups:['EVENT_GROUP_SCREEN'],
 fields:[{key:'mode',label:'Mode',type:'select',defaultValue:'menu',options:[['menu','Open menu'],['home','Arrive home'],['pickup','Collect fork']]}],
 compile(input,h) {
  const v=id=>h.getVariableAlias(String(id));
  const set=(id,n)=>h._setConst(v(id),n);
  const eq=(id,n,label)=>h._ifConst('.EQ',v(id),n,label,0);
  const jump=l=>h._jump(l), label=l=>h._label(l), next=()=>h.getNextLabel();
  const mutate=op=>{for(const id of [0,53,49,50])h._stackPushConst(v(id));h._stackPushConst(op);h._callNative('ff_inventory');h._stackPop(5);};
  if(input.mode==='pickup'){const done=next();eq(49,1,done);eq(49,2,done);set(49,1);label(done);return;}
  h.lock();
  const draw=lines=>{
   h._overlayClear(0,0,20,18,'.UI_COLOR_WHITE',false,false);h._overlayMoveTo(0,0,'.OVERLAY_SPEED_INSTANT');h._overlaySetScroll(0,0,20,18,'.UI_COLOR_WHITE');h._setTextLayer('.TEXT_LAYER_WIN');
   const rows=Array(17).fill('');for(const [y,t] of lines)rows[y]='  '+t;
   h.textDraw(rows.join('\n'),0,0,'overlay');h._overlayWait(true,['.UI_WAIT_WINDOW','.UI_WAIT_TEXT']);
  };
  const choose=ys=>{set(51,1);h._choice(v(51),['.UI_MENU_CANCEL_B','.UI_MENU_SET_START'],ys.length);ys.forEach((y,i)=>h._menuItem(1,y,i+1,i+1,i===0?ys.length:i,i===ys.length-1?1:i+2));};
  const note=lines=>{draw([[1,'EXPEDITION'],...lines,[16,'A/B Back']]);h.inputAwait(['a','b']);};
  const enqueue=(kind,x,y)=>{
   set(43,x);set(44,y);for(const id of [43,44,38,39,40,41,42])h._stackPushConst(v(id));
   h._stackPushConst(0);h._stackPushConst(kind);h._stackPushConst(2);h._callNative('ff_controls');h._stackPop(10);
   // Count only orders actually admitted by the native queue.
   const ok=next(),done=next();eq(41,1,ok);
   note([[5,'Order unavailable'],[8,'Queue full or'],[9,'final order set.']]);jump(done);
   label(ok);h.variableInc('29');label(done);
  };
  const root=next(),home=next(),bag=next(),inspect=next(),stash=next(),collect=next(),ret=next(),depart=next(),equip=next(),deposit=next(),withdraw=next(),close=next();
  if(input.mode==='home')set(48,1);
  label(root);eq(48,1,home);
  draw([[1,'EXPEDITION'],[3,'Fungi: $00$'],[5,'Bag'],[7,'Collect fork'],[9,'Go home'],[12,'Fork: 26,14'],[16,'A Choose  B Back']]);choose([5,7,9]);eq(51,1,bag);eq(51,2,collect);eq(51,3,ret);jump(close);
  label(home);draw([[1,'HIDEOUT'],[5,'Bag'],[7,'Stash'],[9,'Store all'],[11,'Depart'],[14,'Session only'],[16,'A Choose']]);choose([5,7,9,11]);eq(51,1,bag);eq(51,2,stash);eq(51,3,deposit);eq(51,4,depart);jump(home);
  label(depart);set(48,0);jump(close);
  label(collect);eq(49,0,inspect);note([[5,'Fork already found'],[8,'Check bag / stash']]);jump(root);
  // Collect is an approach order, never an immediate remote pickup.
  label(inspect);enqueue(4,26,14);jump(close);
  label(ret);enqueue(5,25,13);jump(close);
  label(bag);const has=next(),on=next(),bagDraw=next();eq(49,1,has);note([[4,'No fork carried'],[7,'Fungi: $00$']]);jump(root);
  label(has);eq(50,1,on);draw([[1,'GILLSONG'],[3,'Carried'],[5,'Fan-gilled fork'],[7,'Ability pending'],[10,'Equip'],[12,'Back'],[16,'A Choose  B Back']]);jump(bagDraw);
  label(on);draw([[1,'GILLSONG'],[3,'Equipped'],[5,'Fan-gilled fork'],[7,'Ability pending'],[10,'Unequip'],[12,'Back'],[16,'A Choose  B Back']]);
  label(bagDraw);choose([10,12]);eq(51,1,equip);jump(root);
  label(equip);mutate(2);jump(bag);
  label(stash);const stored=next();eq(49,2,stored);draw([[1,'HOME STASH'],[3,'Fungi: $53$'],[5,'No fork stored'],[9,'Deposit fork'],[12,'Back'],[16,'A Choose  B Back']]);choose([9,12]);eq(51,1,deposit);jump(home);
  label(stored);draw([[1,'HOME STASH'],[3,'Fungi: $53$'],[5,'Gillsong'],[9,'Withdraw fork'],[12,'Back'],[16,'A Choose  B Back']]);choose([9,12]);eq(51,1,withdraw);jump(home);
  label(deposit);mutate(0);note([[5,'Carried supplies'],[6,'moved to storage'],[9,'Equipped fork is'],[10,'unequipped.']]);jump(home);
  label(withdraw);mutate(1);jump(stash);
  label(close);h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');h._overlayWait(true,['.UI_WAIT_WINDOW']);h.unlock();
 }
};
