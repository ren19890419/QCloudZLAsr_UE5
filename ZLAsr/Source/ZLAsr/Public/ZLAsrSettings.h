#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "ZLAsrTypes.h"
#include "ZLAsrSettings.generated.h"

UENUM(BlueprintType)
enum class EZLAsrLogLevel : uint8
{
    Error,
    Warn,
    Info,
    Debug
};

UCLASS(Config=Game, DefaultConfig, BlueprintType)
class ZLASR_API UZLAsrSettings : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Auth")
    FZLAsrAuthConfig DefaultAuth;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Runtime")
    bool bEnableSdkLogFile = false;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Runtime")
    EZLAsrLogLevel LogLevel = EZLAsrLogLevel::Error;

    UPROPERTY(Config, EditAnywhere, BlueprintReadWrite, Category="Runtime")
    bool bEnableHarmonyExperimental = true;
};
