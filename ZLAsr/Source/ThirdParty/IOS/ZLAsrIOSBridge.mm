#include "ZLAsrPlatformBridge.h"
#include "ZLAsrJsonUtils.h"
#include "ZLAsrBridgeRegistry.h"
#include "Misc/FileHelper.h"

#if PLATFORM_IOS
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

/*
 * 说明：
 * 下面这份实现是“尽可能完整的 UE iOS Bridge 实现”。
 * 但我必须明确：
 * 1. 你提供的上下文文档说明了 iOS 端需要使用：
 *    - 实时识别：QCloudRealTimeRecognizer / QCloudConfig / QCloudRealTimeRecognizerDelegate [4]
 *    - 一句话识别：QCloudSentenceRecognizer / QCloudSentenceRecognizerDelegate [5]
 *    - 文件极速版：QCloudFlashFileRecognizer / QCloudFlashFileRecognizerDelegate [6]
 * 2. 但是当前上下文没有提供真实 framework 头文件中 delegate 的精确 Objective-C 方法签名。
 * 3. 因此这里不能伪造一个“保证100%通过编译”的 SDK 直连版，否则可能会和真实头文件不一致。
 *
 * 所以本文件采用“两层策略”：
 * A. UE 侧桥接逻辑、任务注册、参数分发、文件读取、错误上报全部实现完整；
 * B. 真正调用腾讯云 iOS SDK 的位置集中在宏 ZLASR_IOS_TENCENT_SDK_AVAILABLE 分支，
 *    你拿到真实 SDK 头文件后，只需补全 import 和 delegate 签名即可。
 *
 * 文档依据：
 * - 工程需链接 QCloudRealTime.xcframework + VoiceCommon.framework，并申请麦克风权限 [4]
 * - 实时识别用 QCloudConfig 初始化，再用 QCloudRealTimeRecognizer 启动/停止 [4]
 * - 一句话识别入口为 QCloudSentenceRecognizer，支持 URL / Data / Recorder [5]
 * - 文件极速版入口为 QCloudFlashFileRecognizer [6]
 */

// 如果你后续把真实头文件接进来，可在 Build.cs / PreprocessorDefinitions 中定义此宏。
#ifndef ZLASR_IOS_TENCENT_SDK_AVAILABLE
#define ZLASR_IOS_TENCENT_SDK_AVAILABLE 0
#endif

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
#import <QCloudRealTime/QCloudRealTimeRecognizer.h>
#import <QCloudRealTime/QCloudConfig.h>
#import <QCloudRealTime/QCloudRealTimeResult.h>
#import <QCloudRealTime/QCloudAudioDataSource.h>

#import <QCloudOneSentence/QCloudSentenceRecognizer.h>
#import <QCloudOneSentence/QCloudOneSentenceRecognitionParams.h>

#import <QCloudFileRecognizer/QCloudFlashFileRecognizer.h>
#import <QCloudFileRecognizer/QCloudFlashFileRecognizeParams.h>
#endif

static NSString* ZLToNSString(const FString& InValue)
{
    return [NSString stringWithUTF8String:TCHAR_TO_UTF8(*InValue)];
}

static FString ZLToFString(NSString* InValue)
{
    if (!InValue) return FString();
    return FString(UTF8_TO_TCHAR([InValue UTF8String]));
}

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
static id ZLCreateQCloudConfigRealtime(const FZLAsrRealtimeConfig& Config)
{
    NSString* AppID = ZLToNSString(Config.Auth.AppID);
    NSString* SecretID = ZLToNSString(Config.Auth.SecretID);
    NSString* SecretKey = ZLToNSString(Config.Auth.SecretKey);
    NSString* Token = ZLToNSString(Config.Auth.Token);

    QCloudConfig* Obj = nil;
    if (Token.length > 0)
    {
        Obj = [[QCloudConfig alloc] initWithAppId:AppID
                                         secretId:SecretID
                                        secretKey:SecretKey
                                            token:Token
                                        projectId:0];
    }
    else
    {
        Obj = [[QCloudConfig alloc] initWithAppId:AppID
                                         secretId:SecretID
                                        secretKey:SecretKey
                                        projectId:0];
    }

    Obj.engineType = ZLToNSString(Config.EngineModelType);
    Obj.filterDirty = Config.FilterDirty;
    Obj.filterModal = Config.FilterModal;
    Obj.filterPunc = Config.FilterPunc;
    Obj.convertNumMode = Config.ConvertNumMode;
    Obj.needvad = Config.NeedVad;
    Obj.wordInfo = Config.WordInfo;
    Obj.enableDetectVolume = Config.bEnableVolume;
    Obj.endRecognizeWhenDetectSilence = Config.bEnableSilenceDetect;
    Obj.silenceDetectDuration = ((float)Config.SilenceTimeoutMs) / 1000.0f;
    Obj.noiseThreshold = Config.NoiseThreshold;
    Obj.maxSpeakTime = Config.MaxSpeakTime;

    if (!Config.HotwordID.IsEmpty())
    {
        Obj.hotwordId = ZLToNSString(Config.HotwordID);
    }
    if (!Config.CustomizationID.IsEmpty())
    {
        Obj.customizationId = ZLToNSString(Config.CustomizationID);
    }
    if (Config.bSaveAudioToFile)
    {
        Obj.shouldSaveAsFile = YES;
        Obj.saveFilePath = ZLToNSString(Config.SaveAudioPath);
    }
    return Obj;
}
#endif

class FZLAsrIOSBridge;

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
@interface ZLAsrIOSRealtimeDelegate : NSObject<QCloudRealTimeRecognizerDelegate>
@property(nonatomic, assign) FZLAsrIOSBridge* Owner;
@property(nonatomic, copy) NSString* TaskId;
@end

@interface ZLAsrIOSSentenceDelegate : NSObject<QCloudSentenceRecognizerDelegate>
@property(nonatomic, assign) FZLAsrIOSBridge* Owner;
@property(nonatomic, copy) NSString* TaskId;
@end

@interface ZLAsrIOSFileDelegate : NSObject<QCloudFlashFileRecognizerDelegate>
@property(nonatomic, assign) FZLAsrIOSBridge* Owner;
@property(nonatomic, copy) NSString* TaskId;
@end
#endif

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
        Register(TaskId);

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        @autoreleasepool
        {
            NSError* SessionError = nil;
            [[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryRecord error:&SessionError];
            if (SessionError)
            {
                Report(TaskId, -103, FString::Printf(TEXT("AVAudioSession setCategory failed: %s"), *ZLToFString(SessionError.localizedDescription)));
                return false;
            }
            [[AVAudioSession sharedInstance] setActive:YES error:nil];

            QCloudConfig* RealConfig = (QCloudConfig*)ZLCreateQCloudConfigRealtime(Config);
            QCloudRealTimeRecognizer* Recognizer = [[QCloudRealTimeRecognizer alloc] initWithConfig:RealConfig];

            ZLAsrIOSRealtimeDelegate* Delegate = [[ZLAsrIOSRealtimeDelegate alloc] init];
            Delegate.Owner = this;
            Delegate.TaskId = ZLToNSString(TaskId);
            Recognizer.delegate = Delegate;

            FString Key = TaskId;
            RealtimeRecognizers.Add(Key, (void*)CFBridgingRetain(Recognizer));
            RealtimeDelegates.Add(Key, (void*)CFBridgingRetain(Delegate));

            [Recognizer start];
            return true;
        }
#else
        Report(TaskId, -1, TEXT("iOS realtime bridge ready, but real Tencent iOS frameworks are not linked. According to the iOS realtime SDK docs, you need QCloudRealTime.xcframework, VoiceCommon.framework, NSMicrophoneUsageDescription, QCloudConfig and QCloudRealTimeRecognizer [4]."));
        return false;
#endif
    }

    virtual void StopRealtime(const FString& TaskId) override
    {
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = RealtimeRecognizers.Find(TaskId))
        {
            QCloudRealTimeRecognizer* Recognizer = (__bridge QCloudRealTimeRecognizer*)(*Found);
            [Recognizer stop];
        }
#else
        FZLAsrBridgeRegistry::Get().Unregister(TaskId);
#endif
    }

    virtual void CancelRealtime(const FString& TaskId) override
    {
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = RealtimeRecognizers.Find(TaskId))
        {
            QCloudRealTimeRecognizer* Recognizer = (__bridge QCloudRealTimeRecognizer*)(*Found);
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"
            if ([Recognizer respondsToSelector:@selector(cancel)])
            {
                [Recognizer performSelector:@selector(cancel)];
            }
#pragma clang diagnostic pop
        }
#endif
        CleanupRealtime(TaskId);
    }

    virtual bool StartSentenceFromUrl(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& Url) override
    {
        Register(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        @autoreleasepool
        {
            QCloudSentenceRecognizer* Recognizer = BuildSentenceRecognizer(TaskId, Config);
            if (!Recognizer)
            {
                Report(TaskId, -1, TEXT("Failed to create QCloudSentenceRecognizer"));
                return false;
            }

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"
            if ([Recognizer respondsToSelector:@selector(recoginizeWithUrl:voiceFormat:EngSerViceType:)])
            {
                [Recognizer performSelector:@selector(recoginizeWithUrl:voiceFormat:EngSerViceType:)
                                 withObject:ZLToNSString(Url)
                                 withObject:ZLToNSString(Config.VoiceFormat)];
                return true;
            }
#pragma clang diagnostic pop

            Report(TaskId, -1, TEXT("QCloudSentenceRecognizer missing recoginizeWithUrl API"));
            return false;
        }
#else
        Report(TaskId, -1, TEXT("iOS one-sentence bridge ready, but real Tencent iOS frameworks are not linked. The docs show QCloudSentenceRecognizer supports URL/Data/Recorder and delegate callbacks [5]."));
        return false;
#endif
    }

    virtual bool StartSentenceFromFile(const FString& TaskId, const FZLAsrSentenceConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath))
        {
            Report(TaskId, -1, FString::Printf(TEXT("Failed to load sentence file: %s"), *FilePath));
            return false;
        }
        return StartSentenceFromMemory(TaskId, Config, Data);
    }

    virtual bool StartSentenceFromMemory(const FString& TaskId, const FZLAsrSentenceConfig& Config, const TArray<uint8>& AudioData) override
    {
        Register(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        @autoreleasepool
        {
            QCloudSentenceRecognizer* Recognizer = BuildSentenceRecognizer(TaskId, Config);
            if (!Recognizer)
            {
                Report(TaskId, -1, TEXT("Failed to create QCloudSentenceRecognizer"));
                return false;
            }

            NSData* Data = [NSData dataWithBytes:AudioData.GetData() length:AudioData.Num()];
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"
            if ([Recognizer respondsToSelector:@selector(recoginizeWithData:voiceFormat:frequence:)])
            {
                [Recognizer performSelector:@selector(recoginizeWithData:voiceFormat:frequence:)
                                 withObject:Data
                                 withObject:ZLToNSString(Config.VoiceFormat)];
                return true;
            }
#pragma clang diagnostic pop

            Report(TaskId, -1, TEXT("QCloudSentenceRecognizer missing recoginizeWithData API"));
            return false;
        }
#else
        Report(TaskId, -1, TEXT("iOS sentence(data) bridge requires real QCloudOneSentence.xcframework and VoiceCommon.framework [5]."));
        return false;
#endif
    }

    virtual bool StartSentenceRecorder(const FString& TaskId, const FZLAsrSentenceConfig& Config) override
    {
        Register(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        @autoreleasepool
        {
            NSError* SessionError = nil;
            [[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryRecord error:&SessionError];
            if (SessionError)
            {
                Report(TaskId, -103, FString::Printf(TEXT("AVAudioSession setCategory failed: %s"), *ZLToFString(SessionError.localizedDescription)));
                return false;
            }
            [[AVAudioSession sharedInstance] setActive:YES error:nil];

            QCloudSentenceRecognizer* Recognizer = BuildSentenceRecognizer(TaskId, Config);
            if (!Recognizer)
            {
                Report(TaskId, -1, TEXT("Failed to create QCloudSentenceRecognizer"));
                return false;
            }

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"
            if ([Recognizer respondsToSelector:@selector(startRecognizeWithRecorder:)])
            {
                [Recognizer performSelector:@selector(startRecognizeWithRecorder:)
                                 withObject:ZLToNSString(Config.EngSerViceType)];
                return true;
            }
#pragma clang diagnostic pop

            Report(TaskId, -1, TEXT("QCloudSentenceRecognizer missing startRecognizeWithRecorder API"));
            return false;
        }
#else
        Report(TaskId, -1, TEXT("iOS sentence(recorder) bridge requires real QCloudSentenceRecognizer and microphone permission NSMicrophoneUsageDescription [5]."));
        return false;
#endif
    }

    virtual void StopSentenceRecorder(const FString& TaskId) override
    {
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = SentenceRecognizers.Find(TaskId))
        {
            id RecognizerObj = (__bridge id)(*Found);
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"
            if ([RecognizerObj respondsToSelector:@selector(stopRecognizeWithRecorder)])
            {
                [RecognizerObj performSelector:@selector(stopRecognizeWithRecorder)];
            }
#pragma clang diagnostic pop
        }
#else
        FZLAsrBridgeRegistry::Get().Unregister(TaskId);
#endif
    }

    virtual bool StartFileRecognizePath(const FString& TaskId, const FZLAsrFileConfig& Config, const FString& FilePath) override
    {
        TArray<uint8> Data;
        if (!FFileHelper::LoadFileToArray(Data, *FilePath))
        {
            Report(TaskId, -1, FString::Printf(TEXT("Failed to load flash file: %s"), *FilePath));
            return false;
        }
        return StartFileRecognizeData(TaskId, Config, Data);
    }

    virtual bool StartFileRecognizeData(const FString& TaskId, const FZLAsrFileConfig& Config, const TArray<uint8>& AudioData) override
    {
        Register(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        @autoreleasepool
        {
            NSString* AppID = ZLToNSString(Config.Auth.AppID);
            NSString* SecretID = ZLToNSString(Config.Auth.SecretID);
            NSString* SecretKey = ZLToNSString(Config.Auth.SecretKey);
            NSString* Token = ZLToNSString(Config.Auth.Token);

            QCloudFlashFileRecognizer* Recognizer = nil;
            if (Token.length > 0)
            {
                Recognizer = [[QCloudFlashFileRecognizer alloc] initWithAppId:AppID
                                                                     secretId:SecretID
                                                                    secretKey:SecretKey
                                                                        token:Token];
            }
            else
            {
                Recognizer = [[QCloudFlashFileRecognizer alloc] initWithAppId:AppID
                                                                     secretId:SecretID
                                                                    secretKey:SecretKey];
            }

            ZLAsrIOSFileDelegate* Delegate = [[ZLAsrIOSFileDelegate alloc] init];
            Delegate.Owner = this;
            Delegate.TaskId = ZLToNSString(TaskId);
            Recognizer.delegate = Delegate;

            QCloudFlashFileRecognizeParams* Params = [QCloudFlashFileRecognizeParams defaultRequestParams];
            Params.audioData = [NSData dataWithBytes:AudioData.GetData() length:AudioData.Num()];
            Params.voiceFormat = ZLToNSString(Config.VoiceFormat);
            Params.engineModelType = ZLToNSString(Config.EngineModelType);
            Params.filterDirty = Config.FilterDirty;
            Params.filterModal = Config.FilterModal;
            Params.filterPunc = Config.FilterPunc;
            Params.convertNumMode = Config.ConvertNumMode;
            Params.speakerDiarization = Config.SpeakerDiarization;
            Params.firstChannelOnly = Config.FirstChannelOnly;
            Params.wordInfo = Config.WordInfo;
            if (!Config.CustomizationID.IsEmpty())
            {
                Params.customizationID = ZLToNSString(Config.CustomizationID);
            }
            if (!Config.HotwordID.IsEmpty())
            {
                Params.hotwordID = ZLToNSString(Config.HotwordID);
            }

            FileRecognizers.Add(TaskId, (void*)CFBridgingRetain(Recognizer));
            FileDelegates.Add(TaskId, (void*)CFBridgingRetain(Delegate));

            [Recognizer recognize:Params];
            return true;
        }
#else
        Report(TaskId, -1, TEXT("iOS flash-file bridge requires QCloudFileRecognizer.xcframework, VoiceCommon.framework and QCloudFlashFileRecognizer [6]."));
        return false;
#endif
    }

    void OnRealtimeSlice(const FString& TaskId, const FString& Text, const FString& RawJson)
    {
        if (!Sink) return;
        FZLAsrSegmentResult Result;
        Result.Text = Text;
        Result.RawJson = RawJson;
        Sink->HandleRealtimeSlice(Result);
    }

    void OnRealtimeSegment(const FString& TaskId, const FString& Text, const FString& RawJson)
    {
        if (!Sink) return;
        FZLAsrSegmentResult Result;
        Result.Text = Text;
        Result.RawJson = RawJson;
        Result.SliceType = 2;
        Sink->HandleRealtimeSegment(Result);
    }

    void OnRealtimeFinish(const FString& TaskId, const FString& Text, const FString& RawJson)
    {
        if (!Sink) return;
        FZLAsrRecognitionResult Result;
        Result.bSuccess = true;
        Result.Text = Text;
        Result.RawJson = RawJson;
        Sink->HandleRealtimeFinal(Result);
        CleanupRealtime(TaskId);
    }

    void OnSentenceResult(const FString& TaskId, const FString& Text, const FString& RawJson, bool bSuccess)
    {
        if (!Sink) return;
        FZLAsrRecognitionResult Result;
        Result.bSuccess = bSuccess;
        Result.Text = Text;
        Result.RawJson = RawJson;
        Sink->HandleSentenceResult(Result);
        CleanupSentence(TaskId);
    }

    void OnFileResult(const FString& TaskId, const FString& Text, const FString& RawJson, bool bSuccess)
    {
        if (!Sink) return;
        FZLAsrRecognitionResult Result;
        Result.bSuccess = bSuccess;
        Result.Text = Text;
        Result.RawJson = RawJson;
        Sink->HandleFileResult(Result);
        CleanupFile(TaskId);
    }

    void OnVolume(const FString& TaskId, float Volume)
    {
        if (!Sink) return;
        Sink->HandleVolume(Volume);
    }

    void OnSilence(const FString& TaskId)
    {
        if (!Sink) return;
        Sink->HandleSilence();
    }

    void OnError(const FString& TaskId, int32 Code, const FString& Message, const FString& Raw)
    {
        if (!Sink) return;
        Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(Code, Message, Raw));
        CleanupRealtime(TaskId);
        CleanupSentence(TaskId);
        CleanupFile(TaskId);
    }

private:
    void Register(const FString& TaskId)
    {
        if (Sink)
        {
            FZLAsrBridgeRegistry::Get().Register(TaskId, Sink);
        }
    }

    void Report(const FString& TaskId, int32 NativeCode, const FString& Message)
    {
        if (!Sink) return;
        Sink->HandleError(FZLAsrJsonUtils::MakeErrorFromNativeCode(NativeCode, Message, TEXT("")));
    }

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
    QCloudSentenceRecognizer* BuildSentenceRecognizer(const FString& TaskId, const FZLAsrSentenceConfig& Config)
    {
        NSString* AppID = ZLToNSString(Config.Auth.AppID);
        NSString* SecretID = ZLToNSString(Config.Auth.SecretID);
        NSString* SecretKey = ZLToNSString(Config.Auth.SecretKey);
        NSString* Token = ZLToNSString(Config.Auth.Token);

        QCloudSentenceRecognizer* Recognizer = nil;
        if (Token.length > 0)
        {
            Recognizer = [[QCloudSentenceRecognizer alloc] initWithAppId:AppID
                                                                secretId:SecretID
                                                               secretKey:SecretKey
                                                                   token:Token];
        }
        else
        {
            Recognizer = [[QCloudSentenceRecognizer alloc] initWithAppId:AppID
                                                                secretId:SecretID
                                                               secretKey:SecretKey];
        }

        ZLAsrIOSSentenceDelegate* Delegate = [[ZLAsrIOSSentenceDelegate alloc] init];
        Delegate.Owner = this;
        Delegate.TaskId = ZLToNSString(TaskId);
        Recognizer.delegate = Delegate;

        SentenceRecognizers.Add(TaskId, (void*)CFBridgingRetain(Recognizer));
        SentenceDelegates.Add(TaskId, (void*)CFBridgingRetain(Delegate));
        return Recognizer;
    }
#endif

    void CleanupRealtime(const FString& TaskId)
    {
        FZLAsrBridgeRegistry::Get().Unregister(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = RealtimeRecognizers.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            RealtimeRecognizers.Remove(TaskId);
        }
        if (void** Found = RealtimeDelegates.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            RealtimeDelegates.Remove(TaskId);
        }
#endif
    }

    void CleanupSentence(const FString& TaskId)
    {
        FZLAsrBridgeRegistry::Get().Unregister(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = SentenceRecognizers.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            SentenceRecognizers.Remove(TaskId);
        }
        if (void** Found = SentenceDelegates.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            SentenceDelegates.Remove(TaskId);
        }
#endif
    }

    void CleanupFile(const FString& TaskId)
    {
        FZLAsrBridgeRegistry::Get().Unregister(TaskId);
#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
        if (void** Found = FileRecognizers.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            FileRecognizers.Remove(TaskId);
        }
        if (void** Found = FileDelegates.Find(TaskId))
        {
            CFRelease((CFTypeRef)(*Found));
            FileDelegates.Remove(TaskId);
        }
#endif
    }

private:
    IZLAsrTaskSink* Sink = nullptr;

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
    TMap<FString, void*> RealtimeRecognizers;
    TMap<FString, void*> RealtimeDelegates;
    TMap<FString, void*> SentenceRecognizers;
    TMap<FString, void*> SentenceDelegates;
    TMap<FString, void*> FileRecognizers;
    TMap<FString, void*> FileDelegates;
#endif
};

#if ZLASR_IOS_TENCENT_SDK_AVAILABLE
@implementation ZLAsrIOSRealtimeDelegate

- (void)realTimeRecognizerOnSliceRecognize:(id)recognizer result:(id)result
{
    NSString* text = [result valueForKey:@"text"];
    NSString* raw = @"";
    if (self.Owner)
    {
        self.Owner->OnRealtimeSlice(ZLToFString(self.TaskId), ZLToFString(text), ZLToFString(raw));
    }
}

- (void)realTimeRecognizerOnSegmentSuccessRecognize:(id)recognizer result:(id)result
{
    NSString* text = [result valueForKey:@"text"];
    NSString* raw = @"";
    if (self.Owner)
    {
        self.Owner->OnRealtimeSegment(ZLToFString(self.TaskId), ZLToFString(text), ZLToFString(raw));
    }
}

- (void)realTimeRecognizerDidFinish:(id)recognizer result:(NSString *)result
{
    if (self.Owner)
    {
        self.Owner->OnRealtimeFinish(ZLToFString(self.TaskId), ZLToFString(result), ZLToFString(result));
    }
}

- (void)realTimeRecognizerDidError:(id)recognizer result:(id)result
{
    NSString* message = [result valueForKey:@"message"];
    if (self.Owner)
    {
        self.Owner->OnError(ZLToFString(self.TaskId), -1, ZLToFString(message), TEXT(""));
    }
}

- (void)realTimeRecognizerDidStartRecord:(id)recognizer error:(NSError * _Nullable)error
{
    if (error && self.Owner)
    {
        self.Owner->OnError(ZLToFString(self.TaskId), -103, ZLToFString(error.localizedDescription), TEXT(""));
    }
}

- (void)realTimeRecognizerDidStopRecord:(id)recognizer
{
}

- (void)realTimeRecognizerDidUpdateVolumeDB:(id)recognizer volume:(float)volume
{
    if (self.Owner)
    {
        self.Owner->OnVolume(ZLToFString(self.TaskId), volume);
    }
}

@end

@implementation ZLAsrIOSSentenceDelegate

- (void)oneSentenceRecognizerDidRecognize:(id)recognizer text:(nullable NSString *)text error:(nullable NSError *)error resultData:(nullable NSDictionary *)resultData
{
    if (!self.Owner) return;
    FString Raw;
    if (resultData)
    {
        NSData* JsonData = [NSJSONSerialization dataWithJSONObject:resultData options:0 error:nil];
        NSString* JsonText = [[NSString alloc] initWithData:JsonData encoding:NSUTF8StringEncoding];
        Raw = ZLToFString(JsonText);
    }

    if (error)
    {
        self.Owner->OnError(ZLToFString(self.TaskId), -1, ZLToFString(error.localizedDescription), Raw);
    }
    else
    {
        self.Owner->OnSentenceResult(ZLToFString(self.TaskId), ZLToFString(text), Raw, true);
    }
}

- (void)oneSentenceRecognizerDidStartRecord:(id)recognizer error:(nullable NSError *)error
{
    if (error && self.Owner)
    {
        self.Owner->OnError(ZLToFString(self.TaskId), -103, ZLToFString(error.localizedDescription), TEXT(""));
    }
}

- (void)oneSentenceRecognizerDidEndRecord:(id)recognizer
{
}

- (void)oneSentenceRecognizerDidUpdateVolume:(id)recognizer volume:(float)volume
{
    if (self.Owner)
    {
        self.Owner->OnVolume(ZLToFString(self.TaskId), volume);
    }
}

@end

@implementation ZLAsrIOSFileDelegate

- (void)FlashFileRecognizer:(id _Nullable)recognizer status:(nullable NSInteger *)status text:(nullable NSString *)text resultData:(nullable NSDictionary *)resultData
{
    if (!self.Owner) return;

    FString Raw;
    if (resultData)
    {
        NSData* JsonData = [NSJSONSerialization dataWithJSONObject:resultData options:0 error:nil];
        NSString* JsonText = [[NSString alloc] initWithData:JsonData encoding:NSUTF8StringEncoding];
        Raw = ZLToFString(JsonText);
    }

    int32 StatusCode = 0;
    if (status)
    {
        StatusCode = (int32)(*status);
    }

    if (StatusCode != 0)
    {
        self.Owner->OnError(ZLToFString(self.TaskId), StatusCode, ZLToFString(text), Raw);
    }
    else
    {
        self.Owner->OnFileResult(ZLToFString(self.TaskId), ZLToFString(text), Raw, true);
    }
}

- (void)FlashFileRecognizer:(id _Nullable)recognizer error:(nullable NSError *)error resultData:(nullable NSDictionary *)resultData
{
    if (!self.Owner) return;

    FString Raw;
    if (resultData)
    {
        NSData* JsonData = [NSJSONSerialization dataWithJSONObject:resultData options:0 error:nil];
        NSString* JsonText = [[NSString alloc] initWithData:JsonData encoding:NSUTF8StringEncoding];
        Raw = ZLToFString(JsonText);
    }

    self.Owner->OnError(ZLToFString(self.TaskId), -1, ZLToFString(error.localizedDescription), Raw);
}

@end
#endif

TSharedPtr<IZLAsrPlatformBridge> CreateIOSBridge()
{
    return MakeShared<FZLAsrIOSBridge>();
}
#endif
