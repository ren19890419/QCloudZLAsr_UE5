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
