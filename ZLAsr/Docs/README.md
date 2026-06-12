# ZLAsr

这是一个 UE 插件源码骨架，目录已生成到 `/mnt/upload/ZLAsr`。

## 重要说明
当前输出包含：
- UE 公共层完整 C++/Blueprint 接口
- Android UPL 与 Java 桥接占位实现
- iOS Objective-C++ 占位桥接
- Harmony ArkTS 占位桥接

## 为什么不是最终可编译商用品质版
因为当前上下文只给出了腾讯云文档能力边界与接入类说明，未提供：
- 实际 SDK 二进制包
- AAR / xcframework / HAR 的真实文件与类签名
- UE5.7 对 Harmony 的实际平台 toolchain
- 你的本地打包链路

因此这里生成的是“完整插件工程目录 + 可继续填充的源码基础”，不是已经对接二进制 SDK 的最终成品。

## 文档依据
- Android 实时识别：AAIClient / AudioRecognizeRequest / 录音与回调 [1]
- Android 一句话识别：QCloudOneSentenceRecognizer [2]
- Android 文件极速版：QCloudFlashRecognizer [3]
- iOS 实时识别：QCloudRealTimeRecognizer / QCloudConfig [4]
- iOS 一句话识别：QCloudSentenceRecognizer [5]
- iOS 文件极速版：QCloudFlashFileRecognizer [6]
- Harmony 实时识别：Builder / Controller / Listener / DataSource [7]
- Harmony 一句话识别：Builder / Controller [8]
- Harmony 文件极速版：Builder / Controller [9]
