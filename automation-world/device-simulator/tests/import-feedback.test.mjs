/** DIRECT导入状态回归：业务校验不误报bridge不可用，locale和依赖提示对称。 */
import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import ts from 'typescript';
const source=fs.readFileSync(new URL('../src/console/ipcStatus.ts',import.meta.url),'utf8');
const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {ipcStatusKey}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
test('known UDT validation failure keeps the established bridge healthy',()=>{
    for(const error of ['udt_missing','udt_ambiguous','duplicate_udt','configuration_blocked',null]) assert.equal(ipcStatusKey(true,true,error),'simulator.ipcReady');
    assert.equal(ipcStatusKey(true,true,'ipc_transport_unknown'),'common.local.bootstrapFailed');
    assert.equal(ipcStatusKey(false,false,null),'common.local.desktopPreview');
    assert.equal(ipcStatusKey(true,false,null),'common.local.loading');
    assert.equal(ipcStatusKey(true,false,'storage_open'),'common.local.bootstrapFailed');
});
test('dependency diagnostics have bilingual context and symmetric placeholders',()=>{
    const zh=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/zh-CN.json',import.meta.url),'utf8'));
    const en=JSON.parse(fs.readFileSync(new URL('../src/app/simulator/locales/en-US.json',import.meta.url),'utf8'));
    const flatten=(value,prefix='')=>Object.entries(value).flatMap(([key,v])=>typeof v==='object'?flatten(v,prefix+key+'.'):[[prefix+key,v]]);
    const a=new Map(flatten(zh)),b=new Map(flatten(en));
    assert.deepEqual([...a.keys()].sort(),[...b.keys()].sort());
    for(const [key,value] of a) assert.deepEqual((value.match(/\{[^}]+\}/g)||[]).sort(),(b.get(key).match(/\{[^}]+\}/g)||[]).sort(),key);
    for(const key of ['missing','ambiguous','cycle']) assert.match(zh.importDependency[key],/\{path\}.*\{name\}/);
});
