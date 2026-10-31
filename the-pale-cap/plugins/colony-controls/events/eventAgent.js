// Stable IDs; compiler aliases are resolved individually, never assumed contiguous.
const bases=[61,73], names=['MOSS','PIP'];
function call(h,slot,op,command=0) {
  const ids=[...Array.from({length:12},(_,i)=>bases[slot]+i),93,94,0,21,22,23,24,25,26,27,28,85,89,87,88,90,91,92];
  for(const id of ids.reverse())h._stackPushConst(h.getVariableAlias(String(id)));
  h._stackPushConst(command);h._stackPushConst(slot);h._stackPushConst(op);
  h._callNative('ff_agents');h._stackPop(33);
}

module.exports={
 id:'EVENT_AGENT',name:'World agent: step or initialize',groups:['EVENT_GROUP_ACTOR'],
 fields:[{key:'slot',type:'number',label:'Agent slot',defaultValue:0,min:0,max:1},
 {key:'operation',type:'number',label:'0 initialize / 1 step',defaultValue:1}],
 compile(input,h){
  const slot=Number(input.slot)||0;if(slot<0||slot>=bases.length)throw Error('Unknown agent slot');
  h.actorSetById('bram');h.actorGetPosition('93','94','tiles');
  call(h,slot,Number(input.operation)||0);
 }
};
