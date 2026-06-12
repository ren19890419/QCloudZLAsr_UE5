#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ZLAsrBlueprintLibrary.generated.h"

class UZLAsrRealtimeRecognizer;
class UZLAsrSentenceRecognizer;
class UZLAsrFileRecognizer;

UCLASS()
class UZLAsrBlueprintLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="ZLAsr", meta=(WorldContext="WorldContextObject"))
    static UZLAsrRealtimeRecognizer* CreateRealtimeRecognizer(UObject* WorldContextObject);

    UFUNCTION(BlueprintCallable, Category="ZLAsr", meta=(WorldContext="WorldContextObject"))
    static UZLAsrSentenceRecognizer* CreateSentenceRecognizer(UObject* WorldContextObject);

    UFUNCTION(BlueprintCallable, Category="ZLAsr", meta=(WorldContext="WorldContextObject"))
    static UZLAsrFileRecognizer* CreateFileRecognizer(UObject* WorldContextObject);
};
