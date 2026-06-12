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
