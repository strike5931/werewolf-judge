#!/usr/bin/env python3
"""用 OpenAI 的語音模型產裁判念稿的音檔。目前是試聽階段：同一段台詞用幾種聲音和語氣各產一份。
金鑰從 OPENAI_API_KEY 環境變數讀。輸出到 art/samples/tts/（不進版控）。用法：python3 tools/gen_voice.py [--force]"""
import json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "samples", "tts")
MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
TEXT = "天黑請閉眼。……狼人請睜眼。請確認彼此的身分，並商量今晚要擊殺的目標。請給出你們今晚的刀口。……狼人請閉眼。"
TW = "請用台灣人說國語的口音與咬字（不要捲舌、不要兒化音），以繁體中文的讀音念。"
STYLES = {
    "神秘": TW + "語氣：低沉、緩慢、神秘，像深夜裡說故事的人，帶一點壓迫感。句子之間停頓久一點，「請閉眼」「請睜眼」要念得清楚而堅定。",
    "沉穩": TW + "語氣：沉穩、清楚、不帶情緒的主持人，速度偏慢，每一句之間有明顯停頓，讓人聽得很清楚。",
    "溫柔": TW + "語氣：溫柔、輕聲、像在哄人入睡，但帶著一絲詭異感。速度慢，句尾輕輕收。",
}
# 女聲：coral、nova、shimmer、sage
# 第二輪：使用者選了 shimmer，但要更清亮、口音要修。口音用四種寫法各試一次；另外用舊模型 tts-1-hd 當對照（它不吃語氣指令，口音可能不同）
STYLES.update({
    "清亮A": "請用台灣台北人平常說國語的口音：聲調平穩柔和，ㄓㄔㄕ不捲舌、沒有兒化音，句尾不要上揚或拖長的北京腔。音色清亮、明亮、乾淨，音高偏高一點，咬字清楚。語氣是冷靜而神秘的遊戲主持人，速度偏慢，句子之間停頓明顯。",
    "清亮B": "Voice: bright, clear, crisp young woman, slightly higher pitch, clean articulation. Accent: Taiwanese Mandarin as spoken in Taipei — soft, even tones, no retroflex curling on zh/ch/sh, no erhua, no Beijing-style intonation. Delivery: calm, composed game host with a hint of mystery, unhurried, with clear pauses between sentences.",
    "清亮C": "你是台灣的電視節目女主持人，講的是台灣腔的國語（不是大陸普通話）。聲音清亮、有精神、字正腔圓但不捲舌。語氣沉著，帶一點懸疑感，每一句說完停一下。",
    "清亮D": "Speak in Taiwanese Mandarin (Taiwan accent, 台灣國語腔調), like a Taiwanese audiobook narrator. Bright and clear tone, gentle, measured pace, distinct pauses between sentences. Do not use a mainland China accent.",
})
# 第三輪：使用者要偏少女的聲音
GIRL = "Voice: a girl in her late teens — youthful, light, sweet and bright, higher pitch, a little airy, never deep or mature. Accent: Taiwanese Mandarin as spoken in Taipei — soft even tones, no retroflex curling on zh/ch/sh, no erhua, no Beijing-style intonation. "
STYLES.update({
    "少女神秘": GIRL + "Delivery: a playful but eerie game host who secretly knows everyone's role; calm, a little teasing, unhurried, with clear pauses between sentences.",
    "少女清冷": GIRL + "Delivery: cool, quiet and composed, almost emotionless, like a mysterious girl reading out a ritual; slow, with clear pauses between sentences.",
    "少女活潑": GIRL + "Delivery: cheerful and lively, like a cute game mascot announcing each step, clear and energetic but not rushed, with a short pause between sentences.",
})
JOBS3 = [("shimmer", "少女神秘"), ("nova", "少女神秘"), ("coral", "少女神秘"), ("sage", "少女神秘"), ("shimmer", "少女清冷"), ("nova", "少女活潑")]
# 第四輪：照網路上查到的做法調。三個重點：
#  1. 指令照「Voice Affect / Tone / Pacing / Emotion / Pronunciation」分行寫，每行短、不互相矛盾（官方示範網站 openai.fm 的格式）
#  2. 舊版模型 gpt-4o-mini-tts-2025-03-20 比較聽指令（社群回報新版常常不照做）
#  3. 還有 marin 這個比較新的女聲沒試過
OLD = "gpt-4o-mini-tts-2025-03-20"
STYLES.update({
    "結構少女": "Voice Affect: Youthful, light and sweet; a bright, clear teenage girl's voice.\nTone: Playful but a little eerie, like a girl who secretly knows everyone's role.\nPacing: Unhurried; a clear pause after each sentence.\nEmotion: Calm, quietly amused.\nPronunciation: Taiwanese Mandarin (Taipei); soft even tones, no retroflex zh/ch/sh, no erhua.\nPitch: Higher than normal, bright, never deep or husky.",
    "結構簡短": "Voice: bright, high, sweet young girl.\nAccent: Taiwanese Mandarin.\nPacing: slow, pause between sentences.",
    "結構中文": "聲音：清亮、偏高、甜美的少女聲。\n語氣：俏皮裡帶一點神秘。\n速度：慢，每句之間停頓。\n口音：台灣國語，不捲舌、沒有兒化音。",
})
JOBS4 = [("shimmer", "結構少女", OLD), ("nova", "結構少女", OLD), ("marin", "結構少女", None), ("marin", "結構少女", OLD),
         ("shimmer", "結構簡短", OLD), ("shimmer", "結構中文", OLD), ("coral", "結構少女", OLD)]
# 使用者聽完第四輪，選定：marin＋「結構少女」＋舊版模型（marin_結構少女_舊版.mp3）。這是目前的定案組合。
# 第五輪：使用者另外想要「成熟御姐」那一型的聲線（舉的例子是某遊戲角色的中文配音）。
# 這裡只描述那一型聲線的特質（低、慵懶、從容、帶笑意），不複製任何真人配音員的聲音。
STYLES.update({
    "御姐A": "Voice Affect: Mature, low, velvety woman's voice; smooth and elegant, completely at ease.\nTone: Languid, confident and quietly teasing, as if she already knows how the night will end.\nPacing: Slow and unhurried; lingers slightly at the end of each sentence; a clear pause after each sentence.\nEmotion: Calm amusement, a soft smile in the voice, never excited.\nPronunciation: Taiwanese Mandarin (Taipei); soft even tones, no retroflex zh/ch/sh, no erhua.\nPitch: Low and warm, a little breathy, never bright or girlish.",
    "御姐B": "Voice Affect: Low, husky, alluring mature woman; refined and dangerous.\nTone: Soft-spoken and intimate, almost a whisper, like sharing a secret.\nPacing: Very slow, deliberate; long pauses between sentences.\nEmotion: Amused, composed, slightly ominous.\nPronunciation: Taiwanese Mandarin (Taipei); soft even tones, no retroflex zh/ch/sh, no erhua.",
    "御姐中文": "聲音：成熟、低沉、柔滑的女聲，優雅從容。\n語氣：慵懶、自信，帶一點戲謔的笑意，像早就知道今晚的結局。\n速度：慢，句尾微微拖長，每句之間停頓。\n口音：台灣國語，不捲舌、沒有兒化音。\n音高：偏低、溫暖，帶一點氣音。",
})
JOBS5 = [("marin", "御姐A", OLD), ("sage", "御姐A", OLD), ("coral", "御姐A", OLD), ("shimmer", "御姐A", OLD), ("marin", "御姐B", OLD), ("sage", "御姐B", OLD), ("marin", "御姐中文", OLD)]
JOBS2 = [("shimmer", "清亮A"), ("shimmer", "清亮B"), ("shimmer", "清亮C"), ("shimmer", "清亮D"), ("coral", "清亮B"), ("nova", "清亮B")]
JOBS = [("coral", "神秘"), ("nova", "神秘"), ("shimmer", "神秘"), ("sage", "神秘"), ("coral", "沉穩"), ("shimmer", "溫柔")]

def gen(job):
    voice, style = job[0], job[1]; model = (job[2] if len(job) > 2 else None) or MODEL
    path = os.path.join(OUT, "%s_%s%s.mp3" % (voice, style, "_舊版" if model != MODEL else ""))
    if os.path.exists(path) and "--force" not in sys.argv:
        return path, "已存在，跳過"
    if style == "舊模型":   # tts-1-hd 不支援 instructions
        body = json.dumps({"model": "tts-1-hd", "voice": voice, "input": TEXT, "response_format": "mp3"}).encode()
    else:
        body = json.dumps({"model": model, "voice": voice, "input": TEXT, "instructions": STYLES[style], "response_format": "mp3"}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=body, headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        return path, "失敗 %s：%s" % (e.code, e.read().decode()[:300].replace("\n", " "))
    except Exception as e:
        return path, "失敗：%s" % e
    open(path, "wb").write(raw)
    return path, "完成（%d KB）" % (len(raw) // 1024)

# ───────── 正式產出：整套台詞 × 兩種聲線 ─────────
# 定案：都用 marin＋舊版模型。girl＝「結構少女」，lady＝「御姐A」。輸出到 audio/<聲線>/<雜湊>.mp3（進版控，GitHub Pages 直接提供）。
# 檔名是「念出來的字」的雜湊，網頁端用同一個算法從畫面上的台詞算出檔名，所以台詞改了字就要重產那一句。
VOICES = {"girl": ("marin", "結構少女"), "lady": ("marin", "御姐A")}
LINES = [
    "天黑請閉眼。", "守衛請睜眼。你今晚要守護誰？", "守衛請閉眼。",
    "狼人請睜眼。請確認彼此的身分，並商量今晚要擊殺的目標。請給出你們今晚的刀口。", "狼人請睜眼。請給出你們今晚的刀口。",
    "狼弟請給出你的額外刀口。", "狼人請閉眼。", "狼美人請睜眼。你今晚要魅惑誰？", "狼美人請閉眼。",
    "女巫請睜眼。", "女巫請睜眼。今晚他倒牌了，你要用解藥嗎？你要用毒藥嗎？", "女巫請睜眼。今晚他倒牌了，你要用解藥嗎？",
    "你有一瓶毒藥，要用嗎？要毒誰？", "女巫請閉眼。", "預言家請睜眼。你今晚要查驗誰？", "他的身份是——", "預言家請閉眼。",
    "獵人請睜眼。你今晚的開槍狀態是——", "獵人請閉眼。", "狼兄、狼弟請睜眼，互相確認身份。", "狼兄、狼弟請閉眼。",
    "黑市商人請睜眼。今晚你是否要發動技能進行交易？要交易的話，請比出玩家號碼，再比出要給他的技能：1 是毒藥、2 是獵槍、3 是查驗。",
    "好的，我已確認。黑市商人請閉眼。", "天亮了……等一下，請所有人保持閉眼狀態！",
    "獲得黑市商人交易的玩家請睜眼。你獲得了來自黑市商人的技能，這項技能是——。請確認，請閉眼。",
    "獲得黑市商人技能的玩家請睜眼。今晚是否要使用你的技能？請比出目標號碼。", "請閉眼。",
    "白痴請睜眼……請閉眼。", "騎士請睜眼……請閉眼。", "白痴請睜眼……請閉眼。騎士請睜眼……請閉眼。",
    "天亮了，請睜眼。現在開始警長競選，想上警的玩家請舉手。", "昨夜是平安夜。", "請警長選擇移交警徽，或撕毀警徽。",
] + ["昨夜，%d號玩家死亡。" % n for n in range(1, 21)]

def vhash(t):
    """和網頁端 vhash() 相同的 FNV-1a（32 位元、逐字元），回傳 8 碼十六進位"""
    h = 2166136261
    for ch in t:
        h ^= ord(ch); h = (h * 16777619) & 0xFFFFFFFF
    return "%08x" % h

def build_one(job):
    vk, text = job; voice, style = VOICES[vk]
    d = os.path.join(ROOT, "audio", vk); os.makedirs(d, exist_ok=True); path = os.path.join(d, vhash(text) + ".mp3")
    if os.path.exists(path) and "--force" not in sys.argv:
        return vk, text, "已存在"
    # 破折號和刪節號給模型念會怪，換成停頓
    spoken = text.replace("——。", "……").replace("——", "……")
    body = json.dumps({"model": OLD, "voice": voice, "input": spoken, "instructions": STYLES[style], "response_format": "mp3"}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=body, headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                open(path, "wb").write(r.read())
            return vk, text, "完成"
        except urllib.error.HTTPError as e:
            msg = "失敗 %s：%s" % (e.code, e.read().decode()[:200].replace("\n", " "))
            if e.code not in (429, 500, 502, 503):
                break
        except Exception as e:
            msg = "失敗：%s" % e
    return vk, text, msg

if __name__ == "__main__":
    if "--build" in sys.argv:
        if not os.environ.get("OPENAI_API_KEY"):
            sys.exit("找不到 OPENAI_API_KEY 環境變數。")
        jobs = [(vk, t) for vk in VOICES for t in LINES]; bad = 0
        with ThreadPoolExecutor(4) as ex:
            for vk, text, msg in ex.map(build_one, jobs):
                if msg != "完成" and msg != "已存在":
                    bad += 1; print(vk, text[:16], msg, flush=True)
        print("共 %d 句 × %d 種聲線，失敗 %d" % (len(LINES), len(VOICES), bad)); sys.exit()

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(3) as ex:
        for path, msg in ex.map(gen, JOBS5 if "--round5" in sys.argv else JOBS4 if "--round4" in sys.argv else JOBS3 if "--round3" in sys.argv else (JOBS2 + [("shimmer", "舊模型")]) if "--round2" in sys.argv else JOBS):
            print("%-22s %s" % (os.path.basename(path), msg), flush=True)
