/** DIRECT时间/版本展示自检：仅转译纯函数，不操作GUI、配置库或S7客户端。 */
import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import ts from 'typescript';
async function load(path) {
    const source = fs.readFileSync(new URL(path, import.meta.url), 'utf8');
    const compiled = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
    return import('data:text/javascript;base64,' + Buffer.from(compiled).toString('base64'));
}
const {formatShanghaiTime} = await load('../src/console/time.ts');
const {revisionLabel} = await load('../src/console/revisions.ts');
test('UTC and explicit Shanghai offsets display the same seconds without double conversion', () => {
    assert.equal(formatShanghaiTime('2026-10-23T03:39:15.059Z'),'2026-10-23 11:39:15');
    assert.equal(formatShanghaiTime('2026-10-23T11:39:15.999+08:00'),'2026-10-23 11:39:15');
    assert.equal(formatShanghaiTime('2026-12-31T16:00:00.999Z'),'2027-01-01 00:00:00');
});
test('host timezone does not change display; counters and missing/ambiguous dates are never calendar dates', () => {
    const previous = process.env.TZ;
    try {
        for (const zone of ['UTC','America/New_York']) {
            process.env.TZ = zone;
            assert.equal(formatShanghaiTime('2026-10-23T03:39:15.059Z'),'2026-10-23 11:39:15');
        }
        for (const value of [null,undefined,864628049561000,'864628049561000','2026-10-23T11:39:15','invalid']) assert.equal(formatShanghaiTime(value),null);
    } finally {
        if (previous === undefined) delete process.env.TZ;
        else process.env.TZ = previous;
    }
});
test('same-second saved revisions use actual sequences; missing older sequences are not invented', () => {
    const revisions = [{revisionId:'saved-a',savedSeq:'12'},{revisionId:'saved-b',savedSeq:'13'}];
    assert.equal(revisionLabel('saved-a',revisions),'v12');
    assert.equal(revisionLabel('saved-b',revisions),'v13');
    assert.equal(revisionLabel('older-unlisted-id',revisions),'#older-un');
    assert.equal(revisionLabel(null,revisions),'—');
});
