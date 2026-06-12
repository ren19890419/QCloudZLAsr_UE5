/**
 * ZLAsrHarmony.ets
 *
 * 说明：
 * 1. 这是基于腾讯云 HarmonyOS NEXT 语音识别 SDK 文档能力设计的完整桥接实现。
 * 2. 由于当前上下文只提供了文档，不包含真实 har 的最终导出类型声明文件，
 *    所以这里实现为“尽可能完整、最接近可落地”的 ArkTS 版本。
 * 3. 代码严格围绕三类能力组织：
 *    - 实时语音识别：QCloud.RealTime.Builder / Controller / Listener / DataSource [7]
 *    - 一句话识别：QCloud.OneSentence.Builder / Controller [8]
 *    - 文件极速版：QCloud.FileFlash.Builder / Controller [9]
 */

declare const QCloud: any;

export enum ZLAsrHarmonyErrorCode {
  UNKNOWN = -1,
  NETWORK = 1,
  SERVER = 2,
  SIGNATURE = 3,
  PARAMETER = 4,
  CANCEL = 5,
  CREATE_FILE = 6,
  DATA_LENGTH = 7,
}

export interface ZLAsrAuthConfig {
  appID?: string
  secretID: string
  secretKey: string
  token?: string
}

export interface ZLAsrRealtimeConfig {
  auth: ZLAsrAuthConfig
  engineModelType?: string
  needVad?: number
  hotwordID?: string
  customizationID?: string
  filterDirty?: number
  filterModal?: number
  filterPunc?: number
  filterEmptyResult?: number
  convertNumMode?: number
  wordInfo?: number
  vadSilenceTime?: number
  maxSpeakTime?: number
  noiseThreshold?: number
  hotwordList?: string
  inputSampleRate?: number

  slice?: number
  enableOpus?: boolean
  enableSilence?: boolean
  enableDetectVolume?: boolean
  silenceTimeout?: number
  loggerLevel?: number
  saveDataPath?: string
}

export interface ZLAsrSentenceConfig {
  auth: ZLAsrAuthConfig
  engSerViceType?: string
  sourceType?: number
  voiceFormat?: string
  url?: string
  data?: ArrayBuffer
  filterDirty?: number
  filterModal?: number
  filterPunc?: number
  convertNumMode?: number
  wordInfo?: number
  hotwordID?: string
}

export interface ZLAsrFileConfig {
  auth: ZLAsrAuthConfig
  engineModelType?: string
  voiceFormat?: string
  filterDirty?: number
  filterModal?: number
  filterPunc?: number
  convertNumMode?: number
  speakerDiarization?: number
  firstChannelOnly?: number
  wordInfo?: number
  customizationID?: string
  hotwordID?: string
}

export interface ZLAsrRealtimeListener {
  onSlice?: (data: string, raw: string) => void
  onSegment?: (data: string, raw: string) => void
  onData?: (raw: string) => void
  onSilence?: () => void
  onVolume?: (db: number) => void
  onLogger?: (level: number, message: string) => void
  onError?: (code: number, message: string) => void
  onFinish?: () => void
}

export interface ZLAsrPcmDataSource {
  start: () => Promise<void>
  stop: () => Promise<void>
  read: (ms: number) => Promise<ArrayBuffer>
  empty: boolean
  voice_format: string
}

export interface ZLAsrTaskController<T = string> {
  task: Promise<T>
  stop?: () => void
  cancel?: () => void
  voice_id?: string
}

export class ZLAsrHarmonyUtils {
  static setIfValid(builder: any, key: string, value: string | number | null | undefined): void {
    if (value === undefined) {
      return
    }
    if (value === null) {
      builder.setApiParam(key, null)
      return
    }
    builder.setApiParam(key, value)
  }

  static normalizeError(e: any): { code: number; message: string } {
    if (!e) {
      return { code: ZLAsrHarmonyErrorCode.UNKNOWN, message: 'unknown error' }
    }
    if (typeof e.code === 'number') {
      return { code: e.code, message: `${e.message ?? e.toString?.() ?? 'error'}` }
    }
    return { code: ZLAsrHarmonyErrorCode.UNKNOWN, message: `${e.message ?? e.toString?.() ?? 'error'}` }
  }

  static ensureString(v: any, defaultValue: string = ''): string {
    if (v === undefined || v === null) return defaultValue
    return `${v}`
  }

  static ensureNumber(v: any, defaultValue: number): number {
    if (v === undefined || v === null || Number.isNaN(Number(v))) return defaultValue
    return Number(v)
  }
}

export class ZLAsrRealtimeTask {
  private _controller: any | null = null
  private _listener: ZLAsrRealtimeListener | null = null

  get controller(): any | null {
    return this._controller
  }

  get voiceId(): string {
    if (!this._controller) {
      return ''
    }
    return ZLAsrHarmonyUtils.ensureString(this._controller.voice_id, '')
  }

  async start(config: ZLAsrRealtimeConfig, source: ZLAsrPcmDataSource, listener?: ZLAsrRealtimeListener): Promise<void> {
    this._listener = listener ?? null

    const builder = new QCloud.RealTime.Builder()
    builder.appID = ZLAsrHarmonyUtils.ensureString(config.auth.appID, '')
    builder.secretID = ZLAsrHarmonyUtils.ensureString(config.auth.secretID, '')
    builder.secretKey = ZLAsrHarmonyUtils.ensureString(config.auth.secretKey, '')
    builder.token = ZLAsrHarmonyUtils.ensureString(config.auth.token, '')

    if (config.slice !== undefined) builder.slice = config.slice
    if (config.enableOpus !== undefined) builder.enableOpus = config.enableOpus
    if (config.enableSilence !== undefined) builder.enableSilence = config.enableSilence
    if (config.enableDetectVolume !== undefined) builder.enableDetectVolume = config.enableDetectVolume
    if (config.silenceTimeout !== undefined) builder.silenceTimeout = config.silenceTimeout
    if (config.loggerLevel !== undefined) builder.loggerLevel = config.loggerLevel
    if (config.saveDataPath !== undefined) builder.saveDataPath = config.saveDataPath

    // 这些参数对应 Builder 中封装的 API 参数能力 [7]
    if (config.engineModelType !== undefined) builder.engineModelType = config.engineModelType
    if (config.needVad !== undefined) builder.needVad = config.needVad
    if (config.hotwordID !== undefined) builder.hotwordID = config.hotwordID
    if (config.customizationID !== undefined) builder.customizationID = config.customizationID
    if (config.filterDirty !== undefined) builder.filterDirty = config.filterDirty
    if (config.filterModal !== undefined) builder.filterModal = config.filterModal
    if (config.filterPunc !== undefined) builder.filterPunc = config.filterPunc
    if (config.filterEmptyResult !== undefined) builder.filterEmptyResult = config.filterEmptyResult
    if (config.convertNumMode !== undefined) builder.convertNumMode = config.convertNumMode
    if (config.wordInfo !== undefined) builder.wordInfo = config.wordInfo
    if (config.vadSilenceTime !== undefined) builder.vadSilenceTime = config.vadSilenceTime
    if (config.maxSpeakTime !== undefined) builder.maxSpeakTime = config.maxSpeakTime
    if (config.noiseThreshold !== undefined) builder.noiseThreshold = config.noiseThreshold
    if (config.hotwordList !== undefined) builder.hotwordList = config.hotwordList
    if (config.inputSampleRate !== undefined) builder.inputSampleRate = config.inputSampleRate

    try {
      this._controller = builder.build(source, {
        onSlice: (data: string, raw: string) => {
          if (this._listener?.onSlice) this._listener.onSlice(data, raw)
        },
        onSegment: (data: string, raw: string) => {
          if (this._listener?.onSegment) this._listener.onSegment(data, raw)
        },
        onData: (data: string) => {
          if (this._listener?.onData) this._listener.onData(data)
        },
        onSilence: () => {
          if (this._listener?.onSilence) this._listener.onSilence()
        },
        onVolume: (db: number) => {
          if (this._listener?.onVolume) this._listener.onVolume(db)
        },
        onLogger: (level: number, message: string) => {
          if (this._listener?.onLogger) this._listener.onLogger(level, message)
        },
      })

      await this._controller.task
      if (this._listener?.onFinish) this._listener.onFinish()
    } catch (e) {
      const err = ZLAsrHarmonyUtils.normalizeError(e)
      if (this._listener?.onError) this._listener.onError(err.code, err.message)
      throw e
    }
  }

  stop(): void {
    if (this._controller && typeof this._controller.stop === 'function') {
      this._controller.stop()
    }
  }

  cancel(): void {
    if (this._controller && typeof this._controller.cancel === 'function') {
      this._controller.cancel()
    }
  }
}

export class ZLAsrOneSentenceTask {
  private _controller: any | null = null

  get controller(): any | null {
    return this._controller
  }

  async recognize(config: ZLAsrSentenceConfig): Promise<string> {
    const builder = new QCloud.OneSentence.Builder()
    builder.secretID = ZLAsrHarmonyUtils.ensureString(config.auth.secretID, '')
    builder.secretKey = ZLAsrHarmonyUtils.ensureString(config.auth.secretKey, '')
    builder.token = ZLAsrHarmonyUtils.ensureString(config.auth.token, '')

    // 文档示例通过 setApiParam 设置一句话请求参数 [8]
    ZLAsrHarmonyUtils.setIfValid(builder, QCloud.OneSentence.kEngSerViceType, config.engSerViceType ?? '16k_zh')
    ZLAsrHarmonyUtils.setIfValid(builder, QCloud.OneSentence.kSourceType, config.sourceType ?? 0)
    ZLAsrHarmonyUtils.setIfValid(builder, QCloud.OneSentence.kVoiceFormat, config.voiceFormat ?? 'wav')

    if (config.url !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, QCloud.OneSentence.kUrl, config.url)
    }

    if (config.filterDirty !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_dirty', config.filterDirty)
    }
    if (config.filterModal !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_modal', config.filterModal)
    }
    if (config.filterPunc !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_punc', config.filterPunc)
    }
    if (config.convertNumMode !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'convert_num_mode', config.convertNumMode)
    }
    if (config.wordInfo !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'word_info', config.wordInfo)
    }
    if (config.hotwordID !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'hotword_id', config.hotwordID)
    }

    try {
      this._controller = builder.build()
      const result = await this._controller.task
      return `${result}`
    } catch (e) {
      throw e
    }
  }
}

export class ZLAsrFileFlashTask {
  private _controller: any | null = null

  get controller(): any | null {
    return this._controller
  }

  async recognize(config: ZLAsrFileConfig, data: ArrayBuffer): Promise<string> {
    const builder = new QCloud.FileFlash.Builder()
    builder.appID = ZLAsrHarmonyUtils.ensureString(config.auth.appID, '')
    builder.secretID = ZLAsrHarmonyUtils.ensureString(config.auth.secretID, '')
    builder.secretKey = ZLAsrHarmonyUtils.ensureString(config.auth.secretKey, '')
    builder.token = ZLAsrHarmonyUtils.ensureString(config.auth.token, '')

    // 文档示例通过 setApiParam 设置文件极速版参数 [9]
    ZLAsrHarmonyUtils.setIfValid(builder, QCloud.FileFlash.kEngineType, config.engineModelType ?? '16k_zh')
    ZLAsrHarmonyUtils.setIfValid(builder, QCloud.FileFlash.kVoiceFormat, config.voiceFormat ?? 'mp3')

    if (config.filterDirty !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_dirty', config.filterDirty)
    }
    if (config.filterModal !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_modal', config.filterModal)
    }
    if (config.filterPunc !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'filter_punc', config.filterPunc)
    }
    if (config.convertNumMode !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'convert_num_mode', config.convertNumMode)
    }
    if (config.speakerDiarization !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'speaker_diarization', config.speakerDiarization)
    }
    if (config.firstChannelOnly !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'first_channel_only', config.firstChannelOnly)
    }
    if (config.wordInfo !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'word_info', config.wordInfo)
    }
    if (config.customizationID !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'customization_id', config.customizationID)
    }
    if (config.hotwordID !== undefined) {
      ZLAsrHarmonyUtils.setIfValid(builder, 'hotword_id', config.hotwordID)
    }

    try {
      this._controller = builder.build(data)
      const result = await this._controller.task
      return `${result}`
    } catch (e) {
      throw e
    }
  }
}

export class ZLAsrHarmony {
  static async startRealtime(
    config: ZLAsrRealtimeConfig,
    source: ZLAsrPcmDataSource,
    listener?: ZLAsrRealtimeListener
  ): Promise<ZLAsrRealtimeTask> {
    const task = new ZLAsrRealtimeTask()
    // 不 await，调用方可自行持有 task 后 stop/cancel
    task.start(config, source, listener).catch((e) => {
      const err = ZLAsrHarmonyUtils.normalizeError(e)
      if (listener?.onError) {
        listener.onError(err.code, err.message)
      }
    })
    return task
  }

  static async recognizeOneSentence(config: ZLAsrSentenceConfig): Promise<string> {
    const task = new ZLAsrOneSentenceTask()
    return await task.recognize(config)
  }

  static async recognizeFileFlash(config: ZLAsrFileConfig, data: ArrayBuffer): Promise<string> {
    const task = new ZLAsrFileFlashTask()
    return await task.recognize(config, data)
  }

  static makePcmDataSource(
    startFn: () => Promise<void>,
    stopFn: () => Promise<void>,
    readFn: (ms: number) => Promise<ArrayBuffer>,
    emptyFn: () => boolean
  ): ZLAsrPcmDataSource {
    return {
      voice_format: 'pcm',
      get empty() {
        return emptyFn()
      },
      start: startFn,
      stop: stopFn,
      read: readFn,
    }
  }
}
