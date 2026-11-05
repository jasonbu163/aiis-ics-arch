/** SMA UI本机偏好隔离回归：拒绝坏值、保持其它应用/业务配置、无业务副作用。 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createServer } from 'vite';
import { effectScope, nextTick } from 'vue';

test('theme and locale round-trip only sma UI keys; invalid or unavailable storage falls back', async () => {
  const server=await createServer({configFile:false,optimizeDeps:{noDiscovery:true,include:[],entries:[]},server:{middlewareMode:true,hmr:false,ws:false}});
  const priorWindow=globalThis.window, priorFetch=globalThis.fetch;
  const storage=new Map([['cu.theme','dark'],['cu.locale','en-US'],['sma.theme','invalid'],['sma.locale','unsupported'],['sma.backend-connection.v1','untouched-business-profile']]);
  let ioCalls=0;
  globalThis.window={localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value)}};
  globalThis.fetch=()=>{ioCalls++;throw new Error('UI preference caused HTTP');};
  const scope=effectScope();
  try {
    const {useUiPreferences}=await server.ssrLoadModule('/src/console/uiPreferences.ts');
    let preferences;
    scope.run(()=>{preferences=useUiPreferences();});
    assert.equal(preferences.theme.value,'light');assert.equal(preferences.locale.value,'zh-CN');
    preferences.theme.value='dark';preferences.locale.value='en-US';await nextTick();
    assert.equal(storage.get('sma.theme'),'dark');assert.equal(storage.get('sma.locale'),'en-US');
    const restored=scope.run(()=>useUiPreferences());
    assert.equal(restored.theme.value,'dark');assert.equal(restored.locale.value,'en-US');
    assert.equal(storage.get('cu.theme'),'dark');assert.equal(storage.get('cu.locale'),'en-US');
    assert.equal(storage.get('sma.backend-connection.v1'),'untouched-business-profile');assert.equal(ioCalls,0);
    window.localStorage={getItem(){throw new Error('storage unavailable');},setItem(){throw new Error('storage unavailable');}};
    const unavailable=scope.run(()=>useUiPreferences());
    assert.equal(unavailable.theme.value,'light');assert.equal(unavailable.locale.value,'zh-CN');
    unavailable.theme.value='dark';await nextTick();assert.equal(unavailable.theme.value,'dark');
  } finally {scope.stop();globalThis.window=priorWindow;globalThis.fetch=priorFetch;await server.close();}
});
