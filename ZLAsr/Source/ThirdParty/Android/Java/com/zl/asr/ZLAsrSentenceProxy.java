package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrSentenceProxy {
    private static final String TAG = "ZLAsrSentenceProxy";

    public boolean recognizeUrl(String taskId, String configJson, String url) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence url task=" + taskId + " engine=" + engine + " url=" + url);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android one sentence SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence data task=" + taskId + " engine=" + engine + " size=" + (data != null ? data.length : 0));
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android one sentence SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean startRecorder(String taskId, String configJson) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh");
            Log.i(TAG, "sentence recorder task=" + taskId + " engine=" + engine);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android recorder SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stopRecorder(String taskId) { Log.i(TAG, "stop recorder=" + taskId); }
}
