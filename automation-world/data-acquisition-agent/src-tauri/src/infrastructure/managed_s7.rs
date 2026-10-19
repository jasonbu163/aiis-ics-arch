//! 单actor拥有的持久S7客户端；RemotePort和socket超时显式设置，无短连接/最小驱动回退。
use crate::domain::local_configuration::{LocalResult, Plc};
pub(crate) trait Transport {
    fn connect(&mut self, plc: &Plc) -> LocalResult<()>;
    fn read(&mut self, db: u16, start: u32, size: u32) -> LocalResult<Vec<u8>>;
    fn read_bounded(
        &mut self,
        db: u16,
        start: u32,
        size: u32,
        _remaining: std::time::Duration,
    ) -> LocalResult<Vec<u8>> {
        self.read(db, start, size)
    }
    fn disconnect(&mut self);
    fn connected(&self) -> bool;
}
pub(crate) struct ManagedS7 {
    #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
    client: rust_snap7::S7Client,
    connected: bool,
}
impl ManagedS7 {
    pub fn new() -> Self {
        Self {
            #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
            client: rust_snap7::S7Client::create(),
            connected: false,
        }
    }
}
impl Transport for ManagedS7 {
    fn connect(&mut self, p: &Plc) -> LocalResult<()> {
        #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
        {
            use rust_snap7::{InternalParam as P, InternalParamValue as V};
            for (k, v) in [
                (P::RemotePort, V::U16(p.port)),
                (P::PingTimeout, V::I32(p.connect_timeout_ms as i32)),
                (P::SendTimeout, V::I32(p.io_timeout_ms as i32)),
                (P::RecvTimeout, V::I32(p.io_timeout_ms as i32)),
            ] {
                self.client
                    .set_param(k, v)
                    .map_err(|_| "driver_parameter")?;
            }
            self.client
                .connect_to(&p.host, p.rack as i32, p.slot as i32)
                .map_err(|_| "connection_failed")?;
            self.connected = true;
            Ok(())
        }
        #[cfg(any(not(feature = "rust-snap7-driver"), feature = "local-validation"))]
        {
            let _ = p;
            Err("driver_unavailable".into())
        }
    }
    fn read(&mut self, db: u16, start: u32, size: u32) -> LocalResult<Vec<u8>> {
        #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
        {
            let mut bytes = vec![0; size as usize];
            self.client
                .db_read(db as i32, start as i32, size as i32, &mut bytes)
                .map_err(|_| "read_failed")?;
            Ok(bytes)
        }
        #[cfg(any(not(feature = "rust-snap7-driver"), feature = "local-validation"))]
        {
            let _ = (db, start, size);
            Err("driver_unavailable".into())
        }
    }
    fn read_bounded(
        &mut self,
        db: u16,
        start: u32,
        size: u32,
        remaining: std::time::Duration,
    ) -> LocalResult<Vec<u8>> {
        #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
        {
            use rust_snap7::{InternalParam as P, InternalParamValue as V};
            let ms = (remaining.as_millis() / 2).clamp(1, 500) as i32;
            self.client
                .set_param(P::SendTimeout, V::I32(ms))
                .map_err(|_| "driver_parameter")?;
            self.client
                .set_param(P::RecvTimeout, V::I32(ms))
                .map_err(|_| "driver_parameter")?;
        }
        #[cfg(any(not(feature = "rust-snap7-driver"), feature = "local-validation"))]
        let _ = remaining;
        self.read(db, start, size)
    }
    fn connected(&self) -> bool {
        #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
        {
            let mut value = 0;
            return self.connected && self.client.get_connected(&mut value).is_ok() && value != 0;
        }
        #[cfg(any(not(feature = "rust-snap7-driver"), feature = "local-validation"))]
        {
            self.connected
        }
    }
    fn disconnect(&mut self) {
        #[cfg(all(feature = "rust-snap7-driver", not(feature = "local-validation")))]
        {
            let _ = self.client.disconnect();
        }
        self.connected = false;
    }
}
impl Drop for ManagedS7 {
    fn drop(&mut self) {
        self.disconnect()
    }
}

#[cfg(all(test, feature = "rust-snap7-driver", not(feature = "local-validation")))]
mod tests {
    use super::*;
    use rust_snap7::{AreaCode, InternalParam as P, InternalParamValue as V, S7Server};
    use std::{
        net::TcpListener,
        time::{Duration, Instant},
    };
    fn plc(port: u16) -> Plc {
        Plc {
            id: crate::domain::local_configuration::id(),
            name: "Owned loopback".into(),
            enabled: true,
            host: "127.0.0.1".into(),
            port,
            rack: 0,
            slot: 1,
            connect_timeout_ms: 1000,
            io_timeout_ms: 500,
            deadline_ms: 5000,
        }
    }
    #[test]
    fn owned_remote_port_session_reuse_bad_db_and_disconnect() {
        let reservation = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let port = reservation.local_addr().unwrap().port();
        let server = S7Server::create();
        let mut bytes = [1u8, 2, 3, 4];
        server
            .register_area(AreaCode::S7AreaDB, 1, &mut bytes)
            .unwrap();
        server.set_param(P::LocalPort, V::U16(port)).unwrap();
        drop(reservation);
        server.start_to("127.0.0.1").unwrap();
        let mut client = ManagedS7::new();
        client.connect(&plc(port)).unwrap();
        assert_eq!(client.read(1, 0, 4).unwrap(), [1, 2, 3, 4]);
        assert_eq!(client.read(1, 1, 2).unwrap(), [2, 3]);
        assert!(client.read(99, 0, 2).is_err());
        assert!(
            client.connected(),
            "bad DB must not force transport reconnect"
        );
        let (mut state, mut cpu, mut clients) = (0, 0, 0);
        server
            .get_status(&mut state, &mut cpu, &mut clients)
            .unwrap();
        assert_eq!(clients, 1, "reads must reuse the same managed session");
        server.stop().unwrap();
        assert!(client.read(1, 0, 4).is_err());
        assert!(!client.connected());
        client.disconnect();
        println!("owned_loopback port={port} persistent_clients={clients} bad_db_kept_session=true disconnect_detected=true");
    }
    #[test]
    fn owned_blackhole_connection_timeout() {
        let listener = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        let thread = std::thread::spawn(move || {
            let (socket, _) = listener.accept().unwrap();
            std::thread::sleep(Duration::from_millis(1700));
            drop(socket);
        });
        let mut client = ManagedS7::new();
        let begin = Instant::now();
        assert!(client.connect(&plc(port)).is_err());
        let elapsed = begin.elapsed();
        assert!(elapsed < Duration::from_millis(1500), "{elapsed:?}");
        assert!(!client.connected());
        thread.join().unwrap();
        println!(
            "owned_blackhole port={port} connection_ms={}",
            elapsed.as_millis()
        );
    }
    #[test]
    fn owned_slow_read_obeys_remaining_socket_budget() {
        let reservation = TcpListener::bind(("127.0.0.1", 0)).unwrap();
        let port = reservation.local_addr().unwrap().port();
        let server = S7Server::create();
        server.set_param(P::LocalPort, V::U16(port)).unwrap();
        server
            .set_rw_area_callback(Some(|_, _, _, _, _| {
                std::thread::sleep(Duration::from_millis(1200));
            }))
            .unwrap();
        drop(reservation);
        server.start_to("127.0.0.1").unwrap();
        let mut client = ManagedS7::new();
        client.connect(&plc(port)).unwrap();
        let begin = Instant::now();
        let result = client.read_bounded(1, 0, 4, Duration::from_millis(400));
        let elapsed = begin.elapsed();
        assert!(result.is_err());
        assert!(
            elapsed >= Duration::from_millis(150) && elapsed < Duration::from_millis(700),
            "{elapsed:?}"
        );
        client.disconnect();
        server.stop().unwrap();
        println!(
            "owned_slow_read port={port} remaining_ms=400 actual_ms={}",
            elapsed.as_millis()
        );
    }
}
