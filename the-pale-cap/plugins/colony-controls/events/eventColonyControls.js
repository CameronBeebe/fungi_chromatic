const refs = ['36', '37', '38', '39', '40', '41', '42'];
module.exports = {
  id: 'EVENT_COLONY_CONTROLS', name: 'Colony: cursor and orders',
  groups: ['EVENT_GROUP_ACTOR'],
  fields: [{key:'operation', label:'Operation', type:'select', defaultValue:0,
    options:[[0,'Initialize'],[1,'Poll cursor'],[2,'Enqueue / toggle pending harvest'],[3,'Next worker step'],[4,'Complete order']]},
    {key:'kind',label:'Order type (1 harvest, 2 move, 3 talk)',type:'number',defaultValue:2},
    {key:'target',label:'Target ID',type:'number',defaultValue:0}],
  compile(input, h) {
    // Fixed, named project variables are passed as addresses, never assumed contiguous.
    const args = input.operation === 2 ? ['43', '44', ...refs.slice(2)] : refs;
    for (const id of args) h._stackPushConst(h.getVariableAlias(id));
    h._stackPushConst(input.target || 0);
    h._stackPushConst(input.kind || 0);
    h._stackPushConst(input.operation || 0);
    h._callNative('ff_controls');
    h._stackPop(10);
  }
};
