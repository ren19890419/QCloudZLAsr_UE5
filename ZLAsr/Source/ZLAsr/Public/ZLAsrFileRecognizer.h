#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrFileRecognizer.generated.h"

UCLASS(BlueprintType)
class UZLAsrFileRecognizer : public UObject, public IZLAsrTaskSink
{
    GENERATED_BODY()

public:
    UZLAsrFileRecognizer();

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFile(const FZLAsrFileConfig& Config, const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeData(const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData);

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnFileResult OnResult;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnAsrError OnError;

    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult&) override {}
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult&) override {}
    virtual void HandleFileResult(const FZLAsrRecognitionResult& Result) override;
    virtual void HandleVolume(float) override {}
    virtual void HandleSilence() override {}
    virtual void HandleError(const FZLAsrError& Error) override;

private:
    FString TaskId;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
