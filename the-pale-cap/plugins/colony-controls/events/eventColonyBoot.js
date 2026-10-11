module.exports = {
  id: 'EVENT_COLONY_BOOT', name: 'Colony: title menu',
  groups: ['EVENT_GROUP_SCREEN'], fields: [],
  compile(input,h) {
    h.lock();
    const draw=(lines)=>{
      h._overlayClear(0,0,20,18,'.UI_COLOR_WHITE',false,false);
      h._overlayMoveTo(0,0,'.OVERLAY_SPEED_INSTANT');
      h._overlaySetScroll(0,0,20,18,'.UI_COLOR_WHITE');
      h._setTextLayer('.TEXT_LAYER_WIN');
      const rows=Array(17).fill('');
      for(const [y,text] of lines) rows[y]='  '+text;
      h.textDraw(rows.join('\n'),0,0,'overlay');
      h._overlayWait(true,['.UI_WAIT_WINDOW','.UI_WAIT_TEXT']);
    };
    const menu=h.getNextLabel(), start=h.getNextLabel();
    const choice=h.getVariableAlias('47');
    h._label(menu);
    draw([[3,'THE PALE CAP'],[5,'A living language'],[9,' New Game'],[12,' Controls'],[16,'A Choose']]);
    h._choice(choice,[],2);
    h._menuItem(1,9,1,1,2,2);h._menuItem(1,12,2,2,1,1);
    h._ifConst('.EQ',choice,1,start,0);
    draw([[1,'CONTROLS'],[4,'D-pad Cursor'],[6,'A Move / gather'],[8,'A NPC: talk'],[10,'B Cast'],[12,'SELECT Spells'],[14,'START Inventory'],[16,'A/B Next']]);
    h.inputAwait(['a','b']);
    draw([[1,'GIVE ORDERS'],[4,'Bram does work.'],[6,'Talk ends queue.'],[9,'His spores shape'],[10,'what you see.'],[13,'B casts at cursor'],[16,'A / B Back']]);
    h.inputAwait(['a','b']);h._jump(menu);
    h._label(start);
    h._overlayMoveTo(0,18,'.OVERLAY_SPEED_INSTANT');
    h._overlayWait(true,['.UI_WAIT_WINDOW']);
    h.unlock();
  }
};
