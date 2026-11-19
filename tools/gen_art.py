#!/usr/bin/env python3
"""用 OpenAI 圖像 API 產生 11 張角色卡圖（art/<role>.png）與介面用圖（art/ui/<name>.png）。
用法：OPENAI_API_KEY=... python3 tools/gen_art.py [role ...]
已存在的圖會跳過；要重畫某張就刪掉該檔或加 --force。
可用 OPENAI_IMAGE_MODEL 換模型（預設 gpt-image-2）。"""
import base64, json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "medium")

STYLE = (
    "Tarot-style character card illustration for a social deduction party game. "
    "Hand-painted gouache and ink look, flat shapes with subtle paper grain, strong silhouette, "
    "single figure shown from the waist up, centered, facing the viewer. "
    "Night scene palette: deep navy blue background with a pale gold crescent moon, {accent} as the one accent colour. "
    "Portrait orientation, full bleed, no frame, no border. "
    "Absolutely no text, letters, numbers, logos or watermarks anywhere in the image."
)
WOLF, GOD, VIL = "muted crimson red", "soft sky blue", "sage green"
ROLES = {
    "wolf":      (WOLF, "A werewolf in a ragged villager's coat, glowing eyes, half hidden in shadow among pine trees."),
    "wolfking":  (WOLF, "A large grey wolf king wearing a crude iron crown and a fur mantle, holding an old flintlock pistol."),
    "whitewolf": (WOLF, "A white-furred wolf king with a tattered crimson cape, one clawed hand raised, embers drifting around him."),
    "beauty":    (WOLF, "An elegant woman in a dark gown holding a rose, her shadow on the wall behind her is the shape of a wolf."),
    "seer":      (GOD,  "A hooded seer holding a softly glowing crystal orb, calm expression, stars reflected in the orb."),
    "witch":     (GOD,  "A village witch holding two small glass bottles, one glowing pale blue and one dark violet, herbs hanging behind her."),
    "hunter":    (GOD,  "A weathered hunter in a wide-brimmed hat and long coat, an old hunting rifle resting on his shoulder."),
    "guard":     (GOD,  "A night watchman in simple armour holding a round wooden shield and a lantern, standing protectively."),
    "idiot":     (GOD,  "A cheerful village fool in a patched jester's cap, grinning, holding a playing card face-out with a blank face."),
    "knight":    (GOD,  "A knight in plain plate armour raising a longsword in a duelling salute, moonlight on the blade."),
    "wolfbro":   (WOLF, "A tall, broad-shouldered dark-furred werewolf elder brother in a worn leather coat, a wolf-tooth pendant on his chest, one arm held out protectively."),
    "wolfyb":    (WOLF, "A young, slender werewolf with pale grey fur wearing an oversized hooded villager's cloak, half hiding his muzzle, wide innocent-looking eyes."),
    # 覺醒後的狼弟。實際用的那張是以 art/wolfyb.png 為參考圖、走 /v1/images/edits 改畫的（角色才會一致）；這裡留文字版備用。
    "wolfyb2":   (WOLF, "The same young, slender werewolf with pale grey fur in a tattered grey cloak and red scarf, now awakened and enraged: hood thrown back, jaws open in a furious snarl with fangs bared, fur bristling, eyes blazing with glowing crimson red light, one clawed hand raised."),
    "merchant":  (GOD,  "A shrewd travelling black-market merchant in a patched hooded cloak, holding one side of the coat open to reveal a small crystal orb, a poison vial and an old pistol hanging inside."),
    "villager":  (VIL,  "An ordinary villager in a wool cloak holding a lit candle lantern, looking wary, cottages behind."),
}

SCENE = ("Hand-painted gouache and ink illustration with subtle paper grain and flat shapes, "
         "matching a tarot-style character card set painted in deep navy blue with a pale gold crescent moon. "
         "Absolutely no text, letters, numbers, logos or watermarks anywhere in the image. ")
# 介面用圖：名稱 -> (尺寸, 完整提示詞)，存到 art/ui/
UI = {
    "night": ("1536x1024", SCENE + "Full bleed, no frame. Wide landscape of a small medieval village at night seen from a hill: timber cottages with a few warm lit windows, dark pine forest around, a large pale gold crescent moon, thin mist. Calm and mostly empty upper sky."),
    "day": ("1536x1024", SCENE + "Full bleed, no frame. Wide landscape of the same small medieval village at dawn seen from a hill: the sky shifts from dusky navy at the top to warm peach and gold at the horizon, the sun rising behind the hills, chimney smoke, long soft shadows, the crescent moon fading."),
    "cardback": ("1024x1536", SCENE + "The ornamental back of a tarot card, perfectly symmetrical: a central medallion with a pale gold crescent moon cradling a wolf paw print, surrounded by pine branch and star filigree in gold line work on deep navy, with a thin gold ornamental border."),
    "win_good": ("1536x1024", SCENE + "Full bleed, no frame. Villagers in the village square at dawn raising lanterns and embracing in relief and joy, warm golden sunrise behind the cottages, soft sky blue accents."),
    "win_wolf": ("1536x1024", SCENE + "Full bleed, no frame. A pack of wolves silhouetted on a hill howling at a huge pale gold crescent moon, below them a dark silent village with no lit windows, muted crimson red accents."),
    "appicon": ("1024x1024", SCENE + "A square app icon, full bleed with no rounded corners and no border: a bold simple wolf head in profile howling upward, set inside a large pale gold crescent moon on a deep navy background, strong silhouette readable at small size, centered."),
}

def gen(role):
    if role in UI:
        os.makedirs(os.path.join(OUT, "ui"), exist_ok=True)
        path = os.path.join(OUT, "ui", role + ".png")
    else:
        path = os.path.join(OUT, role + ".png")
    if os.path.exists(path) and "--force" not in sys.argv:
        return role, "已存在，跳過"
    if role in UI:
        size, prompt = UI[role]
    else:
        accent, subject = ROLES[role]
        size, prompt = "1024x1536", subject + " " + STYLE.format(accent=accent)
    body = json.dumps({"model": MODEL, "prompt": prompt, "size": size, "quality": QUALITY, "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body, headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)["data"][0]
    except urllib.error.HTTPError as e:
        return role, "失敗 %s：%s" % (e.code, e.read().decode()[:300])
    except Exception as e:
        return role, "失敗：%s" % e
    if d.get("b64_json"):
        raw = base64.b64decode(d["b64_json"])
    else:
        raw = urllib.request.urlopen(d["url"], timeout=120).read()
    with open(path, "wb") as f:
        f.write(raw)
    return role, "完成（%d KB）" % (len(raw) // 1024)

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    os.makedirs(OUT, exist_ok=True)
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ROLES) + list(UI)
    bad = [r for r in want if r not in ROLES and r not in UI]
    if bad:
        sys.exit("不認得的角色：%s（可用：%s）" % (bad, ", ".join(list(ROLES) + list(UI))))
    with ThreadPoolExecutor(4) as ex:
        for role, msg in ex.map(gen, want):
            print("%-10s %s" % (role, msg), flush=True)
