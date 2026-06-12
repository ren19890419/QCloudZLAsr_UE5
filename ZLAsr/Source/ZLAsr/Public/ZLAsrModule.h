#pragma once
#include "Modules/ModuleManager.h"

DECLARE_LOG_CATEGORY_EXTERN(LogZLAsr, Log, All);

class FZLAsrModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
