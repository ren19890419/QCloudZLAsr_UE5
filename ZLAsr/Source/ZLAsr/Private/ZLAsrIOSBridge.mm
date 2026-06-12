#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"
#include "Misc/FileHelper.h"

#if PLATFORM_IOS
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

class FZLAsrIOSBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig&) override
    {
        Register(TaskId);
        Report(TEXT("iOS realtime bridge requires real Tencent frameworks"));
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString& TaskId) override { FZLAsrBridgeRegistry::Get().Unregister(TaskId); }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(url) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath)) return false;
        return StartSentenceFromMemory(TaskId, Config, Data);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig&, const TArray<uint8>&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(data) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(recorder) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual void StopSentenceRecorder(const FString&) override {}

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig&, const FString&) override
    {
        Register(TaskId);
        Report(TEXT("iOS file(path) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig&, const TArray<uint8>&) override
    {
        Register(TaskId);
        Report(TEXT("iOS file(data) bridge requires real Tencent frameworks"));
        return false;
    }

private:
    void Register(const FString& TaskId)
    {
        if (Sink) FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
    }

    void Report(const FString& Message)
    {
        if (Sink) Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, Message, TEXT("")));
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge()
{
    return MakeShared<FZLAsrIOSBridge>();
}
#endif
