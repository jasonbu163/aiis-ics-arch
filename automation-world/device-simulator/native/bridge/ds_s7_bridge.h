// DS G0 versioned C ABI. No business memory or C++ object layout crosses this boundary.
#pragma once
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct DsS7Server DsS7Server;
#pragma pack(push,1)
typedef struct { int area,db,start,count,wordlen; } DsS7Tag;
#pragma pack(pop)
typedef struct {
 uint32_t abi_version,struct_size;
 int (*accept_reserve)(void*,uint64_t*);
 void (*accept_cancel)(void*,uint64_t);
 int (*accepted)(void*,uint64_t,int,uint64_t*);
 int (*active)(void*,uint64_t);
 int (*cotp)(void*,uint64_t,const unsigned char*,uint32_t);
 int (*setup)(void*,uint64_t);
 int (*begin_pdu)(void*,uint64_t,const unsigned char*,uint32_t,uint64_t*);
 int (*item)(void*,uint64_t,uint64_t,uint32_t,int,const DsS7Tag*,void*,uint32_t);
 void (*end_pdu)(void*,uint64_t,uint64_t);
 void (*closing)(void*,uint64_t);
 void (*joined)(void*,uint64_t,int);
 void (*io)(void*,uint64_t,int,const void*,uint32_t,uint64_t);
} DsS7Callbacks;
typedef struct {
 uint32_t version,tag_size,tag_align,tag_offsets[5],callbacks_size,callbacks_align,callbacks_offsets[14];
 uint32_t worker_size,socket_size,worker_thread_size,fixed_instance_bytes;
 int callback_zero,callback_nonzero;
} DsS7Abi;
DsS7Server* ds_s7_create(const DsS7Callbacks*,void*);
int ds_s7_start(DsS7Server*,const char*,int);
int ds_s7_request_stop(DsS7Server*);
int ds_s7_poll_stop(DsS7Server*);
int ds_s7_close(DsS7Server*,uint64_t);
int ds_s7_destroy(DsS7Server*);
typedef int (*DsS7RWProbe)(void*,int,int,const DsS7Tag*,void*);
int ds_s7_abi_probe(DsS7Abi*,DsS7RWProbe,void*);
uint64_t ds_s7_clock_ns(void);
#ifdef __cplusplus
}
#endif
