/*=============================================================================|
|  PROJECT SNAP7                                                         1.3.0 |
|==============================================================================|
|  Copyright (C) 2013, 2015 Davide Nardella                                    |
|  All rights reserved.                                                        |
|==============================================================================|
|  SNAP7 is free software: you can redistribute it and/or modify               |
|  it under the terms of the Lesser GNU General Public License as published by |
|  the Free Software Foundation, either version 3 of the License, or           |
|  (at your option) any later version.                                         |
|                                                                              |
|  It means that you can distribute your commercial software linked with       |
|  SNAP7 without the requirement to distribute the source code of your         |
|  application and without the requirement that your application be itself     |
|  distributed under LGPL.                                                     |
|                                                                              |
|  SNAP7 is distributed in the hope that it will be useful,                    |
|  but WITHOUT ANY WARRANTY; without even the implied warranty of              |
|  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
|  Lesser GNU General Public License for more details.                         |
|                                                                              |
|  You should have received a copy of the GNU General Public License and a     |
|  copy of Lesser GNU General Public License along with Snap7.                 |
|  If not, see  http://www.gnu.org/licenses/                                   |
|=============================================================================*/

#include "snap_tcpsrvr.h"
#include <thread>
#include <chrono>
#include <fcntl.h>
extern void* ThreadProc(void*);

int TMsgWorkerThread::DsStart() { pthread_t created; int rc=pthread_create(&created,nullptr,ThreadProc,this); if(!rc) Started=true; return rc; }
int TMsgListenerThread::DsStart() { pthread_t created; int rc=pthread_create(&created,nullptr,ThreadProc,this); if(!rc) Started=true; return rc; }
//---------------------------------------------------------------------------
// EVENTS QUEUE
//---------------------------------------------------------------------------

TMsgEventQueue::TMsgEventQueue(const int Capacity, const int BlockSize) 
{
    FCapacity = Capacity;
    Max = FCapacity - 1;
    FBlockSize = BlockSize;
    Buffer = new byte[FCapacity * FBlockSize];
    Flush();
}
//---------------------------------------------------------------------------
TMsgEventQueue::~TMsgEventQueue() 
{
    delete[] Buffer;
}
//---------------------------------------------------------------------------
void TMsgEventQueue::Flush() 
{
    IndexIn = 0;
    IndexOut = 0;
}
//---------------------------------------------------------------------------
void TMsgEventQueue::Insert(void *lpdata) 
{
    pbyte PBlock;
    if (!Full())
    {
        // Calc offset
        if (IndexIn < Max) IndexIn++;
        else IndexIn = 0;
        PBlock = Buffer + uintptr_t(IndexIn * FBlockSize);
        memcpy(PBlock, lpdata, FBlockSize);
    };
}
//---------------------------------------------------------------------------
bool TMsgEventQueue::Extract(void *lpdata) 
{
    int IdxOut;
    pbyte PBlock;

    if (!Empty())
    {
        // stores IndexOut
        IdxOut = IndexOut;
        if (IdxOut < Max) IdxOut++;
        else IdxOut = 0;
        PBlock = Buffer + uintptr_t(IdxOut * FBlockSize);
        // moves data
        memcpy(lpdata, PBlock, FBlockSize);
        // Updates IndexOut
        IndexOut = IdxOut;
        return true;
    }
    else
        return false;
}
//---------------------------------------------------------------------------
bool TMsgEventQueue::Empty() 
{
    return (IndexIn == IndexOut);
}
//---------------------------------------------------------------------------
bool TMsgEventQueue::Full() 
{
    int IdxOut = IndexOut; // To avoid troubles if IndexOut changes during next line
    return ( (IdxOut == IndexIn + 1) || ((IndexIn == Max) && (IdxOut == 0)));
}
//---------------------------------------------------------------------------
// WORKER THREAD
//---------------------------------------------------------------------------
TMsgWorkerThread::TMsgWorkerThread(TMsgSocket *Socket, TCustomMsgServer *Server) 
{
    FreeOnTerminate = Server->DsHooks == nullptr;
    WorkerSocket = Socket;
    FServer = Server;
}
//---------------------------------------------------------------------------
void TMsgWorkerThread::Execute() 
{
    DsThread = pthread_self(); DsReady.store(true);
    bool Exception = false;
    bool SelfClose = false;
    // Working loop
    while ((FServer->DsHooks ? !DsStop.load() : (!Terminated && !FServer->Destroying)) && !SelfClose && !Exception)
    {
        try
        {
            if (!WorkerSocket->Execute()) // False -> End of Activities
                SelfClose = true;
        } catch (...)
        {
            Exception = true;
        }
    };
    if (!FServer->Destroying)
    {
        // Exception detected during Worker activity
        if (Exception)
        {
            WorkerSocket->ForceClose();
            FServer->DoEvent(WorkerSocket->ClientHandle, evcClientException, 0, 0, 0, 0, 0);
        }
        else
            if (SelfClose)
        {
            FServer->DoEvent(WorkerSocket->ClientHandle, evcClientDisconnected, 0, 0, 0, 0, 0);
        }
        else
            FServer->DoEvent(WorkerSocket->ClientHandle, evcClientTerminated, 0, 0, 0, 0, 0);
    }
    if (FServer->DsHooks) {
        FServer->DsHooks->closing(FServer->DsHooks->user, WorkerSocket->DsId);
        DsDone.store(true);
        return; // socket/context/list retained until real pthread_join
    }
    delete WorkerSocket;
    // Delete reference from list
    FServer->Delete(Index);
}
//---------------------------------------------------------------------------
// LISTENER THREAD
//---------------------------------------------------------------------------

TMsgListenerThread::TMsgListenerThread(TMsgSocket *Listener, TCustomMsgServer *Server) 
{
    FServer = Server;
    FListener = Listener;
    FreeOnTerminate = false;
}
//---------------------------------------------------------------------------

void TMsgListenerThread::Execute() 
{
    DsThread = pthread_self(); DsReady.store(true);
    socket_t Sock;
    bool Valid;

    while (FServer->DsHooks ? !DsStop.load() : !Terminated)
    {
        if (FListener->CanRead(FListener->WorkInterval))
        {
            if (FServer->DsHooks && !FServer->DsHooks->reserve_accept(FServer->DsHooks->user)) { SysSleep(5); continue; }
            Sock = FListener->SckAccept(); // in any case we must accept
            Valid = Sock != INVALID_SOCKET;
            if (!Valid && FServer->DsHooks) FServer->DsHooks->cancel_accept(FServer->DsHooks->user);
            // check if we are not destroying
            if (FServer->DsHooks ? !DsStop.load() : ((!Terminated) && (!FServer->Destroying)))
            {
                if (Valid)
                    FServer->Incoming(Sock);
            }
            else
                if (Valid)
                {
                    Msg_CloseSocket(Sock);
                    if (FServer->DsHooks) FServer->DsHooks->cancel_accept(FServer->DsHooks->user);
                }
        };
    }
    DsDone.store(true);
}
//---------------------------------------------------------------------------
// TCP SERVER
//---------------------------------------------------------------------------
TCustomMsgServer::TCustomMsgServer() 
{
    strcpy(FLocalAddress, "0.0.0.0");
    CSList = new TSnapCriticalSection();
    CSEvent = new TSnapCriticalSection();
    FEventQueue = new TMsgEventQueue(MaxEvents, sizeof (TSrvEvent));
    memset(Workers, 0, sizeof (Workers));
    for (int i = 0; i < MaxWorkers; i++)
        Workers[i] = NULL;
    Status = SrvStopped;
    EventMask = 0xFFFFFFFF;
    LogMask = 0xFFFFFFFF;
    Destroying = false;
    SockListener=nullptr; ServerThread=nullptr;
    FLastError = 0;
    ClientsCount = 0;
    LocalBind = 0;
    MaxClients = MaxWorkers;
    OnEvent = NULL;
}
//---------------------------------------------------------------------------
TCustomMsgServer::~TCustomMsgServer() 
{
    Destroying = true;
    Stop();
    OnEvent = NULL;
    delete CSList;
    delete CSEvent;
    delete FEventQueue;
}
//---------------------------------------------------------------------------
void TCustomMsgServer::LockList() 
{
    CSList->Enter();
}
//---------------------------------------------------------------------------
void TCustomMsgServer::UnlockList() 
{
    CSList->Leave();
}
//---------------------------------------------------------------------------
int TCustomMsgServer::FirstFree() 
{
    int i;
    for (i = 0; i < MaxWorkers; i++)
    {
        if (Workers[i] == 0)
            return i;
    }
    return -1;
}
//---------------------------------------------------------------------------

int TCustomMsgServer::StartListener() 
{
    int Result;
    // Creates the listener
    try { SockListener = new TMsgSocket(); } catch (...) { SockListener=nullptr; return ENOMEM; }
    if (DsHooks) SockListener->DsHooks=DsHooks;
    strncpy(SockListener->LocalAddress, FLocalAddress, 16);
    SockListener->LocalPort = LocalPort;
    // Binds
    Result = SockListener->SckBind();
    if (Result == 0)
    {
        LocalBind = SockListener->LocalBind;
        // Listen
        Result = SockListener->SckListen();
        if (Result == 0)
        {
            // G0 accept must not block after readiness is consumed by a reset peer.
            if (DsHooks) {
                int flags=fcntl(SockListener->DsFd(),F_GETFL,0);
                if (flags<0 || fcntl(SockListener->DsFd(),F_SETFL,flags|O_NONBLOCK)<0) { int error=errno; delete SockListener; SockListener=nullptr; return error; }
            }
            // Creates the Listener thread
            try { ServerThread = new TMsgListenerThread(SockListener, this); } catch (...) { delete SockListener; SockListener=nullptr; ServerThread=nullptr; return ENOMEM; }
            if (DsHooks) {
                int rc=ServerThread->DsStart();
                if (rc) { delete ServerThread; ServerThread=nullptr; delete SockListener; SockListener=nullptr; return rc; }
                double start=DsMonotonicSeconds();
                while (!ServerThread->DsReady.load()) {
                    if (DsMonotonicSeconds()-start>1) { ServerThread->DsStop.store(true); return ETIMEDOUT; }
                    SysSleep(1);
                }
            } else ServerThread->Start();
            if (DsHooks) { DsReaping.store(true); try { DsReaper = new std::thread([this] { while (DsReaping.load()) { DsReap(); SysSleep(2); } DsReap(); }); } catch (...) { DsReaping.store(false); ServerThread->DsStop.store(true); return EAGAIN; } }
        }
        else { delete SockListener; SockListener=nullptr; }
    }
    else { delete SockListener; SockListener=nullptr; }

    return Result;
}
//---------------------------------------------------------------------------
void TCustomMsgServer::TerminateAll() 
{
    int c;
    longword Elapsed;
    bool Timeout;

    if (ClientsCount > 0)
    {
        for (c = 0; c < MaxWorkers; c++)
        {
            if (Workers[c] != 0)
                PMsgWorkerThread(Workers[c])->Terminate();
        }
        // Wait for closing
        Elapsed = SysGetTick();
        Timeout = false;
        while (!Timeout && (ClientsCount > 0))
        {
            Timeout = DeltaTime(Elapsed) > WkTimeout;
            if (!Timeout)
                SysSleep(100);
        };
        if (ClientsCount > 0)
            KillAll(); // one o more threads are hanged
        ClientsCount = 0;
    }
}
//---------------------------------------------------------------------------
void TCustomMsgServer::KillAll() 
{
    int c, cnt = 0;
    LockList();
    for (c = 0; c < MaxWorkers; c++)
    {
        if (Workers[c] != 0)
            try
            {
                PMsgWorkerThread(Workers[c])->Kill();
                PMsgWorkerThread(Workers[c])->WorkerSocket->ForceClose();
                delete PMsgWorkerThread(Workers[c]);
                Workers[c] = 0;
                cnt++;
            } catch (...)
            {
            };
    }
    UnlockList();
    DoEvent(0, evcClientsDropped, 0, cnt, 0, 0, 0);
}
//---------------------------------------------------------------------------
bool TCustomMsgServer::CanAccept(socket_t Socket) 
{
    if (DsHooks) return true; // admission already reserved before accept
    return ((MaxClients == 0) || (ClientsCount < MaxClients));
}
//---------------------------------------------------------------------------
PWorkerSocket TCustomMsgServer::CreateWorkerSocket(socket_t Sock) 
{
    PWorkerSocket Result;
    // Creates a funny default class : a tcp echo worker
    Result = new TEcoTcpWorker();
    Result->SetSocket(Sock);
    return Result;
}
//---------------------------------------------------------------------------
void TCustomMsgServer::DoEvent(int Sender, longword Code, word RetCode, word Param1, word Param2, word Param3, word Param4) 
{
    TSrvEvent SrvEvent;
    bool GoLog = (Code & LogMask) != 0;
    bool GoEvent = (Code & EventMask) != 0;

    if (!Destroying && (GoLog || GoEvent))
    {
        CSEvent->Enter();

        time(&SrvEvent.EvtTime);
        SrvEvent.EvtSender = Sender;
        SrvEvent.EvtCode = Code;
        SrvEvent.EvtRetCode = RetCode;
        SrvEvent.EvtParam1 = Param1;
        SrvEvent.EvtParam2 = Param2;
        SrvEvent.EvtParam3 = Param3;
        SrvEvent.EvtParam4 = Param4;

        if (GoEvent && (OnEvent != NULL))
            try
            { // callback is outside here, we have to shield it
                OnEvent(FUsrPtr, &SrvEvent, sizeof (TSrvEvent));
            } catch (...)
            {
            };

        if (GoLog)
            FEventQueue->Insert(&SrvEvent);

        CSEvent->Leave();
    };
}
//---------------------------------------------------------------------------
void TCustomMsgServer::Delete(int Index) 
{
    LockList();
    Workers[Index] = 0;
    ClientsCount--;
    UnlockList();
}
//---------------------------------------------------------------------------
void TCustomMsgServer::Incoming(socket_t Sock) 
{
    int idx;
    PWorkerSocket WorkerSocket;
    longword ClientHandle = Msg_GetSockAddr(Sock);

    if (CanAccept(Sock))
    {
        LockList();
        // First position available in the thread buffer
        idx = FirstFree();
        if (idx >= 0)
        {
            // Creates the Worker and assigns it the connected socket
            try { WorkerSocket = CreateWorkerSocket(Sock); }
            catch (...) { Msg_CloseSocket(Sock); UnlockList(); if (DsHooks) DsHooks->cancel_accept(DsHooks->user); return; }
            if (DsHooks) {
                WorkerSocket->DsHooks = DsHooks;
                try { WorkerSocket->DsId = DsHooks->accepted(DsHooks->user, int(Sock)); }
                catch (...) { delete WorkerSocket; UnlockList(); DsHooks->cancel_accept(DsHooks->user); return; }
                WorkerSocket->DsAcceptedAt = DsMonotonicSeconds();
                WorkerSocket->WorkInterval = 5;
            }
            // Creates the Worker thread
            try { Workers[idx] = new TMsgWorkerThread(WorkerSocket, this); }
            catch (...) { uint64_t id=WorkerSocket->DsId; delete WorkerSocket; UnlockList(); if (DsHooks) DsHooks->joined(DsHooks->user,id,-ENOMEM); return; }
            PMsgWorkerThread(Workers[idx])->Index = idx;
            // Update the number
            ClientsCount++;
            // And Starts the worker
            if (DsHooks) {
                auto w=PMsgWorkerThread(Workers[idx]);
                int rc=w->DsStart();
                if (rc) {
                    uint64_t id=WorkerSocket->DsId; Workers[idx]=nullptr; --ClientsCount;
                    delete WorkerSocket; delete w; UnlockList();
                    DsHooks->joined(DsHooks->user,id,-rc); return; // creation failed: no pthread existed
                }
                double start=DsMonotonicSeconds();
                while (!w->DsReady.load()) {
                    if (DsMonotonicSeconds()-start>1) { w->DsStop.store(true); DsHooks->closing(DsHooks->user,WorkerSocket->DsId); UnlockList(); return; }
                    SysSleep(1);
                }
            } else PMsgWorkerThread(Workers[idx])->Start();
            DoEvent(WorkerSocket->ClientHandle, evcClientAdded, 0, 0, 0, 0, 0);
        }
        else
        {
            if (DsHooks) DsHooks->cancel_accept(DsHooks->user);
            DoEvent(ClientHandle, evcClientNoRoom, 0, 0, 0, 0, 0);
            Msg_CloseSocket(Sock);
        }
        UnlockList();
    }
    else
    {
        Msg_CloseSocket(Sock);
        DoEvent(ClientHandle, evcClientRejected, 0, 0, 0, 0, 0);
    };
}
//---------------------------------------------------------------------------
int TCustomMsgServer::Start() 
{
    int Result = 0;
    if (Status != SrvRunning)
    {
        Result = StartListener();
        if (Result != 0)
        {
            DoEvent(0, evcListenerCannotStart, Result, 0, 0, 0, 0);
            Status = SrvError;
        }
        else
        {
            DoEvent(0, evcServerStarted, SockListener->ClientHandle, LocalPort, 0, 0, 0);
            Status = SrvRunning;
        };
    };
    FLastError = Result;
    return Result;
}
//---------------------------------------------------------------------------
int TCustomMsgServer::StartTo(const char *Address, word Port) 
{
    strncpy(FLocalAddress, Address, 16);
    LocalPort = Port;
    return Start();
}
//---------------------------------------------------------------------------
void TCustomMsgServer::Stop() 
{
    if (Status == SrvRunning || (DsHooks && Status==SrvError))
    {
        // Kills the listener thread
        if (DsHooks) {
            if (ServerThread) ServerThread->DsStop.store(true);
            double begin = DsMonotonicSeconds();
            while (ServerThread && !ServerThread->DsDone.load()) {
                if (DsMonotonicSeconds()-begin > 5) { Status=SrvError; return; }
                SysSleep(1);
            }
            int rc=ServerThread ? pthread_join(ServerThread->DsThread,nullptr) : 0;
            if (rc) { Status=SrvError; return; }
            delete ServerThread; ServerThread=nullptr;
            delete SockListener; SockListener=nullptr;
            LockList();
            for (int i=0;i<MaxWorkers;++i) if (Workers[i]) {
                auto w=PMsgWorkerThread(Workers[i]); w->DsStop.store(true);
                shutdown(w->WorkerSocket->DsFd(),SHUT_RDWR);
            }
            UnlockList();
            for (;;) {
                if (!DsReaper) DsReap();
                LockList(); bool remaining=ClientsCount>0; UnlockList(); if (!remaining) break;
                if (DsMonotonicSeconds()-begin > 5) { Status=SrvError; return; }
                SysSleep(1);
            }
            DsReaping.store(false); if (DsReaper) { static_cast<std::thread*>(DsReaper)->join(); delete static_cast<std::thread*>(DsReaper); DsReaper=nullptr; }
            Status=SrvStopped; LocalBind=0; return;
        }
        ServerThread->Terminate();
        if (ServerThread->WaitFor(ThTimeout) != WAIT_OBJECT_0)
            ServerThread->Kill();
        delete ServerThread;
        // Kills the listener
        delete SockListener;

        // Terminate all client threads
        TerminateAll();

        Status = SrvStopped;
        LocalBind = 0;
        DoEvent(0, evcServerStopped, 0, 0, 0, 0, 0);
    };
    FLastError = 0;
}
//---------------------------------------------------------------------------
int TCustomMsgServer::SetEventsCallBack(pfn_SrvCallBack PCallBack, void *UsrPtr) 
{
    OnEvent = PCallBack;
    FUsrPtr = UsrPtr;
    return 0;
}
//---------------------------------------------------------------------------
bool TCustomMsgServer::PickEvent(void *pEvent) 
{
    try
    {
        return FEventQueue->Extract(pEvent);
    } catch (...)
    {
        return false;
    };
}
//---------------------------------------------------------------------------
bool TCustomMsgServer::EventEmpty() 
{
    return FEventQueue->Empty();
}
//---------------------------------------------------------------------------
void TCustomMsgServer::EventsFlush() 
{
    CSEvent->Enter();
    FEventQueue->Flush();
    CSEvent->Leave();
}
//---------------------------------------------------------------------------



// DS G0: reaper never holds CSList while joining or invoking owner callbacks.
void TCustomMsgServer::DsReap() {
 for (int i=0;i<MaxWorkers;++i) {
  LockList(); auto w=PMsgWorkerThread(Workers[i]);
  bool take=w && w->DsDone.load() && !w->DsJoining.exchange(true); UnlockList();
  if (!take) continue;
  uint64_t id=w->WorkerSocket->DsId;
  int rc=pthread_join(w->DsThread,nullptr);
  if (rc) { w->DsJoining.store(false); continue; }
  LockList(); Workers[i]=nullptr; UnlockList();
  delete w->WorkerSocket; delete w;
  DsHooks->joined(DsHooks->user,id,rc);
  LockList(); --ClientsCount; UnlockList();
 }
}
void TCustomMsgServer::DsClose(uint64_t id) {
 LockList();
 for (int i=0;i<MaxWorkers;++i) if (Workers[i]) {
  auto w=PMsgWorkerThread(Workers[i]);
  if (w->WorkerSocket->DsId==id) { w->DsStop.store(true); shutdown(w->WorkerSocket->DsFd(),SHUT_RDWR); }
 }
 UnlockList();
}
