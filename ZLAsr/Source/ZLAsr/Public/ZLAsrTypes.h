#pragma once

#include "CoreMinimal.h"
#include "ZLAsrTypes.generated.h"

UENUM(BlueprintType)
enum class EZLAsrAuthMode : uint8
{
    Direct UMETA(DisplayName="Direct"),
    STS UMETA(DisplayName="STS")
};

UENUM(BlueprintType)
enum class EZLAsrTaskType : uint8
{
    Realtime,
    Sentence,
    File
};

UENUM(BlueprintType)
enum class EZLAsrErrorCode : uint8
{
    None,
    Unknown,
    Network,
    Timeout,
    MicInitFailed,
    MicStartFailed,
    PermissionDenied,
    InvalidParameter,
    AuthFailed,
    ServerError,
    Cancelled,
    DataSourceError
};

USTRUCT(BlueprintType)
struct FZLAsrAuthConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    EZLAsrAuthMode AuthMode = EZLAsrAuthMode::Direct;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString AppID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString SecretID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString SecretKey;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString Token;
};

USTRUCT(BlueprintType)
struct FZLAsrRealtimeConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString EngineModelType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 NeedVad = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString HotwordID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString CustomizationID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    float NoiseThreshold = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 MaxSpeakTime = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    bool bEnableVolume = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    bool bEnableSilenceDetect = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 SilenceTimeoutMs = 5000;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    bool bSaveAudioToFile = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString SaveAudioPath;
};

USTRUCT(BlueprintType)
struct FZLAsrSentenceConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString EngSerViceType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString VoiceFormat = TEXT("wav");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString HotwordID;
};

USTRUCT(BlueprintType)
struct FZLAsrFileConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString EngineModelType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString VoiceFormat = TEXT("mp3");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 SpeakerDiarization = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 FirstChannelOnly = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString CustomizationID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="ZLAsr")
    FString HotwordID;
};

USTRUCT(BlueprintType)
struct FZLAsrSegmentResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString Text;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 Seq = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 SliceType = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 StartTime = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 EndTime = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString VoiceId;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString Message;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString RawJson;
};

USTRUCT(BlueprintType)
struct FZLAsrRecognitionResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    bool bSuccess = false;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString Text;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString RawJson;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 StatusCode = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString RequestId;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    TArray<FZLAsrSegmentResult> Segments;
};

USTRUCT(BlueprintType)
struct FZLAsrError
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    EZLAsrErrorCode Code = EZLAsrErrorCode::None;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    int32 NativeCode = 0;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString Message;

    UPROPERTY(BlueprintReadOnly, Category="ZLAsr")
    FString Raw;
};
