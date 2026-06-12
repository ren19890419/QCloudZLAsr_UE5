#include "ZLAsrJsonUtils.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

static TSharedPtr<FJsonObject> MakeAuth(const FZLAsrAuthConfig& InAuth)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetStringField(TEXT("AppID"), InAuth.AppID);
    Obj->SetStringField(TEXT("SecretID"), InAuth.SecretID);
    Obj->SetStringField(TEXT("SecretKey"), InAuth.SecretKey);
    Obj->SetStringField(TEXT("Token"), InAuth.Token);
    return Obj;
}

static FString SerializeObj(TSharedPtr<FJsonObject> Obj)
{
    FString Out;
    auto Writer = TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&Out);
    FJsonSerializer::Serialize(Obj.ToSharedRef(), Writer);
    return Out;
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrRealtimeConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuth(InConfig.Auth));
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
    return SerializeObj(Obj);
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrSentenceConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuth(InConfig.Auth));
    Obj->SetStringField(TEXT("EngSerViceType"), InConfig.EngSerViceType);
    Obj->SetStringField(TEXT("VoiceFormat"), InConfig.VoiceFormat);
    Obj->SetNumberField(TEXT("FilterDirty"), InConfig.FilterDirty);
    Obj->SetNumberField(TEXT("FilterModal"), InConfig.FilterModal);
    Obj->SetNumberField(TEXT("FilterPunc"), InConfig.FilterPunc);
    Obj->SetNumberField(TEXT("ConvertNumMode"), InConfig.ConvertNumMode);
    Obj->SetNumberField(TEXT("WordInfo"), InConfig.WordInfo);
    Obj->SetStringField(TEXT("HotwordID"), InConfig.HotwordID);
    return SerializeObj(Obj);
}

FString FZLAsrJsonUtils::ToJsonString(const FZLAsrFileConfig& InConfig)
{
    TSharedPtr<FJsonObject> Obj = MakeShared<FJsonObject>();
    Obj->SetObjectField(TEXT("Auth"), MakeAuth(InConfig.Auth));
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
    return SerializeObj(Obj);
}

bool FZLAsrJsonUtils::ParseJsonObject(const FString& Json, TSharedPtr<FJsonObject>& OutObj)
{
    TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Json);
    return FJsonSerializer::Deserialize(Reader, OutObj) && OutObj.IsValid();
}

FZLAsrSegmentResult FZLAsrJsonUtils::ParseRealtimeSegment(const FString& Json)
{
    FZLAsrSegmentResult R;
    R.RawJson = Json;
    TSharedPtr<FJsonObject> Obj;
    if (!ParseJsonObject(Json, Obj))
    {
        R.Message = TEXT("Invalid Json");
        return R;
    }
    if (Obj->HasField(TEXT("text"))) R.Text = Obj->GetStringField(TEXT("text"));
    if (Obj->HasField(TEXT("seq"))) R.Seq = (int32)Obj->GetIntegerField(TEXT("seq"));
    if (Obj->HasField(TEXT("sliceType"))) R.SliceType = (int32)Obj->GetIntegerField(TEXT("sliceType"));
    if (Obj->HasField(TEXT("startTime"))) R.StartTime = (int32)Obj->GetIntegerField(TEXT("startTime"));
    if (Obj->HasField(TEXT("endTime"))) R.EndTime = (int32)Obj->GetIntegerField(TEXT("endTime"));
    if (Obj->HasField(TEXT("voiceId"))) R.VoiceId = Obj->GetStringField(TEXT("voiceId"));
    if (Obj->HasField(TEXT("message"))) R.Message = Obj->GetStringField(TEXT("message"));
    return R;
}

FZLAsrRecognitionResult FZLAsrJsonUtils::ParseRecognitionResult(const FString& Json)
{
    FZLAsrRecognitionResult R;
    R.RawJson = Json;
    R.bSuccess = true;
    TSharedPtr<FJsonObject> Obj;
    if (!ParseJsonObject(Json, Obj))
    {
        R.bSuccess = false;
        R.Text = Json;
        return R;
    }
    if (Obj->HasField(TEXT("text"))) R.Text = Obj->GetStringField(TEXT("text"));
    else if (Obj->HasField(TEXT("result"))) R.Text = Obj->GetStringField(TEXT("result"));
    if (Obj->HasField(TEXT("request_id"))) R.RequestId = Obj->GetStringField(TEXT("request_id"));
    if (Obj->HasField(TEXT("code")))
    {
        R.StatusCode = (int32)Obj->GetIntegerField(TEXT("code"));
        R.bSuccess = R.StatusCode == 0;
    }
    return R;
}

FZLAsrError FZLAsrJsonUtils::MakeErrorFromNativeCode(int32 NativeCode, const FString& Message, const FString& Raw)
{
    FZLAsrError E;
    E.NativeCode = NativeCode;
    E.Message = Message;
    E.Raw = Raw;
    switch (NativeCode)
    {
        case -100: E.Code = EZLAsrErrorCode::MicInitFailed; break;
        case -101: E.Code = EZLAsrErrorCode::MicStartFailed; break;
        case -104: E.Code = EZLAsrErrorCode::DataSourceError; break;
        case -105: E.Code = EZLAsrErrorCode::InvalidParameter; break;
        case -106: E.Code = EZLAsrErrorCode::Network; break;
        case 1: E.Code = EZLAsrErrorCode::Network; break;
        case 2: E.Code = EZLAsrErrorCode::ServerError; break;
        case 3: E.Code = EZLAsrErrorCode::AuthFailed; break;
        case 4: E.Code = EZLAsrErrorCode::InvalidParameter; break;
        case 5: E.Code = EZLAsrErrorCode::Cancelled; break;
        case 7: E.Code = EZLAsrErrorCode::DataSourceError; break;
        default: E.Code = EZLAsrErrorCode::Unknown; break;
    }
    return E;
}
