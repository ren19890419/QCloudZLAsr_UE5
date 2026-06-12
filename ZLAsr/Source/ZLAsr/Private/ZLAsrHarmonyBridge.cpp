#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

class FZLAsrHarmonyBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig&) override
    {
        Register(TaskId);
        Report(TEXT("Harmony bridge needs UE <-> ArkTS integration"));
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString& TaskId) override { FZLAsrBridgeRegistry::Get().Unregister(TaskId); }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony sentence(url) bridge not wired")); return false; }
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony sentence(file) bridge not wired")); return false; }
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig&, const TArray<uint8>&) override { Register(TaskId); Report(TEXT("Harmony sentence(data) bridge not wired")); return false; }
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig&) override { Register(TaskId); Report(TEXT("Harmony recorder bridge not wired")); return false; }
    virtual void StopSentenceRecorder(const FString&) override {}
    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony file(path) bridge not wired")); return false; }
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig&, const TArray<uint8>&) override { Register(TaskId); Report(TEXT("Harmony file(data) bridge not wired")); return false; }

private:
    void Register(const FString& TaskId)
    {
        if (Sink) FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
    }

    void Report(const FString& Message)
    {
        if (Sink) Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, Message, TEXT("")));
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge()
{
    return MakeShared<FZLAsrHarmonyBridge>();
}
