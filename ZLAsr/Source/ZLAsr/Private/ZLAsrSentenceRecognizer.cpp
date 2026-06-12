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
