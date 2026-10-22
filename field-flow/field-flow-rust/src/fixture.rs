//! 文件：src/fixture.rs；仅test-fixture编译的本项目loopback HTTP/透明TPKT夹具。
use crate::{domain::now_ms, Result};
use serde_json::{json, Value};
use std::{
    io::{BufRead, BufReader, Read, Write},
    net::{Shutdown, TcpListener, TcpStream},
    process::{Child, Command, Stdio},
    sync::{
        atomic::{AtomicBool, AtomicU64, Ordering},
        Arc, Mutex,
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};
#[derive(Clone)]
pub struct Behavior {
    pub body: Vec<u8>,
    pub status: u16,
    pub content_type: String,
    pub delay_ms: u64,
    pub fault: String,
}
impl Default for Behavior {
    fn default() -> Self {
        Self{body:serde_json::to_vec(&json!({"schema_version":1,"source_id":"demo01-feed","ready":false,"command_id":null,"value":null,"issued_at_ms":null,"expires_at_ms":null})).unwrap(),status:200,content_type:"application/json".into(),delay_ms:0,fault:String::new()}
    }
}
#[derive(Default)]
pub struct Counters {
    pub gets: AtomicU64,
    pub sessions: AtomicU64,
    pub writes: AtomicU64,
    pub reads: AtomicU64,
    pub applied: AtomicU64,
    pub trace: Mutex<Vec<Value>>,
}
pub struct Fixture {
    pub behavior: Arc<Mutex<Behavior>>,
    pub counts: Arc<Counters>,
    stop: Arc<AtomicBool>,
    sockets: Arc<Mutex<Vec<TcpStream>>>,
    threads: Vec<JoinHandle<()>>,
    child: Option<Child>,
    pub native_pid: u32,
}
fn frame(s: &mut TcpStream) -> std::io::Result<Vec<u8>> {
    let mut h = [0; 4];
    s.read_exact(&mut h)?;
    let n = u16::from_be_bytes([h[2], h[3]]) as usize;
    if h[..2] != [3, 0] || !(4..=4096).contains(&n) {
        return Err(std::io::ErrorKind::InvalidData.into());
    }
    let mut b = vec![0; n];
    b[..4].copy_from_slice(&h);
    s.read_exact(&mut b[4..])?;
    Ok(b)
}
fn pause(stop: &AtomicBool, ms: u64) -> bool {
    let end = Instant::now() + Duration::from_millis(ms);
    while Instant::now() < end {
        if stop.load(Ordering::Acquire) {
            return false;
        }
        thread::sleep(Duration::from_millis(5));
    }
    true
}
fn record(c: &Counters, v: Value) {
    let mut t = c.trace.lock().unwrap();
    if t.len() < 2000 {
        t.push(v);
    }
}
impl Fixture {
    pub fn start(executable: &std::path::Path) -> Result<Self> {
        let proxy = TcpListener::bind("127.0.0.1:31102").map_err(|_| "fixture_port_conflict")?;
        let http = TcpListener::bind("127.0.0.1:31880").map_err(|_| "fixture_port_conflict")?;
        drop(TcpListener::bind("127.0.0.1:31103").map_err(|_| "fixture_port_conflict")?);
        let mut child = Command::new(executable)
            .arg("__native_fixture")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|_| "fixture_spawn")?;
        let native_pid = child.id();
        let mut out = BufReader::new(child.stdout.take().ok_or("fixture_output")?);
        let mut line = String::new();
        out.read_line(&mut line).map_err(|_| "fixture_ready")?;
        if line.trim() != "ready" {
            return Err("fixture_ready".into());
        }
        let behavior = Arc::new(Mutex::new(Behavior::default()));
        let counts = Arc::new(Counters::default());
        let stop = Arc::new(AtomicBool::new(false));
        let sockets = Arc::new(Mutex::new(Vec::new()));
        let mut threads = Vec::new();
        for (listener, is_http) in [(proxy, false), (http, true)] {
            listener
                .set_nonblocking(true)
                .map_err(|_| "fixture_listener")?;
            let b = behavior.clone();
            let c = counts.clone();
            let s = stop.clone();
            let sockets = sockets.clone();
            threads.push(thread::spawn(move||{let mut clients=Vec::new();while !s.load(Ordering::Acquire){match listener.accept(){Ok((mut front,_))=>{front.set_nonblocking(false).unwrap();front.set_read_timeout(Some(Duration::from_secs(10))).unwrap();front.set_write_timeout(Some(Duration::from_secs(1))).unwrap();sockets.lock().unwrap().push(front.try_clone().unwrap());let b=b.clone();let c=c.clone();let s=s.clone();let sockets=sockets.clone();clients.push(thread::spawn(move||{
   if is_http {let mut bytes=Vec::new();let mut one=[0];while bytes.len()<4096&&front.read_exact(&mut one).is_ok(){bytes.push(one[0]);if bytes.ends_with(b"\r\n\r\n"){break}}
    c.gets.fetch_add(1,Ordering::SeqCst);let behavior=b.lock().unwrap().clone();if !pause(&s,behavior.delay_ms){return}let header=format!("HTTP/1.1 {} synthetic\r\nContent-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",behavior.status,behavior.content_type,behavior.body.len());let _=front.write_all(header.as_bytes()).and_then(|_|front.write_all(&behavior.body));return;
   }
   c.sessions.fetch_add(1,Ordering::SeqCst);let Ok(mut back)=TcpStream::connect("127.0.0.1:31103")else{return};back.set_read_timeout(Some(Duration::from_secs(10))).unwrap();back.set_write_timeout(Some(Duration::from_secs(1))).unwrap();sockets.lock().unwrap().push(back.try_clone().unwrap());
   let mut last_read_ref=None;let mut last_write_ref=None;
   while let Ok(request)=frame(&mut front){let fault=b.lock().unwrap().fault.clone();let job=request.get(7..9)==Some(&[0x32,1]);let op=if job{request.get(17).copied().unwrap_or(0)}else{0};if fault=="silent_cotp"&&op==0{while pause(&s,50){}break}
    if fault=="disconnect" {break}
    if back.write_all(&request).is_err(){break}let Ok(response)=frame(&mut back)else{break};
    if op==5 {c.writes.fetch_add(1,Ordering::SeqCst);if response.last()==Some(&0xff){c.applied.fetch_add(1,Ordering::SeqCst);}}
    if op==4 {c.reads.fetch_add(1,Ordering::SeqCst);}
    record(&c,json!({"at_ms":now_ms(),"operation":op,"request_ref":request.get(11..13),"response_ref":response.get(11..13),"positive":response.last()==Some(&0xff),"request_hex":request.iter().map(|b|format!("{b:02x}")).collect::<String>(),"original_response_hex":response.iter().map(|b|format!("{b:02x}")).collect::<String>(),"sent_response_hex":if matches!(fault.as_str(),"stale_once"|"short_ack"){None}else{Some(response.iter().map(|b|format!("{b:02x}")).collect::<String>())}}));
    let previous_same_ref=if op==4{last_read_ref}else{last_write_ref};let previous_other_ref=if op==4{last_write_ref}else{last_read_ref};if op==4{last_read_ref=Some([request[11],request[12]]);}if op==5{last_write_ref=Some([request[11],request[12]]);}
    if fault.starts_with("corrupt:")&&(op==4||op==5){let field=&fault[8..];let mut sent=response.clone();match field{
      "id"=>sent[7]^=1,"rosctr"=>sent[8]^=1,"reserved0"=>sent[9]=1,"reserved1"=>sent[10]=1,"ref0"=>sent[11]^=1,"ref1"|"follow_correct"=>sent[12]=sent[12].wrapping_add(1),"oldref"=>{let Some(prior)=previous_same_ref else{break};sent[11..13].copy_from_slice(&prior);},"otherref"=>{let Some(prior)=previous_other_ref else{break};sent[11..13].copy_from_slice(&prior);},
      "global0"=>sent[17]=1,"global1"=>sent[18]=1,"function"=>sent[19]=if op==4{5}else{4},"count"=>sent[20]=2,"item"=>sent[21]=0,"param_length"=>sent[14]=3,"data_length"=>sent[16]=0,
      "transport"=>sent[22]=5,"bits"=>sent[24]=8,"short_header"=>sent.truncate(15),"short_data"=>{sent.pop();},"empty"=>sent.truncate(7),"extra"=>sent.push(0),"payload4096"=>sent.resize(4103,0),"payload4097"=>sent.resize(4104,0),_=>break
    }let length=sent.len()as u16;sent[2..4].copy_from_slice(&length.to_be_bytes());record(&c,json!({"event":"corrupt_response_sent","fault":field,"operation":op,"previous_same_ref":previous_same_ref,"previous_other_ref":previous_other_ref,"request_hex":request.iter().map(|b|format!("{b:02x}")).collect::<String>(),"original_response_hex":response.iter().map(|b|format!("{b:02x}")).collect::<String>(),"sent_response_hex":sent.iter().map(|b|format!("{b:02x}")).collect::<String>()}));if front.write_all(&sent).is_err(){break}if field=="follow_correct"{if !pause(&s,20){break}let _=front.write_all(&response);}continue;}
    if fault=="short_ack"&&(op==4||op==5) {let mut short=response[..17].to_vec();let length=short.len()as u16;short[2..4].copy_from_slice(&length.to_be_bytes());record(&c,json!({"event":"short_response_sent","operation":op,"request_hex":request.iter().map(|b|format!("{b:02x}")).collect::<String>(),"original_response_hex":response.iter().map(|b|format!("{b:02x}")).collect::<String>(),"sent_response_hex":short.iter().map(|b|format!("{b:02x}")).collect::<String>()}));if front.write_all(&short).is_err(){break}continue;}
    if fault=="stale_once"&&(op==4||op==5) {let mut unmatched=response.clone();unmatched[12]=unmatched[12].wrapping_add(1);record(&c,json!({"event":"unmatched_response_sent","operation":op,"request_pdu_ref":request[11..13].to_vec(),"original_response_pdu_ref":response[11..13].to_vec(),"sent_response_pdu_ref":unmatched[11..13].to_vec(),"changed_absolute_tpkt_index":12,"request_hex":request.iter().map(|b|format!("{b:02x}")).collect::<String>(),"original_response_hex":response.iter().map(|b|format!("{b:02x}")).collect::<String>(),"sent_response_hex":unmatched.iter().map(|b|format!("{b:02x}")).collect::<String>()}));if front.write_all(&unmatched).is_err(){break}continue;}
    if fault=="delay600"&&(op==4||op==5)&&!pause(&s,600){break}
    if op==5&&fault=="hold_ack" {while !s.load(Ordering::Acquire)&&b.lock().unwrap().fault=="hold_ack"{thread::sleep(Duration::from_millis(5));}break}
    if matches!(fault.as_str(),"split"|"slow"|"stale")&&(op==4||op==5){
     if fault=="stale"{let mut old=response.clone();if old.len()>12{old[12]=old[12].wrapping_add(1)}for _ in 0..100{if !pause(&s,70)||front.write_all(&old).is_err(){break}}break}
     if fault=="slow"{for byte in response {if !pause(&s,300)||front.write_all(&[byte]).is_err(){break}}break}
     if !pause(&s,3000)||front.write_all(&response[..7]).is_err(){break}if !pause(&s,3000)||front.write_all(&response[7..]).is_err(){break}
    }else if front.write_all(&response).is_err(){break}
   }
   let _=front.shutdown(Shutdown::Both);let _=back.shutdown(Shutdown::Both);
  }));},Err(e)if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(5)),Err(_)=>break}}
  for t in clients {t.join().unwrap();}
 }));
        }
        Ok(Self {
            behavior,
            counts,
            stop,
            sockets,
            threads,
            child: Some(child),
            native_pid,
        })
    }
    pub fn command(&self, id: &str, value: Value) {
        let now = now_ms();
        self.body(json!({"schema_version":1,"source_id":"demo01-feed","ready":true,"command_id":id,"value":value,"issued_at_ms":now,"expires_at_ms":now+60000}));
    }
    pub fn body(&self, value: Value) {
        self.behavior.lock().unwrap().body = serde_json::to_vec(&value).unwrap();
    }
    pub fn fault(&self, value: &str) {
        self.behavior.lock().unwrap().fault = value.into();
    }
    pub fn disconnect(&self) {
        for socket in self.sockets.lock().unwrap().drain(..) {
            let _ = socket.shutdown(Shutdown::Both);
        }
    }
    pub fn snapshot(&self) -> Value {
        json!({"gets":self.counts.gets.load(Ordering::SeqCst),"sessions":self.counts.sessions.load(Ordering::SeqCst),"writes":self.counts.writes.load(Ordering::SeqCst),"reads":self.counts.reads.load(Ordering::SeqCst),"applied":self.counts.applied.load(Ordering::SeqCst),"native_pid":self.native_pid,"trace":self.counts.trace.lock().unwrap().clone()})
    }
    pub fn close(&mut self) -> Result<()> {
        self.stop.store(true, Ordering::Release);
        self.disconnect();
        for t in self.threads.drain(..) {
            t.join().map_err(|_| "fixture_join")?;
        }
        if let Some(mut c) = self.child.take() {
            c.stdin
                .as_mut()
                .ok_or("fixture_stdin")?
                .write_all(b"stop\n")
                .map_err(|_| "fixture_stop")?;
            drop(c.stdin.take());
            let end = Instant::now() + Duration::from_secs(5);
            loop {
                if let Some(status) = c.try_wait().map_err(|_| "fixture_wait")? {
                    if !status.success() {
                        return Err("fixture_exit".into());
                    }
                    break;
                }
                if Instant::now() >= end {
                    c.kill().map_err(|_| "fixture_cleanup")?;
                    c.wait().map_err(|_| "fixture_wait")?;
                    return Err("fixture_forced_cleanup".into());
                }
                thread::sleep(Duration::from_millis(10));
            }
        }
        for port in [31102, 31103, 31880] {
            drop(TcpListener::bind(("127.0.0.1", port)).map_err(|_| "fixture_port_release")?);
        }
        Ok(())
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        if self.child.is_some() {
            let _ = self.close();
        }
    }
}
pub fn native_server() -> Result<()> {
    use rust_snap7::{AreaCode, InternalParam as P, InternalParamValue as V, S7Server};
    let mut memory = [0xa5u8; 16];
    let server = S7Server::create();
    server
        .set_param(P::LocalPort, V::U16(31103))
        .map_err(|_| "fixture_server")?;
    server
        .register_area(AreaCode::S7AreaDB, 1, &mut memory)
        .map_err(|_| "fixture_memory")?;
    server.start_to("127.0.0.1").map_err(|_| "fixture_server")?;
    println!("ready");
    std::io::stdout().flush().map_err(|_| "fixture_ready")?;
    let mut line = String::new();
    std::io::stdin()
        .read_line(&mut line)
        .map_err(|_| "fixture_stdin")?;
    server.stop().map_err(|_| "fixture_stop")?;
    drop(server);
    std::hint::black_box(memory);
    Ok(())
}
