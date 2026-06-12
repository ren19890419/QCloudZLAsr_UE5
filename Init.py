import os
from textwrap import dedent

base = "C:\Users\thinker\Desktop\ZLAsr"
if not os.path.exists(base):
    os.makedirs(base, exist_ok=True)

def write(rel, content):
    path = os.path.join(base, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(dedent(content).lstrip("\n"))

# 1) Improve uplugin
write("ZLAsr.uplugin", r'''
{
  "FileVersion": 3,
  "Version": 2,
  "VersionName": "0.2.0",
  "FriendlyName": "ZLAsr",
  "Description": "UE5 speech recognition plugin for Android/iOS/Harmony based on Tencent Cloud ASR SDKs.",
  "Category": "Audio",
  "CreatedBy": "OpenAI",
  "CanContainContent": false,
  "IsBetaVersion": true,
  "Installed": false,
  "Modules": [
    {
      "Name": "ZLAsr",
      "Type": "Runtime",
      "LoadingPhase": "Default"
    }
  ],
  "SupportedTargetPlatforms": [
    "Android",
    "IOS"
  ]
}
''')

# 2) Build.cs
write("Source/ZLAsr/ZLAsr.Build.cs", r'''
using UnrealBuildTool;
using System.IO;

public class ZLAsr : ModuleRules
{
    public ZLAsr(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp17;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Projects",
            "Json",
            "JsonUtilities"
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "Slate",
            "SlateCore"
        });

        PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));
        PrivateIncludePaths.Add(Path.Combine(ModuleDirectory, "Private"));

        if (Target.Platform == UnrealTargetPlatform.Android)
        {
            PrivateDependencyModuleNames.Add("Launch");
            AdditionalPropertiesForReceipt.Add("AndroidPlugin", Path.Combine(ModuleDirectory, "ZLAsr_Android_UPL.xml"));
        }

        if (Target.Platform == UnrealTargetPlatform.IOS)
        {
            PublicFrameworks.AddRange(new string[]
            {
                "AVFoundation",
                "AudioToolbox"
            });

            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudRealTime",
                    "../ThirdParty/IOS/QCloudRealTime.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudOneSentence",
                    "../ThirdParty/IOS/QCloudOneSentence.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "QCloudFileRecognizer",
                    "../ThirdParty/IOS/QCloudFileRecognizer.xcframework.zip"
                )
            );
            PublicAdditionalFrameworks.Add(
                new Framework(
                    "VoiceCommon",
                    "../ThirdParty/IOS/VoiceCommon.framework.zip"
                )
            );
        }
    }
}
''')

# 3) Android UPL with java copy and manifest/plist-like config
write("Source/ZLAsr/ZLAsr_Android_UPL.xml", r'''
<?xml version="1.0" encoding="utf-8"?>
<root xmlns:android="http://schemas.android.com/apk/res/android">
    <init>
        <log text="ZLAsr UPL init"/>
    </init>

    <androidManifestUpdates>
        <addPermission android:name="android.permission.RECORD_AUDIO"/>
        <addPermission android:name="android.permission.INTERNET"/>
        <addPermission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    </androidManifestUpdates>

    <gameActivityImportAdditions>
        <insert>
import com.zl.asr.ZLAsrBridge;
        </insert>
    </gameActivityImportAdditions>

    <gameActivityOnCreateAdditions>
        <insert>
            ZLAsrBridge.initialize(this);
        </insert>
    </gameActivityOnCreateAdditions>

    <buildGradleAdditions>
        <insert>
dependencies {
    implementation(name: 'asr-realtime-release', ext: 'aar')
    implementation(name: 'asr-one-sentence-release', ext: 'aar')
    implementation(name: 'asr-file-recognize-release', ext: 'aar')
    implementation 'com.squareup.okhttp3:okhttp:4.2.2'
    implementation 'com.google.code.gson:gson:2.8.5'
}
        </insert>
    </buildGradleAdditions>

    <AARImports>
        <insertValue value="libs/asr-realtime-release.aar"/>
        <insertValue value="libs/asr-one-sentence-release.aar"/>
        <insertValue value="libs/asr-file-recognize-release.aar"/>
    </AARImports>

    <resourceCopies>
        <copyDir src="$S(PluginDir)/Source/ThirdParty/Android/Java" dst="$S(BuildDir)/src"/>
    </resourceCopies>
</root>
''')

# 4) New common utils headers/cpps
write("Source/ZLAsr/Public/ZLAsrJsonUtils.h", r'''
#pragma once
#include "CoreMinimal.h"
#include "Dom/JsonObject.h"
#include "ZLAsrTypes.h"

class ZLASR_API FZLAsrJsonUtils
{
public:
    static FString ToJsonString(const FZLAsrAuthConfig& InConfig);
    static FString ToJsonString(const FZLAsrRealtimeConfig& InConfig);
    static FString ToJsonString(const FZLAsrSentenceConfig& InConfig);
    static FString ToJsonString(const FZLAsrFileConfig& InConfig);

    static bool ParseJsonObject(const FString& Json, TSharedPtr<FJsonObject>& OutObj);
    static FZLAsrSegmentResult ParseRealtimeSegment(const FString& Json);
    static FZLAsrRecognitionResult ParseRecognitionResult(const FString& Json);
    static FZLAsrError MakeErrorFromNativeCode(int32 NativeCode, const FString& Message, const FString& Raw);
};
''')

write("Source/ZLAsr/Private/ZLAsrJsonUtils.cpp", r'''
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
''')

write("Source/ZLAsr/Public/ZLAsrBridgeRegistry.h", r'''
#pragma once
#include "CoreMinimal.h"
#include "ZLAsrPlatformBridge.h"

class ZLASR_API FZLAsrBridgeRegistry
{
public:
    static FZLAsrBridgeRegistry& Get();

    void Register(const FString& TaskId, IZLAsrTaskSink* Sink);
    void Unregister(const FString& TaskId);
    IZLAsrTaskSink* Find(const FString& TaskId);

private:
    FCriticalSection Mutex;
    TMap<FString, IZLAsrTaskSink*> Map;
};
''')

write("Source/ZLAsr/Private/ZLAsrBridgeRegistry.cpp", r'''
#include "ZLAsrBridgeRegistry.h"

FZLAsrBridgeRegistry& FZLAsrBridgeRegistry::Get()
{
    static FZLAsrBridgeRegistry Instance;
    return Instance;
}

void FZLAsrBridgeRegistry::Register(const FString& TaskId, IZLAsrTaskSink* Sink)
{
    FScopeLock Lock(&Mutex);
    Map.Add(TaskId, Sink);
}

void FZLAsrBridgeRegistry::Unregister(const FString& TaskId)
{
    FScopeLock Lock(&Mutex);
    Map.Remove(TaskId);
}

IZLAsrTaskSink* FZLAsrBridgeRegistry::Find(const FString& TaskId)
{
    FScopeLock Lock(&Mutex);
    if (IZLAsrTaskSink** Found = Map.Find(TaskId))
    {
        return *Found;
    }
    return nullptr;
}
''')

# 5) Android bridge
write("Source/ZLAsr/Private/ZLAsrAndroidBridge.cpp", r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"
#include "Async/Async.h"

#if PLATFORM_ANDROID
#include "Android/AndroidApplication.h"
#include "Android/AndroidJNI.h"
#include "Android/AndroidJavaEnv.h"

static jclass GBridgeClass = nullptr;
static jmethodID GRealtimeCtor = nullptr;
static jmethodID GSentenceCtor = nullptr;
static jmethodID GFileCtor = nullptr;

static jmethodID GRealtimeStart = nullptr;
static jmethodID GRealtimeStop = nullptr;
static jmethodID GRealtimeCancel = nullptr;

static jmethodID GSentenceUrl = nullptr;
static jmethodID GSentenceData = nullptr;
static jmethodID GSentenceRecorderStart = nullptr;
static jmethodID GSentenceRecorderStop = nullptr;

static jmethodID GFilePath = nullptr;
static jmethodID GFileData = nullptr;

class FZLAsrAndroidBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        CacheJNI();
        return true;
    }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);

        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GRealtimeCtor);
        if (!Proxy) return false;

        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));

        const bool bOk = Env->CallBooleanMethod(Proxy, GRealtimeStart, JTaskId, JConfig);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

    virtual void StopRealtime(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GRealtimeCtor);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Proxy, GRealtimeStop, JTaskId);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(Proxy);
    }

    virtual void CancelRealtime(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GRealtimeCtor);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Proxy, GRealtimeCancel, JTaskId);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(Proxy);
    }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GSentenceCtor);
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jstring JUrl = Env->NewStringUTF(TCHAR_TO_UTF8(*Url));
        bool bOk = Env->CallBooleanMethod(Proxy, GSentenceUrl, JTaskId, JConfig, JUrl);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(JUrl);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *FilePath))
        {
            return false;
        }
        return StartSentenceFromMemory(TaskId, Config, Bytes);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GSentenceCtor);
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jbyteArray Arr = Env->NewByteArray(AudioData.Num());
        if (AudioData.Num() > 0)
        {
            Env->SetByteArrayRegion(Arr, 0, AudioData.Num(), reinterpret_cast<const jbyte*>(AudioData.GetData()));
        }
        bool bOk = Env->CallBooleanMethod(Proxy, GSentenceData, JTaskId, JConfig, Arr);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(Arr);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GSentenceCtor);
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        bool bOk = Env->CallBooleanMethod(Proxy, GSentenceRecorderStart, JTaskId, JConfig);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

    virtual void StopSentenceRecorder(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GSentenceCtor);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Proxy, GSentenceRecorderStop, JTaskId);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(Proxy);
    }

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GFileCtor);
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jstring JPath = Env->NewStringUTF(TCHAR_TO_UTF8(*FilePath));
        bool bOk = Env->CallBooleanMethod(Proxy, GFilePath, JTaskId, JConfig, JPath);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(JPath);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Proxy = Env->NewObject(GBridgeClass, GFileCtor);
        FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTaskId = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JConfig = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jbyteArray Arr = Env->NewByteArray(AudioData.Num());
        if (AudioData.Num() > 0)
        {
            Env->SetByteArrayRegion(Arr, 0, AudioData.Num(), reinterpret_cast<const jbyte*>(AudioData.GetData()));
        }
        bool bOk = Env->CallBooleanMethod(Proxy, GFileData, JTaskId, JConfig, Arr);
        Env->DeleteLocalRef(JTaskId);
        Env->DeleteLocalRef(JConfig);
        Env->DeleteLocalRef(Arr);
        Env->DeleteLocalRef(Proxy);
        return bOk;
    }

private:
    bool CacheJNI()
    {
        if (GBridgeClass) return true;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jclass LocalClass = FAndroidApplication::FindJavaClass("com/zl/asr/ZLAsrNativeEntry");
        if (!LocalClass) return false;
        GBridgeClass = (jclass)Env->NewGlobalRef(LocalClass);
        Env->DeleteLocalRef(LocalClass);

        GRealtimeCtor = Env->GetMethodID(GBridgeClass, "<init>", "()V");
        GSentenceCtor = GRealtimeCtor;
        GFileCtor = GRealtimeCtor;

        GRealtimeStart = Env->GetMethodID(GBridgeClass, "startRealtime", "(Ljava/lang/String;Ljava/lang/String;)Z");
        GRealtimeStop = Env->GetMethodID(GBridgeClass, "stopRealtime", "(Ljava/lang/String;)V");
        GRealtimeCancel = Env->GetMethodID(GBridgeClass, "cancelRealtime", "(Ljava/lang/String;)V");

        GSentenceUrl = Env->GetMethodID(GBridgeClass, "startSentenceUrl", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z");
        GSentenceData = Env->GetMethodID(GBridgeClass, "startSentenceData", "(Ljava/lang/String;Ljava/lang/String;[B)Z");
        GSentenceRecorderStart = Env->GetMethodID(GBridgeClass, "startSentenceRecorder", "(Ljava/lang/String;Ljava/lang/String;)Z");
        GSentenceRecorderStop = Env->GetMethodID(GBridgeClass, "stopSentenceRecorder", "(Ljava/lang/String;)V");

        GFilePath = Env->GetMethodID(GBridgeClass, "startFilePath", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z");
        GFileData = Env->GetMethodID(GBridgeClass, "startFileData", "(Ljava/lang/String;Ljava/lang/String;[B)Z");
        return GRealtimeStart && GRealtimeStop && GRealtimeCancel && GSentenceUrl && GSentenceData && GSentenceRecorderStart && GSentenceRecorderStop && GFilePath && GFileData;
    }

    void Register(const FString& TaskId)
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
        }
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

static FString JStringToFString(JNIEnv* Env, jstring Str)
{
    if (!Str) return FString();
    const char* Chars = Env->GetStringUTFChars(Str, 0);
    FString Out(UTF8_TO_TCHAR(Chars));
    Env->ReleaseStringUTFChars(Str, Chars);
    return Out;
}

extern "C"
{
    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnRealtimeSlice(JNIEnv* Env, jclass, jstring TaskId, jstring Json)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Payload = JStringToFString(Env, Json);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleRealtimeSlice(FZLAsrJsonUtils::ParseRealtimeSegment(Payload));
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnRealtimeSegment(JNIEnv* Env, jclass, jstring TaskId, jstring Json)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Payload = JStringToFString(Env, Json);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleRealtimeSegment(FZLAsrJsonUtils::ParseRealtimeSegment(Payload));
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnRealtimeFinal(JNIEnv* Env, jclass, jstring TaskId, jstring Json)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Payload = JStringToFString(Env, Json);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleRealtimeFinal(FZLAsrJsonUtils::ParseRecognitionResult(Payload));
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnSentenceResult(JNIEnv* Env, jclass, jstring TaskId, jstring Json)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Payload = JStringToFString(Env, Json);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleSentenceResult(FZLAsrJsonUtils::ParseRecognitionResult(Payload));
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnFileResult(JNIEnv* Env, jclass, jstring TaskId, jstring Json)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Payload = JStringToFString(Env, Json);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleFileResult(FZLAsrJsonUtils::ParseRecognitionResult(Payload));
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnVolume(JNIEnv* Env, jclass, jstring TaskId, jfloat Volume)
    {
        FString Id = JStringToFString(Env, TaskId);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleVolume((float)Volume);
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnSilence(JNIEnv* Env, jclass, jstring TaskId)
    {
        FString Id = JStringToFString(Env, TaskId);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleSilence();
        }
    }

    JNIEXPORT void JNICALL Java_com_zl_asr_ZLAsrBridge_nativeOnError(JNIEnv* Env, jclass, jstring TaskId, jint NativeCode, jstring Message, jstring Raw)
    {
        FString Id = JStringToFString(Env, TaskId);
        FString Msg = JStringToFString(Env, Message);
        FString RawStr = JStringToFString(Env, Raw);
        if (IZLAsrTaskSink* Sink = FZLAsrBridgeRegistry::Get().Find(Id))
        {
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode((int32)NativeCode, Msg, RawStr));
        }
    }
}

TSharedPtr<IZLAsrPlatformBridge> CreateAndroidBridge()
{
    return MakeShared<FZLAsrAndroidBridge>();
}
#endif
''')

# 6) iOS bridge skeleton closer to compile
write("Source/ZLAsr/Private/ZLAsrIOSBridge.mm", r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

#if PLATFORM_IOS
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

// 下面这些头文件需要用户放入真实腾讯云 iOS SDK 后才可编译通过 [4][5][6]
// #import <QCloudRealTime/QCloudRealTimeRecognizer.h>
// #import <QCloudRealTime/QCloudConfig.h>
// #import <QCloudOneSentence/QCloudSentenceRecognizer.h>
// #import <QCloudFileRecognizer/QCloudFlashFileRecognizer.h>

class FZLAsrIOSBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        return true;
    }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual void StopRealtime(const FString& TaskId) override {}
    virtual void CancelRealtime(const FString& TaskId) override {}

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath))
        {
            return false;
        }
        return StartSentenceFromMemory(TaskId, Config, Data);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence memory bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS sentence recorder bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual void StopSentenceRecorder(const FString& TaskId) override {}

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS file bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("iOS file data bridge requires actual Tencent iOS SDK frameworks linked"), TEXT("")));
        }
        return false;
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge()
{
    return MakeShared<FZLAsrIOSBridge>();
}
#endif
''')

# 7) Harmony bridge stub closer to integration
write("Source/ZLAsr/Private/ZLAsrHarmonyBridge.cpp", r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

class FZLAsrHarmonyBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        return true;
    }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) override
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, TEXT("Harmony bridge needs UE<->ArkTS native bridge integration"), TEXT("")));
        }
        return false;
    }

    virtual void StopRealtime(const FString& TaskId) override {}
    virtual void CancelRealtime(const FString& TaskId) override {}
    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override { return StartUnsupported(TaskId); }
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override { return StartUnsupported(TaskId); }
    virtual void StopSentenceRecorder(const FString& TaskId) override {}
    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override { return StartUnsupported(TaskId); }
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override { return StartUnsupported(TaskId); }

private:
    bool StartUnsupported(const FString& TaskId)
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
            Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, TEXT("Harmony bridge needs UE<->ArkTS native bridge integration"), TEXT("")));
        }
        return false;
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge()
{
    return MakeShared<FZLAsrHarmonyBridge>();
}
''')

# 8) Replace platform factory
write("Source/ZLAsr/Private/ZLAsrPlatformBridge.cpp", r'''
#include "ZLAsrPlatformBridge.h"
#include "Async/Async.h"
#include "ZLAsrJsonUtils.h"

TSharedPtr<IZLAsrPlatformBridge> CreateAndroidBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge();

class FZLAsrStubBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        return true;
    }

    virtual bool StartRealtime(const FString&, const FZLAsrRealtimeConfig&) override
    {
        if (Sink)
        {
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("Current platform bridge is unsupported on this target"), TEXT("")));
            });
        }
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString&) override {}
    virtual bool StartSentenceFromUrl(const FString&, const FZLAsrSentenceConfig&, const FString&) override { return false; }
    virtual bool StartSentenceFromFile(const FString&, const FZLAsrSentenceConfig&, const FString&) override { return false; }
    virtual bool StartSentenceFromMemory(const FString&, const FZLAsrSentenceConfig&, const TArray<uint8>&) override { return false; }
    virtual bool StartSentenceRecorder(const FString&, const FZLAsrSentenceConfig&) override { return false; }
    virtual void StopSentenceRecorder(const FString&) override {}
    virtual bool StartFileRecognizePath(const FString&, const FZLAsrFileConfig&, const FString&) override { return false; }
    virtual bool StartFileRecognizeData(const FString&, const FZLAsrFileConfig&, const TArray<uint8>&) override { return false; }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> FZLAsrPlatformBridgeFactory::Create()
{
#if PLATFORM_ANDROID
    if (TSharedPtr<IZLAsrPlatformBridge> Bridge = CreateAndroidBridge())
    {
        return Bridge;
    }
#elif PLATFORM_IOS
    if (TSharedPtr<IZLAsrPlatformBridge> Bridge = CreateIOSBridge())
    {
        return Bridge;
    }
#else
    if (TSharedPtr<IZLAsrPlatformBridge> Bridge = CreateHarmonyBridge())
    {
        return Bridge;
    }
#endif
    return MakeShared<FZLAsrStubBridge>();
}
''')

# 9) Update recognizers to register/unregister
write("Source/ZLAsr/Private/ZLAsrRealtimeRecognizer.cpp", r'''
#include "ZLAsrRealtimeRecognizer.h"
#include "Async/Async.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrRealtimeRecognizer::UZLAsrRealtimeRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid())
    {
        Bridge->Init(this);
    }
}

bool UZLAsrRealtimeRecognizer::StartRealtimeRecognition(const FZLAsrRealtimeConfig& Config)
{
    if (!Bridge.IsValid() || bRunning)
    {
        return false;
    }
    bRunning = Bridge->StartRealtime(TaskId, Config);
    return bRunning;
}

void UZLAsrRealtimeRecognizer::StopRealtimeRecognition()
{
    if (Bridge.IsValid())
    {
        Bridge->StopRealtime(TaskId);
    }
}

void UZLAsrRealtimeRecognizer::CancelRealtimeRecognition()
{
    bRunning = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    if (Bridge.IsValid())
    {
        Bridge->CancelRealtime(TaskId);
    }
}

void UZLAsrRealtimeRecognizer::HandleRealtimeSlice(const FZLAsrSegmentResult& Result)
{
    AsyncTask(ENamedThreads::GameThread, [this, Result]() { OnSlice.Broadcast(Result); });
}

void UZLAsrRealtimeRecognizer::HandleRealtimeSegment(const FZLAsrSegmentResult& Result)
{
    AsyncTask(ENamedThreads::GameThread, [this, Result]() { OnSegment.Broadcast(Result); });
}

void UZLAsrRealtimeRecognizer::HandleRealtimeFinal(const FZLAsrRecognitionResult& Result)
{
    bRunning = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Result]() { OnFinalResult.Broadcast(Result); });
}

void UZLAsrRealtimeRecognizer::HandleVolume(float Volume)
{
    AsyncTask(ENamedThreads::GameThread, [this, Volume]() { OnVolumeChanged.Broadcast(Volume); });
}

void UZLAsrRealtimeRecognizer::HandleSilence()
{
    AsyncTask(ENamedThreads::GameThread, [this]() { OnSilenceDetected.Broadcast(); });
}

void UZLAsrRealtimeRecognizer::HandleError(const FZLAsrError& Error)
{
    bRunning = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Error]() { OnError.Broadcast(Error); });
}
''')

write("Source/ZLAsr/Private/ZLAsrSentenceRecognizer.cpp", r'''
#include "ZLAsrSentenceRecognizer.h"
#include "Async/Async.h"
#include "Misc/FileHelper.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrSentenceRecognizer::UZLAsrSentenceRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid())
    {
        Bridge->Init(this);
    }
}

bool UZLAsrSentenceRecognizer::RecognizeFromUrl(const FZLAsrSentenceConfig& Config, const FString& Url)
{
    return Bridge.IsValid() ? Bridge->StartSentenceFromUrl(TaskId, Config, Url) : false;
}

bool UZLAsrSentenceRecognizer::RecognizeFromFile(const FZLAsrSentenceConfig& Config, const FString& FilePath)
{
    return Bridge.IsValid() ? Bridge->StartSentenceFromFile(TaskId, Config, FilePath) : false;
}

bool UZLAsrSentenceRecognizer::RecognizeFromMemory(const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData)
{
    return Bridge.IsValid() ? Bridge->StartSentenceFromMemory(TaskId, Config, AudioData) : false;
}

bool UZLAsrSentenceRecognizer::StartRecognizeWithRecorder(const FZLAsrSentenceConfig& Config)
{
    bRecording = Bridge.IsValid() ? Bridge->StartSentenceRecorder(TaskId, Config) : false;
    return bRecording;
}

void UZLAsrSentenceRecognizer::StopRecognizeWithRecorder()
{
    bRecording = false;
    if (Bridge.IsValid())
    {
        Bridge->StopSentenceRecorder(TaskId);
    }
}

void UZLAsrSentenceRecognizer::HandleSentenceResult(const FZLAsrRecognitionResult& Result)
{
    bRecording = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Result]() { OnResult.Broadcast(Result); });
}

void UZLAsrSentenceRecognizer::HandleVolume(float Volume)
{
    AsyncTask(ENamedThreads::GameThread, [this, Volume]() { OnVolumeChanged.Broadcast(Volume); });
}

void UZLAsrSentenceRecognizer::HandleError(const FZLAsrError& Error)
{
    bRecording = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Error]() { OnError.Broadcast(Error); });
}
''')

write("Source/ZLAsr/Private/ZLAsrFileRecognizer.cpp", r'''
#include "ZLAsrFileRecognizer.h"
#include "Async/Async.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrFileRecognizer::UZLAsrFileRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid())
    {
        Bridge->Init(this);
    }
}

bool UZLAsrFileRecognizer::RecognizeFile(const FZLAsrFileConfig& Config, const FString& FilePath)
{
    return Bridge.IsValid() ? Bridge->StartFileRecognizePath(TaskId, Config, FilePath) : false;
}

bool UZLAsrFileRecognizer::RecognizeData(const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData)
{
    return Bridge.IsValid() ? Bridge->StartFileRecognizeData(TaskId, Config, AudioData) : false;
}

void UZLAsrFileRecognizer::HandleFileResult(const FZLAsrRecognitionResult& Result)
{
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Result]() { OnResult.Broadcast(Result); });
}

void UZLAsrFileRecognizer::HandleError(const FZLAsrError& Error)
{
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    AsyncTask(ENamedThreads::GameThread, [this, Error]() { OnError.Broadcast(Error); });
}
''')

# 10) Update headers if needed
write("Source/ZLAsr/Public/ZLAsrRealtimeRecognizer.h", r'''
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrRealtimeRecognizer.generated.h"

UCLASS(BlueprintType)
class ZLASR_API UZLAsrRealtimeRecognizer : public UObject, public IZLAsrTaskSink
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

    UFUNCTION(BlueprintPure, Category="ZLAsr")
    bool IsRunning() const { return bRunning; }

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
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) override {}
    virtual void HandleFileResult(const FZLAsrRecognitionResult& Result) override {}
    virtual void HandleVolume(float Volume) override;
    virtual void HandleSilence() override;
    virtual void HandleError(const FZLAsrError& Error) override;

protected:
    FString TaskId;
    bool bRunning = false;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
''')

# 11) Android Java complete-ish entry and proxies
write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrBridge.java", r'''
package com.zl.asr;

import android.app.Activity;
import android.util.Log;

public class ZLAsrBridge {
    private static final String TAG = "ZLAsrBridge";
    private static Activity sActivity;

    public static void initialize(Activity activity) {
        sActivity = activity;
        Log.i(TAG, "initialize");
    }

    public static Activity getActivity() {
        return sActivity;
    }

    public static void onRealtimeSlice(String taskId, String json) { nativeOnRealtimeSlice(taskId, json); }
    public static void onRealtimeSegment(String taskId, String json) { nativeOnRealtimeSegment(taskId, json); }
    public static void onRealtimeFinal(String taskId, String json) { nativeOnRealtimeFinal(taskId, json); }
    public static void onSentenceResult(String taskId, String json) { nativeOnSentenceResult(taskId, json); }
    public static void onFileResult(String taskId, String json) { nativeOnFileResult(taskId, json); }
    public static void onVolume(String taskId, float volume) { nativeOnVolume(taskId, volume); }
    public static void onSilence(String taskId) { nativeOnSilence(taskId); }
    public static void onError(String taskId, int nativeCode, String message, String raw) { nativeOnError(taskId, nativeCode, message, raw); }

    private static native void nativeOnRealtimeSlice(String taskId, String json);
    private static native void nativeOnRealtimeSegment(String taskId, String json);
    private static native void nativeOnRealtimeFinal(String taskId, String json);
    private static native void nativeOnSentenceResult(String taskId, String json);
    private static native void nativeOnFileResult(String taskId, String json);
    private static native void nativeOnVolume(String taskId, float volume);
    private static native void nativeOnSilence(String taskId);
    private static native void nativeOnError(String taskId, int nativeCode, String message, String raw);
}
''')

write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrConfigParser.java", r'''
package com.zl.asr;

import org.json.JSONObject;

public class ZLAsrConfigParser {
    public static JSONObject parse(String json) throws Exception {
        return new JSONObject(json);
    }

    public static JSONObject auth(JSONObject root) throws Exception {
        return root.getJSONObject("Auth");
    }

    public static String string(JSONObject obj, String key, String def) {
        return obj.has(key) ? obj.optString(key, def) : def;
    }

    public static int integer(JSONObject obj, String key, int def) {
        return obj.has(key) ? obj.optInt(key, def) : def;
    }

    public static boolean bool(JSONObject obj, String key, boolean def) {
        return obj.has(key) ? obj.optBoolean(key, def) : def;
    }

    public static double number(JSONObject obj, String key, double def) {
        return obj.has(key) ? obj.optDouble(key, def) : def;
    }
}
''')

write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrNativeEntry.java", r'''
package com.zl.asr;

public class ZLAsrNativeEntry {
    private final ZLAsrRealtimeProxy realtimeProxy = new ZLAsrRealtimeProxy();
    private final ZLAsrSentenceProxy sentenceProxy = new ZLAsrSentenceProxy();
    private final ZLAsrFileProxy fileProxy = new ZLAsrFileProxy();

    public boolean startRealtime(String taskId, String configJson) {
        return realtimeProxy.start(taskId, configJson);
    }

    public void stopRealtime(String taskId) {
        realtimeProxy.stop(taskId);
    }

    public void cancelRealtime(String taskId) {
        realtimeProxy.cancel(taskId);
    }

    public boolean startSentenceUrl(String taskId, String configJson, String url) {
        return sentenceProxy.recognizeUrl(taskId, configJson, url);
    }

    public boolean startSentenceData(String taskId, String configJson, byte[] data) {
        return sentenceProxy.recognizeData(taskId, configJson, data);
    }

    public boolean startSentenceRecorder(String taskId, String configJson) {
        return sentenceProxy.startRecorder(taskId, configJson);
    }

    public void stopSentenceRecorder(String taskId) {
        sentenceProxy.stopRecorder(taskId);
    }

    public boolean startFilePath(String taskId, String configJson, String path) {
        return fileProxy.recognizePath(taskId, configJson, path);
    }

    public boolean startFileData(String taskId, String configJson, byte[] data) {
        return fileProxy.recognizeData(taskId, configJson, data);
    }
}
''')

write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrRealtimeProxy.java", r'''
package com.zl.asr;

import android.app.Activity;
import android.util.Log;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class ZLAsrRealtimeProxy {
    private static final String TAG = "ZLAsrRealtimeProxy";

    private final Map<String, Object> tasks = new HashMap<>();

    public boolean start(String taskId, String configJson) {
        Activity activity = ZLAsrBridge.getActivity();
        if (activity == null) {
            ZLAsrBridge.onError(taskId, -1, "Activity is null", "");
            return false;
        }

        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            JSONObject auth = ZLAsrConfigParser.auth(root);

            String appIdStr = ZLAsrConfigParser.string(auth, "AppID", "");
            String secretId = ZLAsrConfigParser.string(auth, "SecretID", "");
            String secretKey = ZLAsrConfigParser.string(auth, "SecretKey", "");
            String token = ZLAsrConfigParser.string(auth, "Token", "");

            String engineModelType = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            int filterDirty = ZLAsrConfigParser.integer(root, "FilterDirty", 0);
            int filterModal = ZLAsrConfigParser.integer(root, "FilterModal", 0);
            int filterPunc = ZLAsrConfigParser.integer(root, "FilterPunc", 0);
            int convertNumMode = ZLAsrConfigParser.integer(root, "ConvertNumMode", 1);
            int needVad = ZLAsrConfigParser.integer(root, "NeedVad", 1);
            int wordInfo = ZLAsrConfigParser.integer(root, "WordInfo", 0);
            String hotwordID = ZLAsrConfigParser.string(root, "HotwordID", "");
            String customizationID = ZLAsrConfigParser.string(root, "CustomizationID", "");
            double noiseThreshold = ZLAsrConfigParser.number(root, "NoiseThreshold", 0.0);
            int maxSpeakTime = ZLAsrConfigParser.integer(root, "MaxSpeakTime", 0);
            boolean enableVolume = ZLAsrConfigParser.bool(root, "EnableVolume", true);
            boolean enableSilence = ZLAsrConfigParser.bool(root, "EnableSilenceDetect", false);
            int silenceTimeoutMs = ZLAsrConfigParser.integer(root, "SilenceTimeoutMs", 5000);

            Log.i(TAG, "Realtime start taskId=" + taskId + " appId=" + appIdStr + " engine=" + engineModelType);

            // 这里按腾讯云 Android 实时识别文档需要使用 AAIClient、AudioRecognizeRequest、
            // AudioRecognizeConfiguration、AudioRecognizeResultListener 和 AudioRecognizeStateListener [1]
            // 由于当前对话上下文无法访问真实 AAR 中的 classpath 和 import 符号，下面保留最接近接入点。
            // 接入真实 SDK 时，请在这里：
            // 1. 构造 AAIClient（支持直接鉴权或 STS）[1]
            // 2. 构造 AudioRecognizeRequest.Builder 并设置 engine/filter/hotword/customization/vad/wordInfo/noiseThreshold/maxSpeakTime [1]
            // 3. 构造 AudioRecognizeConfiguration 开启静音检测、音量回调 [1]
            // 4. 在回调 onSliceSuccess / onSegmentSuccess / onSuccess / onFailure 中透传给 ZLAsrBridge [1]
            // 5. 在 AudioRecognizeStateListener.onVoiceVolume / onSilentDetectTimeOut 中透传音量和静音事件 [1]

            ZLAsrBridge.onError(taskId, -1, "Tencent Android realtime SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stop(String taskId) {
        Log.i(TAG, "stop realtime: " + taskId);
        // aaiClient.stopAudioRecognize() [1]
    }

    public void cancel(String taskId) {
        Log.i(TAG, "cancel realtime: " + taskId);
        // aaiClient.cancelAudioRecognize() [1]
    }
}
''')

write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrSentenceProxy.java", r'''
package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrSentenceProxy {
    private static final String TAG = "ZLAsrSentenceProxy";

    public boolean recognizeUrl(String taskId, String configJson, String url) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeUrl taskId=" + taskId + " url=" + url + " engine=" + ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh"));
            // 按文档这里应使用 QCloudOneSentenceRecognizer，支持 URL 模式 [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence URL SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeData taskId=" + taskId + " size=" + (data != null ? data.length : 0));
            // 按文档这里应使用 QCloudOneSentenceRecognizer，支持 data 模式 [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence data SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean startRecorder(String taskId, String configJson) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "startRecorder taskId=" + taskId + " engine=" + ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh"));
            // 按文档这里应使用 recognizeWithRecorder() [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence recorder SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stopRecorder(String taskId) {
        Log.i(TAG, "stopRecorder " + taskId);
    }
}
''')

write("Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrFileProxy.java", r'''
package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrFileProxy {
    private static final String TAG = "ZLAsrFileProxy";

    public boolean recognizePath(String taskId, String configJson, String path) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizePath taskId=" + taskId + " path=" + path + " engine=" + ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh"));
            // 按文档这里应使用 QCloudFlashRecognizer + params.setPath(path) [3]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android file path SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeData taskId=" + taskId + " size=" + (data != null ? data.length : 0) + " engine=" + ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh"));
            // 按文档这里应使用 QCloudFlashRecognizer + params.setData(data) [3]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android file data SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }
}
''')

# 12) Harmony ArkTS fuller file
write("Source/ThirdParty/Harmony/ZLAsrHarmony.ets", r'''
// 基于腾讯云 Harmony SDK 的桥接草案：
// 实时识别：Builder + Controller + Listener + DataSource [7]
// 一句话识别：Builder + Controller [8]
// 文件极速版：Builder + Controller.build(data) [9]

export class ZLAsrHarmony {
  static async startRealtime(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, source: any, listener: any): Promise<any> {
    // 真实接入时:
    // let builder = new QCloud.RealTime.Builder()
    // builder.appID = appID
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return builder.build(source, listener)
    throw new Error("Harmony realtime bridge placeholder");
  }

  static async startOneSentence(secretID: string, secretKey: string, token: string, params: Map<string, string>): Promise<string> {
    // let builder = new QCloud.OneSentence.Builder()
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return await builder.build().task
    throw new Error("Harmony one sentence bridge placeholder");
  }

  static async startFileFlash(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, data: ArrayBuffer): Promise<string> {
    // let builder = new QCloud.FileFlash.Builder()
    // builder.appID = appID
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return await builder.build(data).task
    throw new Error("Harmony file flash bridge placeholder");
  }
}
''')

# 13) iOS bridge file in ThirdParty updated notes
write("Source/ThirdParty/IOS/ZLAsrIOSBridge.mm", r'''
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

// 对接说明：
// 实时识别需要 QCloudRealTime.xcframework + VoiceCommon.framework，并使用
// QCloudRealTimeRecognizer / QCloudConfig / delegate [4]
// 一句话识别需要 QCloudOneSentence.xcframework + VoiceCommon.framework，并使用
// QCloudSentenceRecognizer / delegate [5]
// 文件极速版需要 QCloudFileRecognizer.xcframework + VoiceCommon.framework，并使用
// QCloudFlashFileRecognizer / delegate [6]

@interface ZLAsrIOSBridge : NSObject
@end

@implementation ZLAsrIOSBridge
@end
''')

# 14) Add docs
write("Docs/BUILD_NOTES.md", r'''
# ZLAsr 构建说明

## 当前状态
本目录已补到“尽可能可编译”的版本：
- UE 公共层已完整补齐
- Android 侧已补 JNI/C++ 桥接、Java 配置解析、入口类
- iOS 侧已补 Objective-C++ 桥接骨架
- Harmony 侧已补 ArkTS 任务桥接草案

## 仍然不能保证直接通过编译的原因
1. Android 真实 AAR 中的类包名和签名需要以 SDK 实际内容为准 [1][2][3]
2. iOS 真实 framework 头文件名和符号需要以 SDK 实际内容为准 [4][5][6]
3. Harmony 需要你本地 UE 到 ArkTS 的桥接通道 [7][8][9]

## Android 对接点
- 实时识别：AAIClient / AudioRecognizeRequest / AudioRecognizeConfiguration / Listeners [1]
- 一句话识别：QCloudOneSentenceRecognizer [2]
- 文件极速版：QCloudFlashRecognizer [3]

## iOS 对接点
- 实时识别：QCloudRealTimeRecognizer / QCloudConfig / delegate [4]
- 一句话识别：QCloudSentenceRecognizer / delegate [5]
- 文件极速版：QCloudFlashFileRecognizer / delegate [6]

## Harmony 对接点
- 实时识别：QCloud.RealTime.Builder.build(source, listener) [7]
- 一句话识别：QCloud.OneSentence.Builder.build().task [8]
- 文件极速版：QCloud.FileFlash.Builder.build(data).task [9]
''')

# 15) List files summary
all_files = []
for root, _, fs in os.walk(base):
    for f in fs:
        all_files.append(os.path.relpath(os.path.join(root, f), base))
all_files.sort()

print("已继续补全到目录:", base)
print("当前文件总数:", len(all_files))
print("新增/更新的关键文件:")
for item in [
    "ZLAsr.uplugin",
    "Source/ZLAsr/ZLAsr.Build.cs",
    "Source/ZLAsr/ZLAsr_Android_UPL.xml",
    "Source/ZLAsr/Public/ZLAsrJsonUtils.h",
    "Source/ZLAsr/Public/ZLAsrBridgeRegistry.h",
    "Source/ZLAsr/Private/ZLAsrJsonUtils.cpp",
    "Source/ZLAsr/Private/ZLAsrBridgeRegistry.cpp",
    "Source/ZLAsr/Private/ZLAsrAndroidBridge.cpp",
    "Source/ZLAsr/Private/ZLAsrIOSBridge.mm",
    "Source/ZLAsr/Private/ZLAsrHarmonyBridge.cpp",
    "Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrNativeEntry.java",
    "Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrConfigParser.java",
    "Source/ThirdParty/Harmony/ZLAsrHarmony.ets",
    "Docs/BUILD_NOTES.md",
]:
    print(" -", item)

print("\n简要分析：")
print("1. Android 已补到 JNI + Java 入口 + 配置解析 + UE 桥接层，但真实腾讯云 AAR 类型和包签名仍需用本地 SDK 校正 [1][2][3]。")
print("2. iOS 已补到 UE 侧 Objective-C++ 桥接层位，但真实 framework 符号仍需用本地 SDK 头文件补齐 [4][5][6]。")
print("3. Harmony 已补到 ArkTS 任务桥接草案，但 UE<->ArkTS 调用链仍需你本地工具链实现 [7][8][9]。")
print("4. 这已经比简单框架更完整，但仍不是我能够诚实声称“无条件直接编译”的终态。")

print("\n下一步最有价值：")
print("A. 你把真实 Android AAR / iOS xcframework / Harmony har 放进插件目录后，我可以继续按实际符号替换占位实现。")
print("B. 我可以下一轮继续直接修改 /mnt/upload/ZLAsr，把 Android 先补到最接近可编译。")