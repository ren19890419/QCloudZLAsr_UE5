# ZLAsr 编译问题清单

## 一、总体状态

- 已具备 UE 插件基础结构、Blueprint/C++ 接口、平台桥接抽象。
- 已具备 Android JNI/C++/Java 调用链基础。
- 已具备 iOS Objective-C++ 桥接入口。
- 已具备 Harmony ArkTS 桥接草案。
- 但距离“直接编译通过”仍差真实 SDK 符号绑定、平台构建细节和若干源码问题。

## 二、优先级最高的问题

1. Android AAR 真实类名/包名/方法签名未绑定。
2. iOS xcframework 头文件和符号未接入。
3. Harmony UE <-> ArkTS 调用链未落地。
4. uplugin 仅声明 Android/IOS，未声明 Harmony。
5. 部分源码存在潜在编译问题，例如缺少头文件包含、Factory 选择逻辑对 Harmony 不准确。

## 三、按平台问题明细

### Android

- 依赖 `asr-realtime-release.aar`、`okhttp:4.2.2`，并需录音/网络权限 [1]。
- 一句话识别依赖 `asr-one-sentence-release.aar`、`gson:2.8.5` [2]。
- 文件极速版依赖 `asr-file-recognize-release.aar`、`gson:2.8.5` [3]。
- 当前 Java 已建立 `ZLAsrNativeEntry` 和 3 个 proxy，但未替换成真实 `AAIClient / QCloudOneSentenceRecognizer / QCloudFlashRecognizer` 调用 [1][2][3]。
- `ZLAsrAndroidBridge.cpp` 可能需要补 `Misc/FileHelper.h` 等头文件。
- UPL 的 Java 复制路径和 AAR 放置路径仍需按实际工程核对。

### iOS

- 实时识别需要 `QCloudRealTime.xcframework + VoiceCommon.framework`，并申请麦克风权限 [4]。
- 一句话识别需要 `QCloudOneSentence.xcframework + VoiceCommon.framework` [5]。
- 文件极速版需要 `QCloudFileRecognizer.xcframework + VoiceCommon.framework` [6]。
- 当前 `ZLAsrIOSBridge.mm` 仍是桥接入口，未接 `QCloudRealTimeRecognizer / QCloudSentenceRecognizer / QCloudFlashFileRecognizer` 真实调用 [4][5][6]。
- Build.cs 中 AdditionalFrameworks 路径需与你本地 zip/framework 实际文件名核对。

### Harmony

- 实时识别 har 依赖 `qcloudrealtime`，基于 Builder/Controller/Listener/DataSource [7]。
- 一句话识别 har 依赖 `qcloudonesentence`，通过 Builder.build().task 获取结果 [8]。
- 文件极速版 har 依赖 `qcloudfileflash`，通过 Builder.build(data).task 获取结果 [9]。
- 当前 ArkTS 只有桥接草案，未与 UE runtime 建立消息通道。
- 另外 `.uplugin` 尚未声明 Harmony 平台。

## 四、建议修复顺序

1. 先修 Android：文档最完整、当前 JNI 链已打通 [1][2][3]。
2. 再修 iOS：Objective-C++ 桥接较直接 [4][5][6]。
3. 最后修 Harmony：依赖 UE 到 ArkTS 的实际平台方案 [7][8][9]。
