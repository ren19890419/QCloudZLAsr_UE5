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
