/** DS-001最小纯函数自检：既有TypeScript转译，无GUI/IPC/profile或新增依赖。 */
import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import ts from 'typescript';
const source=fs.readFileSync(new URL('../src/app/simulator/policyEditing.ts',import.meta.url),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {parseScalar,batchCandidate,draftBaseline,draftRows,selectedIds,effectivePolicy,newRule,clone}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const point=(id,type='INT',byte=2,policy={})=>({id,name:id,displayName:'',dataType:type,enabled:true,sourcePath:id,segments:[],byte,bit:type==='BOOL'?0:null,manualReason:'synthetic',manual:true,policy,confirmations:{initial:'server-initial',policy:'server-policy'}});
const fixture=()=>({id:'plc-a',name:'A',policy:{},dbs:[{id:'db-a',number:31,name:'Manual',length:64,enabled:true,manual:true,binding:null,regions:[],policy:{},addressConfirmation:null,points:[point('bool','BOOL',0),point('int','INT',2),point('real','REAL',4)]}]});
function batch(i,ids,patch,baseline=draftBaseline(i,[])){return batchCandidate(i,ids,patch,baseline,draftBaseline(i,[]));}
test('typed false/zero/nonzero/negative/string; incomplete and invalid values fail',()=>{
 for(const [type,text,value] of [['BOOL','false',false],['INT','0',0],['INT','7',7],['INT','-7',-7],['REAL','20.5',20.5],['INT','12',12],['STRING[8]','','']])assert.equal(parseScalar(type,text),value);
 for(const text of ['','-','2e','abc','1.5','32768'])assert.throws(()=>parseScalar('INT',text));assert.throws(()=>parseScalar('REAL','1e39'));assert.throws(()=>parseScalar('BYTE','-1'));assert.throws(()=>parseScalar('CHAR','ab'));
});
test('stable all-filter selection contains 11 points across a ten-row page',()=>{
 const i=fixture();i.dbs[0].points=Array.from({length:11},(_,n)=>point('p'+n,'INT',n*2));const rows=draftRows(i,[]),selection=new Set(rows.map(r=>r.point.id));assert.equal(rows.slice(0,10).length,10);assert.equal(selectedIds(rows,selection).length,11);assert.equal(selectedIds(rows.slice(10),selection).length,1);assert.deepEqual(draftRows(i,['unknown']),[]);assert.notEqual(draftBaseline(i,[]),draftBaseline(i,['db-a']));
});
test('three-state read patch preserves unselected properties/points and only invalidates policy confirmation',()=>{
 const i=fixture(),original=JSON.stringify(i),r=batch(i,['int'],{clientRead:{action:'set',value:false}});assert.ok(r.candidate);const p=r.candidate.dbs[0].points[1];assert.deepEqual(p.policy,{clientRead:false});assert.equal(p.confirmations.initial,'server-initial');assert.equal(p.confirmations.policy,null);assert.deepEqual(r.candidate.dbs[0].points[0],i.dbs[0].points[0]);assert.deepEqual(r.candidate.policy,i.policy);assert.equal(JSON.stringify(i),original);
 const inherited=batch(r.candidate,['int'],{clientRead:{action:'inherit'}});assert.equal(inherited.candidate.dbs[0].points[1].policy.clientRead,null);assert.equal(inherited.changes[0].after.policy.clientRead,true);assert.equal(inherited.changes[0].after.sources.clientRead,'default');assert.equal(batch(i,['int'],{}).noop,true);assert.equal(batch(i,['int'],{initial:{action:'keep',value:999}}).candidate,null);
});
test('mixed toggle/initial failures block whole candidate and retain original',()=>{
 const i=fixture(),original=JSON.stringify(i);for(const patch of [{mode:{action:'set',value:'toggle'}},{initial:{action:'set',value:'7'}}]){const r=batch(i,['bool','int'],patch);assert.equal(r.candidate,null);assert.ok(r.issues.some(e=>e.pointId===(patch.mode?'int':'bool')));assert.equal(JSON.stringify(i),original);}
});
test('mode links/fixed12 and false/zero are explicit; no automatic unrelated confirmations',()=>{
 const i=fixture(),r=batch(i,['int','real'],{mode:{action:'set',value:'fixed'},rule:{action:'set',value:{...newRule('fixed'),fixedValue:'12'}}});assert.ok(r.candidate);for(const c of r.changes){assert.equal(c.after.policy.owner,'rule');assert.equal(c.after.policy.uiWrite,false);assert.equal(c.after.policy.rule.fixedValue,12);}assert.equal(r.candidate.dbs[0].points[1].confirmations.initial,'server-initial');assert.equal(r.candidate.dbs[0].points[0].confirmations.policy,'server-policy');assert.equal(batch(i,['int'],{initial:{action:'set',value:'0'}}).candidate.dbs[0].points[1].policy.initial,0);assert.equal(batch(i,['bool'],{initial:{action:'set',value:'false'}}).candidate.dbs[0].points[0].policy.initial,false);
});
test('stale/empty/missing stable IDs reject; discarding candidate preserves draft',()=>{
 const i=fixture(),original=JSON.stringify(i);assert.equal(batch(i,[],{}).error,'staleSelection');assert.equal(batch(i,['missing'],{clientRead:{action:'set',value:false}}).error,'staleSelection');assert.equal(batch(i,['int'],{},'stale').error,'staleSelection');assert.ok(batch(i,['int'],{initial:{action:'set',value:'7'}}).candidate);assert.equal(JSON.stringify(i),original);const changed=clone(i);changed.dbs[0].points[1].name='changed';assert.notEqual(draftBaseline(i,[]),draftBaseline(changed,[]));
});
test('property inheritance and region split/overlap diagnostics',()=>{
 const i=fixture(),db=i.dbs[0],p=db.points[1];i.policy={clientRead:false};db.policy={initial:7};db.regions=[{id:'r',firstBit:16,bitLength:16,policy:{clientRead:true}}];p.policy={owner:'ui',uiWrite:true};const e=effectivePolicy(i,db,p);assert.deepEqual(e.errors,[]);assert.equal(e.policy.initial,7);assert.equal(e.sources.initial,'db');assert.equal(e.sources.clientRead,'region:r');assert.equal(e.sources.owner,'point');db.regions[0].bitLength=8;assert.ok(effectivePolicy(i,db,p).errors.includes('policy_split_field'));db.regions.push({id:'r2',firstBit:17,bitLength:16,policy:{}});assert.ok(effectivePolicy(i,db,p).errors.includes('policy_region_overlap'));
});
