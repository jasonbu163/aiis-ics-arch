//! 文件：src/bin/ff-fixture.rs；独立本机合成夹具入口，无参仅帮助。
fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len()==2 && args[0]=="__catalog_native" {
        std::process::exit(match field_flow::fixture::catalog_demo::native(&args[1]){Ok(())=>0,Err(e)=>{eprintln!("{e}");1}});
    }
    if args.len()==3 && args[0]=="--catalog-demo" && args[1]=="--evidence-dir" {
        std::process::exit(match field_flow::fixture::catalog_demo::manual(std::path::Path::new(&args[2])){Ok(())=>0,Err(e)=>{eprintln!("{e}");1}});
    }
    if args == ["__native_fixture"] {
        std::process::exit(if field_flow::fixture::native_server().is_ok() {
            0
        } else {
            1
        })
    }
    if args.is_empty() || args == ["--help"] {
        let lang=if std::env::var("LANG").unwrap_or_default().starts_with("zh"){include_str!("../../locales/zh-CN.json")}else{include_str!("../../locales/en-US.json")};
        let text:serde_json::Value=serde_json::from_str(lang).unwrap();println!("{}",text["fixture_help"].as_str().unwrap());
        return;
    }
    if args.len() != 4 || args[0] != "--config" || args[2] != "--evidence-dir" {
        std::process::exit(2)
    }
    let result = (|| -> field_flow::Result<()> {
        let c = field_flow::config::Config::load(std::path::Path::new(&args[1]))?;
        if c.plcs[0].host != "127.0.0.1" || c.plcs[0].port != 31102 {
            return Err("fixture_loopback_only".into());
        }
        let dir = std::path::Path::new(&args[3]);
        std::fs::create_dir(dir).map_err(|_| "fixture_new_directory")?;
        let mut f = field_flow::fixture::Fixture::start(&std::env::current_exe().unwrap())?;
        f.command("cmd-001", serde_json::json!(42));
        let mut line = String::new();
        std::io::stdin()
            .read_line(&mut line)
            .map_err(|_| "fixture_stdin")?;
        f.close()?;
        std::fs::write(
            dir.join("protocol.json"),
            serde_json::to_vec_pretty(&f.snapshot()).unwrap(),
        )
        .map_err(|_| "fixture_evidence")?;
        Ok(())
    })();
    if let Err(e) = result {
        eprintln!("{e}");
        std::process::exit(1)
    }
}
