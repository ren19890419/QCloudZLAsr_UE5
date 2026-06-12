#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "Async/Async.h"

TSharedPtr<IZLAsrPlatformBridge> CreateAndroidBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge();

class FZLAsrStubBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString&, const FZLAsrRealtimeConfig&) override
    {
        if (Sink)
        {
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("Unsupported platform"), TEXT("")));
            });
        }
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString&) override {}
    virtual bool StartSentenceFromUrl(const FString&, const FZLAsrSentenceConfig&, const FString&) override { return false; }
    virtual bool StartSentenceFromFile(const FString&, const FZLAsrSentenceConfig&, const FString&) override { return false; }
    virtual bool StartSentenceFromMemory(const FString&, const FZLAsrSentenceConfig&, const TArray<uint8>&) override { return false; }
    virtual bool StartSentenceRecorder(const FString&, const FZLAsrSentenceConfig&) override { return false; }
    virtual void StopSentenceRecorder(const FString&) override {}
    virtual bool StartFileRecognizePath(const FString&, const FZLAsrFileConfig&, const FString&) override { return false; }
    virtual bool StartFileRecognizeData(const FString&, const FZLAsrFileConfig&, const TArray<uint8>&) override { return false; }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> FZLAsrPlatformBridgeFactory::Create()
{
#if PLATFORM_ANDROID
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateAndroidBridge()) return B;
#elif PLATFORM_IOS
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateIOSBridge()) return B;
#else
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateHarmonyBridge()) return B;
#endif
    return MakeShared<FZLAsrStubBridge>();
}
