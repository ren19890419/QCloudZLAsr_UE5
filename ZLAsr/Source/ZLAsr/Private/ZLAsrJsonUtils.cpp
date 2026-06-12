#include "ZLAsrJsonUtils.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

static TSharedPtr<FJsonObject> MakeAuthObject(const FZLAsrAuthConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetStringField(TEXT("AppID"), InConfig.AppID);
    Obj->SetStringField(TEXT("SecretID"), InConfig.SecretID);
    Obj->SetStringField(TEXT("SecretKey"), InConfig.SecretKey);
    Obj->SetStringField(TEXT("Token"), InConfig.Token);
    Obj->SetStringField(TEXT("AuthMode"), StaticEnum<EZLAsrAuthMode>()->GetNameStringByValue((int64)InConfig.AuthMode));
    return Obj;
}

template<typename TWriterFactory>
static FString WriteObjectToString(const TSharedPtr<FJsonObject>& Obj)
{
    FString Out;
    auto Writer = TJsonWriterFactory<TCHAR, TWriterFactory>::Create(&Out);
    FJsonSerializer::Serialize(Obj.ToSharedRef(), Writer);
    return Out;
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrAuthConfig& InConfig)
{
    return WriteObjectToString<TCondensedJsonPrintPolicy<TCHAR>>(MakeAuthObject(InConfig));
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrRealtimeConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuthObject(InConfig.Auth));
    Obj->SetStringField(TEXT("EngineModelType"), InConfig.EngineModelType);
    Obj->SetNumberField(TEXT("FilterDirty"), InConfig.FilterDirty);
    Obj->SetNumberField(TEXT("FilterModal"), InConfig.FilterModal);
    Obj->SetNumberField(TEXT("FilterPunc"), InConfig.FilterPunc);
    Obj->SetNumberField(TEXT("ConvertNumMode"), InConfig.ConvertNumMode);
    Obj->SetNumberField(TEXT("NeedVad"), InConfig.NeedVad);
    Obj->SetNumberField(TEXT("WordInfo"), InConfig.WordInfo);
    Obj->SetStringField(TEXT("HotwordID"), InConfig.HotwordID);
    Obj->SetStringField(TEXT("CustomizationID"), InConfig.CustomizationID);
    Obj->SetNumberField(TEXT("NoiseThreshold"), InConfig.NoiseThreshold);
    Obj->SetNumberField(TEXT("MaxSpeakTime"), InConfig.MaxSpeakTime);
    Obj->SetBoolField(TEXT("EnableVolume"), InConfig.bEnableVolume);
    Obj->SetBoolField(TEXT("EnableSilenceDetect"), InConfig.bEnableSilenceDetect);
    Obj->SetNumberField(TEXT("SilenceTimeoutMs"), InConfig.SilenceTimeoutMs);
    Obj->SetBoolField(TEXT("SaveAudioToFile"), InConfig.bSaveAudioToFile);
    Obj->SetStringField(TEXT("SaveAudioPath"), InConfig.SaveAudioPath);
    return WriteObjectToString<TCondensedJsonPrintPolicy<TCHAR>>(Obj);
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrSentenceConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuthObject(InConfig.Auth));
    Obj->SetStringField(TEXT("EngSerViceType"), InConfig.EngSerViceType);
    Obj->SetStringField(TEXT("VoiceFormat"), InConfig.VoiceFormat);
    Obj->SetNumberField(TEXT("FilterDirty"), InConfig.FilterDirty);
    Obj->SetNumberField(TEXT("FilterModal"), InConfig.FilterModal);
    Obj->SetNumberField(TEXT("FilterPunc"), InConfig.FilterPunc);
    Obj->SetNumberField(TEXT("ConvertNumMode"), InConfig.ConvertNumMode);
    Obj->SetNumberField(TEXT("WordInfo"), InConfig.WordInfo);
    Obj->SetStringField(TEXT("HotwordID"), InConfig.HotwordID);
    return WriteObjectToString<TCondensedJsonPrintPolicy<TCHAR>>(Obj);
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrFileConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuthObject(InConfig.Auth));
    Obj->SetStringField(TEXT("EngineModelType"), InConfig.EngineModelType);
    Obj->SetStringField(TEXT("VoiceFormat"), InConfig.VoiceFormat);
    Obj->SetNumberField(TEXT("FilterDirty"), InConfig.FilterDirty);
    Obj->SetNumberField(TEXT("FilterModal"), InConfig.FilterModal);
    Obj->SetNumberField(TEXT("FilterPunc"), InConfig.FilterPunc);
    Obj->SetNumberField(TEXT("ConvertNumMode"), InConfig.ConvertNumMode);
    Obj->SetNumberField(TEXT("SpeakerDiarization"), InConfig.SpeakerDiarization);
    Obj->SetNumberField(TEXT("FirstChannelOnly"), InConfig.FirstChannelOnly);
    Obj->SetNumberField(TEXT("WordInfo"), InConfig.WordInfo);
    Obj->SetStringField(TEXT("CustomizationID"), InConfig.CustomizationID);
    Obj->SetStringField(TEXT("HotwordID"), InConfig.HotwordID);
    return WriteObjectToString<TCondensedJsonPrintPolicy<TCHAR>>(Obj);
}

bool FZLAsrJsonUtils::ParseJsonObject(const FString& Json, TSharedPtr<FJsonObject>& OutObj)
{
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Json);
    return FJsonSerializer::Deserialize(Reader, OutObj) && OutObj.IsValid();
}

FZLAsrSegmentResult FZLAsrJsonUtils::ParseRealtimeSegment(const FString& Json)
{
    FZLAsrSegmentResult Result;
    Result.RawJson = Json;

    TSharedPtr<FJsonObject> Obj;
    if (!ParseJsonObject(Json, Obj))
    {
        Result.Message = TEXT("Invalid Json");
        return Result;
    }

    Result.Text = Obj->GetStringField(TEXT("text"));
    Result.Seq = Obj->HasField(TEXT("seq")) ? (int32)Obj->GetIntegerField(TEXT("seq")) : 0;
    Result.SliceType = Obj->HasField(TEXT("sliceType")) ? (int32)Obj->GetIntegerField(TEXT("sliceType")) : (Obj->HasField(TEXT("slice_type")) ? (int32)Obj->GetIntegerField(TEXT("slice_type")) : 0);
    Result.StartTime = Obj->HasField(TEXT("startTime")) ? (int32)Obj->GetIntegerField(TEXT("startTime")) : 0;
    Result.EndTime = Obj->HasField(TEXT("endTime")) ? (int32)Obj->GetIntegerField(TEXT("endTime")) : 0;
    Result.VoiceId = Obj->HasField(TEXT("voiceId")) ? Obj->GetStringField(TEXT("voiceId")) : TEXT("");
    Result.Message = Obj->HasField(TEXT("message")) ? Obj->GetStringField(TEXT("message")) : TEXT("");
    return Result;
}

FZLAsrRecognitionResult FZLAsrJsonUtils::ParseRecognitionResult(const FString& Json)
{
    FZLAsrRecognitionResult Result;
    Result.RawJson = Json;
    Result.bSuccess = true;

    TSharedPtr<FJsonObject> Obj;
    if (!ParseJsonObject(Json, Obj))
    {
        Result.bSuccess = false;
        Result.Text = Json;
        return Result;
    }

    if (Obj->HasField(TEXT("text")))
    {
        Result.Text = Obj->GetStringField(TEXT("text"));
    }
    else if (Obj->HasField(TEXT("result")))
    {
        Result.Text = Obj->GetStringField(TEXT("result"));
    }
    else
    {
        Result.Text = Json;
    }

    if (Obj->HasField(TEXT("request_id")))
    {
        Result.RequestId = Obj->GetStringField(TEXT("request_id"));
    }
    else if (Obj->HasField(TEXT("requestId")))
    {
        Result.RequestId = Obj->GetStringField(TEXT("requestId"));
    }

    if (Obj->HasField(TEXT("code")))
    {
        Result.StatusCode = (int32)Obj->GetIntegerField(TEXT("code"));
        Result.bSuccess = Result.StatusCode == 0;
    }

    return Result;
}

FZLAsrError FZLAsrJsonUtils::MakeErrorFromNativeCode(int32 NativeCode, const FString& Message, const FString& Raw)
{
    FZLAsrError Err;
    Err.NativeCode = NativeCode;
    Err.Message = Message;
    Err.Raw = Raw;

    switch (NativeCode)
    {
        case -100: Err.Code = EZLAsrErrorCode::MicInitFailed; break;
        case -101: Err.Code = EZLAsrErrorCode::MicStartFailed; break;
        case -102: Err.Code = EZLAsrErrorCode::MicStartFailed; break;
        case -103: Err.Code = EZLAsrErrorCode::MicInitFailed; break;
        case -104: Err.Code = EZLAsrErrorCode::DataSourceError; break;
        case -105: Err.Code = EZLAsrErrorCode::InvalidParameter; break;
        case -106: Err.Code = EZLAsrErrorCode::Network; break;
        case 1: Err.Code = EZLAsrErrorCode::Network; break;
        case 2: Err.Code = EZLAsrErrorCode::ServerError; break;
        case 3: Err.Code = EZLAsrErrorCode::AuthFailed; break;
        case 4: Err.Code = EZLAsrErrorCode::InvalidParameter; break;
        case 5: Err.Code = EZLAsrErrorCode::Cancelled; break;
        case 7: Err.Code = EZLAsrErrorCode::DataSourceError; break;
        default: Err.Code = EZLAsrErrorCode::Unknown; break;
    }
    return Err;
}
