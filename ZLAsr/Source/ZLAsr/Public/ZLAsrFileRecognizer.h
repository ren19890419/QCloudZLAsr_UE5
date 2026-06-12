#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrFileRecognizer.generated.h"

UCLASS(BlueprintType)
class ZLASR_API UZLAsrFileRecognizer : public UObject, public IZLAsrTaskSink
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

    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult& Result) override {}
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult& Result) override {}
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult& Result) override {}
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) override {}
    virtual void HandleFileResult(const FZLAsrRecognitionResult& Result) override;
    virtual void HandleVolume(float Volume) override {}
    virtual void HandleSilence() override {}
    virtual void HandleError(const FZLAsrError& Error) override;

protected:
    FString TaskId;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
