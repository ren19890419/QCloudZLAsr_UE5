#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrRealtimeRecognizer.generated.h"

UCLASS(BlueprintType)
class UZLAsrRealtimeRecognizer : public UObject, public IZLAsrTaskSink
{
    GENERATED_BODY()

public:
    UZLAsrRealtimeRecognizer();

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool StartRealtimeRecognition(const FZLAsrRealtimeConfig& Config);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    void StopRealtimeRecognition();

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    void CancelRealtimeRecognition();

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnRealtimeSlice OnSlice;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnRealtimeSegment OnSegment;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnRealtimeFinal OnFinalResult;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnVolumeChanged OnVolumeChanged;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnSilenceDetected OnSilenceDetected;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnAsrError OnError;

    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult& Result) override;
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult& Result) override;
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult& Result) override;
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult&) override {}
    virtual void HandleFileResult(const FZLAsrRecognitionResult&) override {}
    virtual void HandleVolume(float Volume) override;
    virtual void HandleSilence() override;
    virtual void HandleError(const FZLAsrError& Error) override;

private:
    FString TaskId;
    bool bRunning = false;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
