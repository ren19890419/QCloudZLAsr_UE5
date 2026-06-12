#pragma once
#include "CoreMinimal.h"
#include "ZLAsrPlatformBridge.h"

class FZLAsrBridgeRegistry
{
public:
    static FZLAsrBridgeRegistry& Get();
    void Register(const FString& TaskId, IZLAsrTaskSink* Sink);
    void Unregister(const FString& TaskId);
    IZLAsrTaskSink* Find(const FString& TaskId);

private:
    FCriticalSection Mutex;
    TMap<FString, IZLAsrTaskSink*> Map;
};
