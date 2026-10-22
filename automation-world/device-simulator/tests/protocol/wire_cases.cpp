// DS协议回归 raw客户端只生成批准的有限向量；独立核S7结果，不复用server判断。
#include "wire_cases.hpp"
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdexcept>
#include <cstring>
namespace wire {
Bytes unhex(const std::string& s){if(s.size()%2)throw std::runtime_error("hex");Bytes b;for(size_t i=0;i<s.size();i+=2)b.push_back(std::stoul(s.substr(i,2),nullptr,16));return b;}
std::string hex(const Bytes& b){static const char* h="0123456789abcdef";std::string s;for(auto c:b){s+=h[c>>4];s+=h[c&15];}return s;}
Client::~Client(){close();}void Client::close(){if(fd>=0){::shutdown(fd,SHUT_RDWR);::close(fd);fd=-1;}}
void Client::fault(bool reset){if(fd>=0){if(reset){linger l{1,0};setsockopt(fd,SOL_SOCKET,SO_LINGER,&l,sizeof(l));}else ::shutdown(fd,SHUT_WR);::close(fd);fd=-1;}}
int Client::local_port() const{sockaddr_in local{};socklen_t n=sizeof(local);if(fd<0||getsockname(fd,reinterpret_cast<sockaddr*>(&local),&n))return 0;return ntohs(local.sin_port);}
Bytes Client::exchange(const Bytes& b){if(fd<0)return {};size_t n=0;while(n<b.size()){auto k=::send(fd,b.data()+n,b.size()-n,0);if(k<=0){close();return {};}n+=k;}Bytes result(4);n=0;while(n<4){auto k=recv(fd,result.data()+n,4-n,0);if(k<=0){close();return {};}n+=k;}int len=int(result[2])*256+result[3];if(len<4||len>512){close();return {};}result.resize(len);while(n<result.size()){auto k=recv(fd,result.data()+n,result.size()-n,0);if(k<=0){close();return {};}n+=k;}return result;}
bool Client::connect(int port,int slot){if((port!=30102&&port!=30103&&port!=30104)||slot<0||slot>31)return false;close();fd=socket(AF_INET,SOCK_STREAM,0);if(fd<0)return false;int one=1;setsockopt(fd,SOL_SOCKET,SO_NOSIGPIPE,&one,sizeof(one));timeval t{1,0};setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&t,sizeof(t));setsockopt(fd,SOL_SOCKET,SO_SNDTIMEO,&t,sizeof(t));sockaddr_in a{};a.sin_len=sizeof(a);a.sin_family=AF_INET;a.sin_port=htons(port);inet_pton(AF_INET,"127.0.0.1",&a.sin_addr);if(::connect(fd,reinterpret_cast<sockaddr*>(&a),sizeof(a))){close();return false;}
 auto cr=unhex("0300001611e00000000100c0010ac1020100c2020101");cr.back()=slot;auto cc=exchange(cr);if(cc.size()<7||cc[5]!=0xd0){close();return false;}auto setup=unhex("0300001902f08032010000000100080000f0000001000101e0");auto ack=exchange(setup);if(ack.size()!=27||ack[8]!=3||ack[17]||ack[18]){close();return false;}return true;}
Bytes Client::frame(bool write,const std::vector<Item>& items,uint16_t seq){Bytes p={0x32,1,0,0,uint8_t(seq>>8),uint8_t(seq),0,0,0,0,uint8_t(write?5:4),uint8_t(items.size())};int param=2+12*items.size();p[6]=param>>8;p[7]=param;Bytes data;for(size_t i=0;i<items.size();++i){const auto& x=items[i];int raw=x.wordlen==1?x.start:x.start*8;p.insert(p.end(),{0x12,10,0x10,uint8_t(x.wordlen),uint8_t(x.count>>8),uint8_t(x.count),uint8_t(x.db>>8),uint8_t(x.db),uint8_t(x.area),uint8_t(raw>>16),uint8_t(raw>>8),uint8_t(raw)});if(write){int transport=x.wordlen==1?3:x.wordlen==8?7:4;int bits=transport==3?1:transport==7?x.data.size():x.data.size()*8;data.insert(data.end(),{0,uint8_t(transport),uint8_t(bits>>8),uint8_t(bits)});data.insert(data.end(),x.data.begin(),x.data.end());if(i+1<items.size()&&x.data.size()%2)data.push_back(0);}}
 p[8]=data.size()>>8;p[9]=data.size();p.insert(p.end(),data.begin(),data.end());int n=p.size()+7;Bytes result={3,0,uint8_t(n>>8),uint8_t(n),2,0xf0,0x80};result.insert(result.end(),p.begin(),p.end());return result;}
Bytes Client::request(bool w,const std::vector<Item>& i){return exchange(frame(w,i,++sequence));}
std::vector<int> Client::results(const Bytes& b,bool write){std::vector<int> out;if(b.size()<21||b[7]!=0x32||b[8]!=3||b[17]||b[18])return out;int param=int(b[13])*256+b[14],pos=19+param,count=b[20];for(int i=0;i<count;++i){if(pos>=int(b.size()))return {};out.push_back(b[pos]);if(write)++pos;else{if(pos+4>int(b.size()))return {};int t=b[pos+1],n=int(b[pos+2])*256+b[pos+3];int bytes=t==3?(n+7)/8:t==4||t==5?n/8:n;pos+=4+bytes;if(i+1<count&&bytes%2)++pos;}}return out;}
Bytes Client::payload(const Bytes& b){if(b.size()<25||b[21]!=255)return {};int t=b[22],n=int(b[23])*256+b[24];int len=t==3?(n+7)/8:t==4||t==5?n/8:n;if(25+len>int(b.size()))return {};return Bytes(b.begin()+25,b.begin()+25+len);}
}
