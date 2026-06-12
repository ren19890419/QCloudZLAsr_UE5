package com.zl.asr;

public class ZLAsrNativeEntry {
    private final ZLAsrRealtimeProxy realtimeProxy = new ZLAsrRealtimeProxy();
    private final ZLAsrSentenceProxy sentenceProxy = new ZLAsrSentenceProxy();
    private final ZLAsrFileProxy fileProxy = new ZLAsrFileProxy();

    public boolean startRealtime(String taskId, String configJson) {
        return realtimeProxy.start(taskId, configJson);
    }

    public void stopRealtime(String taskId) {
        realtimeProxy.stop(taskId);
    }

    public void cancelRealtime(String taskId) {
        realtimeProxy.cancel(taskId);
    }

    public boolean startSentenceUrl(String taskId, String configJson, String url) {
        return sentenceProxy.recognizeUrl(taskId, configJson, url);
    }

    public boolean startSentenceData(String taskId, String configJson, byte[] data) {
        return sentenceProxy.recognizeData(taskId, configJson, data);
    }

    public boolean startSentenceRecorder(String taskId, String configJson) {
        return sentenceProxy.startRecorder(taskId, configJson);
    }

    public void stopSentenceRecorder(String taskId) {
        sentenceProxy.stopRecorder(taskId);
    }

    public boolean startFilePath(String taskId, String configJson, String path) {
        return fileProxy.recognizePath(taskId, configJson, path);
    }

    public boolean startFileData(String taskId, String configJson, byte[] data) {
        return fileProxy.recognizeData(taskId, configJson, data);
    }
}
