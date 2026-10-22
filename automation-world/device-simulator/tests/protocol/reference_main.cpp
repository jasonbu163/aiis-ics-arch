// DS协议回归参考client CLI：stdin有限raw向量，独立S7 item解码与原native API对照。
#include "snap7.h"
#include "wire_cases.hpp"
#include <iostream>
#include <sstream>
#include <map>
#include <chrono>
namespace ds { std::string resources(); }
int main(int argc,char**argv){if(argc!=3||std::string(argv[1])!="--run-root"){std::cout<<"ds-s7-reference --run-root <owned-run> (stdin finite vectors)\n";return argc==1?0:2;}std::map<int,wire::Client> clients;std::string line;int ticket=0;while(std::getline(std::cin,line)){std::istringstream in(line);int id;std::string cmd;in>>id>>cmd;if(cmd=="resources"){std::cout<<"{"<<ds::resources()<<"}"<<std::endl;continue;}bool ok=false;wire::Bytes raw,tx;auto start=std::chrono::steady_clock::now();
 try{if(cmd=="connect"){int port,slot;in>>port>>slot;ok=clients[id].connect(port,slot);}else if(cmd=="close"){clients[id].close();ok=true;}else if(cmd=="half"||cmd=="error"){clients[id].fault(cmd=="error");ok=true;}else if(cmd=="native"){int port;in>>port;S7Object c=Cli_Create();word p=port;Cli_SetParam(c,2,&p);int rc=Cli_ConnectTo(c,"127.0.0.1",0,port==30102?1:2);wire::Bytes bytes(64);ok=rc==0&&Cli_DBRead(c,57,0,64,bytes.data())==0;Cli_Disconnect(c);Cli_Destroy(&c);raw=bytes;}else if(cmd=="raw"){std::string s;in>>s;tx=wire::unhex(s);raw=clients[id].exchange(tx);ok=!raw.empty();}else{bool w=cmd=="write"||cmd=="multi"||cmd=="bit";std::vector<wire::Item> items;int count=cmd=="multi"?3:1;for(int k=0;k<count;++k){wire::Item x;std::string data;in>>x.db>>x.start;if(w){in>>data;x.data=wire::unhex(data);x.count=cmd=="bit"?1:x.data.size();x.wordlen=cmd=="bit"?1:2;}else in>>x.count;items.push_back(x);}tx=wire::Client::frame(w,items,ticket+1);raw=clients[id].exchange(tx);auto result=wire::Client::results(raw,w);ok=result.size()==items.size();}}
 catch(...){ok=false;}
 double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();std::cout<<"{\"event\":\"reference_result\",\"ticket\":"<<++ticket<<",\"id\":"<<id<<",\"local_port\":"<<clients[id].local_port()<<",\"command\":\""<<cmd<<"\",\"ok\":"<<(ok?"true":"false")<<",\"ms\":"<<ms<<",\"tx\":\""<<wire::hex(tx)<<"\",\"rx\":\""<<wire::hex(raw)<<"\",\"codes\":[";auto codes=wire::Client::results(raw,cmd=="write"||cmd=="multi"||cmd=="bit");for(size_t j=0;j<codes.size();++j){if(j)std::cout<<',';std::cout<<codes[j];}std::cout<<"],\"payload\":\""<<wire::hex(wire::Client::payload(raw))<<"\"}"<<std::endl;
 }return 0;}
