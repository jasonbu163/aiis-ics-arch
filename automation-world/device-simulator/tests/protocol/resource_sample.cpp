// DS协议回归宿主资源采样：CPU时间/墙钟、RSS、线程、FD和Mach ports分项。
#include <string>
#include <mach/mach.h>
#include <sys/resource.h>
#include <libproc.h>
#include <unistd.h>
namespace ds {
std::string resources(){
 rusage r{};getrusage(RUSAGE_SELF,&r);mach_task_basic_info_data_t info{};mach_msg_type_number_t n=MACH_TASK_BASIC_INFO_COUNT;task_info(mach_task_self(),MACH_TASK_BASIC_INFO,reinterpret_cast<task_info_t>(&info),&n);
 thread_act_array_t threads=nullptr;mach_msg_type_number_t nt=0;task_threads(mach_task_self(),&threads,&nt);for(unsigned i=0;i<nt;++i)mach_port_deallocate(mach_task_self(),threads[i]);if(threads)vm_deallocate(mach_task_self(),reinterpret_cast<vm_address_t>(threads),nt*sizeof(thread_t));
 mach_port_name_array_t names=nullptr;mach_port_type_array_t types=nullptr;mach_msg_type_number_t nn=0,tn=0;mach_port_names(mach_task_self(),&names,&nn,&types,&tn);if(names)vm_deallocate(mach_task_self(),reinterpret_cast<vm_address_t>(names),nn*sizeof(mach_port_name_t));if(types)vm_deallocate(mach_task_self(),reinterpret_cast<vm_address_t>(types),tn*sizeof(mach_port_type_t));
 int bytes=proc_pidinfo(getpid(),PROC_PIDLISTFDS,0,nullptr,0);double cpu=r.ru_utime.tv_sec+r.ru_utime.tv_usec/1e6+r.ru_stime.tv_sec+r.ru_stime.tv_usec/1e6;
 return "\"event\":\"resources\",\"pid\":"+std::to_string(getpid())+",\"cpu_seconds\":"+std::to_string(cpu)+",\"rss\":"+std::to_string(info.resident_size)+",\"threads\":"+std::to_string(nt)+",\"fd\":"+std::to_string(bytes>0?bytes/int(sizeof(proc_fdinfo)):0)+",\"mach_ports\":"+std::to_string(nn);
}}
