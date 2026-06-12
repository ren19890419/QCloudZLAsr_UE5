package com.zl.asr;

import android.util.Log;
import org.json.JSONObject;

public class ZLAsrFileProxy {
    private static final String TAG = "ZLAsrFileProxy";

    public boolean recognizePath(String taskId, String configJson, String path) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizePath taskId=" + taskId + " path=" + path + " engine=" + ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh"));
            // 按文档这里应使用 QCloudFlashRecognizer + params.setPath(path) [3]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android file path SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }

    public boolean recognizeData(String taskId, String configJson, byte[] data) {
        try {
            JSONObject root = ZLAsrConfigParser.parse(configJson);
            Log.i(TAG, "recognizeData taskId=" + taskId + " size=" + (data != null ? data.length : 0) + " engine=" + ZLAsrConfigParser.string(root, "EngineModelType", "16k_zh"));
            // 按文档这里应使用 QCloudFlashRecognizer + params.setData(data) [3]
            ZLAsrBridge.onError(taskId, -1, "Tencent Android file data SDK symbols not linked in current source package", configJson);
            return false;
        } catch (Exception e) {
            ZLAsrBridge.onError(taskId, -1, e.getMessage(), configJson);
            return false;
        }
    }
}
