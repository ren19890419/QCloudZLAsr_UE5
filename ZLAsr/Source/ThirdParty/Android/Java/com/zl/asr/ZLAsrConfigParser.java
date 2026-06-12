package com.zl.asr;

import org.json.JSONObject;

public class ZLAsrConfigParser {
    public static JSONObject parse(String json) throws Exception { return new JSONObject(json); }
    public static JSONObject auth(JSONObject root) throws Exception { return root.getJSONObject("Auth"); }
    public static String string(JSONObject obj, String key, String def) { return obj.has(key) ? obj.optString(key, def) : def; }
    public static int integer(JSONObject obj, String key, int def) { return obj.has(key) ? obj.optInt(key, def) : def; }
    public static boolean bool(JSONObject obj, String key, boolean def) { return obj.has(key) ? obj.optBoolean(key, def) : def; }
    public static double number(JSONObject obj, String key, double def) { return obj.has(key) ? obj.optDouble(key, def) : def; }
}
