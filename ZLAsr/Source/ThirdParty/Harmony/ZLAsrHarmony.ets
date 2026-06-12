// 基于腾讯云 Harmony SDK 的桥接草案：
// 实时识别：Builder + Controller + Listener + DataSource [7]
// 一句话识别：Builder + Controller [8]
// 文件极速版：Builder + Controller.build(data) [9]

export class ZLAsrHarmony {
  static async startRealtime(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, source: any, listener: any): Promise<any> {
    // 真实接入时:
    // let builder = new QCloud.RealTime.Builder()
    // builder.appID = appID
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return builder.build(source, listener)
    throw new Error("Harmony realtime bridge placeholder");
  }

  static async startOneSentence(secretID: string, secretKey: string, token: string, params: Map<string, string>): Promise<string> {
    // let builder = new QCloud.OneSentence.Builder()
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return await builder.build().task
    throw new Error("Harmony one sentence bridge placeholder");
  }

  static async startFileFlash(appID: string, secretID: string, secretKey: string, token: string, params: Map<string, string>, data: ArrayBuffer): Promise<string> {
    // let builder = new QCloud.FileFlash.Builder()
    // builder.appID = appID
    // builder.secretID = secretID
    // builder.secretKey = secretKey
    // builder.token = token
    // params.forEach((v, k) => builder.setApiParam(k, v))
    // return await builder.build(data).task
    throw new Error("Harmony file flash bridge placeholder");
  }
}
