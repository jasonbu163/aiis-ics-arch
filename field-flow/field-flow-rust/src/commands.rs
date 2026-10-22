//! 文件：src/commands.rs；双语CLI解析与装配；无参/help无配置读取及状态IO。
use crate::{config::Config, domain::id, infrastructure::state, Result};
use serde_json::Value;
use std::{collections::HashMap, path::PathBuf};
fn locale(lang: &str) -> Value {
    serde_json::from_str(if lang == "zh-CN" {
        include_str!("../locales/zh-CN.json")
    } else {
        include_str!("../locales/en-US.json")
    })
    .unwrap()
}
fn flags(args: &[String], allowed: &[&str], switches: &[&str]) -> Result<HashMap<String, String>> {
    let mut m = HashMap::new();
    let mut at = 0;
    while at < args.len() {
        let key = &args[at];
        if !allowed.contains(&key.as_str()) && !switches.contains(&key.as_str())
            || m.contains_key(key)
        {
            return Err("cli_arguments".into());
        }
        let value = if switches.contains(&key.as_str()) {
            "true".into()
        } else {
            at += 1;
            args.get(at)
                .filter(|v| !v.starts_with("--"))
                .ok_or("cli_arguments")?
                .clone()
        };
        m.insert(key.clone(), value);
        at += 1;
    }
    Ok(m)
}
fn required(m: &HashMap<String, String>, key: &str) -> Result<String> {
    m.get(key).cloned().ok_or("cli_arguments".into())
}
pub async fn execute(mut args: Vec<String>) -> i32 {
    if args == ["__driver"] {
        for fd in [3, 4, 6] {
            let mut typ = 0;
            let mut size = std::mem::size_of_val(&typ) as libc::socklen_t;
            if unsafe {
                libc::getsockopt(
                    fd,
                    libc::SOL_SOCKET,
                    libc::SO_TYPE,
                    (&mut typ as *mut i32).cast(),
                    &mut size,
                )
            } != 0
            {
                return 2;
            }
        }
        return crate::driver_process::child_main();
    }
    let mut lang = "en-US".to_string();
    if let Some(index) = args.iter().position(|s| s == "--lang") {
        if index + 1 >= args.len() {
            return 2;
        }
        lang = args.remove(index + 1);
        args.remove(index);
    }
    let text = locale(&lang);
    if !matches!(lang.as_str(), "zh-CN" | "en-US") {
        eprintln!("{}: cli_language", text["error"].as_str().unwrap());
        return 2;
    }
    if args.is_empty() || args == ["--help"] {
        println!("{}", text["help"].as_str().unwrap());
        return 0;
    }
    let result:Result<()>=async{
  match args[0].as_str(){
   "state" if args.get(1).is_some_and(|s|s=="init")=>{let f=flags(&args[2..],&["--mode","--state-dir","--instance-id"],&["--synthetic"])?;if !f.contains_key("--synthetic"){return Err("synthetic_required".into())}let dir=PathBuf::from(required(&f,"--state-dir")?);let instance=required(&f,"--instance-id")?;state::init(&dir,&required(&f,"--mode")?,&instance)?;let mut audit=crate::infrastructure::audit::Audit::open(&dir,&id(),&instance)?;audit.emit("state_init",serde_json::json!({"result":"ok"}))?;Ok(())},
   "state" if args.get(1).is_some_and(|s|s=="inspect")=>{let f=flags(&args[2..],&["--state-dir"],&[])?;let v=state::inspect(&PathBuf::from(required(&f,"--state-dir")?))?;println!("{v}");Ok(())},
   "run"=>{let f=flags(&args[1..],&["--config","--state-dir"],&["--execute"])?;let c=Config::load(&PathBuf::from(required(&f,"--config")?))?;let dir=PathBuf::from(required(&f,"--state-dir")?);let mode=if f.contains_key("--execute"){"execute"}else{"dry_run"};let(state,state_task)=state::State::open(&dir,mode,&c.instance_id,&id())?;
    let mut runtime=crate::runtime::Runtime::start(&c,&dir,&std::env::current_exe().map_err(|_|"runtime_executable")?,state.clone())?;runtime.launch_flows(&c)?;
    let mut terminate=tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).map_err(|_|"signal_setup")?;let mut tick=tokio::time::interval(std::time::Duration::from_secs(5));
    loop{tokio::select!{_=tokio::signal::ctrl_c()=>break,_=terminate.recv()=>break,_=tick.tick()=>{let _=runtime.health().await;}}}
    let end=tokio::time::Instant::now()+std::time::Duration::from_millis(c.shutdown_timeout_ms);
    let mut outcome=runtime.shutdown(c.shutdown_timeout_ms).await;
    if outcome.is_ok(){match tokio::time::timeout_at(end,state.finalize()).await{Ok(Ok(()))=>{},Ok(Err(e))=>outcome=Err(format!("runtime_finalize:{e}")),Err(_)=>outcome=Err("shutdown_incomplete".into())}}
    drop(state);
    match tokio::time::timeout_at(end,state_task.join()).await{Ok(Ok(()))=>{},Ok(Err(e))=>outcome=Err(format!("runtime_state_join:{e}")),Err(_)=>outcome=Err("shutdown_incomplete".into())}
    outcome
   },_=>Err("cli_arguments".into())
  }
 }.await;
    match result {
        Ok(()) => 0,
        Err(e) => {
            eprintln!("{}: {e}", text["error"].as_str().unwrap());
            if e.starts_with("config_")
                || e.starts_with("state_")
                || e.starts_with("cli_")
                || e == "synthetic_required"
            {
                2
            } else {
                1
            }
        }
    }
}
