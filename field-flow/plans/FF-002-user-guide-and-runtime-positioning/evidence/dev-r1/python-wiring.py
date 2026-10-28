from pathlib import Path
p = Path("src/field_flow/config.py")
s = p.read_text()
old = 'f.kind == "demo01"'
assert s.count(old) == 1
p.write_text(s.replace(old, 'f.kind in ("demo01", "teaching01")'))
p = Path("src/field_flow/runtime.py")
s = p.read_text()
assert s.count('from field_flow.app import demo01') == 1
s = s.replace('from field_flow.app import demo01', 'from field_flow.app import demo01, teaching01')
old = 'result = await demo01.once(self.http, flow, plc, execution)'
new = 'case = {"demo01": demo01.once, "teaching01": teaching01.once}[flow.kind]\n                result = await case(self.http, flow, plc, execution)'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
