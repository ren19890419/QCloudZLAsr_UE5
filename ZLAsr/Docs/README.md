# ZLAsr

这个插件生成器基于腾讯云三端 SDK 能力边界组织：
- Android 实时识别：AAIClient / AudioRecognizeRequest / AudioRecognizeConfiguration [1]
- Android 一句话识别：QCloudOneSentenceRecognizer [2]
- Android 文件极速版：QCloudFlashRecognizer [3]
- iOS 实时识别：QCloudRealTimeRecognizer / QCloudConfig [4]
- iOS 一句话识别：QCloudSentenceRecognizer [5]
- iOS 文件极速版：QCloudFlashFileRecognizer [6]
- Harmony 实时识别：Builder / Controller / Listener / DataSource [7]
- Harmony 一句话识别：Builder / Controller [8]
- Harmony 文件极速版：Builder.build(data) [9]

注意：
这份脚本生成的是“完整插件工程代码清单 + 三端桥接骨架”。
若要真正编译，需要你本地放入真实 AAR / xcframework / har，并按实际 SDK 符号补全最终桥接。
