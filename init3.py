import os
from textwrap import dedent

script_path = "/mnt/uploads/create_zlasr_plugin.py"

script = dedent(r'''
import os
from textwrap import dedent

BASE = "/mnt/uploads/ZLAsr"

def norm(text: str) -> str:
    return dedent(text).lstrip("\n")

def write_file(rel_path: str, content: str):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(norm(content))

def main():
    os.makedirs(BASE, exist_ok=True)

    dirs = [
        "Config",
        "Docs",
        "Resources",
        "Source/ZLAsr/Public",
        "Source/ZLAsr/Private",
        "Source/ThirdParty/Android/Java/com/zl/asr",
        "Source/ThirdParty/IOS",
        "Source/ThirdParty/Harmony",
    ]
    for d in dirs:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)

    files = {}

    files["ZLAsr.uplugin"] = r'''
{
  "FileVersion": 3,
  "Version": 1,
  "VersionName": "1.0.0",
  "FriendlyName": "ZLAsr",
  "Description": "UE speech recognition plugin for Android / iOS / Harmony based on Tencent Cloud ASR SDK wrappers.",
  "Category": "Audio",
  "CreatedBy": "OpenAI",
  "CanContainContent": false,
  "Installed": false,
  "IsBetaVersion": true,
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
'''

    files["Source/ZLAsr/ZLAsr.Build.cs"] = r'''
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

            PublicAdditionalFrameworks.Add(new Framework("QCloudRealTime", "../ThirdParty/IOS/QCloudRealTime.xcframework.zip"));
            PublicAdditionalFrameworks.Add(new Framework("QCloudOneSentence", "../ThirdParty/IOS/QCloudOneSentence.xcframework.zip"));
            PublicAdditionalFrameworks.Add(new Framework("QCloudFileRecognizer", "../ThirdParty/IOS/QCloudFileRecognizer.xcframework.zip"));
            PublicAdditionalFrameworks.Add(new Framework("VoiceCommon", "../ThirdParty/IOS/VoiceCommon.framework.zip"));
        }
    }
}
'''

    files["Source/ZLAsr/ZLAsr_Android_UPL.xml"] = r'''
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
'''

    files["Source/ZLAsr/Public/ZLAsrTypes.h"] = r'''
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
'''

    files["Source/ZLAsr/Public/ZLAsrDelegates.h"] = r'''
#pragma once
#include "CoreMinimal.h"
#include "ZLAsrTypes.h"
#include "ZLAsrDelegates.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeSlice, const FZLAsrSegmentResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeSegment, const FZLAsrSegmentResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeFinal, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnSentenceResult, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnFileResult, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnVolumeChanged, float, Volume);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FZLAsrOnSilenceDetected);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnAsrError, const FZLAsrError&, Error);
'''

    files["Source/ZLAsr/Public/ZLAsrPlatformBridge.h"] = r'''
#pragma once
#include "CoreMinimal.h"
#include "ZLAsrTypes.h"

class IZLAsrTaskSink
{
public:
    virtual ~IZLAsrTaskSink() = default;
    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult& Result) = 0;
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult& Result) = 0;
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleFileResult(const FZLAsrRecognitionResult& Result) = 0;
    virtual void HandleVolume(float Volume) = 0;
    virtual void HandleSilence() = 0;
    virtual void HandleError(const FZLAsrError& Error) = 0;
};

class IZLAsrPlatformBridge
{
public:
    virtual ~IZLAsrPlatformBridge() = default;
    virtual bool Init(IZLAsrTaskSink* InSink) = 0;

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) = 0;
    virtual void StopRealtime(const FString& TaskId) = 0;
    virtual void CancelRealtime(const FString& TaskId) = 0;

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) = 0;
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) = 0;
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) = 0;
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) = 0;
    virtual void StopSentenceRecorder(const FString& TaskId) = 0;

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) = 0;
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) = 0;
};

class FZLAsrPlatformBridgeFactory
{
public:
    static TSharedPtr<IZLAsrPlatformBridge> Create();
};
'''

    files["Source/ZLAsr/Public/ZLAsrJsonUtils.h"] = r'''
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
'''

    files["Source/ZLAsr/Public/ZLAsrBridgeRegistry.h"] = r'''
#pragma once
#include "CoreMinimal.h"
#include "ZLAsrPlatformBridge.h"

class FZLAsrBridgeRegistry
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
'''

    files["Source/ZLAsr/Public/ZLAsrModule.h"] = r'''
#pragma once
#include "Modules/ModuleManager.h"

DECLARE_LOG_CATEGORY_EXTERN(LogZLAsr, Log, All);

class FZLAsrModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
'''

    files["Source/ZLAsr/Public/ZLAsrBlueprintLibrary.h"] = r'''
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
'''

    files["Source/ZLAsr/Public/ZLAsrRealtimeRecognizer.h"] = r'''
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
'''

    files["Source/ZLAsr/Public/ZLAsrSentenceRecognizer.h"] = r'''
#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrDelegates.h"
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrSentenceRecognizer.generated.h"

UCLASS(BlueprintType)
class UZLAsrSentenceRecognizer : public UObject, public IZLAsrTaskSink
{
    GENERATED_BODY()

public:
    UZLAsrSentenceRecognizer();

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromUrl(const FZLAsrSentenceConfig& Config, const FString& Url);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromFile(const FZLAsrSentenceConfig& Config, const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool RecognizeFromMemory(const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    bool StartRecognizeWithRecorder(const FZLAsrSentenceConfig& Config);

    UFUNCTION(BlueprintCallable, Category="ZLAsr")
    void StopRecognizeWithRecorder();

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnSentenceResult OnResult;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnVolumeChanged OnVolumeChanged;

    UPROPERTY(BlueprintAssignable, Category="ZLAsr")
    FZLAsrOnAsrError OnError;

    virtual void HandleRealtimeSlice(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeSegment(const FZLAsrSegmentResult&) override {}
    virtual void HandleRealtimeFinal(const FZLAsrRecognitionResult&) override {}
    virtual void HandleSentenceResult(const FZLAsrRecognitionResult& Result) override;
    virtual void HandleFileResult(const FZLAsrRecognitionResult&) override {}
    virtual void HandleVolume(float Volume) override;
    virtual void HandleSilence() override {}
    virtual void HandleError(const FZLAsrError& Error) override;

private:
    FString TaskId;
    bool bRecording = false;
    TSharedPtr<IZLAsrPlatformBridge> Bridge;
};
'''

    files["Source/ZLAsr/Public/ZLAsrFileRecognizer.h"] = r'''
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
'''

    files["Source/ZLAsr/Private/ZLAsrModule.cpp"] = r'''
#include "ZLAsrModule.h"
DEFINE_LOG_CATEGORY(LogZLAsr);

void FZLAsrModule::StartupModule()
{
    UE_LOG(LogZLAsr, Log, TEXT("ZLAsr startup"));
}

void FZLAsrModule::ShutdownModule()
{
    UE_LOG(LogZLAsr, Log, TEXT("ZLAsr shutdown"));
}

IMPLEMENT_MODULE(FZLAsrModule, ZLAsr)
'''

    files["Source/ZLAsr/Private/ZLAsrBridgeRegistry.cpp"] = r'''
#include "ZLAsrBridgeRegistry.h"

FZLAsrBridgeRegistry& FZLAsrBridgeRegistry::Get()
{
    static FZLAsrBridgeRegistry I;
    return I;
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
'''

    files["Source/ZLAsr/Private/ZLAsrJsonUtils.cpp"] = r'''
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
'''

    files["Source/ZLAsr/Private/ZLAsrPlatformBridge.cpp"] = r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "Async/Async.h"

TSharedPtr<IZLAsrPlatformBridge> CreateAndroidBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge();
TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge();

class FZLAsrStubBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString&, const FZLAsrRealtimeConfig&) override
    {
        if (Sink)
        {
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, TEXT("Unsupported platform"), TEXT("")));
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
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateAndroidBridge()) return B;
#elif PLATFORM_IOS
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateIOSBridge()) return B;
#else
    if (TSharedPtr<IZLAsrPlatformBridge> B = CreateHarmonyBridge()) return B;
#endif
    return MakeShared<FZLAsrStubBridge>();
}
'''

    files["Source/ZLAsr/Private/ZLAsrAndroidBridge.cpp"] = r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"
#include "Misc/FileHelper.h"

#if PLATFORM_ANDROID
#include "Android/AndroidApplication.h"
#include "Android/AndroidJNI.h"
#include "Android/AndroidJavaEnv.h"

static jclass GBridgeClass = nullptr;
static jmethodID GCtor = nullptr;
static jmethodID GRealtimeStart = nullptr;
static jmethodID GRealtimeStop = nullptr;
static jmethodID GRealtimeCancel = nullptr;
static jmethodID GSentenceUrl = nullptr;
static jmethodID GSentenceData = nullptr;
static jmethodID GSentenceRecorderStart = nullptr;
static jmethodID GSentenceRecorderStop = nullptr;
static jmethodID GFilePath = nullptr;
static jmethodID GFileData = nullptr;

static FString JStringToFString(JNIEnv* Env, jstring Str)
{
    if (!Str) return FString();
    const char* Chars = Env->GetStringUTFChars(Str, 0);
    FString Out(UTF8_TO_TCHAR(Chars));
    Env->ReleaseStringUTFChars(Str, Chars);
    return Out;
}

class FZLAsrAndroidBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override
    {
        Sink = InSink;
        return CacheJNI();
    }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig& Config) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jboolean Ok = Env->CallBooleanMethod(Obj, GRealtimeStart, JTask, JCfg);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

    virtual void StopRealtime(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return;
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Obj, GRealtimeStop, JTask);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(Obj);
    }

    virtual void CancelRealtime(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return;
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Obj, GRealtimeCancel, JTask);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(Obj);
    }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jstring JUrl = Env->NewStringUTF(TCHAR_TO_UTF8(*Url));
        jboolean Ok = Env->CallBooleanMethod(Obj, GSentenceUrl, JTask, JCfg, JUrl);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(JUrl);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Bytes;
        if (!FFileHelper::LoadFileToArray(Bytes, *FilePath)) return false;
        return StartSentenceFromMemory(TaskId, Config, Bytes);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jbyteArray Arr = Env->NewByteArray(AudioData.Num());
        if (AudioData.Num() > 0)
        {
            Env->SetByteArrayRegion(Arr, 0, AudioData.Num(), reinterpret_cast<const jbyte*>(AudioData.GetData()));
        }
        jboolean Ok = Env->CallBooleanMethod(Obj, GSentenceData, JTask, JCfg, Arr);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(Arr);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jboolean Ok = Env->CallBooleanMethod(Obj, GSentenceRecorderStart, JTask, JCfg);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

    virtual void StopSentenceRecorder(const FString& TaskId) override
    {
        if (!CacheJNI()) return;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return;
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        Env->CallVoidMethod(Obj, GSentenceRecorderStop, JTask);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(Obj);
    }

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jstring JPath = Env->NewStringUTF(TCHAR_TO_UTF8(*FilePath));
        jboolean Ok = Env->CallBooleanMethod(Obj, GFilePath, JTask, JCfg, JPath);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(JPath);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override
    {
        if (!CacheJNI()) return false;
        Register(TaskId);
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jobject Obj = Env->NewObject(GBridgeClass, GCtor);
        if (!Obj) return false;
        const FString Json = FZLAsrJsonUtils::ToJsonString(Config);
        jstring JTask = Env->NewStringUTF(TCHAR_TO_UTF8(*TaskId));
        jstring JCfg = Env->NewStringUTF(TCHAR_TO_UTF8(*Json));
        jbyteArray Arr = Env->NewByteArray(AudioData.Num());
        if (AudioData.Num() > 0)
        {
            Env->SetByteArrayRegion(Arr, 0, AudioData.Num(), reinterpret_cast<const jbyte*>(AudioData.GetData()));
        }
        jboolean Ok = Env->CallBooleanMethod(Obj, GFileData, JTask, JCfg, Arr);
        Env->DeleteLocalRef(JTask);
        Env->DeleteLocalRef(JCfg);
        Env->DeleteLocalRef(Arr);
        Env->DeleteLocalRef(Obj);
        return Ok == JNI_TRUE;
    }

private:
    bool CacheJNI()
    {
        if (GBridgeClass) return true;
        JNIEnv* Env = FAndroidApplication::GetJavaEnv();
        jclass LocalClass = FAndroidApplication::FindJavaClass("com/zl/asr/ZLAsrNativeEntry");
        if (!LocalClass) return false;

        GBridgeClass = reinterpret_cast<jclass>(Env->NewGlobalRef(LocalClass));
        Env->DeleteLocalRef(LocalClass);

        GCtor = Env->GetMethodID(GBridgeClass, "<init>", "()V");
        GRealtimeStart = Env->GetMethodID(GBridgeClass, "startRealtime", "(Ljava/lang/String;Ljava/lang/String;)Z");
        GRealtimeStop = Env->GetMethodID(GBridgeClass, "stopRealtime", "(Ljava/lang/String;)V");
        GRealtimeCancel = Env->GetMethodID(GBridgeClass, "cancelRealtime", "(Ljava/lang/String;)V");
        GSentenceUrl = Env->GetMethodID(GBridgeClass, "startSentenceUrl", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z");
        GSentenceData = Env->GetMethodID(GBridgeClass, "startSentenceData", "(Ljava/lang/String;Ljava/lang/String;[B)Z");
        GSentenceRecorderStart = Env->GetMethodID(GBridgeClass, "startSentenceRecorder", "(Ljava/lang/String;Ljava/lang/String;)Z");
        GSentenceRecorderStop = Env->GetMethodID(GBridgeClass, "stopSentenceRecorder", "(Ljava/lang/String;)V");
        GFilePath = Env->GetMethodID(GBridgeClass, "startFilePath", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Z");
        GFileData = Env->GetMethodID(GBridgeClass, "startFileData", "(Ljava/lang/String;Ljava/lang/String;[B)Z");

        return GCtor && GRealtimeStart && GRealtimeStop && GRealtimeCancel &&
               GSentenceUrl && GSentenceData && GSentenceRecorderStart &&
               GSentenceRecorderStop && GFilePath && GFileData;
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
'''

    files["Source/ZLAsr/Private/ZLAsrIOSBridge.mm"] = r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"
#include "Misc/FileHelper.h"

#if PLATFORM_IOS
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

class FZLAsrIOSBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig&) override
    {
        Register(TaskId);
        Report(TEXT("iOS realtime bridge requires real Tencent frameworks"));
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString& TaskId) override { FZLAsrBridgeRegistry::Get().Unregister(TaskId); }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(url) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath)) return false;
        return StartSentenceFromMemory(TaskId, Config, Data);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig&, const TArray<uint8>&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(data) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig&) override
    {
        Register(TaskId);
        Report(TEXT("iOS sentence(recorder) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual void StopSentenceRecorder(const FString&) override {}

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig&, const FString&) override
    {
        Register(TaskId);
        Report(TEXT("iOS file(path) bridge requires real Tencent frameworks"));
        return false;
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig&, const TArray<uint8>&) override
    {
        Register(TaskId);
        Report(TEXT("iOS file(data) bridge requires real Tencent frameworks"));
        return false;
    }

private:
    void Register(const FString& TaskId)
    {
        if (Sink) FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
    }

    void Report(const FString& Message)
    {
        if (Sink) Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(-1, Message, TEXT("")));
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge()
{
    return MakeShared<FZLAsrIOSBridge>();
}
#endif
'''

    files["Source/ZLAsr/Private/ZLAsrHarmonyBridge.cpp"] = r'''
#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"

class FZLAsrHarmonyBridge final : public IZLAsrPlatformBridge
{
public:
    virtual bool Init(IZLAsrTaskSink* InSink) override { Sink = InSink; return true; }

    virtual bool StartRealtime(const FString& TaskId, const FZLAsrRealtimeConfig&) override
    {
        Register(TaskId);
        Report(TEXT("Harmony bridge needs UE <-> ArkTS integration"));
        return false;
    }

    virtual void StopRealtime(const FString&) override {}
    virtual void CancelRealtime(const FString& TaskId) override { FZLAsrBridgeRegistry::Get().Unregister(TaskId); }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony sentence(url) bridge not wired")); return false; }
    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony sentence(file) bridge not wired")); return false; }
    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig&, const TArray<uint8>&) override { Register(TaskId); Report(TEXT("Harmony sentence(data) bridge not wired")); return false; }
    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig&) override { Register(TaskId); Report(TEXT("Harmony recorder bridge not wired")); return false; }
    virtual void StopSentenceRecorder(const FString&) override {}
    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig&, const FString&) override { Register(TaskId); Report(TEXT("Harmony file(path) bridge not wired")); return false; }
    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig&, const TArray<uint8>&) override { Register(TaskId); Report(TEXT("Harmony file(data) bridge not wired")); return false; }

private:
    void Register(const FString& TaskId)
    {
        if (Sink) FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
    }

    void Report(const FString& Message)
    {
        if (Sink) Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(4, Message, TEXT("")));
    }

private:
    IZLAsrTaskSink* Sink = nullptr;
};

TSharedPtr<IZLAsrPlatformBridge> CreateHarmonyBridge()
{
    return MakeShared<FZLAsrHarmonyBridge>();
}
'''

    files["Source/ZLAsr/Private/ZLAsrBlueprintLibrary.cpp"] = r'''
#include "ZLAsrBlueprintLibrary.h"
#include "ZLAsrRealtimeRecognizer.h"
#include "ZLAsrSentenceRecognizer.h"
#include "ZLAsrFileRecognizer.h"

UZLAsrRealtimeRecognizer* UZLAsrBlueprintLibrary::CreateRealtimeRecognizer(UObject* WorldContextObject)
{
    return NewObject<UZLAsrRealtimeRecognizer>(WorldContextObject ? WorldContextObject : GetTransientPackage());
}

UZLAsrSentenceRecognizer* UZLAsrBlueprintLibrary::CreateSentenceRecognizer(UObject* WorldContextObject)
{
    return NewObject<UZLAsrSentenceRecognizer>(WorldContextObject ? WorldContextObject : GetTransientPackage());
}

UZLAsrFileRecognizer* UZLAsrBlueprintLibrary::CreateFileRecognizer(UObject* WorldContextObject)
{
    return NewObject<UZLAsrFileRecognizer>(WorldContextObject ? WorldContextObject : GetTransientPackage());
}
'''

    files["Source/ZLAsr/Private/ZLAsrRealtimeRecognizer.cpp"] = r'''
#include "ZLAsrRealtimeRecognizer.h"
#include "Async/Async.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrRealtimeRecognizer::UZLAsrRealtimeRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid()) Bridge->Init(this);
}

bool UZLAsrRealtimeRecognizer::StartRealtimeRecognition(const FZLAsrRealtimeConfig& Config)
{
    if (!Bridge.IsValid() || bRunning) return false;
    bRunning = Bridge->StartRealtime(TaskId, Config);
    return bRunning;
}

void UZLAsrRealtimeRecognizer::StopRealtimeRecognition()
{
    if (Bridge.IsValid()) Bridge->StopRealtime(TaskId);
}

void UZLAsrRealtimeRecognizer::CancelRealtimeRecognition()
{
    bRunning = false;
    FZLAsrBridgeRegistry::Get().Unregister(TaskId);
    if (Bridge.IsValid()) Bridge->CancelRealtime(TaskId);
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
'''

    files["Source/ZLAsr/Private/ZLAsrSentenceRecognizer.cpp"] = r'''
#include "ZLAsrSentenceRecognizer.h"
#include "Async/Async.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrSentenceRecognizer::UZLAsrSentenceRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid()) Bridge->Init(this);
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
    if (Bridge.IsValid()) Bridge->StopSentenceRecorder(TaskId);
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
'''

    files["Source/ZLAsr/Private/ZLAsrFileRecognizer.cpp"] = r'''
#include "ZLAsrFileRecognizer.h"
#include "Async/Async.h"
#include "ZLAsrBridgeRegistry.h"

UZLAsrFileRecognizer::UZLAsrFileRecognizer()
{
    TaskId = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    Bridge = FZLAsrPlatformBridgeFactory::Create();
    if (Bridge.IsValid()) Bridge->Init(this);
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
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrBridge.java"] = r'''
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
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrConfigParser.java"] = r'''
package com.zl.asr;

import org.json.JSONObject;

public class ZLAsrConfigParser {
    public static JSONObject parse(String json) throws Exception { return new JSONObject(json); }
    public static JSONObject auth(JSONObject root) throws Exception { return root.getJSONObject("Auth"); }
    public static String string(JSONObject obj, String key, String def) { return obj.has(key) ? obj.optString(key, def) : def; }
    public static int integer(JSONObject obj, String key, int def) { return obj.has(key) ? obj.optInt(key, def) : def; }
    public static boolean bool(JSONObject obj, String key, boolean def) { return obj.has(key) ? obj.optBoolean(key, def) : def; }
    public static double number(JSONObject obj, String key, double def) { return obj.has(key) ? obj.optDouble(key, def) : def; }
}
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrNativeEntry.java"] = r'''
package com.zl.asr;

public class ZLAsrNativeEntry {
    private final ZLAsrRealtimeProxy realtimeProxy = new ZLAsrRealtimeProxy();
    private final ZLAsrSentenceProxy sentenceProxy = new ZLAsrSentenceProxy();
    private final ZLAsrFileProxy fileProxy = new ZLAsrFileProxy();

    public boolean startRealtime(String taskId, String configJson) { return realtimeProxy.start(taskId, configJson); }
    public void stopRealtime(String taskId) { realtimeProxy.stop(taskId); }
    public void cancelRealtime(String taskId) { realtimeProxy.cancel(taskId); }

    public boolean startSentenceUrl(String taskId, String configJson, String url) { return sentenceProxy.recognizeUrl(taskId, configJson, url); }
    public boolean startSentenceData(String taskId, String configJson, byte[] data) { return sentenceProxy.recognizeData(taskId, configJson, data); }
    public boolean startSentenceRecorder(String taskId, String configJson) { return sentenceProxy.startRecorder(taskId, configJson); }
    public void stopSentenceRecorder(String taskId) { sentenceProxy.stopRecorder(taskId); }

    public boolean startFilePath(String taskId, String configJson, String path) { return fileProxy.recognizePath(taskId, configJson, path); }
    public boolean startFileData(String taskId, String configJson, byte[] data) { return fileProxy.recognizeData(taskId, configJson, data); }
}
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrRealtimeProxy.java"] = r'''
package com.zl.asr;

import android.app.Activity;
import android.util.Log;
import org.json.JSONObject;

public class ZLAsrRealtimeProxy {
    private static final String TAG = "ZLAsrRealtimeProxy";

    public boolean start(String taskId, String configJson) {
        Activity activity = ZLAsrBridge.getActivity();
        if (activity == null) {
            ZLAsrBridge.onError(taskId, -1, "Activity is null", "");
            return false;
        }

        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            JSONObject auth = ZLAsrConfigParser.auth(root);

            String appId = ZLAsrConfigParser.string(auth, "AppID", "");
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
            String hotwordId = ZLAsrConfigParser.string(root, "HotwordID", "");
            String customizationId = ZLAsrConfigParser.string(root, "CustomizationID", "");
            double noiseThreshold = ZLAsrConfigParser.number(root, "NoiseThreshold", 0.0);
            int maxSpeakTime = ZLAsrConfigParser.integer(root, "MaxSpeakTime", 0);
            boolean enableVolume = ZLAsrConfigParser.bool(root, "EnableVolume", true);
            boolean enableSilence = ZLAsrConfigParser.bool(root, "EnableSilenceDetect", false);
            int silenceTimeoutMs = ZLAsrConfigParser.integer(root, "SilenceTimeoutMs", 5000);

            Log.i(TAG, "Realtime task=" + taskId + " appId=" + appId + " engine=" + engineModelType);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android realtime SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stop(String taskId) { Log.i(TAG, "stop realtime=" + taskId); }
    public void cancel(String taskId) { Log.i(TAG, "cancel realtime=" + taskId); }
}
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrSentenceProxy.java"] = r'''
package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrSentenceProxy {
    private static final String TAG = "ZLAsrSentenceProxy";

    public boolean recognizeUrl(String taskId, String configJson, String url) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence url task=" + taskId + " engine=" + engine + " url=" + url);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android one sentence SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence data task=" + taskId + " engine=" + engine + " size=" + (data != null ? data.length : 0));
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android one sentence SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean startRecorder(String taskId, String configJson) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence recorder task=" + taskId + " engine=" + engine);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android recorder SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stopRecorder(String taskId) { Log.i(TAG, "stop recorder=" + taskId); }
}
'''

    files["Source/ThirdParty/Android/Java/com/zl/asr/ZLAsrFileProxy.java"] = r'''
package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrFileProxy {
    private static final String TAG = "ZLAsrFileProxy";

    public boolean recognizePath(String taskId, String configJson, String path) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            Log.i(TAG, "file path task=" + taskId + " engine=" + engine + " path=" + path);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android flash file SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            Log.i(TAG, "file data task=" + taskId + " engine=" + engine + " size=" + (data != null ? data.length : 0));
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android flash file SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }
}
'''

    files["Source/ThirdParty/IOS/ZLAsrIOSBridge.mm"] = r'''
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

// QCloudRealTime.xcframework + VoiceCommon.framework 用于实时识别 [4]
// QCloudOneSentence.xcframework + VoiceCommon.framework 用于一句话识别 [5]
// QCloudFileRecognizer.xcframework + VoiceCommon.framework 用于文件极速版 [6]
'''

    files["Source/ThirdParty/Harmony/ZLAsrHarmony.ets"] = r'''
export class ZLAsrHarmony {
  static async startRealtime(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, source: any, listener: any): Promise<any> {
    throw new Error("Harmony realtime bridge placeholder")
  }

  static async startOneSentence(secretID: string, secretKey: string, token: string, params: Map<string, string>): Promise<string> {
    throw new Error("Harmony one sentence bridge placeholder")
  }

  static async startFileFlash(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, data: ArrayBuffer): Promise<string> {
    throw new Error("Harmony file flash bridge placeholder")
  }
}
'''

    files["Docs/README.md"] = r'''
# ZLAsr

这个插件生成器基于腾讯云三端 SDK 能力边界组织：
- Android 实时识别：AAIClient / AudioRecognizeRequest / AudioRecognizeConfiguration [1]
- Android 一句话识别：QCloudOneSentenceRecognizer [2]
- Android 文件极速版：QCloudFlashRecognizer [3]
- iOS 实时识别：QCloudRealTimeRecognizer / QCloudConfig [4]
- iOS 一句话识别：QCloudSentenceRecognizer [5]
- iOS 文件极速版：QCloudFlashFileRecognizer [6]
- Harmony 实时识别：Builder / Controller / Listener / DataSource [7]
- Harmony 一句话识别：Builder / Controller [8]
- Harmony 文件极速版：Builder.build(data) [9]

注意：
这份脚本生成的是“完整插件工程代码清单 + 三端桥接骨架”。
若要真正编译，需要你本地放入真实 AAR / xcframework / har，并按实际 SDK 符号补全最终桥接。
'''

    for rel, content in files.items():
        write_file(rel, content)

    all_files = []
    for root, _, fs in os.walk(BASE):
        for f in fs:
            all_files.append(os.path.relpath(os.path.join(root, f), BASE))
    all_files.sort()

    manifest = os.path.join(BASE, "Docs", "CODE_LIST.md")
    with open(manifest, "w", encoding="utf-8") as mf:
        mf.write("# ZLAsr 完整代码清单\n\n")
        mf.write("以下文件由 create_zlasr_plugin.py 一键生成。\n\n")
        for item in all_files:
            mf.write(f"- {item}\n")

    print("ZLAsr 插件已生成到:", BASE)
    print("共生成文件数:", len(all_files))
    print("代码清单:", manifest)
    print("\n文件列表预览:")
    for item in all_files[:40]:
        print(" -", item)

if __name__ == "__main__":
    main()
''').lstrip("\n")

os.makedirs("/mnt/uploads", exist_ok=True)
with open(script_path, "w", encoding="utf-8") as f:
    f.write(script)

print("已写出完整脚本到:", script_path)
print("脚本总行数:", len(script.splitlines()))
print("\n前 40 行预览：")
for i, line in enumerate(script.splitlines()[:40], 1):
    print(f"{i:03d}: {line}")

print("\n说明：")
print("1. 这是完整的 create_zlasr_plugin.py。")
print("2. 运行后会在 /mnt/uploads/ZLAsr 下生成插件目录。")
print("3. 该脚本已按腾讯云 Android/iOS/Harmony 三端能力边界组织结构：")
print("   - Android 实时识别依赖 AAI