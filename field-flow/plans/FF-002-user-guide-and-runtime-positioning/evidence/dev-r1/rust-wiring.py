from pathlib import Path
p = Path("src/app/mod.rs")
s = p.read_text()
assert "pub mod teaching01;" not in s
p.write_text(s + "\npub mod teaching01;\n")
p = Path("src/config.rs")
s = p.read_text()
old = 'f.kind != "demo01"'
assert s.count(old) == 1
p.write_text(s.replace(old, '!matches!(f.kind.as_str(), "demo01" | "teaching01")'))
p = Path("src/runtime.rs")
s = p.read_text()
old = 'crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await'
new = 'match f.kind.as_str() { "demo01" => crate::app::demo01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await, "teaching01" => crate::app::teaching01::iteration(&f,&plc,&http,&owner,&state,&stop,&mut clock).await, _ => Err("config_flow".into()) }'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
