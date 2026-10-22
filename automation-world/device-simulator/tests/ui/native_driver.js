/* r5非默认原生DOM回归。只操作真实表单/按钮/File，不读写Vue内部状态或绕过正常IPC。 */
(async () => {
  const scenario = window.__DS_TEST_SCENARIO__
  const pause = ms => new Promise(resolve => setTimeout(resolve, ms))
  const visible = element => !!element && element.getClientRects().length > 0
  const all = selector => Array.from(document.querySelectorAll(selector)).filter(visible)
  const one = selector => all(selector)[0]
  const bounded = value => new TextDecoder().decode(new TextEncoder().encode(String(value)).slice(0, 1000))
  const id = name => `[data-testid="${name}"]`
  async function until(predicate, label, timeout = 20000) {
    const deadline = performance.now() + timeout
    while (performance.now() < deadline) {
      const value = predicate()
      if (value) return value
      await pause(50)
    }
    throw Error('timeout: ' + label + ' / ' + document.body.innerText.slice(-800))
  }
  function geometry(label) {
    const root = document.documentElement
    if (root.scrollWidth > innerWidth + 2) throw Error('page horizontal overflow: ' + label)
    const cards = all('.ds-card-stack')
    for (const card of cards) if (parseFloat(getComputedStyle(card).rowGap) < 8) throw Error('card content gap: ' + label)
    const dialogs = all('.el-dialog')
    for (const dialog of dialogs) {
      const rect = dialog.getBoundingClientRect()
      if (rect.left < -1 || rect.right > innerWidth + 1 || rect.top < -1 || rect.bottom > innerHeight + 1) throw Error('dialog outside viewport: ' + label + ' ' + JSON.stringify([rect.left,rect.top,rect.right,rect.bottom,innerWidth,innerHeight]))
      const buttons = Array.from(dialog.querySelectorAll('.el-dialog__footer button')).filter(visible)
      for (let index = 1; index < buttons.length; index++) {
        const a = buttons[index - 1].getBoundingClientRect(), b = buttons[index].getBoundingClientRect()
        if (Math.abs(a.top - b.top) < 2 && b.left - a.right < 7) throw Error('dialog footer gap: ' + label)
      }
    }
    for (const cell of all('.ds-technical-table th .cell')) if (getComputedStyle(cell).whiteSpace !== 'nowrap') throw Error('technical header wraps: ' + label)
    return JSON.stringify({ label, viewport: [innerWidth, innerHeight], theme: document.documentElement.dataset.theme, cards: cards.length, dialogs: dialogs.map(e => { const r=e.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)] }), rootWidth: root.scrollWidth })
  }
  async function report(step, details = []) {
    details = [...details, geometry(step)]
    await window.__TAURI_INTERNALS__.invoke('ds_test_report', { report: { scenario, step, status: 'pass', details: details.map(bounded) } })
  }
  async function click(selector) {
    const element = await until(() => one(selector), selector)
    if (element.disabled || element.getAttribute('aria-disabled') === 'true') throw Error('disabled: ' + selector)
    if (element.closest('.el-dialog')) {
      let previous = ''
      await until(() => {
        const boxes = all('.el-dialog').map(dialog => dialog.getBoundingClientRect())
        if (boxes.some(rect => rect.left < 0 || rect.top < 0 || rect.right > innerWidth || rect.bottom > innerHeight)) { previous = ''; return false }
        const current = JSON.stringify(boxes.map(rect => [rect.left, rect.top, rect.right, rect.bottom].map(value => Math.round(value * 10))))
        const stable = current === previous; previous = current; return stable
      }, 'visible dialog rectangles stable within viewport')
    }
    element.scrollIntoView({ block: 'center' }); geometry('before ' + selector); element.click(); await pause(120)
  }
  async function input(selector, value) {
    const wrapper = await until(() => one(selector), selector)
    const element = wrapper.matches('input,textarea') ? wrapper : wrapper.querySelector('input,textarea')
    if (!element) throw Error('input missing: ' + selector)
    element.focus()
    Object.getOwnPropertyDescriptor(element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set.call(element, String(value))
    element.dispatchEvent(new Event('input', { bubbles: true })); element.dispatchEvent(new Event('change', { bubbles: true })); element.blur(); await pause(100)
  }
  async function select(selector, label = null, index = 0) {
    const control = await until(() => one(selector), selector)
    await click(selector + ' .el-select__wrapper')
    const list = await until(() => {
      const input = control.querySelector('[aria-controls]')
      const listId = input?.getAttribute('aria-controls')
      const node = listId && document.getElementById(listId)
      return visible(node) ? node : null
    }, 'owned option list ' + selector)
    const option = await until(() => {
      const options = Array.from(list.querySelectorAll('.el-select-dropdown__item')).filter(e => visible(e) && !e.classList.contains('is-disabled'))
      return label === null ? options[index] : options.find(e => e.innerText.trim() === label || e.innerText.trim().startsWith(label))
    }, 'option ' + label + ' in ' + selector)
    const chosen = option.innerText.trim()
    option.click()
    document.body.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    document.body.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    await until(() => control.innerText.includes(chosen), 'selected ' + chosen + ' in ' + selector)
    await pause(180)
  }
  async function nav(page) {
    const leaf = `[data-navigation-id="${page}"]`
    if (!visible(document.querySelector(leaf))) await click('[data-navigation-id="configuration"] > .el-sub-menu__title')
    const changed = !one(id('page-' + page))
    await click(leaf); await until(() => one(id('page-' + page)), 'page ' + page)
    if (changed && document.querySelector('.agent-workspace').scrollTop > 2) throw Error('new page retains scroll: ' + page)
    geometry('page ' + page)
  }
  async function settled() {
    await pause(250)
    await until(() => !all('.is-loading').length, 'UI idle')
    if (one(id('ipc-error'))) throw Error('IPC error: ' + one(id('ipc-error')).dataset.errorCode + ': ' + one(id('ipc-error')).innerText)
  }
  async function save() { await click(id('configuration-save')); await settled() }
  async function selectAllPages() {
    const pager = one(id('page-points')).querySelector('.el-pagination')
    const first = pager?.querySelector('.el-pager li.number')
    first?.click(); await pause(100)
    for (let page = 0; page < 410; page++) {
      const check = one(id('point-select-page')).querySelector('input')
      if (!check.checked) await click(id('point-select-page'))
      const next = pager.querySelector('.btn-next')
      if (next.disabled) break
      next.click(); await pause(100)
    }
    first?.click(); await pause(100)
  }
  async function confirmPreview() { await click(id('preview-confirm')); await until(() => !one(id('preview-confirm')), 'preview closed'); await settled() }
  async function confirmDb(index, manual = false) {
    await select(id('points-db'), null, index)
    if (manual) { await click(id('layout-open')); await input(id('layout-reason'), 'explicit native UI synthetic address'); await click(id('layout-preview')) }
    else await click(id('standard-layout'))
    await confirmPreview(); await selectAllPages(); await click(id('names-open')); await confirmPreview(); await click(id('points-confirm-initial')); await settled()
  }
  async function createInstance() {
    await nav('instances'); await click(id('instance-add')); await input(id('instance-name'), 'Native A'); await input(id('instance-port'), 30102); await click(id('instance-confirm')); await save()
    await report('instance_created', [one(id('page-instances')).innerText.slice(0, 900)])
  }
  const dbSource = 'DATA_BLOCK "Alpha"\n{ S7_Optimized_Access := \'FALSE\' }\nVAR\n Value : DINT := 91;\n PairValue : "NativePair";\n Items : ARRAY[-1..20] OF UINT;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK\nDATA_BLOCK "Beta"\n{ S7_Optimized_Access := \'FALSE\' }\nVAR\n Signal : REAL;\nEND_VAR\nBEGIN\nEND_DATA_BLOCK\n'
  const udtSource = 'TYPE "NativePair"\nSTRUCT\n Temperature : REAL;\n Ready : BOOL;\nEND_STRUCT;\nEND_TYPE\n'
  const alternateUdtSource = 'TYPE "NativePair"\nSTRUCT\n Temperature : DINT;\n Ready : BYTE;\nEND_STRUCT;\nEND_TYPE\n'
  async function importSources() {
    await nav('points')
    const transfer = new DataTransfer(); transfer.items.add(new File([dbSource], 'native.db', { type: 'text/plain' })); transfer.items.add(new File([udtSource], 'native.udt', { type: 'text/plain' })); transfer.items.add(new File([alternateUdtSource], 'native.udt', { type: 'text/plain' }))
    const files = one(id('source-files')); files.files = transfer.files; files.dispatchEvent(new Event('change', { bubbles: true }))
    await until(() => all(id('source-file-row')).length === 3, 'three actual source Files')
    const rows = all(id('source-file-row')), labels = rows.map(row => row.querySelector(id('source-file-label')).textContent.trim())
    if (labels[1] === labels[2] || !labels[1].includes('[2:') || !labels[2].includes('[3:') || rows[1].dataset.inputId === rows[2].dataset.inputId) throw Error('same-basename source identity is ambiguous')
    await click(id('source-scan')); await settled(); await click(id('import-select-Alpha')); await click(id('import-select-Beta'))
    const numbers = all(id('import-db-number')); await inputElement(numbers[0], 71); await inputElement(numbers[1], 72)
    await select(id('import-closure-Alpha'), 'NativePair · ' + labels[1])
    await click(id('source-preview')); await settled(); await click(id('import-cancel')); await report('import_cancelled', ['real preview cancelled before confirmation'])
    await click(id('source-preview')); await settled(); await click(id('import-confirm')); await until(() => !one(id('import-confirm')), 'import confirmed'); await settled()
    await report('import_confirmed', ['three source Files; same-basename/name UDTs have distinct visible batch/input identities', 'explicit DB71/72 and closure: NativePair · ' + labels[1]])
  }
  async function inputElement(wrapper, value) { if (!wrapper) throw Error('input wrapper absent'); const element = wrapper.querySelector('input'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(element, String(value)); element.dispatchEvent(new Event('input', { bubbles: true })); element.dispatchEvent(new Event('change', { bubbles: true })); element.blur(); await pause(100) }
  async function manualPoint() {
    await click(id('db-add')); await input(id('db-name'), 'ManualValues'); await input(id('db-number'), 73); await input(id('db-length'), 8)
    await click(id('point-add')); await input(id('point-name'), 'UiValue'); await select(id('point-type'), 'UINT'); await input(id('point-byte'), 0); await input(id('point-reason'), 'explicit native UI manual point'); await click(id('point-confirm')); await save(); await confirmDb(2, true)
    await report('manual_point_confirmed', ['manual DB73/UiValue UINT with confirmed explicit address'])
  }
  async function policies() {
    await nav('policies'); await select(id('policy-level'), 'Instance'); await select(id('policy-owner'), 'S7 client'); await select(id('policy-clientWrite'), 'Allow'); await select(id('policy-uiMaintenance'), 'Allow'); await save()
    await select(id('policy-level'), 'Point'); await select(id('policy-db'), 'Beta'); await select(id('policy-point'), null, 0)
    for (const mode of ['Ramp', 'Sine', 'Deterministic random']) { await select(id('policy-mode'), mode); await click(id('policy-confirm')); await settled() }
    await select(id('policy-db'), 'ManualValues'); await select(id('policy-point'), 'UiValue'); await select(id('policy-owner'), 'UI'); await select(id('policy-clientWrite'), 'Deny'); await select(id('policy-uiWrite'), 'Allow'); await select(id('policy-uiMaintenance'), 'Deny'); await click(id('policy-initial-override')); await input(id('policy-initial'), 12); await click(id('policy-confirm')); await settled()
    await nav('points'); for (let index = 0; index < 3; index++) { await select(id('points-db'), null, index); await selectAllPages(); await click(id('points-confirm-initial')); await settled() }
    await report('policies_saved', ['instance/client maintenance inheritance; Ramp -> Sine -> Random saved through real UI; UiValue UI owner initial12'])
  }
  async function apply() {
    await nav('instances'); await select(id('revision-selection'), null, 0); await click(id('apply-open')); await settled(); await click(id('apply-ack')); await click(id('apply-confirm')); await until(() => !one(id('apply-preview')), 'apply closed'); await settled(); await nav('overview'); await until(() => one(id('control-start')) && !one(id('control-start')).disabled, 'loaded stopped')
    await report('applied', [one(id('revision-facts')).innerText])
  }
  async function preferences() {
    const language = one('.aw-language-switch'); if (!language) throw Error('CU LanguageSwitch missing')
    const original = language.querySelector('.is-active').innerText; language.click(); await pause(120); if (one('.aw-language-switch .is-active').innerText === original) throw Error('language did not change')
    if (one('.aw-language-switch .is-active').innerText !== 'EN') { language.click(); await pause(100) }
    const theme = one('.aw-theme-toggle'); const before = theme.getAttribute('aria-pressed'); theme.click(); await pause(120); if (theme.getAttribute('aria-pressed') === before) throw Error('theme did not change'); theme.click(); await pause(100)
    for (const page of ['overview', 'instances', 'points', 'policies', 'values', 'logs']) {
      const workspace = document.querySelector('.agent-workspace'); workspace.scrollTop = workspace.scrollHeight
      await nav(page)
    }
    await report('ui_preferences', ['CU 中/EN active state and theme toggles; six real navigation pages; native viewport=' + innerWidth + 'x' + innerHeight, 'DS title=' + document.title])
  }
  async function startAndClient() {
    await nav('overview'); await click(id('control-start')); await until(() => one(id('runtime-state'))?.dataset.state === 'running', 'runtime running'); await nav('values'); await report('listener_started', ['normal ds_control_instance start; awaiting independent real S7 client'])
    await until(() => all(id('connection-close')).length > 0, 'real client connection', 30000)
  }
  async function typedWrite(row, maintenance, value) {
    const selector = id(maintenance ? 'value-maintenance' : 'value-write'); const button = Array.from(row.querySelectorAll(selector)).find(e => !e.disabled); if (!button) throw Error('write permission missing')
    button.click(); await input(id('value-input'), value); await click(id('value-ack')); await click(id('value-confirm')); await until(() => !one(id('value-write-dialog')), 'typed write closed'); await settled()
  }
  await until(() => one(id('ds-ready'))?.dataset.ready === 'true', 'real bootstrap ready', 30000)
  await report('ready', ['real WebView ready; scenario=' + scenario, 'title=' + document.title])
  if (scenario === 'N1') {
    await preferences(); await createInstance(); await importSources(); await confirmDb(0); await confirmDb(1); await report('layout_names_confirmed', ['full imported DB layouts and all-page point selection/name/initial confirmations'])
    await manualPoint(); await policies(); await apply(); await nav('instances')
    await click(id('instance-add')); await input(id('instance-name'), 'Native B pending'); await input(id('instance-port'), 30103); await click(id('instance-confirm')); await save()
    await select(id('instance-selection'), 'Native A'); await report('second_instance', ['second UUID draft instance saved/stopped/unloaded; A selected image remains distinct'])
    await click(id('instance-edit')); await input(id('instance-name'), 'Native A saved'); await report('dirty_save_ready', ['unsaved real instance editor remains open'])
    await report('close_ready'); await until(() => one(id('dirty-close-dialog')), 'dirty save close dialog'); await click(id('dirty-close-save'))
  } else if (scenario === 'N2') {
    await nav('overview'); await until(() => one(id('runtime-state'))?.dataset.state === 'stopped', 'reopen stopped'); await nav('values'); await until(() => one(id('value-UiValue'))?.innerText.trim() === '12', 'reopen typed initial12'); await report('reopened_stopped', ['selected restore initialized/stopped; UiValue12'])
    await startAndClient(); const uiRow = await until(() => one(id('value-UiValue'))?.closest('tr'), 'UiValue row'); await typedWrite(uiRow, false, 42); await until(() => one(id('value-UiValue'))?.innerText.trim() === '42', 'ordinary readback42'); await report('ordinary_write', ['real typed UI write + owner snapshot readback42'])
    const clientRow = await until(() => all(id('value-maintenance')).find(e => !e.disabled)?.closest('tr'), 'maintenance permitted row'); await typedWrite(clientRow, true, 9); await report('maintenance_write', ['explicit one-time maintenance CAS and confirmation via normal IPC'])
    const realRow = await until(() => all('#app tr').find(e => e.innerText.includes('REAL') && e.innerText.includes('Signal')), 'rule REAL row'); const before = realRow.innerText; await pause(1200); if (realRow.innerText === before) throw Error('rule metadata/value did not progress'); await report('rules_observed', [realRow.innerText])
    await select(id('values-instance'), 'Native B pending'); await until(() => !one(id('value-UiValue')), 'A values hidden for unloaded B'); await pause(1100)
    if (one(id('value-UiValue'))) throw Error('late A values crossed into selected B')
    await select(id('values-instance'), 'Native A saved'); await until(() => one(id('value-UiValue'))?.innerText.trim() === '42', 'A values recovered after selection'); await report('selection_isolated', ['B has no loaded rows; late A response cannot populate B; A42 recovers'])
    await report('snapshot_stale_ready', ['external owned SQLite exclusive-lock window begins after this fixed report'])
    await until(() => one(id('ipc-error')) && one(id('page-values')).innerText.includes('Stale'), 'actual snapshot failure retains old rows', 12000)
    if (one(id('value-UiValue'))?.innerText.trim() !== '42') throw Error('snapshot failure discarded last good A values')
    await report('snapshot_stale_observed', ['real normal snapshot IPC error + stale UI + prior UiValue42 retained'])
    await until(() => !one(id('page-values')).innerText.includes('Stale'), 'snapshot recovers after owned SQL lock release')
    await nav('overview'); await click(id('control-pause')); await settled(); await report('snapshot_recovered', ['real subsequent snapshot recovered; explicit pause succeeds without retried write']); await report('close_ready')
  } else if (scenario === 'N3') {
    await nav('values'); await until(() => one(id('value-UiValue'))?.innerText.trim() === '12', 'runtime value reset on reopen'); await report('reopened_initial', ['previous runtime42 not persisted; selected initial12/stopped'])
    await startAndClient(); await click(id('connection-close')); await click(id('connection-close-confirm')); await until(() => !all(id('connection-close')).length, 'single connection truly released'); await report('connection_closed', ['normal confirmed single connection close + real snapshot empty'])
    await nav('instances'); await click(id('instance-edit')); await input(id('instance-name'), 'Unsaved must discard'); await report('dirty_cancel_ready'); await until(() => one(id('dirty-close-dialog')), 'cancel dialog'); await click(id('dirty-close-cancel')); await until(() => !one(id('dirty-close-dialog')), 'cancel keeps window'); if (!one(id('instance-editor'))) throw Error('dirty input lost after cancel'); await report('dirty_cancelled', ['normal close cancelled; editor and running runtime retained'])
    await report('close_ready'); await until(() => one(id('dirty-close-dialog')), 'discard dialog'); await click(id('dirty-close-discard'))
  } else throw Error('unknown fixed scenario')
})().catch(async error => {
  try { await window.__TAURI_INTERNALS__.invoke('ds_test_report', { report: { scenario: window.__DS_TEST_SCENARIO__, step: 'failed', status: 'fail', details: [String(error).slice(0, 200), document.body.innerText.slice(-200)] } }) } catch (failure) { console.error(failure) }
})
