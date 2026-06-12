#pragma once

#include "CoreMinimal.h"
#include "ZLAsrTypes.h"

class IZLAsrTaskSink
{
public:
    virtual ~IZLAsrTaskSink() = default;
    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult& Result) = 0;
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult& Result) = 0;
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleFileResult(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleVolume(float Volume) = 0;
    virtual void HandleSilence() = 0;
    virtual void HandleError(const FZLAsrError& Error) = 0;
};

class IZLAsrPlatformBridge
{
public:
    virtual ~IZLAsrPlatformBridge() = default;

    virtual bool Init(IZLAsrTaskSink* InSink) = 0;

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) = 0;
    virtual void StopRealtime(const FString& TaskId) = 0;
    virtual void CancelRealtime(const FString& TaskId) = 0;

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) = 0;
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) = 0;
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) = 0;
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) = 0;
    virtual void StopSentenceRecorder(const FString& TaskId) = 0;

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) = 0;
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) = 0;
};

class ZLASR_API FZLAsrPlatformBridgeFactory
{
public:
    static TSharedPtr<IZLAsrPlatformBridge> Create();
};
