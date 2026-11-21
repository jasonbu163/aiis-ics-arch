// Run with Playwright CLI run-code --filename. No dev API or user profile is used.
async page => {
  await page.context().addInitScript(() => {
    localStorage.setItem("sma.locale", "zh-CN");
    localStorage.setItem("sma.theme", "light");
    const when = "2026-11-20T08:02:03.000000+08:00";
    const points = [
      {pointId:"value",name:"Fixture zero",valueText:"0",dataType:"INT",quality:"good",reason:null,observedAt:when,sampleId:"old",sourceType:"external"},
      {pointId:"state",name:"Fixture false",valueText:"false",dataType:"BOOL",quality:"good",reason:null,observedAt:when,sampleId:"new",sourceType:"external"},
    ];
    const sample = {id:"1",sampleId:"fixture-sample",plcId:"fixture",dbNumber:21,pointCount:2,sourceType:"external",sampledAt:when,points};
    let snapshot = {schemaVersion:1,revision:4,updatedAt:when,document:{
      connection:{scheme:"http",host:"127.0.0.1",port:8000},catalog:[],
      materials:[{materialKey:"fixture-get",httpMethod:"GET",path:"/api/v1/acquisition-data/latest",name:"fixture"}],
      targetApis:[],mappingValueRules:[],mappings:[],sourceMetadata:[],
      acquisitionLoopback:{materialKey:"fixture-get",plcId:"fixture",dbNumber:21,pointIds:[],target:{plcId:"fixture",dbNumber:61421,instanceId:"fixture",sourceGeneration:"g1"},moves:[],groupId:null,configRevision:null}
    }};
    let sends = 0;
    window.__SMA_BROWSER_SENDS__ = () => sends;
    window.__TAURI_INTERNALS__ = {invoke: async (command, args) => {
      if (command === "load_app_defaults") return {externalIoEnabled:true,backendBaseUrl:"http://127.0.0.1:8000",configurationSource:"fixture"};
      if (command === "load_local_configuration") return structuredClone(snapshot);
      if (command === "get_api_first_mapping_runtime") return {runtimeType:"api_first_mapping",status:"idle",runId:null,logs:[],processedItems:0,successfulTransactions:0,failedTransactions:0};
      if (command === "acquisition_options") return {items:[{plcId:"fixture",dbNumbers:[21]}]};
      if (command === "acquisition_latest") return {items: points.filter(p=>!args.pointIds.length || args.pointIds.includes(p.pointId)),missingPointIds:[]};
      if (command === "acquisition_history") return {items:[sample],total:1,page:1,totalPages:1};
      if (command === "acquisition_sample") return sample;
      if (command === "save_acquisition_loopback") {
        snapshot = {...snapshot, revision:snapshot.revision+1, document:{...snapshot.document, acquisitionLoopback:args.config}};
        return structuredClone(snapshot);
      }
      if (command === "acquisition_preview") return {id:"preview",sampleId:"fixture-target",url:"http://127.0.0.1:8000/api/v1/integration/plc-facts/samples",body:JSON.stringify({sampleId:"fixture-target",sourceSeq:args.sourceSeq,points},null,2),sampledAt:when};
      if (command === "acquisition_test_push") {
        sends++;
        if (sends === 1) throw "SMA_ACQUISITION_RESULT_UNKNOWN:SMA_ACQUISITION_TRANSPORT";
        return {httpStatus:200,receipt:{outcome:"duplicate",sampleId:"fixture-target",status:"committed",instanceId:"fixture",contractVersion:"plc-facts/v2"}};
      }
      if (command === "acquisition_readback") return {...sample, sampleId:"fixture-target",dbNumber:61421};
      if (command === "acquisition_forget_preview") return undefined;
      return null;
    }};
  });
  await page.setViewportSize({width:1280,height:800});
  await page.goto("http://127.0.0.1:15208/");
  await page.getByRole("menuitem",{name:"源事实",exact:true}).click();
  await page.getByRole("menuitem",{name:"事实表",exact:true}).click();
  await page.getByText("采集 API 手工回环").waitFor();
  await page.getByRole("button",{name:"读取 PLC 和 DB"}).click();
  await page.getByRole("button",{name:"测试获取"}).click();
  await page.getByText("Fixture zero").waitFor();
  await page.getByText(/最新值来自多个样本/).waitFor();
  if (await page.evaluate(() => window.__SMA_BROWSER_SENDS__()) !== 0) throw Error("read triggered a POST");
  const edge = page.getByText("点位标识",{exact:true}).first();
  const hit = await edge.locator("xpath=ancestor::th").boundingBox();
  if (!hit) throw Error("cannot locate active column header");
  await page.mouse.move(hit.x + hit.width - 2, hit.y + hit.height / 2);
  await page.mouse.down();
  await page.mouse.move(hit.x + hit.width + 44, hit.y + hit.height / 2,{steps:6});
  await page.mouse.up();
  const key = "aiis.table-widths.v1:sma:acquisition.latest";
  const savedWidth = await page.evaluate(key => JSON.parse(localStorage.getItem(key) || "{}").pointId, key);
  if (!(savedWidth > 140)) throw Error("column resize was not stored");
  await page.getByRole("button",{name:"恢复默认列宽"}).first().click();
  if (await page.evaluate(key => localStorage.getItem(key), key) !== null) throw Error("column reset did not clear it");
  await page.getByLabel("采集时间起（上海时间）").fill("2026-11-20T08:02");
  await page.getByLabel("采集时间止（上海时间）").fill("2026-11-20T08:03");
  await page.getByRole("button",{name:"查询历史"}).click();
  await page.getByRole("button",{name:"选择样本"}).click();
  await page.getByText("当前样本").waitFor();
  await page.getByLabel("目标采样序号").fill("7");
  await page.getByRole("button",{name:"预览 POST 请求"}).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button",{name:"测试推送"}).waitFor();
  if (await page.evaluate(() => window.__SMA_BROWSER_SENDS__()) !== 0) throw Error("preview triggered a POST");
  await page.keyboard.press("Escape");
  await dialog.waitFor({state:"hidden"});
  await page.getByRole("button",{name:"切换为暗色"}).click();
  await page.getByRole("button",{name:"切换为英文"}).click();
  await page.getByText("Acquisition API loopback").waitFor();
  await page.setViewportSize({width:1024,height:720});
  await page.getByRole("button",{name:"Preview POST request"}).click();
  await dialog.getByRole("button",{name:"Test POST"}).waitFor();
  const bounds = await dialog.boundingBox();
  if (!bounds || bounds.x < 0 || bounds.x + bounds.width > 1024) throw Error("dialog exceeds compact viewport");
  if (await page.locator("#sma-overlays").getAttribute("data-aw-theme") !== "dark") throw Error("dialog theme changed out of sync");
  await dialog.getByRole("button",{name:"Test POST"}).focus();
  await page.keyboard.press("Enter");
  await dialog.getByText("The POST outcome is unknown.").waitFor();
  await dialog.getByRole("button",{name:"Retry same request"}).click();
  await dialog.getByText("HTTP 200 · committed · duplicate").waitFor();
  await dialog.getByRole("button",{name:"Read back target sample"}).click();
  await page.getByRole("dialog",{name:"Read back target sample"}).getByText("Fixture false").waitFor();
  if (await page.evaluate(() => window.__SMA_BROWSER_SENDS__()) !== 2) throw Error("unexpected POST count");
  return "1280×800 zh-CN/light and 1024×720 en-US/dark, keyboard, dialog bounds, column width save/reset, unknown/retry/readback passed";
}
