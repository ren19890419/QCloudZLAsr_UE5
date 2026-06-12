#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrSentenceRecognizer.generated.h"

UCLASS(BlueprintType)
class UZLAsrSentenceRecognizer : public UObject, public IZLAsrTaskSink
{
    GENERATED_BODY()

public:
    UZLAsrSentenceRecognizer();

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromUrl(const FZLAsrSentenceConfig& Config, const FString& Url);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromFile(const FZLAsrSentenceConfig& Config, const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromMemory(const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool StartRecognizeWithRecorder(const FZLAsrSentenceConfig& Config);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    void StopRecognizeWithRecorder();

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnSentenceResult OnResult;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnVolumeChanged OnVolumeChanged;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnAsrError OnError;

    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult&) override {}
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) override;
    virtual void HandleFileResult(const FZLAsrRecognitionResult&) override {}
    virtual void HandleVolume(float Volume) override;
    virtual void HandleSilence() override {}
    virtual void HandleError(const FZLAsrError& Error) override;

private:
    FString TaskId;
    bool bRecording = false;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
