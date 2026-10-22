//! required-features测试宿主；唯一产品App/owner，裸入口仅帮助，无默认输入/监听。
use ds_runtime::{
    app::App,
    domain::request::{Request, Source},
    infrastructure::{clock, logging, native_ffi},
    testing::hooks::{self, Manifest},
};
use serde_json::{json, Value};
use std::{
    io::{self, BufRead, Read},
    path::Path,
};
fn main() {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let result = match args.as_slice() {
        [probe] if probe == "--probe" => probe_abi(),
        [flag, path] if flag == "--ds-test-manifest" => run(Path::new(path)),
        [] => {
            println!(
                "ds-test-host --probe | --ds-test-manifest <owned absolute manifest> (test-only)"
            );
            Ok(())
        }
        _ => Err("test_arguments".into()),
    };
    if let Err(error) = result {
        eprintln!("{}", json!({"event":"test_host_failed","errorCode":error}));
        std::process::exit(1)
    }
}
fn probe_abi() -> Result<(), String> {
    let abi = native_ffi::probe()?;
    let clock = native_ffi::clock_samples()?;
    println!(
        "{}",
        json!({"abi":abi,"clock":clock,"descriptor_size":std::mem::size_of::<native_ffi::Descriptor>(),"owner_job_size":std::mem::size_of::<ds_runtime::services::owner::Job>(),"connection_size":std::mem::size_of::<ds_runtime::services::lifecycle::Connection>()})
    );
    Ok(())
}
fn run(path: &Path) -> Result<(), String> {
    let manifest = Manifest::read(path)?;
    if manifest.scenario.is_some() {
        return Err("protocol_host_scenario".into());
    }
    let app = App::open(&manifest.profile_dir)?;
    let sink = logging::start_sink(app.events.clone(), &manifest.profile_dir)?;
    if let Some(workspace) = manifest.workspace {
        let bytes = std::fs::read(workspace).map_err(|_| "test_workspace_read")?;
        if bytes.len() > 16 * 1024 * 1024 {
            return Err("test_workspace_capacity".into());
        }
        hooks::prepare_workspace(
            &app,
            serde_json::from_slice(&bytes).map_err(|_| "test_workspace_format")?,
        )?;
    }
    let aliases = app
        .configuration
        .get()?
        .workspace
        .instances
        .into_iter()
        .map(|i| (i.name, i.id))
        .collect::<std::collections::BTreeMap<_, _>>();
    let budgets=app.instances.lock().unwrap().values().map(|instance|{let mut budget=instance.context.owner.test_budget();let transport=instance.context.transport.lock().unwrap();budget["connectionBaseCharge"]=transport.base.into();budget["nativeFixedCharge"]=transport.fixed.into();budget["protocolByteCaps"]=json!(transport.budgets);budget["wholePduReservation"]=json!({"retainedS7Input":480,"descriptors":4*64,"typedStageTotal":480,"extraPayloadCopiesTotal":480,"worstResponseFrame":512,"total":2208});budget}).collect::<Vec<_>>();
    app.events.put(json!({"event":"baseline_budget","instances":budgets,"threadAdmissionFormula":"host fixed + actual owners + 2 active listeners/reapers + tcp <= 64","hostFixedThreads":app.global.lock().unwrap().fixed_threads,"threadLimit":64,"coreBytesLimit":512*1024*1024}));
    app.events.put(json!({"event":"ready_stopped","pid":std::process::id(),"profile_id":"ds-product-protocol-v1","sourceCandidate":manifest.source_candidate,"aliases":aliases,"anchor_monotonic_ns":clock::ns(),"anchor_wall_unix_ns":std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()}));
    let mut reader = io::stdin().lock();
    let mut ticket = 0;
    loop {
        let mut line = Vec::new();
        let n = reader
            .by_ref()
            .take(2049)
            .read_until(b'\n', &mut line)
            .map_err(|_| "test_stdin_read")?;
        if n == 0 {
            break;
        }
        if n > 2048 || line.last() != Some(&b'\n') {
            return Err("test_stdin_capacity".into());
        }
        let text = std::str::from_utf8(&line).map_err(|_| "test_stdin_utf8")?;
        let words = text.split_whitespace().collect::<Vec<_>>();
        if words.is_empty() {
            continue;
        }
        if words[0] == "quit" {
            break;
        }
        let name = words.get(1).copied().unwrap_or("A");
        let Some(id) = aliases.get(name) else {
            return Err("test_instance_alias".into());
        };
        let instance = app.instance(id)?;
        let owner = &instance.context.owner;
        let arg = words
            .get(2)
            .and_then(|s| s.parse::<u64>().ok())
            .unwrap_or(0);
        let mut data = json!({});
        let ok = match words[0] {
            "start" => instance.start(),
            "stop" => instance.stop(),
            "close" => instance.close(arg),
            "snapshot" => {
                data = owner.test_snapshot();
                for (k, v) in instance.context.snapshot().as_object().unwrap() {
                    data[k] = v.clone()
                }
                if let Some(rows) = data["connections"].as_array_mut() {
                    for row in rows {
                        for key in [
                            "connection",
                            "accepted_ns",
                            "established_ns",
                            "last_receive_complete_ns",
                            "last_send_complete_ns",
                        ] {
                            if let Some(number) =
                                row[key].as_str().and_then(|s| s.parse::<u64>().ok())
                            {
                                row[key] = number.into();
                            }
                        }
                    }
                }
                true
            }
            "reconfigure" => hooks::reconfigure(&app, id).is_ok(),
            "maintenance" => hooks::maintenance(&app, id, arg != 0).is_ok(),
            "budget" => {
                let limits = words
                    .iter()
                    .skip(2)
                    .map(|s| s.parse::<usize>())
                    .collect::<Result<Vec<_>, _>>();
                if let Ok(limits) = limits {
                    if limits.len() == 3 {
                        instance.budget(limits[0], limits[1], limits[2]);
                        true
                    } else {
                        false
                    }
                } else {
                    false
                }
            }
            "overlay" => owner.test_overlay(arg != 0),
            "write" => write(&instance, &words, &mut data),
            "ping" | "measurement_begin" | "measurement_end" => {
                let phase = words.get(2).copied().unwrap_or("");
                data = json!({"phase":phase,"clock_ns":clock::ns(),"begin_ns":owner.test_snapshot()["next_tick_ns"]});
                app.events.put(
                    json!({"event":words[0],"instance":id,"phase":phase,"clock_ns":clock::ns()}),
                );
                true
            }
            "pause" | "resume" | "barrier" | "release" => owner.control(words[0], arg),
            "reset" => instance.stopped() && owner.control("reset", 0),
            _ => false,
        };
        ticket += 1;
        let mut receipt = json!({"event":"control_result","ticket":ticket,"request_id":ticket,"command":words[0],"instance":id,"ok":ok});
        for (k, v) in data.as_object().unwrap() {
            receipt[k] = v.clone()
        }
        app.events.put(receipt);
    }
    let clean = app.shutdown();
    app.events.put(
        json!({"event":"process_close","clean":clean,"observability":app.events.query(0,0,None)}),
    );
    sink.stop();
    if clean {
        Ok(())
    } else {
        Err("test_shutdown_pending".into())
    }
}
fn write(
    instance: &ds_runtime::services::lifecycle::Instance,
    words: &[&str],
    out: &mut Value,
) -> bool {
    if words.len() != 9 {
        return false;
    }
    let Some(source) = words[2].parse().ok().and_then(Source::from_i32) else {
        return false;
    };
    if source == Source::Read {
        return false;
    }
    let Ok(start) = words[3].parse::<usize>() else {
        return false;
    };
    let Ok(bit) = words[4].parse::<i32>() else {
        return false;
    };
    if !(-1..=7).contains(&bit) {
        return false;
    }
    let bytes = words[5];
    if !bytes.is_ascii() || bytes.len() % 2 != 0 || bytes.len() > 512 {
        return false;
    }
    let (mut epoch, mut revision, mut cas) = (0, 0, 0);
    for (target, value) in [
        (&mut epoch, words[6]),
        (&mut revision, words[7]),
        (&mut cas, words[8]),
    ] {
        let Ok(number) = value.parse() else {
            return false;
        };
        *target = number;
    }
    let mut request = Request {
        source,
        db: 41,
        start,
        bit: (bit >= 0).then_some(bit as u8),
        size: bytes.len() / 2,
        epoch,
        revision,
        cas,
        ..Request::default()
    };
    for (index, pair) in bytes.as_bytes().chunks(2).enumerate() {
        let Ok(value) = u8::from_str_radix(std::str::from_utf8(pair).unwrap(), 16) else {
            return false;
        };
        request.data[index] = value;
    }
    let result = instance.context.owner.call(request);
    *out = json!({"seq":result.seq});
    result.ok
}
