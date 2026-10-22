//! DS协议回归真实ManagedS7显式loopback互操作入口；裸运行只有帮助。
mod domain;
mod infrastructure;
use domain::local_configuration::Plc;
use infrastructure::managed_s7::{ManagedS7, Transport};
use std::{
    thread,
    time::{Duration, Instant},
};
fn plc(port: u16, rack: u8, slot: u8) -> Plc {
    Plc {
        id: domain::local_configuration::id(),
        name: "DS owned loopback".into(),
        enabled: true,
        host: "127.0.0.1".into(),
        port,
        rack,
        slot,
        connect_timeout_ms: 1000,
        io_timeout_ms: 500,
        deadline_ms: 5000,
    }
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    if (a.len() != 3 && a.len() != 5) || a[1] != "--run-root" {
        println!("ds-s7-daa-client --run-root <owned-run-path> [--case D02]");
        return;
    }
    let root = std::path::Path::new(&a[2]);
    if !root.is_absolute() || !root.is_dir() {
        std::process::exit(2);
    }
    if a.len() == 5 {
        if a[3] != "--case" || a[4] != "D02" {
            std::process::exit(2);
        }
        for (port, rack, slot) in [(30102, 0, 2), (30103, 0, 1), (30104, 0, 1), (30102, 1, 1)] {
            for trial in 0..3 {
                let mut c = ManagedS7::new();
                let result = c.connect(&plc(port, rack, slot));
                println!(
                    "{}",
                    serde_json::json!({"event":"negative_connect","port":port,"rack":rack,"slot":slot,"trial":trial,"rejected":result.is_err(),"error":result.err()})
                );
                c.disconnect();
                if c.connected() {
                    std::process::exit(1);
                }
            }
        }
        return;
    }
    let mut clients = Vec::new();
    for (port, slot) in [(30102, 1), (30103, 2)] {
        let p = plc(port, 0, slot);
        let mut c = ManagedS7::new();
        if let Err(e) = c.connect(&p) {
            println!(
                "{}",
                serde_json::json!({"event":"connect_failed","port":port,"error":e})
            );
            std::process::exit(1);
        }
        println!(
            "{}",
            serde_json::json!({"event":"connect_complete","port":port,"rack":0,"slot":slot,"connected":c.connected(),"connect_timeout_ms":1000,"io_timeout_ms":500,"deadline_ms":5000,"driver":true,"local_validation":false})
        );
        clients.push(c);
    }
    let start = Instant::now();
    for round in 0..60 {
        for (i, c) in clients.iter_mut().enumerate() {
            for (db, result) in [
                (57, c.read(57, 0, 64)),
                (41, c.read_bounded(41, 512, 8, Duration::from_millis(400))),
            ] {
                match result {
                    Ok(bytes) => println!(
                        "{}",
                        serde_json::json!({"event":"read_complete","round":round,"instance":i,"db":db,"bytes":bytes})
                    ),
                    Err(e) => {
                        println!("{}", serde_json::json!({"event":"read_failed","error":e}));
                        std::process::exit(1);
                    }
                }
            }
        }
        thread::sleep(Duration::from_secs(round + 1).saturating_sub(start.elapsed()));
    }
    for c in &mut clients {
        c.disconnect();
    }
}
