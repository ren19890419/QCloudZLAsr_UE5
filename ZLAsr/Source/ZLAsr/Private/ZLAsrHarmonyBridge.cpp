#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

class FZLAsrHarmonyBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        return true;
    }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, TEXT("Harmony bridge needs UE<->ArkTS native bridge integration"), TEXT("")));
        }
        return false;
    }

    virtual void StopRealtime(const FString& TaskId) override {}
    virtual void CancelRealtime(const FString& TaskId) override {}
    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override { return StartUnsupported(TaskId); }
    virtual void StopSentenceRecorder(const FString& TaskId) override {}
    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override { return StartUnsupported(TaskId); }
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override { return StartUnsupported(TaskId); }

private:
    bool StartUnsupported(const FString& TaskId)
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, TEXT("Harmony bridge needs UE<->ArkTS native bridge integration"), TEXT("")));
        }
        return false;
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge()
{
    return MakeShared<FZLAsrHarmonyBridge>();
}
