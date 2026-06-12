package com.zl.asr;

import android.app.Activity;
import android.util.Log;

public class ZLAsrBridge {
    private static final String TAG = "ZLAsrBridge";
    private static Activity sActivity;

    public static void initialize(Activity activity) {
        sActivity = activity;
        Log.i(TAG, "initialize");
    }

    public static Activity getActivity() {
        return sActivity;
    }

    public static void onRealtimeSlice(String taskId, String json) { nativeOnRealtimeSlice(taskId, json); }
    public static void onRealtimeSegment(String taskId, String json) { nativeOnRealtimeSegment(taskId, json); }
    public static void onRealtimeFinal(String taskId, String json) { nativeOnRealtimeFinal(taskId, json); }
    public static void onSentenceResult(String taskId, String json) { nativeOnSentenceResult(taskId, json); }
    public static void onFileResult(String taskId, String json) { nativeOnFileResult(taskId, json); }
    public static void onVolume(String taskId, float volume) { nativeOnVolume(taskId, volume); }
    public static void onSilence(String taskId) { nativeOnSilence(taskId); }
    public static void onError(String taskId, int nativeCode, String message, String raw) { nativeOnError(taskId, nativeCode, message, raw); }

    private static native void nativeOnRealtimeSlice(String taskId, String json);
    private static native void nativeOnRealtimeSegment(String taskId, String json);
    private static native void nativeOnRealtimeFinal(String taskId, String json);
    private static native void nativeOnSentenceResult(String taskId, String json);
    private static native void nativeOnFileResult(String taskId, String json);
    private static native void nativeOnVolume(String taskId, float volume);
    private static native void nativeOnSilence(String taskId);
    private static native void nativeOnError(String taskId, int nativeCode, String message, String raw);
}
