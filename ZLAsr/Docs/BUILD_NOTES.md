# ZLAsr 构建说明

## 当前状态
本目录已补到“尽可能可编译”的版本：
- UE 公共层已完整补齐
- Android 侧已补 JNI/C++ 桥接、Java 配置解析、入口类
- iOS 侧已补 Objective-C++ 桥接骨架
- Harmony 侧已补 ArkTS 任务桥接草案

## 仍然不能保证直接通过编译的原因
1. Android 真实 AAR 中的类包名和签名需要以 SDK 实际内容为准 [1][2][3]
2. iOS 真实 framework 头文件名和符号需要以 SDK 实际内容为准 [4][5][6]
3. Harmony 需要你本地 UE 到 ArkTS 的桥接通道 [7][8][9]

## Android 对接点
- 实时识别：AAIClient / AudioRecognizeRequest / AudioRecognizeConfiguration / Listeners [1]
- 一句话识别：QCloudOneSentenceRecognizer [2]
- 文件极速版：QCloudFlashRecognizer [3]

## iOS 对接点
- 实时识别：QCloudRealTimeRecognizer / QCloudConfig / delegate [4]
- 一句话识别：QCloudSentenceRecognizer / delegate [5]
- 文件极速版：QCloudFlashFileRecognizer / delegate [6]

## Harmony 对接点
- 实时识别：QCloud.RealTime.Builder.build(source, listener) [7]
- 一句话识别：QCloud.OneSentence.Builder.build().task [8]
- 文件极速版：QCloud.FileFlash.Builder.build(data).task [9]
