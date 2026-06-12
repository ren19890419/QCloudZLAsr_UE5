package com.zl.asr;

import android.app.Activity;
import android.util.Log;

import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class ZLAsrRealtimeProxy {
    private static final String TAG = "ZLAsrRealtimeProxy";

    private final Map<String, Object> tasks = new HashMap<>();

    public boolean start(String taskId, String configJson) {
        Activity activity = ZLAsrBridge.getActivity();
        if (activity == null) {
            ZLAsrBridge.onError(taskId, -1, "Activity is null", "");
            return false;
        }

        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            JSONObject auth = ZLAsrConfigParser.auth(root);

            String appIdStr = ZLAsrConfigParser.string(auth, "AppID", "");
            String secretId = ZLAsrConfigParser.string(auth, "SecretID", "");
            String secretKey = ZLAsrConfigParser.string(auth, "SecretKey", "");
            String token = ZLAsrConfigParser.string(auth, "Token", "");

            String engineModelType = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            int filterDirty = ZLAsrConfigParser.integer(root, "FilterDirty", 0);
            int filterModal = ZLAsrConfigParser.integer(root, "FilterModal", 0);
            int filterPunc = ZLAsrConfigParser.integer(root, "FilterPunc", 0);
            int convertNumMode = ZLAsrConfigParser.integer(root, "ConvertNumMode", 1);
            int needVad = ZLAsrConfigParser.integer(root, "NeedVad", 1);
            int wordInfo = ZLAsrConfigParser.integer(root, "WordInfo", 0);
            String hotwordID = ZLAsrConfigParser.string(root, "HotwordID", "");
            String customizationID = ZLAsrConfigParser.string(root, "CustomizationID", "");
            double noiseThreshold = ZLAsrConfigParser.number(root, "NoiseThreshold", 0.0);
            int maxSpeakTime = ZLAsrConfigParser.integer(root, "MaxSpeakTime", 0);
            boolean enableVolume = ZLAsrConfigParser.bool(root, "EnableVolume", true);
            boolean enableSilence = ZLAsrConfigParser.bool(root, "EnableSilenceDetect", false);
            int silenceTimeoutMs = ZLAsrConfigParser.integer(root, "SilenceTimeoutMs", 5000);

            Log.i(TAG, "Realtime start taskId=" + taskId + " appId=" + appIdStr + " engine=" + engineModelType);

            // 这里按腾讯云 Android 实时识别文档需要使用 AAIClient、AudioRecognizeRequest、
            // AudioRecognizeConfiguration、AudioRecognizeResultListener 和 AudioRecognizeStateListener [1]
            // 由于当前对话上下文无法访问真实 AAR 中的 classpath 和 import 符号，下面保留最接近接入点。
            // 接入真实 SDK 时，请在这里：
            // 1. 构造 AAIClient（支持直接鉴权或 STS）[1]
            // 2. 构造 AudioRecognizeRequest.Builder 并设置 engine/filter/hotword/customization/vad/wordInfo/noiseThreshold/maxSpeakTime [1]
            // 3. 构造 AudioRecognizeConfiguration 开启静音检测、音量回调 [1]
            // 4. 在回调 onSliceSuccess / onSegmentSuccess / onSuccess / onFailure 中透传给 ZLAsrBridge [1]
            // 5. 在 AudioRecognizeStateListener.onVoiceVolume / onSilentDetectTimeOut 中透传音量和静音事件 [1]

            ZLAsrBridge.onError(taskId, -1, "Tencent Android realtime SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stop(String taskId) {
        Log.i(TAG, "stop realtime: " + taskId);
        // aaiClient.stopAudioRecognize() [1]
    }

    public void cancel(String taskId) {
        Log.i(TAG, "cancel realtime: " + taskId);
        // aaiClient.cancelAudioRecognize() [1]
    }
}
