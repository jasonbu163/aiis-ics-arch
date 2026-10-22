// DS协议回归独立raw向量与item返回解码；固定有限client，不实现server。
#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace wire {
using Bytes=std::vector<uint8_t>;
struct Item {int db=41,start=0,count=0,wordlen=2,area=0x84;Bytes data;};
class Client {
 int fd=-1;uint16_t sequence=0;
public:
 ~Client();void close();void fault(bool reset);int local_port() const;bool connect(int port,int slot);
 Bytes exchange(const Bytes& frame);
 Bytes request(bool write,const std::vector<Item>& items);
 static Bytes frame(bool write,const std::vector<Item>& items,uint16_t sequence);
 static std::vector<int> results(const Bytes&,bool write);
 static Bytes payload(const Bytes&);
};
Bytes unhex(const std::string&);std::string hex(const Bytes&);
}
