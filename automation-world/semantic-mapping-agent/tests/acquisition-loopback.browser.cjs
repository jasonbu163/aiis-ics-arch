// Run with Playwright CLI run-code --filename. No dev API or user profile is used.
async page => {
  await page.context().addInitScript(() => {
    localStorage.setItem("sma.locale", "zh-CN");
    localStorage.setItem("sma.theme", "light");
    const when = "2026-11-20T08:02:03.000000+08:00";
    const points = [
      {pointId:"value",name:"Fixture zero",valueText:"0",dataType:"INT",quality:"good",reason:null,observedAt:when,sampleId:"old",sourceType:"external"},
      {pointId:"state",name:"Fixture false",valueText:"false",dataType:"BOOL",quality:"bad",reason:"fixture-reason",observedAt:when,sampleId:"new",sourceType:"external"},
    ];
    const sample = {id:"1",sampleId:"fixture-sample",plcId:"fixture",dbNumber:21,pointCount:2,sourceType:"external",sampledAt:when,points};
    let snapshot = {schemaVersion:1,revision:4,updatedAt:when,document:{
      connection:{scheme:"http",host:"127.0.0.1",port:8000},catalog:[],
      materials:[{materialKey:"fixture-get",httpMethod:"GET",path:"/api/v1/acquisition-data/latest",name:"fixture"}],
      targetApis:[],mappingValueRules:[],mappings:[],sourceMetadata:[],
      acquisitionLoopback:{materialKey:"fixture-get",plcId:"fixture",dbNumber:21,pointIds:[],target:{plcId:"fixture",dbNumber:61421,instanceId:"fixture",sourceGeneration:"g1"},moves:[],groupId:null,configRevision:null}
    }};
    let sends = 0;
    let historyCalls = 0;
    let saves = 0;
    let delayHistory;
    let saveConflict = true;
    let previewId = "";
    const sentIds = [];
    window.__SMA_FIXTURE__ = {
      holdHistory: false,
      historyMode: "normal",
      optionsMode: "normal",
      missingPoint: false,
      finishHistory: () => delayHistory?.(),
      counts: () => ({historyCalls, saves, sentIds}),
    };
    window.__SMA_BROWSER_SENDS__ = () => sends;
    window.__TAURI_INTERNALS__ = {invoke: async (command, args) => {
      if (command === "load_app_defaults") return {externalIoEnabled:true,backendBaseUrl:"http://127.0.0.1:8000",configurationSource:"fixture"};
      if (command === "load_local_configuration") return structuredClone(snapshot);
      if (command === "get_api_first_mapping_runtime") return {runtimeType:"api_first_mapping",status:"idle",runId:null,logs:[],processedItems:0,successfulTransactions:0,failedTransactions:0};
      if (command === "acquisition_options") {
        const mode = window.__SMA_FIXTURE__.optionsMode;
        if (mode === "offline") throw "SMA_ACQUISITION_TRANSPORT";
        return {items:mode === "empty" ? [] : [{plcId:"fixture",dbNumbers:[21]}]};
      }
      if (command === "acquisition_latest") {
        const missing = window.__SMA_FIXTURE__.missingPoint && args.pointIds.includes("state");
        const items = points.filter(p => (!args.pointIds.length || args.pointIds.includes(p.pointId)) && (!missing || p.pointId !== "state"));
        return {items,missingPointIds:missing ? ["state"] : []};
      }
      if (command === "acquisition_history") {
        historyCalls++;
        if (window.__SMA_FIXTURE__.holdHistory) await new Promise(resolve => { delayHistory = resolve; });
        const mode = window.__SMA_FIXTURE__.historyMode;
        if (mode === "timeout") throw "SMA_ACQUISITION_TIMEOUT";
        if (mode === "failure") throw "SMA_ACQUISITION_HTTP(503)";
        if (mode === "empty") return {items:[],total:0,page:1,totalPages:0};
        return {items:args.page === 1 ? [{...sample,id:"older",sampleId:"older-sample"}] : [sample],total:2,page:args.page,totalPages:2};
      }
      if (command === "acquisition_sample") return sample;
      if (command === "save_acquisition_loopback") {
        saves++;
        if (saveConflict) {
          saveConflict = false;
          throw "SMA_LOCAL_CONFIGURATION_REVISION_CONFLICT";
        }
        snapshot = {...snapshot, revision:snapshot.revision+1, document:{...snapshot.document, acquisitionLoopback:args.config}};
        return structuredClone(snapshot);
      }
      if (command === "acquisition_preview") {
        previewId = `preview-${args.sourceSeq}`;
        return {id:previewId,sampleId:"fixture-target",url:"http://127.0.0.1:8000/api/v1/integration/plc-facts/samples",body:JSON.stringify({sampleId:"fixture-target",sourceSeq:args.sourceSeq,points,details:"x".repeat(3000)},null,2),sampledAt:when};
      }
      if (command === "acquisition_test_push") {
        if (args.previewId !== previewId) throw "stale preview";
        sentIds.push(args.previewId);
        sends++;
        if (sends === 1) throw "SMA_ACQUISITION_RESULT_UNKNOWN:SMA_ACQUISITION_TRANSPORT";
        return {httpStatus:200,receipt:{outcome:"duplicate",sampleId:"fixture-target",status:"committed",instanceId:"fixture",contractVersion:"plc-facts/v2"}};
      }
      if (command === "acquisition_readback") return sends === 1 ? null : {...sample, sampleId:"fixture-target",dbNumber:61421};
      if (command === "acquisition_forget_preview") return undefined;
      return null;
    }};
  });
  await page.setViewportSize({width:1280,height:800});
  await page.goto("http://127.0.0.1:15208/");
  const sourceGroup = page.getByRole("menuitem",{name:"源事实",exact:true});
  const facts = page.getByRole("menuitem",{name:"事实表",exact:true});
  const loopback = page.getByRole("menuitem",{name:"手工回环",exact:true});
  const factsKey = "aiis.table-widths.v1:sma:acquisition.latest";
  const loopbackKey = "aiis.table-widths.v1:sma:acquisition.loopback.latest";
  const column = page.getByText("点位标识",{exact:true}).filter({visible:true}).first().locator("xpath=ancestor::th");
  const storedWidth = key => page.evaluate(key => JSON.parse(localStorage.getItem(key) || "null")?.pointId ?? null, key);
  const displayedWidth = () => column.evaluate(header => Math.round(header.getBoundingClientRect().width));
  const resizeColumn = async growth => {
    await column.scrollIntoViewIfNeeded();
    const hit = await column.boundingBox();
    if (!hit) throw Error("could not locate the visible point ID column");
    await page.mouse.move(hit.x + hit.width - 2, hit.y + hit.height / 2);
    await page.mouse.down();
    await page.mouse.move(hit.x + hit.width + growth, hit.y + hit.height / 2, {steps:6});
    await page.mouse.up();
  };
  const loadSources = page.getByRole("button",{name:"读取 PLC 和 DB"});
  const get = page.getByRole("button",{name:"测试获取"});
  const firstPoint = page.getByText("Fixture zero").filter({visible:true});
  const loadLatest = async () => {
    await loadSources.click();
    await get.click();
    await firstPoint.waitFor();
  };
  const resetWidth = page.locator(".acquisition-table:visible").getByRole("button",{name:"恢复默认列宽"});
  await page.evaluate(([facts, loop]) => {
    localStorage.setItem(facts, JSON.stringify({pointId:210}));
    localStorage.removeItem(loop);
  }, [factsKey, loopbackKey]);
  await sourceGroup.click();
  await facts.click();
  await page.getByText("采集最新值（只读）").waitFor();
  if (await page.getByRole("navigation",{name:"手工回环步骤"}).isVisible()) throw Error("the fact table shows loopback controls");
  await loadLatest();
  if (await displayedWidth() !== 210) throw Error("the old acquisition width no longer restores in Facts");
  await resizeColumn(24);
  const factsWidth = await storedWidth(factsKey);
  if (!(factsWidth > 210)) throw Error("resizing Facts did not persist");
  if (await loopback.count() || await page.getByRole("button",{name:"手工回环",exact:true}).count()) throw Error("retired loopback entry is visible");
  await resetWidth.click();
  if (await storedWidth(factsKey) !== null) throw Error("resetting Facts width failed");
  return "Read-only acquisition GET, column widths and retired navigation checked.";
}
