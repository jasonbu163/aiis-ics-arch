//! FF-001 r1 候选 native 驱动有限预检；真实子进程 server、透明 TPKT proxy。
mod silent;
use rust_snap7::{AreaCode, InternalParam as P, InternalParamValue as V, S7Client, S7Server};
use std::{
    io::{BufRead, BufReader, Read, Write},
    net::{TcpListener, TcpStream},
    process::{Command, Stdio},
    sync::{
        atomic::{AtomicUsize, Ordering},
        Arc,
    },
    thread,
    time::{Duration, Instant},
};
fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect()
}
fn frame(s: &mut TcpStream) -> std::io::Result<Vec<u8>> {
    let mut h = [0; 4];
    s.read_exact(&mut h)?;
    assert_eq!(h[..2], [3, 0]);
    let n = u16::from_be_bytes([h[2], h[3]]) as usize;
    assert!((4..=4096).contains(&n));
    let mut b = vec![0; n];
    b[..4].copy_from_slice(&h);
    s.read_exact(&mut b[4..])?;
    Ok(b)
}
fn server() {
    let mut memory = [0xa5u8; 16];
    let server = S7Server::create();
    server.set_param(P::LocalPort, V::U16(31103)).unwrap();
    server
        .register_area(AreaCode::S7AreaDB, 1, &mut memory)
        .unwrap();
    server.start_to("127.0.0.1").unwrap();
    println!("ready");
    std::io::stdout().flush().unwrap();
    let mut command = String::new();
    std::io::stdin().read_line(&mut command).unwrap();
    assert_eq!(command.trim(), "stop");
    server.stop().unwrap();
    drop(server); // native 已销毁后才读/释放注册buffer。
    println!("{{\"native_server_memory_hex\":\"{}\"}}", hex(&memory));
}
fn native(mode: &str) {
    let listener = TcpListener::bind("127.0.0.1:31102").expect("proxy port conflict");
    drop(TcpListener::bind("127.0.0.1:31103").expect("native port conflict"));
    let mut child = Command::new(std::env::current_exe().unwrap())
        .arg("server")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .unwrap();
    let mut childout = BufReader::new(child.stdout.take().unwrap());
    let mut ready = String::new();
    childout.read_line(&mut ready).unwrap();
    assert_eq!(ready.trim(), "ready");
    let writes = Arc::new(AtomicUsize::new(0));
    let w = writes.clone();
    let mode_owned = mode.to_owned();
    let proxy = thread::spawn(move || {
        let (mut front, _) = listener.accept().unwrap();
        let mut back = TcpStream::connect("127.0.0.1:31103").unwrap();
        front
            .set_read_timeout(Some(Duration::from_secs(10)))
            .unwrap();
        back.set_read_timeout(Some(Duration::from_secs(10)))
            .unwrap();
        let mut ack = String::new();
        loop {
            let request = match frame(&mut front) {
                Ok(x) => x,
                Err(e)
                    if matches!(
                        e.kind(),
                        std::io::ErrorKind::UnexpectedEof | std::io::ErrorKind::ConnectionReset
                    ) =>
                {
                    break
                }
                Err(e) => panic!("{e}"),
            };
            back.write_all(&request).unwrap();
            let response = frame(&mut back).unwrap();
            let job = request.get(7..9) == Some(&[0x32, 1]);
            let is_write = job && request.get(17) == Some(&5);
            let is_read = job && request.get(17) == Some(&4);
            if is_write {
                w.fetch_add(1, Ordering::SeqCst);
                assert_eq!(&request[11..13], &response[11..13]);
                ack = format!(
                    "pdu_ref={} header_error={} status={}",
                    hex(&response[11..13]),
                    hex(&response[17..19]),
                    hex(&response[response.len() - 1..])
                );
            }
            let split = ((mode_owned == "native_split" || mode_owned == "native_split_budgeted")
                && is_write)
                || (mode_owned == "native_read_split" && is_read);
            if split {
                thread::sleep(Duration::from_secs(3));
                if front.write_all(&response[..7]).is_err() {
                    break;
                }
                thread::sleep(Duration::from_secs(3));
                if front.write_all(&response[7..]).is_err() {
                    break;
                }
            } else {
                front.write_all(&response).unwrap();
            }
        }
        ack
    });
    let client = S7Client::create();
    client.set_param(P::RemotePort, V::U16(31102)).unwrap();
    for p in [P::PingTimeout, P::SendTimeout, P::RecvTimeout] {
        client.set_param(p, V::I32(3000)).unwrap();
    }
    let start = Instant::now();
    client.connect_to("127.0.0.1", 0, 1).unwrap();
    let connect_ms = start.elapsed().as_millis();
    let native_io_param_ms = if mode == "native_split_budgeted" {
        10
    } else {
        5000
    };
    for p in [P::SendTimeout, P::RecvTimeout] {
        client.set_param(p, V::I32(native_io_param_ms)).unwrap();
    }
    let mut bytes = 42i16.to_be_bytes();
    let start = Instant::now();
    let written = client.db_write(1, 4, 2, &mut bytes);
    let write_ms = start.elapsed().as_millis();
    let mut observed = [0; 16];
    let start = Instant::now();
    let read = client.db_read(1, 0, 16, &mut observed);
    let read_ms = start.elapsed().as_millis();
    client.disconnect().unwrap();
    drop(client);
    let ack = proxy.join().unwrap();
    child.stdin.as_mut().unwrap().write_all(b"stop\n").unwrap();
    drop(child.stdin.take());
    let status = child.wait().unwrap();
    let mut server_result = String::new();
    childout.read_to_string(&mut server_result).unwrap();
    for p in [31102, 31103] {
        drop(TcpListener::bind(("127.0.0.1", p)).expect("port not released"));
    }
    println!("{{\"package\":\"rust-snap7\",\"version\":\"1.142.2\",\"probe_mode\":\"{mode}\",\"connect_elapsed_ms\":{connect_ms},\"write_elapsed_ms\":{write_ms},\"read_elapsed_ms\":{read_ms},\"write_success\":{},\"read_success\":{},\"write_requests\":{},\"protocol_ack\":\"{ack}\",\"read_hex\":\"{}\",\"native_server_exitcode\":{},\"proxy_joined\":true,\"ports_released\":[31102,31103]}}",written.is_ok(),read.is_ok(),writes.load(Ordering::SeqCst),hex(&observed),status.code().unwrap_or(-1));
    print!("{server_result}");
    assert!(status.success() && writes.load(Ordering::SeqCst) == 1);
    if mode == "native_split_budgeted" {
        assert!(written.is_err() && write_ms <= 5500);
        return; // 只观察这一条分段路径及时失败，不声称Purge等错误路径已被约束。
    }
    assert!(written.is_ok() && read.is_ok());
    assert_eq!(hex(&observed), "a5a5a5a5002aa5a5a5a5a5a5a5a5a5a5");
    assert!(
        connect_ms <= 3500 && write_ms <= 5500 && read_ms <= 5500,
        "R04 native total driver budget violated"
    );
}
fn main() {
    let mode = std::env::args().nth(1).unwrap_or_else(|| "silent".into());
    match mode.as_str() {
        "server" => server(),
        "silent" => silent::run(),
        "native_standard" | "native_split" | "native_split_budgeted" | "native_read_split" => {
            native(&mode)
        }
        _ => panic!("unknown preflight mode"),
    }
}
