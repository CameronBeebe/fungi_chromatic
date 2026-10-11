#pragma bank 255
#include <gbdk/platform.h>
#include "vm.h"
#include <stdint.h>
#define COUNT 20
#define SIZE 55
#define VALUE(n) (*(UWORD *)VM_REF_TO_PTR(-(n)-1))
#define OUT(n) (script_memory[VALUE(n)])
static uint8_t record[SIZE], best[SIZE];
static uint16_t crc(const uint8_t *p,uint8_t n) {
 uint16_t c=0xffff;uint8_t i;
 while(n--){c^=(uint16_t)*p++<<8;for(i=0;i<8;i++)c=c&0x8000?(c<<1)^0x1021:c<<1;}return c;
}
static uint32_t sequence(const uint8_t *p){return (uint32_t)p[8]|(uint32_t)p[9]<<8|(uint32_t)p[10]<<16|(uint32_t)p[11]<<24;}
static uint16_t word(const uint8_t *p,uint8_t i){return (uint16_t)p[12+2*i]|(uint16_t)p[13+2*i]<<8;}
static uint8_t valid(const uint8_t *p){
 uint16_t c;
 if(p[0]!='P'||p[1]!='C'||p[2]!='H'||p[3]!='1'||p[4]!=1||p[5]!=COUNT||p[6]||p[7]||p[54]!=0xa5)return 0;
 c=crc(p,52);if(p[52]!=(uint8_t)c||p[53]!=(uint8_t)(c>>8))return 0;
 if(word(p,17)>2||word(p,18)>1||(word(p,18)&&word(p,17)!=1))return 0;
 if(word(p,0)>32767||word(p,19)>999||word(p,3)>1||word(p,4)>3||word(p,8)>100)return 0;
 return 1;
}
/* Explicit stable schema, not engine snapshots: safe because saves are home-only.
 * No VM stacks, actor continuations, queue pointers or compiler aliases on disk.
 * Each copy occupies a separate SRAM bank. Hardware retention is tested separately.
 */
void ff_home_save(SCRIPT_CTX *THIS) OLDCALL BANKED {
 uint8_t bank,i,matches,found=0,newest=0,dirty=0,op=VALUE(0);uint16_t c;uint32_t seq=0;
 volatile uint8_t *ram=(volatile uint8_t *)0xa000;
 ENABLE_RAM;
 for(bank=0;bank<2;bank++){
  SWITCH_RAM(bank);for(i=0;i<SIZE;i++)record[i]=ram[i];
  matches=(record[0]=='P')+(record[1]=='C')+(record[2]=='H')+(record[3]=='1');
  if(matches>=3)dirty=1; /* Fresh SRAM can be arbitrary, not only 00/FF. */
  if(valid(record)&&(!found||(int32_t)(sequence(record)-seq)>0)){
   found=1;newest=bank;seq=sequence(record);for(i=0;i<SIZE;i++)best[i]=record[i];
  }
 }
 OUT(1)=found?1:(dirty?3:0);
 if(op==1&&found){for(i=0;i<COUNT;i++)OUT(i+2)=word(best,i);}
 if(op==2){
  for(i=0;i<SIZE;i++)record[i]=0;
  record[0]='P';record[1]='C';record[2]='H';record[3]='1';record[4]=1;record[5]=COUNT;
  ++seq;for(i=0;i<4;i++)record[8+i]=(uint8_t)(seq>>(8*i));
  for(i=0;i<COUNT;i++){uint16_t v=OUT(i+2);record[12+2*i]=v;record[13+2*i]=v>>8;}
  c=crc(record,52);record[52]=c;record[53]=c>>8;record[54]=0xa5;
  if(!valid(record)){OUT(1)=2;goto done;}
  SWITCH_RAM(found?(newest^1):0);
  ram[54]=0;if(ram[54]!=0){OUT(1)=2;goto done;}
  for(i=0;i<54;i++)ram[i]=record[i];
  for(i=0;i<54;i++)if(ram[i]!=record[i]){OUT(1)=2;goto done;}
  ram[54]=0xa5;OUT(1)=ram[54]==0xa5?1:2;
 }
 done: SWITCH_RAM(0);DISABLE_RAM;
}
