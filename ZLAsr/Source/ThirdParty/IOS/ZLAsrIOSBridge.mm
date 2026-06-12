#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>

// 对接说明：
// 实时识别需要 QCloudRealTime.xcframework + VoiceCommon.framework，并使用
// QCloudRealTimeRecognizer / QCloudConfig / delegate [4]
// 一句话识别需要 QCloudOneSentence.xcframework + VoiceCommon.framework，并使用
// QCloudSentenceRecognizer / delegate [5]
// 文件极速版需要 QCloudFileRecognizer.xcframework + VoiceCommon.framework，并使用
// QCloudFlashFileRecognizer / delegate [6]

@interface ZLAsrIOSBridge : NSObject
@end

@implementation ZLAsrIOSBridge
@end
