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
