/** SMA-004前端本地门面/草稿CAS/纯文件边界回归。IPC响应是明确的内存fixture，不冒充SQLite证明。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createServer } from 'vite';
import * as XLSX from 'xlsx';
import { ID_INJECTION_KEY, ZINDEX_INJECTION_KEY } from 'element-plus';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'node:path';
import { createSSRApp, defineComponent, effectScope, proxyRefs, ssrContextKey } from 'vue';
import { renderToString } from 'vue/server-renderer';
async function fixture(run, options = {}) {
 const server=await createServer({configFile:false,plugins:[{
  name:'headless-preview-dialog',enforce:'pre',
  transform(code,id) { if (!id.endsWith('/MappingBatchOperationsDialog.vue')) return; return code.replace('import { ElDialog } from "element-plus";', 'import { defineComponent, h } from "vue"; const ElDialog = defineComponent({ setup(_, { slots }) { return () => h("section", slots.default?.()); } });'); }
 },vue()],resolve:{alias:{'@aw-ui':resolve('../console-ui/src/ui/index.ts')},dedupe:['vue','element-plus']},ssr:{external:['vue','element-plus']},optimizeDeps:{noDiscovery:true,include:[],entries:[]},server:{middlewareMode:true,hmr:false,ws:false}});
 const oldWindow=globalThis.window,oldFetch=globalThis.fetch;
 const target={id:'targetApis:target',apiKey:'target',name:'Target',httpMethod:'POST',path:'/fixture',schemaSource:'manual',originType:'manual',originMaterialKey:null,operationId:null,bodyTemplate:{v:null},parameterSchema:[{parameterKey:'body:v',location:'body',name:'v',jsonPath:'v',dataType:'integer',required:true}],idempotencySupported:false,enabled:true,rowVersion:null,createdAt:'2026-11-04T18:00:00.000+08:00',updatedAt:'2026-11-04T18:00:00.000+08:00'};
 const mapping={id:'mappings:map',mappingKey:'map',name:'Map',sourceKey:null,targetApiKey:'target',targetApiId:target.id,bindings:{'body:v':{kind:'fact',value:null,sourceKey:'unknown',factName:'v',valueRuleKey:null}},intervalMs:1000,enabled:true,rowVersion:null,createdAt:target.createdAt,updatedAt:target.updatedAt};
 let snapshot={schemaVersion:1,revision:0,updatedAt:target.updatedAt,document:{connection:options.connection ?? {scheme:'http',host:'',port:0},catalog:[],materials:[],targetApis:[target],mappingValueRules:[],mappings:[mapping],sourceMetadata:[]}};
 const calls=[],events=[];let fetches=0;
 globalThis.fetch=async(...args)=>{fetches++;if(options.fetch)return options.fetch(...args);throw new Error('Unexpected external request');};
 globalThis.window={dispatchEvent:event=>{events.push(event.type);return true;},localStorage:{getItem:()=>JSON.stringify({scheme:'http',host:'old.invalid',port:9999})},__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  calls.push({command,args:structuredClone(args)});
  if(command==='load_app_defaults')return{backendBaseUrl:'http://environment.invalid:9900',externalIoEnabled:Boolean(options.ioEnabled),configurationSource:'memory-fixture'};
  if(command==='load_local_configuration')return structuredClone(snapshot);
  if(command==='export_local_configuration')return JSON.stringify({format:'aiis.sma.configuration',schemaVersion:1,document:snapshot.document});
  if(command==='save_collection_fact_file')return true;
  if(command==='check_external_io'){if(!options.ioEnabled)throw new Error('SMA_EXTERNAL_IO_DISABLED');return;}
  if(command==='change_local_configuration'){if(args.expectedRevision!==snapshot.revision)throw new Error('SMA_CONFIGURATION_CONFLICT');snapshot={...snapshot,revision:snapshot.revision+1,document:{...snapshot.document,...(args.intent.kind==='connection'?{connection:args.intent.payload}:{})}};return structuredClone(snapshot);}
  if(command==='preview_local_configuration')return{token:'fixture',expectedRevision:snapshot.revision,createdKeys:[],updatedKeys:[],unchangedKeys:[],deletedKeys:[],errors:[]};
  if(command==='apply_local_configuration'){if(args.expectedRevision!==snapshot.revision)throw new Error('SMA_CONFIGURATION_CONFLICT');return structuredClone(snapshot);}
  if(command==='preview_saved_local_mapping')return{mappingKey:'map',revision:snapshot.revision,request:null,sourceReferences:[{sourceKey:'unknown',factName:'v',status:'unverified'}]};
  throw new Error(`Unexpected IPC ${command}`);
 }}};
 try{const local=await server.ssrLoadModule('/src/app/twin-facts/api/localConfiguration.ts');await local.loadLocalConfiguration();await run({server,local,calls,events,state:()=>structuredClone(snapshot),advance:()=>{snapshot={...snapshot,revision:snapshot.revision+1}},fetches:()=>fetches});}finally{await server.close();globalThis.window=oldWindow;globalThis.fetch=oldFetch;}
}
test('offline mapping open and saved preview do not read facts or audits; stale editor keeps observed revision',()=>fixture(async({server,local,calls,advance,fetches})=>{
 const {useMappingConfigurationsStore}=await server.ssrLoadModule('/src/app/twin-facts/store/mappingConfigurations.ts');const store=useMappingConfigurationsStore();await store.load();await store.open('mappings:map');assert.equal(fetches(),0);assert.equal(store.draft.value.bindings['body:v'].sourceKey,'unknown');
 store.updateDraft({name:'Unsaved editor name'});await store.previewSaved('mappings:map');assert.equal(calls.at(-1).command,'preview_saved_local_mapping');assert.deepEqual(Object.keys(calls.at(-1).args).sort(),['expectedRevision','mappingId']);assert.equal(store.savedPreview.value.mappingKey,'map');
 advance();await local.loadLocalConfiguration();await assert.rejects(store.save(),/SMA_CONFIGURATION_CONFLICT/);assert.equal(calls.at(-1).args.expectedRevision,0);assert.equal(store.draft.value.name,'Unsaved editor name');assert.equal(fetches(),0);
}));
test('selection and resource import preserve their preview/load revision; changed file requires preview again',()=>fixture(async({server,local,calls,advance,fetches})=>{
 const api=await server.ssrLoadModule('/src/app/twin-facts/api/index.ts');const items=[{apiKey:'fixture'}];await api.previewTargetApiImportInBackend(items);const before=calls.length;items[0].apiKey='changed';await assert.rejects(api.applyTargetApiImportInBackend(items),/SMA_CONFIGURATION_PREVIEW_CHANGED/);assert.equal(calls.length,before);
 const connection=await server.ssrLoadModule('/src/app/connection/api/index.ts');await connection.loadAppDefaults();assert.deepEqual(connection.loadBackendConnectionProfile(),{scheme:'http',host:'',port:0});
 const {useTargetApiConfigurationStore}=await server.ssrLoadModule('/src/app/twin-facts/store/targetApiConfiguration.ts');const store=useTargetApiConfigurationStore();await store.load();await store.open('targetApis:target');store.updateDraft({name:'Old editor'});advance();await local.loadLocalConfiguration();await assert.rejects(store.save(),/SMA_CONFIGURATION_CONFLICT/);assert.equal(calls.at(-1).args.expectedRevision,0);assert.equal(fetches(),0);
}));
test('XLSX formulas/macros and files above the fixed limit are rejected before native apply',()=>fixture(async({server,calls})=>{
 const files=await server.ssrLoadModule('/src/app/twin-facts/utils/mappingConfigurationFiles.ts');const generated=files.createMappingConfigurationTemplateFile('targetApis','xlsx');const workbook=XLSX.read(generated.contents,{type:'array'});workbook.Sheets.targetApis.A2={t:'n',v:1,f:'1+1'};workbook.Sheets.targetApis['!ref']='A1:K2';const formula=XLSX.write(workbook,{type:'buffer',bookType:'xlsx'});await assert.rejects(files.parseMappingConfigurationFile('targetApis',new File([formula],'formula.xlsx')),/FORMULA_UNSUPPORTED/);
 const legacy = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(legacy, XLSX.utils.aoa_to_sheet([
 ['apiKey','name','path','schemaSource','operationId','bodyTemplateJson','parameterSchemaJson','idempotencySupported','enabled'],
 ['legacy','Legacy','/legacy','manual','', '{}', '[]', false, true]
 ]), 'targetApis'); const oldBytes=XLSX.write(legacy,{type:'buffer',bookType:'xlsx'});const oldRows=await files.parseMappingConfigurationFile('targetApis',new File([oldBytes],'legacy.xlsx')); assert.equal(oldRows[0].httpMethod,'POST');
 const macro=XLSX.utils.book_new();XLSX.utils.book_append_sheet(macro,XLSX.utils.aoa_to_sheet([['apiKey']]),'targetApis');macro.vbaraw=Buffer.from('isolated fixture macro');const bytes=XLSX.write(macro,{type:'buffer',bookType:'xlsm'});await assert.rejects(files.parseMappingConfigurationFile('targetApis',new File([bytes],'renamed.xlsx')),/WORKBOOK_INVALID/);
 await assert.rejects(files.parseMappingConfigurationFile('targetApis',{name:'large.json',size:10*1024*1024+1,text:()=>{throw new Error('must not read oversized file')}}),/LIMIT_EXCEEDED/);assert.equal(calls.filter(c=>c.command==='apply_local_configuration').length,0);
}));

// The vendor dialog wrapper is stubbed only for headless SSR; product slot content and handlers are unchanged.
async function setupHandlers(Component, props) {
 let handlers;
 const wrapper=defineComponent({ setup() { handlers=Component.setup(props,{expose(){},emit:props.emit ?? (()=>{})}); return ()=>null; } });
 await renderToString(createSSRApp(wrapper));
 return proxyRefs(handlers);
}
function setupLiveHandlers(Component, props) {
 const scope=effectScope();
 const app=createSSRApp({});app.provide(ssrContextKey,{modules:new Set()});
 const handlers=app.runWithContext(()=>scope.run(()=>Component.setup(props,{expose(){},emit:props.emit ?? (()=>{})})));
 return {view:proxyRefs(handlers),stop:()=>scope.stop()};
}
test('backup uses the native UTF-8 save contract and file controls select without writing configuration',()=>fixture(async({server,calls})=>{
 const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');
 const {default:Workspace}=await server.ssrLoadModule('/src/app/twin-facts/components/TwinJsonContractPanel.vue');
 const workspace=await setupHandlers(Workspace,{labels:getMessages('zh-CN'),enabled:false,page:'mappingIdentity',view:'apiMaterials'});
 await workspace.exportBackup();
 const save=calls.find(call=>call.command==='save_collection_fact_file');
 assert.equal(save.args.fileName,'sma-configuration.json');assert.equal(save.args.mimeType,'application/json;charset=utf-8');
 const saved=JSON.parse(new TextDecoder().decode(Uint8Array.from(save.args.contents)));
 assert.equal(saved.format,'aiis.sma.configuration');assert.equal(saved.document.mappings[0].mappingKey,'map');
 let chooserClicks=0;workspace.restoreFileInput={click(){chooserClicks++;}};workspace.chooseRestoreFile();assert.equal(chooserClicks,1);
 const file=new File([JSON.stringify(saved)],'reviewed-backup.json',{type:'application/json'});const input={files:[file],value:'selected'};
 await workspace.previewRestore({target:input});assert.equal(input.value,'');assert.equal(workspace.restoreFileName,file.name);assert.equal(workspace.restoreConfirmed,false);
 assert.equal(calls.at(-1).command,'preview_local_configuration');assert.equal(calls.some(c=>c.command==='apply_local_configuration'||c.command==='change_local_configuration'),false);
 const {default:Materials}=await server.ssrLoadModule('/src/app/twin-facts/components/ApiMaterialsPanel.vue');const events=[];
 const props={labels:getMessages('zh-CN'),operations:[],savedMaterials:[],selectedIdentities:[],missingSavedCount:0,busy:false,canSave:false,result:null,error:'',enabled:true,emit:(...event)=>events.push(event)};
 const materials=await setupHandlers(Materials,props);materials.openApiFileInput={click(){chooserClicks++;}};materials.chooseOpenApiFile();assert.equal(chooserClicks,2);
 const openapi=new File(['{}'],'source-api.json');materials.importOpenApiFile({target:{files:[openapi],value:'selected'}});assert.equal(materials.openApiFileName,openapi.name);assert.deepEqual(events,[['import-open-api',openapi]]);
 for(const locale of ['zh-CN','en-US']){const labels=getMessages(locale);const html=await renderToString(createSSRApp(Materials,{...props,labels}).provide(ID_INJECTION_KEY,{prefix:1,current:0}).provide(ZINDEX_INJECTION_KEY,{current:0}));assert.ok(html.includes(labels.localOpenApiImport));assert.ok(html.includes(labels.localConfigurationNoFileSelected));assert.match(html,/<button[^>]*type="button"/);assert.match(html,/class="facts-file-input"[^>]*type="file"/);}
}));
test('real batch-dialog content renders create/update/unchanged/error keys for each resource in both locales',()=>fixture(async({server})=>{
 const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');const {default:Dialog}=await server.ssrLoadModule('/src/app/twin-facts/components/MappingBatchOperationsDialog.vue');
 for(const resource of ['targetApis','mappingValueRules','mappings'])for(const locale of ['zh-CN','en-US']){
  const keys=['create','update','unchanged','error'].map(kind=>`${resource}:${kind}-fixture`);
  const preview={createdKeys:[keys[0]],updatedKeys:[keys[1]],unchangedKeys:[keys[2]],errors:[{key:keys[3],errorCode:'fixture_reference_missing'}]};
  const context={};const html=await renderToString(createSSRApp(Dialog,{labels:getMessages(locale),title:resource,busy:false,savingFile:false,preview,error:'',enabled:true}),context);const rendered=html+Object.values(context.teleports ?? {}).join('');
  for(const key of keys)assert.match(rendered,new RegExp(`<code[^>]*>${key}</code>`),`${locale} missing ${key}`);
 }
}));

test('draft OpenAPI test leaves the saved connection, catalog, selections and revision unchanged',()=>{
 const requests=[];
 return fixture(async({server,calls,events,state,fetches})=>{
  const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');
  const {default:View}=await server.ssrLoadModule('/src/app/connection/views/ConnectionModuleView.vue');
  const {view,stop}=setupLiveHandlers(View,{labels:getMessages('zh-CN')});
  const before=state();
  view.backendProfile.host=' fixture.invalid ';view.backendProfile.port=8081;
  await view.testBackendConnectionOpenApi();
  assert.equal(view.testStatus,'connected');
  assert.equal(view.testTarget,'http://fixture.invalid:8081/openapi.json');
  assert.equal(view.saveMessage,getMessages('zh-CN').backendConnectionUnsaved);
  assert.equal(view.backendOpenApiResult.openApiVersion,'3.1.0');
  assert.deepEqual(requests,[{url:'http://fixture.invalid:8081/openapi.json',redirect:'error'}]);
  assert.equal(fetches(),1);assert.deepEqual(state(),before);assert.deepEqual(events,[]);
  assert.equal(calls.some(call=>call.command==='change_local_configuration'),false);stop();
 },{connection:{scheme:'http',host:'saved.invalid',port:9000},ioEnabled:true,fetch:async(url,options)=>{
  requests.push({url,redirect:options.redirect});return Response.json({openapi:'3.1.0',paths:{}});
 }});
});

test('draft address validation rejects host injection and invalid ports before fetch',()=>fixture(async({server,fetches})=>{
 const {testBackendDraftOpenApi,formatBackendOpenApiBaseUrl}=await server.ssrLoadModule('/src/app/connection/api/index.ts');
 assert.equal(formatBackendOpenApiBaseUrl({scheme:'https',host:' [::1] ',port:443}),'https://[::1]');
 for(const host of ['', 'bad host', 'example.invalid/path', 'user@example.invalid', 'example.invalid?x', 'example.invalid#x', 'example.invalid\\path', 'example.invalid:8080', 'example.invalid%2fpath', '-bad.invalid']){
  await assert.rejects(testBackendDraftOpenApi({scheme:'http',host,port:8081}),/BACKEND_(HOST_REQUIRED|ADDRESS_INVALID)/,host);
 }
 for(const port of [0,65536,3.5,'']) await assert.rejects(testBackendDraftOpenApi({scheme:'http',host:'fixture.invalid',port}),/BACKEND_PORT_INVALID/);
 await assert.rejects(testBackendDraftOpenApi({scheme:'ftp',host:'fixture.invalid',port:80}),/BACKEND_ADDRESS_INVALID/);
 assert.equal(fetches(),0);
},{ioEnabled:true}));

test('materials catalog preview retains the existing saved-connection request behavior',()=>{
 const requests=[];
 return fixture(async({server,calls,state})=>{
  const {useApiMaterialsStore}=await server.ssrLoadModule('/src/app/twin-facts/store/apiMaterials.ts');
  const before=state(),store=useApiMaterialsStore();await store.previewCatalog();
  assert.deepEqual(requests,[{url:'http://saved.invalid:9000/openapi.json',redirect:undefined}]);
  assert.ok(store.catalogPreview.value);assert.equal(calls.at(-1).command,'preview_local_configuration');
  assert.deepEqual(state(),before);
 },{connection:{scheme:'http',host:'saved.invalid',port:9000},ioEnabled:true,fetch:async(url,options)=>{
  requests.push({url,redirect:options.redirect});return Response.json({openapi:'3.1.0',paths:{}});
 }});
});

test('a stale OpenAPI response cannot overwrite a later test after an address changes back',()=>{
 const pending=[];
 return fixture(async({server,state,events})=>{
  const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');
  const {default:View}=await server.ssrLoadModule('/src/app/connection/views/ConnectionModuleView.vue');
  const {view,stop}=setupLiveHandlers(View,{labels:getMessages('en-US')});
  const before=state();view.backendProfile.host='fixture.invalid';view.backendProfile.port=8081;
  const first=view.testBackendConnectionOpenApi();await new Promise(resolve=>setImmediate(resolve));
  view.backendProfile.host='other.invalid';view.backendProfile.host='fixture.invalid';
  assert.equal(view.testStatus,'idle');assert.equal(view.testTarget,'');
  const second=view.testBackendConnectionOpenApi();await new Promise(resolve=>setImmediate(resolve));
  assert.equal(pending.length,2);
  pending[1](Response.json({openapi:'3.1.0',paths:{}}));await second;
  pending[0](Response.json({openapi:'3.0.1',paths:{}}));await first;
  assert.equal(view.testStatus,'connected');assert.equal(view.backendOpenApiResult.openApiVersion,'3.1.0');
  assert.equal(view.testTarget,'http://fixture.invalid:8081/openapi.json');assert.deepEqual(state(),before);assert.deepEqual(events,[]);stop();
 },{ioEnabled:true,fetch:()=>new Promise(resolve=>pending.push(resolve))});
});

test('test feedback and explicit offline save preserve the observed revision and conflicting draft',()=>{
 const responses=[new Response('',{status:503}),new Response('{',{status:200}),Response.json({paths:{}}),new TypeError('redirect rejected')];
 return fixture(async({server,calls,events,state,fetches,advance})=>{
  const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');const labels=getMessages('en-US');
  const {default:View}=await server.ssrLoadModule('/src/app/connection/views/ConnectionModuleView.vue');
  const {view,stop}=setupLiveHandlers(View,{labels});view.backendProfile.host='fixture.invalid';view.backendProfile.port=8081;
  for(const expected of [labels.openApiHttpFailed,labels.openApiInvalidResponse,labels.openApiInvalidResponse,labels.openApiUnreachable]){
   await view.testBackendConnectionOpenApi();assert.equal(view.testStatus,'failed');assert.ok(view.testMessage.includes(expected));
  }
  assert.equal(fetches(),4);assert.equal(state().revision,0);assert.deepEqual(events,[]);
  advance();await view.saveBackendConnection();assert.equal(view.saveStatus,'failed');assert.equal(view.saveMessage,labels.localConfigurationConflict);
  assert.equal(view.backendProfile.host,'fixture.invalid');assert.equal(state().revision,1);
  assert.equal(calls.filter(call=>call.command==='change_local_configuration').at(-1).args.expectedRevision,0);stop();
 },{connection:{scheme:'http',host:'saved.invalid',port:9000},ioEnabled:true,fetch:async()=>{
  const response=responses.shift();if(response instanceof Error)throw response;return response;
 }});
});

test('disabled HTTP can still explicitly save a connection without fetching',()=>fixture(async({server,calls,events,state,fetches})=>{
 const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');const labels=getMessages('zh-CN');
 const {default:View}=await server.ssrLoadModule('/src/app/connection/views/ConnectionModuleView.vue');
 const {view,stop}=setupLiveHandlers(View,{labels});view.backendProfile.host='new.invalid';view.backendProfile.port=9001;
 await view.testBackendConnectionOpenApi();assert.equal(view.testMessage,labels.externalIoDisabled);
 await view.saveBackendConnection();assert.equal(view.saveStatus,'saved');assert.equal(state().revision,1);
 assert.deepEqual(state().document.connection,{scheme:'http',host:'new.invalid',port:9001});
 assert.deepEqual(events,['sma-backend-connection-changing','sma-backend-connection-changed']);
 assert.equal(calls.filter(call=>call.command==='change_local_configuration').length,1);assert.equal(fetches(),0);stop();
},{connection:{scheme:'http',host:'saved.invalid',port:9000}}));

test('draft OpenAPI timeout is reported without writing local configuration',()=>fixture(async({server,calls,state})=>{
 const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');const labels=getMessages('en-US');
 const {default:View}=await server.ssrLoadModule('/src/app/connection/views/ConnectionModuleView.vue');
 const {view,stop}=setupLiveHandlers(View,{labels});const before=state();
 view.backendProfile.host='fixture.invalid';view.backendProfile.port=8081;
 await view.testBackendConnectionOpenApi();assert.equal(view.testStatus,'failed');assert.equal(view.testMessage,labels.openApiTimeout);
 assert.equal(calls.some(call=>call.command==='change_local_configuration'),false);assert.deepEqual(state(),before);stop();
},{ioEnabled:true,fetch:(_url,options)=>new Promise((_resolve,reject)=>{
 options.signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')),{once:true});
})}));

test('runtime diagnostics expose only applicable pause and stop controls in both languages',()=>fixture(async({server})=>{
 const {getMessages}=await server.ssrLoadModule('/src/locales/index.ts');
 const {default:Panel}=await server.ssrLoadModule('/src/app/twin-facts/components/ApiFirstMappingRuntimePanel.vue');
 for(const locale of ['zh-CN','en-US'])for(const status of ['idle','running','paused']){
  const labels=getMessages(locale),runtime={status,processedItems:2,successfulTransactions:1,failedTransactions:1,cursor:null,lastErrorCode:null,logs:[]};
  const html=await renderToString(createSSRApp(Panel,{labels,runtime,busy:false,error:''}).provide(ID_INJECTION_KEY,{prefix:1,current:0}).provide(ZINDEX_INJECTION_KEY,{current:0}));
  const buttons=html.match(/<button\b[^>]*>[\s\S]*?<\/button>/g) ?? [];
  const hasButton=label=>buttons.some(button=>button.includes(label));
  assert.ok(html.includes(labels.mappingDeliveryUnavailable));assert.equal(hasButton(labels.startRuntime),false);
  assert.equal(hasButton(labels.resumeRuntime),false);assert.equal(html.includes(labels.runtimeAutoStartOnOpen),false);
  assert.equal(hasButton(labels.pauseRuntime),status==='running');assert.equal(hasButton(labels.stopRuntime),status!=='idle');
 }
}));
