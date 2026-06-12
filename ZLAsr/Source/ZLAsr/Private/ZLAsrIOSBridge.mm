#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

#if PLATFORM_IOS
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

// 下面这些头文件需要用户放入真实腾讯云 iOS SDK 后才可编译通过 [4][5][6]
// #import <QCloudRealTime/QCloudRealTimeRecognizer.h>
// #import <QCloudRealTime/QCloudConfig.h>
// #import <QCloudOneSentence/QCloudSentenceRecognizer.h>
// #import <QCloudFileRecognizer/QCloudFlashFileRecognizer.h>

class FZLAsrIOSBridge final : public IZLAsrPlatformBridge
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
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual void StopRealtime(const FString& TaskId) override {}
    virtual void CancelRealtime(const FString& TaskId) override {}

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath))
        {
            return false;
        }
        return StartSentenceFromMemory(TaskId, Config, Data);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence memory bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence recorder bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual void StopSentenceRecorder(const FString& TaskId) override {}

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS file bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS file data bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge()
{
    return MakeShared<FZLAsrIOSBridge>();
}
#endif
