// DS G0 native protocol/lifecycle bridge only. Rust owns every policy/image/queue/budget decision.
#include "ds_s7_bridge.h"
#include "s7_server.h"
#include <atomic>
#include <thread>
#include <mutex>
#include <time.h>
#include <cstddef>
#include <arpa/inet.h>
struct DsS7Server {
 DsS7Callbacks cb; void* user; DsS7Hooks hooks{}; TSnap7Server native;
 std::mutex stop_mutex; std::thread stopper; std::atomic<bool> stopping{false},done{true};
 std::atomic<int> stop_result{0};
};
static thread_local uint64_t token=0,conn=0,pdu=0;
static thread_local uint32_t item_index=0;
static thread_local DsS7Server* current=nullptr;
extern "C" uint64_t ds_s7_clock_ns(){timespec t{};if(clock_gettime(_CLOCK_MONOTONIC,&t))return 0;return uint64_t(t.tv_sec)*1000000000ULL+t.tv_nsec;}
static int S7API rw(void* u,int,int op,PS7Tag tag,void* data){
 try{auto s=static_cast<DsS7Server*>(u);if(current!=s||!tag||!data)return 1;
 int width=tag->WordLen==1||tag->WordLen==2?1:tag->WordLen==4||tag->WordLen==5?2:tag->WordLen==6||tag->WordLen==7||tag->WordLen==8?4:0;
 if(width==0||tag->Size<1||tag->Size>256/width)return 1;
 return s->cb.item(s->user,conn,pdu,item_index,op,reinterpret_cast<DsS7Tag*>(tag),data,uint32_t(tag->Size*width));
 }catch(...){return 1;}
}
extern "C" DsS7Server* ds_s7_create(const DsS7Callbacks* cb,void* user){try{
 if(!cb||cb->abi_version!=1||cb->struct_size!=sizeof(DsS7Callbacks)||!user)return nullptr;
 auto s=new DsS7Server;s->cb=*cb;s->user=user;s->hooks.user=s;
 s->hooks.reserve_accept=[](void* u){try{auto s=static_cast<DsS7Server*>(u);token=0;return s->cb.accept_reserve(s->user,&token)==0;}catch(...){return false;}};
 s->hooks.cancel_accept=[](void* u){try{auto s=static_cast<DsS7Server*>(u);s->cb.accept_cancel(s->user,token);token=0;}catch(...){}};
 s->hooks.accepted=[](void* u,int fd)->uint64_t{auto s=static_cast<DsS7Server*>(u);uint64_t id=0;if(s->cb.accepted(s->user,token,fd,&id)!=0)throw 1;token=0;return id;};
 s->hooks.active=[](void* u,uint64_t id){try{auto s=static_cast<DsS7Server*>(u);return s->cb.active(s->user,id)==0;}catch(...){return false;}};
 s->hooks.cotp=[](void* u,uint64_t id,const unsigned char* b,int n){try{auto s=static_cast<DsS7Server*>(u);return n>=0&&s->cb.cotp(s->user,id,b,n)==0;}catch(...){return false;}};
 s->hooks.setup=[](void* u,uint64_t id){try{auto s=static_cast<DsS7Server*>(u);return s->cb.setup(s->user,id)==0;}catch(...){return false;}};
 s->hooks.begin_pdu=[](void* u,uint64_t id,const unsigned char* b,int n){try{auto s=static_cast<DsS7Server*>(u);uint64_t pid=0;if(n<0||s->cb.begin_pdu(s->user,id,b,n,&pid))return false;current=s;conn=id;pdu=pid;item_index=0;return true;}catch(...){return false;}};
 s->hooks.end_pdu=[](void* u,uint64_t id){try{auto s=static_cast<DsS7Server*>(u);s->cb.end_pdu(s->user,id,pdu);current=nullptr;}catch(...){}};
 s->hooks.item=[](void*,uint64_t,int i){item_index=i;};
 s->hooks.closing=[](void* u,uint64_t id){try{auto s=static_cast<DsS7Server*>(u);s->cb.closing(s->user,id);}catch(...){}};
 s->hooks.joined=[](void* u,uint64_t id,int rc){try{auto s=static_cast<DsS7Server*>(u);s->cb.joined(s->user,id,rc);}catch(...){}};
 s->hooks.io=[](void* u,uint64_t id,int op,const void* b,int n,double start){try{auto s=static_cast<DsS7Server*>(u);s->cb.io(s->user,id,op,b,n<0?0:uint32_t(n),uint64_t(start*1e9));}catch(...){}};
 s->native.DsHooks=&s->hooks;s->native.WorkInterval=5;s->native.SetRWAreaCallBack(rw,s);return s;
 }catch(...){return nullptr;}}
extern "C" int ds_s7_start(DsS7Server* s,const char* host,int port){try{in_addr address{};if(!s||!host||port<1||port>65535||inet_pton(AF_INET,host,&address)!=1||(ntohl(address.s_addr)>>24)!=127||s->stopping)return 1;std::lock_guard<std::mutex> l(s->stop_mutex);if(s->stopper.joinable())s->stopper.join();word p=port;s->native.SetParam(1,&p);return s->native.StartTo(host);}catch(...){return 1;}}
extern "C" int ds_s7_request_stop(DsS7Server* s){try{if(!s)return 1;std::lock_guard<std::mutex> l(s->stop_mutex);if(s->stopping)return 0;if(s->stopper.joinable())s->stopper.join();s->stopping=true;s->done=false;s->stopper=std::thread([s]{try{s->native.Stop();s->stop_result=s->native.Status==SrvStopped?0:1;}catch(...){s->stop_result=1;}s->done=true;});return 0;}catch(...){return 1;}}
extern "C" int ds_s7_poll_stop(DsS7Server* s){try{if(!s)return -1;if(!s->stopping)return s->native.Status==SrvStopped?0:1;if(!s->done)return 1;std::lock_guard<std::mutex> l(s->stop_mutex);if(s->stopper.joinable())s->stopper.join();int rc=s->stop_result;s->stopping=false;return rc?-1:0;}catch(...){return -1;}}
extern "C" int ds_s7_close(DsS7Server* s,uint64_t id){try{if(!s)return 1;s->native.DsClose(id);return 0;}catch(...){return 1;}}
extern "C" int ds_s7_destroy(DsS7Server* s){try{if(!s||s->stopping||s->native.Status!=SrvStopped||s->stopper.joinable())return 1;delete s;return 0;}catch(...){return 1;}}
extern "C" int ds_s7_abi_probe(DsS7Abi* a,DsS7RWProbe cb,void* u){try{if(!a||!cb)return 1;*a={};a->version=1;a->tag_size=sizeof(TS7Tag);a->tag_align=alignof(TS7Tag);a->tag_offsets[0]=offsetof(TS7Tag,Area);a->tag_offsets[1]=offsetof(TS7Tag,DBNumber);a->tag_offsets[2]=offsetof(TS7Tag,Start);a->tag_offsets[3]=offsetof(TS7Tag,Size);a->tag_offsets[4]=offsetof(TS7Tag,WordLen);a->callbacks_size=sizeof(DsS7Callbacks);a->callbacks_align=alignof(DsS7Callbacks);a->callbacks_offsets[0]=offsetof(DsS7Callbacks,abi_version);a->callbacks_offsets[1]=offsetof(DsS7Callbacks,struct_size);a->callbacks_offsets[2]=offsetof(DsS7Callbacks,accept_reserve);a->callbacks_offsets[3]=offsetof(DsS7Callbacks,accept_cancel);a->callbacks_offsets[4]=offsetof(DsS7Callbacks,accepted);a->callbacks_offsets[5]=offsetof(DsS7Callbacks,active);a->callbacks_offsets[6]=offsetof(DsS7Callbacks,cotp);a->callbacks_offsets[7]=offsetof(DsS7Callbacks,setup);a->callbacks_offsets[8]=offsetof(DsS7Callbacks,begin_pdu);a->callbacks_offsets[9]=offsetof(DsS7Callbacks,item);a->callbacks_offsets[10]=offsetof(DsS7Callbacks,end_pdu);a->callbacks_offsets[11]=offsetof(DsS7Callbacks,closing);a->callbacks_offsets[12]=offsetof(DsS7Callbacks,joined);a->callbacks_offsets[13]=offsetof(DsS7Callbacks,io);a->worker_size=sizeof(TS7Worker);a->socket_size=sizeof(TMsgSocket);a->worker_thread_size=sizeof(TMsgWorkerThread);a->fixed_instance_bytes=sizeof(TSnap7Server)+1500*sizeof(TSrvEvent)+sizeof(TMsgEventQueue)+3*sizeof(TSnapCriticalSection)+sizeof(TMsgListenerThread)+sizeof(TMsgSocket)+sizeof(std::thread)+256+2048;DsS7Tag tag{0x84,41,512,1,2};unsigned char data=77;a->callback_zero=cb(u,0,0,&tag,&data);a->callback_nonzero=cb(u,0,37,&tag,&data);return 0;}catch(...){return 1;}}
