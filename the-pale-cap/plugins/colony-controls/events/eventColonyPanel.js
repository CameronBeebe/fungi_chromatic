module.exports = {
  id: 'EVENT_COLONY_PANEL', name: 'Colony: overlay menu',
  groups: ['EVENT_GROUP_SCREEN'],
  fields: [
    {key:'page',label:'Panel',type:'select',defaultValue:'spells',options:[['spells','Spells'],['inventory','Inventory']]},
    {key:'equipped',label:'Equipped spell',type:'select',defaultValue:0,options:[[0,'Reveal Mycelium'],[1,'Fungal Bloom']]}
  ],
  compile(input,h) {
    h.lock();
    const draw=(bloom)=>{
      h._overlayClear(0,0,20,18,'.UI_COLOR_WHITE',false,false);
      h._overlayMoveTo(0,0,'.OVERLAY_SPEED_INSTANT');
      h._overlaySetScroll(0,0,20,18,'.UI_COLOR_WHITE');
      h._setTextLayer('.TEXT_LAYER_WIN');
      // One text draw stays within the native window's tile buffer.
      const rows=Array(17).fill('');
      const line=(text,x,y)=>{ rows[y]=' '.repeat(x)+text; };
      if(input.page==='spells') {
        line('SPELLS',2,1);
        line('EQUIPPED',2,3);
        line(bloom?'FUNGAL BLOOM':'REVEAL MYCELIUM',2,4);
        line('Reveal Mycelium',3,7);
        line('Free',3,8);
        line('Fungal Bloom',3,11);
        line('Wake 2 / regrow 1',3,12);
        line('A Equip   B Close',2,16);
      } else {
        line('INVENTORY',2,1);
        line('FUNGI       $00$',2,4);
        line('ORDERS      $29$',2,6);
        line('ROOTS       $07$/3',2,8);
        line('EQUIPPED SPELL',2,11);
        line(bloom?'Fungal Bloom':'Reveal Mycelium',2,12);
        line('A / B Back',1,16);
      }
      h.textDraw(rows.join('\n'),0,0,'overlay');
      h._overlayWait(true,['.UI_WAIT_WINDOW','.UI_WAIT_TEXT']);
    };
    if(input.page==='spells') {
      const loop=h.getNextLabel(), bloom=h.getNextLabel(), choose=h.getNextLabel();
      const equipBloom=h.getNextLabel(), close=h.getNextLabel();
      const equipped=h.getVariableAlias('5'), choice=h.getVariableAlias('45');
      h._label(loop);
      h._ifConst('.EQ',equipped,1,bloom,0);
      draw(false); h._jump(choose);
      h._label(bloom); draw(true);
      h._label(choose);
      h._choice(choice,['.UI_MENU_CANCEL_B','.UI_MENU_SET_START'],2);
      h._menuItem(1,7,1,1,2,2);
      h._menuItem(1,11,2,2,1,1);
      h._ifConst('.EQ',choice,0,close,0);
      h._ifConst('.EQ',choice,2,equipBloom,0);
      h._setConst(equipped,0); h._jump(loop);
      h._label(equipBloom); h._setConst(equipped,1); h._jump(loop);
      h._label(close);
    } else {
      draw(Number(input.equipped)===1);
      h.inputAwait(['a','b','start']);
    }
    h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');
    h._overlayWait(true,['.UI_WAIT_WINDOW']);
    h.unlock();
  }
};
