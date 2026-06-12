#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "ZLAsrTypes.h"

class FZLAsrJsonUtils
{
public:
    static FString ToJsonString(const FZLAsrRealtimeConfig& InConfig);
    static FString ToJsonString(const FZLAsrSentenceConfig& InConfig);
    static FString ToJsonString(const FZLAsrFileConfig& InConfig);

    static bool ParseJsonObject(const FString& Json, TSharedPtr<FJsonObject>& OutObj);
    static FZLAsrSegmentResult ParseRealtimeSegment(const FString& Json);
    static FZLAsrRecognitionResult ParseRecognitionResult(const FString& Json);
    static FZLAsrError MakeErrorFromNativeCode(int32 NativeCode, const FString& Message, const FString& Raw);
};
