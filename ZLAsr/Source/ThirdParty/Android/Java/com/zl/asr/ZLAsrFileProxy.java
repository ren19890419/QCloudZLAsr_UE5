package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrFileProxy {
    private static final String TAG = "ZLAsrFileProxy";

    public boolean recognizePath(String taskId, String configJson, String path) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            Log.i(TAG, "file path task=" + taskId + " engine=" + engine + " path=" + path);
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android flash file SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            String engine = ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh");
            Log.i(TAG, "file data task=" + taskId + " engine=" + engine + " size=" + (data != null ? data.length : 0));
            ZLAsrBridge.onError(taskId, -1, "Bind real Tencent Android flash file SDK classes here", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }
}
