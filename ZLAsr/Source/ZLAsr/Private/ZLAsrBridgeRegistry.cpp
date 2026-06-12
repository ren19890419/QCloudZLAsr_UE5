#include "ZLAsrBridgeRegistry.h"

FZLAsrBridgeRegistry& FZLAsrBridgeRegistry::Get()
{
    static FZLAsrBridgeRegistry I;
    return I;
}

void FZLAsrBridgeRegistry::Register(const FString& TaskId, IZLAsrTaskSink* Sink)
{
    FScopeLock Lock(&Mutex);
    Map.Add(TaskId, Sink);
}

void FZLAsrBridgeRegistry::Unregister(const FString& TaskId)
{
    FScopeLock Lock(&Mutex);
    Map.Remove(TaskId);
}

IZLAsrTaskSink* FZLAsrBridgeRegistry::Find(const FString& TaskId)
{
    FScopeLock Lock(&Mutex);
    if (IZLAsrTaskSink** Found = Map.Find(TaskId))
    {
        return *Found;
    }
    return nullptr;
}
