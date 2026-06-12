#pragma once
#include "CoreMinimal.h"
#include "ZLAsrTypes.h"
#include "ZLAsrDelegates.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeSlice, const FZLAsrSegmentResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeSegment, const FZLAsrSegmentResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnRealtimeFinal, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnSentenceResult, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnFileResult, const FZLAsrRecognitionResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnVolumeChanged, float, Volume);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FZLAsrOnSilenceDetected);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FZLAsrOnAsrError, const FZLAsrError&, Error);
