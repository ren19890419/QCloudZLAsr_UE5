package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrSentenceProxy {
    private static final String TAG = "ZLAsrSentenceProxy";

    public boolean recognizeUrl(String taskId, String configJson, String url) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeUrl taskId=" + taskId + " url=" + url + " engine=" + ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh"));
            // 按文档这里应使用 QCloudOneSentenceRecognizer，支持 URL 模式 [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence URL SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeData taskId=" + taskId + " size=" + (data != null ? data.length : 0));
            // 按文档这里应使用 QCloudOneSentenceRecognizer，支持 data 模式 [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence data SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean startRecorder(String taskId, String configJson) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "startRecorder taskId=" + taskId + " engine=" + ZLAsrConfigParser.string(root, "EngSerViceType", "16k_zh"));
            // 按文档这里应使用 recognizeWithRecorder() [2]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android sentence recorder SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public void stopRecorder(String taskId) {
        Log.i(TAG, "stopRecorder " + taskId);
    }
}
