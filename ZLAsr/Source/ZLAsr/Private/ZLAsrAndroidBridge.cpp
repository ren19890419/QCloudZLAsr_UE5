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
