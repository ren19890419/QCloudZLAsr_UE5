#pragma once
#include "CoreMinimal.h"
#include "ZLAsrTypes.generated.h"

UENUM(BlueprintType)
enum class EZLAsrAuthMode : uint8
{
    Direct,
    STS
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

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    EZLAsrAuthMode AuthMode = EZLAsrAuthMode::Direct;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString AppID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString SecretID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString SecretKey;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Token;
};

USTRUCT(BlueprintType)
struct FZLAsrRealtimeConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString EngineModelType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 NeedVad = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString HotwordID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString CustomizationID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    float NoiseThreshold = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 MaxSpeakTime = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bEnableVolume = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bEnableSilenceDetect = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 SilenceTimeoutMs = 5000;
};

USTRUCT(BlueprintType)
struct FZLAsrSentenceConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString EngSerViceType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString VoiceFormat = TEXT("wav");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString HotwordID;
};

USTRUCT(BlueprintType)
struct FZLAsrFileConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FZLAsrAuthConfig Auth;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString EngineModelType = TEXT("16k_zh");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString VoiceFormat = TEXT("mp3");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterDirty = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterModal = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FilterPunc = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 ConvertNumMode = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 SpeakerDiarization = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 FirstChannelOnly = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 WordInfo = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString CustomizationID;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString HotwordID;
};

USTRUCT(BlueprintType)
struct FZLAsrSegmentResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    FString Text;

    UPROPERTY(BlueprintReadOnly)
    int32 Seq = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 SliceType = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 StartTime = 0;

    UPROPERTY(BlueprintReadOnly)
    int32 EndTime = 0;

    UPROPERTY(BlueprintReadOnly)
    FString VoiceId;

    UPROPERTY(BlueprintReadOnly)
    FString Message;

    UPROPERTY(BlueprintReadOnly)
    FString RawJson;
};

USTRUCT(BlueprintType)
struct FZLAsrRecognitionResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    bool bSuccess = false;

    UPROPERTY(BlueprintReadOnly)
    FString Text;

    UPROPERTY(BlueprintReadOnly)
    FString RawJson;

    UPROPERTY(BlueprintReadOnly)
    int32 StatusCode = 0;

    UPROPERTY(BlueprintReadOnly)
    FString RequestId;
};

USTRUCT(BlueprintType)
struct FZLAsrError
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    EZLAsrErrorCode Code = EZLAsrErrorCode::None;

    UPROPERTY(BlueprintReadOnly)
    int32 NativeCode = 0;

    UPROPERTY(BlueprintReadOnly)
    FString Message;

    UPROPERTY(BlueprintReadOnly)
    FString Raw;
};
