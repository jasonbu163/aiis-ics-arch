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
  await loopback.click();
  await page.getByRole("navigation",{name:"手工回环步骤"}).waitFor();
  await loadLatest();
  if (await displayedWidth() === factsWidth) throw Error("Loopback inherited Facts column width");
  await resizeColumn(135);
  const loopbackWidth = await storedWidth(loopbackKey);
  if (!(loopbackWidth > factsWidth) || await storedWidth(factsKey) !== factsWidth) throw Error("resizing Loopback changed Facts preferences");
  await page.reload();
  await sourceGroup.click();
  await facts.click();
  await loadLatest();
  if (await displayedWidth() !== factsWidth) throw Error("Facts column width was lost on reload");
  await resetWidth.click();
  if (await storedWidth(factsKey) !== null || await storedWidth(loopbackKey) !== loopbackWidth) throw Error("resetting Facts changed Loopback preferences");
  await loopback.click();
  await loadLatest();
  if (await displayedWidth() !== loopbackWidth) throw Error("Loopback column width was lost on reload or switching pages");
  await facts.click();
  await resizeColumn(28);
  const independentFactsWidth = await storedWidth(factsKey);
  await loopback.click();
  await resetWidth.click();
  if (!(independentFactsWidth > 140) || await storedWidth(loopbackKey) !== null || await storedWidth(factsKey) !== independentFactsWidth) throw Error("resetting Loopback changed Facts preferences");
  await page.evaluate(() => { window.__SMA_FIXTURE__.optionsMode = "offline"; });
  await loadSources.click();
  await page.getByText("无法连接采集接口，请检查已保存地址后重试。").waitFor();
  await page.evaluate(() => { window.__SMA_FIXTURE__.optionsMode = "empty"; });
  await loadSources.click();
  await page.getByText("没有数据",{exact:true}).filter({visible:true}).waitFor();
  await page.evaluate(() => { window.__SMA_FIXTURE__.optionsMode = "normal"; });
  await loadSources.click();
  await page.getByRole("button",{name:"测试获取"}).click();
  await page.getByText("Fixture zero").filter({visible:true}).waitFor();
  await page.getByText(/最新值来自多个样本/).waitFor();
  const result = page.getByRole("row").filter({hasText:"Fixture false"});
  await result.getByText("false",{exact:true}).waitFor();
  await result.getByText("fixture-reason",{exact:true}).waitFor();
  await page.getByRole("row").filter({hasText:"Fixture zero"}).getByText("0",{exact:true}).waitFor();
  await page.getByRole("checkbox",{name:"全部点位"}).uncheck();
  await page.getByRole("checkbox",{name:"value",exact:true}).check();
  await get.click();
  await page.getByText("Fixture zero").filter({visible:true}).waitFor();
  if (await result.isVisible()) throw Error("single-point selection returned another point");
  await page.getByRole("checkbox",{name:"state",exact:true}).check();
  await page.evaluate(() => { window.__SMA_FIXTURE__.missingPoint = true; });
  await get.click();
  await page.getByText("所选点位有缺失 state").waitFor();
  await page.evaluate(() => { window.__SMA_FIXTURE__.missingPoint = false; });
  await get.click();
  await result.getByText("false",{exact:true}).waitFor();
  await page.getByRole("checkbox",{name:"全部点位"}).check();
  await get.click();
  await result.getByText("false",{exact:true}).waitFor();
  if (await page.evaluate(() => window.__SMA_BROWSER_SENDS__()) !== 0) throw Error("read triggered a POST");
  const counts = () => page.evaluate(() => window.__SMA_FIXTURE__.counts());
  await page.getByRole("button",{name:"下一步：查历史"}).click();
  const search = page.getByRole("button",{name:"查询历史"});
  const from = page.getByLabel("采集时间起（上海时间）");
  const to = page.getByLabel("采集时间止（上海时间）");
  if (!(await search.isDisabled())) throw Error("history did not require a range");
  await page.getByText("请填写采集开始时间。").waitFor();
  await from.fill("2026-11-20T08:02");
  await page.getByText("请填写采集结束时间。").waitFor();
  await to.fill("2026-11-20T08:01");
  await page.getByText(/结束时间应晚于开始时间/).waitFor();
  await to.fill("2026-11-20T08:03");
  await page.evaluate(() => { window.__SMA_FIXTURE__.holdHistory = true; });
  await search.click();
  await to.fill("2026-11-20T08:04");
  await page.evaluate(() => {
    window.__SMA_FIXTURE__.holdHistory = false;
    window.__SMA_FIXTURE__.finishHistory();
  });
  await page.getByText("查询后，在对应结果行点击「使用此样本」。").waitFor();
  if (await page.getByText("fixture-sample",{exact:true}).isVisible()) throw Error("dated response overwrote the latest search");
  for (const [mode, expected] of [
    ["timeout","读取超时，请检查后端连接。"],
    ["failure","采集接口返回错误。"],
    ["empty","没有数据"],
  ]) {
    await page.evaluate(value => { window.__SMA_FIXTURE__.historyMode = value; }, mode);
    await search.click();
    await page.getByText(expected,{exact:false}).filter({visible:true}).waitFor();
  }
  await page.evaluate(() => { window.__SMA_FIXTURE__.historyMode = "normal"; });
  await search.click();
  await page.getByText("older-sample",{exact:true}).waitFor();
  await page.getByRole("button",{name:"下一页",exact:true}).click();
  const sampleRow = page.getByRole("row").filter({hasText:"fixture-sample"});
  await sampleRow.getByRole("button",{name:"使用此样本"}).click();
  await page.getByText("当前样本").waitFor();
  await page.getByRole("button",{name:"下一步：配目标"}).click();
  const targetDb = page.getByLabel("目标 DB",{exact:true});
  const sequence = page.getByLabel("目标采样序号");
  await targetDb.fill("21");
  await page.getByText("请使用不同的测试目标 PLC/DB 组合。").waitFor();
  await targetDb.fill("61421");
  await sequence.fill("7");
  await page.getByLabel("采集组常量（可选）").fill("batch");
  await page.getByRole("button",{name:"上一步",exact:true}).click();
  if (await to.inputValue() !== "2026-11-20T08:04") throw Error("history range was lost");
  await page.getByRole("button",{name:"已选样本"}).waitFor();
  await page.getByRole("button",{name:"下一步：配目标"}).click();
  if (await page.getByLabel("采集组常量（可选）").inputValue() !== "batch") throw Error("target draft was lost");
  await page.getByRole("button",{name:"保存配置"}).click();
  await page.getByText("配置或目标序号有冲突，请核对后再操作。").waitFor();
  if (await page.getByLabel("采集组常量（可选）").inputValue() !== "batch") throw Error("conflict discarded draft");
  await page.getByRole("button",{name:"保存配置"}).click();
  await page.getByText("配置已保存",{exact:true}).waitFor();
  await page.getByRole("button",{name:"下一步：预览与推送"}).click();
  await page.getByRole("button",{name:"预览 POST 请求"}).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button",{name:"测试推送"}).waitFor();
  await dialog.getByText("fixture / DB 21",{exact:true}).waitFor();
  await dialog.getByText("fixture / DB 61421",{exact:true}).waitFor();
  if ((await counts()).sentIds.length) throw Error("preview triggered a POST");
  await page.keyboard.press("Escape");
  await dialog.waitFor({state:"hidden"});
  await page.getByRole("button",{name:"预览 POST 请求"}).click();
  await dialog.getByRole("button",{name:"返回修改"}).click();
  await dialog.waitFor({state:"hidden"});
  if (await sequence.inputValue() !== "7") throw Error("editing discarded the sequence");
  await sequence.fill("8");
  await page.getByRole("button",{name:"下一步：预览与推送"}).click();
  await page.getByRole("button",{name:"切换为暗色"}).click();
  await page.getByRole("button",{name:"切换为英文"}).click();
  await page.setViewportSize({width:1024,height:720});
  await page.getByRole("button",{name:"Preview POST request"}).click();
  await dialog.getByRole("button",{name:"Test POST"}).waitFor();
  await dialog.locator(".acquisition-dialog-content:focus").waitFor();
  const bounds = await dialog.boundingBox();
  if (!bounds || bounds.x < 0 || bounds.y < 0 || bounds.x + bounds.width > 1024 || bounds.y + bounds.height > 720) throw Error("dialog exceeds compact viewport");
  if (await page.locator("#sma-overlays").getAttribute("data-aw-theme") !== "dark") throw Error("dialog theme changed out of sync");
  if (!(await dialog.locator(".el-dialog__body").evaluate(body => body.scrollHeight > body.clientHeight))) throw Error("long preview does not scroll independently");
  await dialog.getByRole("button",{name:"Test POST"}).focus();
  await page.keyboard.press("Enter");
  await dialog.getByText("The POST outcome is unknown.").waitFor();
  await dialog.getByRole("button",{name:"Read back target sample"}).click();
  await dialog.getByText("The sample is not visible in target history yet. Check again.").waitFor();
  await dialog.getByRole("button",{name:"Close",exact:true}).click();
  await dialog.getByRole("button",{name:"Retry same request"}).click();
  await dialog.getByText("HTTP 200 · committed · duplicate").waitFor();
  await dialog.getByRole("button",{name:"Read back target sample"}).click();
  await page.getByRole("dialog",{name:"Read back target sample"}).getByText("Fixture false").waitFor();
  const {historyCalls,saves,sentIds} = await counts();
  if (historyCalls !== 6 || saves !== 2 || sentIds.join(",") !== "preview-8,preview-8") throw Error("unexpected history, save or POST counts/identity");
  return "Separate facts, isolated column widths across reload/reset, point filtering, empty/error states, four steps, time validation, delayed history, pagination, conflict retention, previews, compact scroll, unknown/readback/retry and matching preview ID passed. 1280×800 zh-CN/light and 1024×720 en-US/dark.";
}
