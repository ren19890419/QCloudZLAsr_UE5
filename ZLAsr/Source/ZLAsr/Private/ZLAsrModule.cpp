#include "ZLAsrModule.h"

DEFINE_LOG_CATEGORY(LogZLAsr);

void FZLAsrModule::StartupModule()
{
    UE_LOG(LogZLAsr, Log, TEXT("ZLAsr module startup"));
}

void FZLAsrModule::ShutdownModule()
{
    UE_LOG(LogZLAsr, Log, TEXT("ZLAsr module shutdown"));
}

IMPLEMENT_MODULE(FZLAsrModule, ZLAsr)
