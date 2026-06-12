package com.zl.asr;

import android.app.Activity;
import android.util.Log;
import org.json.JSONObject;

public class ZLAsrRealtimeProxy {
    private static final String TAG = "ZLAsrRealtimeProxy";

    public boolean start(String taskId, String configJson) {
        Activity activity = ZLAsrBridge.getActivity();
        if (activity == null) {
            ZLAsrBridge.onError(taskId, -1, "Activity is null", "");
            return false;
        }

        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            JSONObject auth = ZLAsrConfigParser.auth(root);

            String appId = ZLAsrConfigParser.string(auth, "AppID", "");
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
            String hotwordId = ZLAsrConfigParser.string(root, "HotwordID", "");
            String customizationId = ZLAsrConfigParser.string(root, "CustomizationID", "");
            double noiseThreshold = ZLAsrConfigParser.number(root, "NoiseThreshold", 0.0);
            int maxSpeakTime = ZLAsrConfigParser.integer(root, "MaxSpeakTime", 0);
            boolean enableVolume = ZLAsrConfigParser.bool(root, "EnableVolume", true);
            boolean enableSilence = ZLAsrConfigParser.bool(root, "EnableSilenceDetect", false);
            int silenceTimeoutMs = ZLAsrConfigParser.integer(root, "SilenceTimeoutMs", 5000);

            Log.i(TAG, "Realtime task=" + taskId + " appId=" + appId + " engine=" + engineModelType);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android realtime SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stop(String taskId) { Log.i(TAG, "stop realtime=" + taskId); }
    public void cancel(String taskId) { Log.i(TAG, "cancel realtime=" + taskId); }
}
