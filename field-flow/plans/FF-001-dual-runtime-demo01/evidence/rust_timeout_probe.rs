//! FF-001 r1 候选 native 驱动预检；不属于可交付 runtime。
use rust_snap7::{InternalParam as P, InternalParamValue as V, S7Client};
use std::{io::Read, net::TcpListener, thread, time::{Duration, Instant}};
fn main() {
    let listener = TcpListener::bind("127.0.0.1:31102").expect("fixed port conflict");
    let peer = thread::spawn(move || {
        let (mut socket, _) = listener.accept().unwrap();
        socket.set_read_timeout(Some(Duration::from_secs(4))).unwrap();
        let mut b = [0; 1024];
        let n = socket.read(&mut b).unwrap();
        thread::sleep(Duration::from_millis(1200));
        n
    });
    let client = S7Client::create();
    client.set_param(P::RemotePort, V::U16(31102)).unwrap();
    for param in [P::PingTimeout, P::SendTimeout, P::RecvTimeout] {
        client.set_param(param, V::I32(500)).unwrap();
    }
    let start = Instant::now();
    let result = client.connect_to("127.0.0.1", 0, 1);
    let elapsed = start.elapsed().as_millis();
    client.disconnect().unwrap();
    let bytes = peer.join().unwrap();
    TcpListener::bind("127.0.0.1:31102").expect("port not released");
    println!("{{\"package\":\"rust-snap7\",\"version\":\"1.142.2\",\"configured_ms\":500,\"connect_elapsed_ms\":{elapsed},\"result_is_error\":{},\"cotp_request_bytes\":{bytes},\"peer_thread_joined\":true,\"port_released\":true}}", result.is_err());
    assert!(result.is_err() && elapsed <= 3500);
}
