#!/usr/bin/env python3
"""用 OpenAI 產角色卡與介面圖。金鑰從 OPENAI_API_KEY 環境變數讀。

畫法（第二版）：平塗的塔羅牌，像多層剪紙或琺瑯徽章。每張牌一個主色，線條是同色系深一階的細線，
人物修長、臉不畫五官但輪廓有型。好人牌是淺底（白天），狼人牌是黑底（晚上），外框結構相同。
試產過程與各輪提示詞留在 tools/gen_samples.py。

用法：
  python3 tools/gen_art.py                 產全部還沒有的圖
  python3 tools/gen_art.py witch guard     只產指定的
  python3 tools/gen_art.py witch --force   已存在也重產
產完跑 python3 tools/build.py 把圖嵌進頁面。
"""
import base64, json, os, sys, uuid, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "medium")

NO_TEXT = "Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
LOOK = (
    "Flat vector illustration in the look of a layered paper-cut or a soft-enamel pin. "
    "Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or sketchy strokes. "
    "Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its own colour, or in white, rather than black; "
    "metallic gold appears only on a few trims and ornaments. "
)
PALETTE = (
    "Colour scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of the costume, "
    "combined with large areas of {base}, {neutral} and {light}. The figure itself is mostly rendered in the pale neutral tones, with the dominant hue as accents. "
)
FACE_HUMAN = (
    "The face has no eyes, no mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-quarter view: "
    "a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow bump on the profile edge, a visible ear, a slender neck, "
    "and layered bangs and loose hair strands overlapping the forehead and cheeks so the head never looks like a plain oval or egg. "
)
FACE_WOLF = (
    "The head is a clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at the cheeks; "
    "the only facial detail is two small glowing eye shapes, no other features. "
)
CARD = (
    "A collectible tarot-style character card. " + LOOK + PALETTE +
    "Figure: tall, slender, elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose that overlaps the frame, "
    "hair, fur and drapery drawn as big flowing flat shapes. {face}"
    "Behind the figure sits one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure ({motifs}). "
    "Frame: a thin double-line border in a muted tan, with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue, "
    "containing interlaced ribbon and knot-work lines and a row of three to five small round medallions, each holding a simple white icon. "
    "At the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left completely blank. "
    "Portrait orientation, full bleed. " + NO_TEXT
)
DAY = dict(base="warm cream", neutral="pale grey-beige", light="white")
NIGHT = dict(base="matte black", neutral="dark slate grey", light="pale ash white")
NIGHT_LINE = " On this dark card, outline dark shapes with a slightly lighter shade of their own colour instead of gold; keep gold for a few trims only."

def card(pal, face, hue, motifs, subject):
    return (CARD.format(face=face, motifs=motifs, **pal) + " Dominant hue: " + hue + ". Subject: " + subject + (NIGHT_LINE if pal is NIGHT else ""))

V, R = "deep violet", "deep crimson"   # 一般狼人暗紫，特殊狼深紅
ROLES = {
    # ── 好人：淺底，各自一個主色 ──
    "seer":     card(DAY, FACE_HUMAN, "sky blue with touches of gold", "lilies, feathers, small sunbursts, strings of beads",
                     "a winged oracle with a laurel crown and long flowing hair, in layered robes and a cape, lifting a round crystal orb."),
    "witch":    card(DAY, FACE_HUMAN, "jade teal with touches of gold", "herb sprigs, small bottles, drifting bubbles, tiny stars",
                     "a witch in a wide-brimmed pointed hat and a layered travelling dress, long braided hair, holding up one small potion bottle while a second bottle hangs at her belt."),
    "hunter":   card(DAY, FACE_HUMAN, "forest green with touches of gold", "pine sprigs, arrows, small stars, falling leaves",
                     "a rugged male hunter in a long travelling coat and wide-brimmed hat, short tousled hair, holding a long rifle upright, cloak blowing to one side."),
    "guard":    card(DAY, FACE_HUMAN, "navy blue with touches of gold", "small shields, lanterns, oak leaves, chain links",
                     "a steadfast guardian in light plate armour and a long tabard, short neat hair, bracing a large kite shield in front and holding a spear upright, cape billowing."),
    "idiot":    card(DAY, FACE_HUMAN, "marigold orange with touches of gold", "juggling balls, playing cards, small bells, ribbons",
                     "a cheerful fool in a two-pointed jester's cap with bells and a patchwork tunic, balancing on one foot and tossing playing cards into the air."),
    "knight":   card(DAY, FACE_HUMAN, "dusty rose with touches of gold", "roses, crossed swords, small banners, laurel leaves",
                     "a noble knight in elegant plate armour with a long cape and a plume, shoulder-length hair, raising a longsword in a duelling salute."),
    "merchant": card(DAY, FACE_HUMAN, "amber ochre with touches of gold", "coins, small keys, vials, dangling charms",
                     "a shrewd travelling merchant in a hooded patchwork cloak, hair hidden by the hood, holding one side of the cloak open to show a small crystal orb, a vial and an old pistol hanging inside."),
    "villager": card(DAY, FACE_HUMAN, "wheat yellow with touches of gold", "wheat stalks, small cottages, daisies, sparrows",
                     "an ordinary young villager in a simple tunic and wool cloak, short hair, holding up a candle lantern and looking back over one shoulder."),
    # ── 狼人：黑底 ──
    "wolf":      card(NIGHT, FACE_WOLF, V, "crescent moons, bats, pine silhouettes, crystal shards",
                      "a lean werewolf in a ragged long villager's coat, bushy tail, crouched forward with one clawed hand reaching out."),
    "wolfbro":   card(NIGHT, FACE_WOLF, V, "crescent moons, wolf-tooth charms, thorn sprigs, pine silhouettes",
                      "a tall, broad-shouldered werewolf elder brother in a worn long leather coat with a wolf-tooth pendant, bushy tail, one arm held out protectively to the side."),
    "wolfyb":    card(NIGHT, FACE_WOLF, "muted lavender violet", "small crescent moons, falling leaves, tiny stars, thorn sprigs",
                      "a young, slender werewolf with pale fur wrapped in an oversized hooded villager's cloak, the hood up and one paw holding the cloak over his muzzle, timid posture."),
    "wolfking":  card(NIGHT, FACE_WOLF, R, "crowns, crescent moons, thorn sprigs, small flames",
                      "a commanding werewolf king wearing a jagged crown and a fur-trimmed mantle over a long coat, bushy tail, aiming an old flintlock pistol with one outstretched arm."),
    "whitewolf": card(NIGHT, FACE_WOLF, R, "sparks, small starbursts, crescent moons, shattered crystal shards",
                      "a white-furred werewolf king with a jagged crown and a tattered cape, bushy white tail, both clawed hands flung wide as sparks burst around him."),
    "beauty":    card(NIGHT, FACE_HUMAN, R, "roses, thorn sprigs, crescent moons, small hearts",
                      "an alluring woman with small wolf ears and a wolf tail, long wavy hair, in an elegant layered gown, holding a single rose, glancing over her shoulder."),
}
# 覺醒後的狼弟：拿產好的 wolfyb.png 當參考圖改畫，角色才會是同一隻
EDITS = {
    "wolfyb2": ("wolfyb", "Redraw this same card as the character's awakened, enraged form. Keep exactly the same flat paper-cut illustration style, the same black card, "
                "the same frame, top band with medallions and blank bottom banner, and the same young slender pale-furred werewolf and cloak. "
                "Changes: the hood is thrown back, he no longer hides his muzzle, his jaws are open in a snarl with fangs showing, fur bristling, one clawed hand raised, "
                "his two eye shapes now glow bright crimson red, and the dominant hue shifts from lavender violet to a hotter violet with crimson accents. "
                "The bottom banner stays completely blank. " + NO_TEXT),
}

SCENE = (LOOK + "It belongs to the same art set as a deck of flat paper-cut tarot cards. No characters in the foreground. " + NO_TEXT + " ")
UI = {
    "day": ("1536x1024", SCENE + "Wide landscape, full bleed, no frame: a small medieval village on rolling hills in daylight, built from simple layered flat shapes. "
            "Palette: warm cream sky, sky blue and pale grey-beige hills, white clouds, a large flat pale-gold sun disc with thin rays, a few laurel and lily shapes at the edges. Calm, bright and airy, with plenty of empty sky."),
    "night": ("1536x1024", SCENE + "Wide landscape, full bleed, no frame: the same small medieval village on rolling hills at night, built from simple layered flat shapes. "
              "Palette: matte black sky, deep violet and dark slate hills, a large flat pale ash-white crescent moon, a few tiny gold stars, a handful of small lit windows, thorn and pine silhouettes at the edges. Quiet and ominous, with plenty of empty sky."),
    "cardback": ("1024x1536", SCENE + "The ornamental back of a tarot card, perfectly symmetrical, portrait, full bleed. Left half of the palette is warm cream with sky blue, right half is matte black with deep violet, "
                 "meeting in the centre. A central round medallion holds a sun and a crescent moon joined together with a wolf paw print in the middle. "
                 "Around it, interlaced ribbon knot-work, small round medallions, laurel on the light side and thorn sprigs on the dark side, thin double-line tan border with rounded corners."),
    "win_good": ("1536x1024", SCENE.replace("No characters in the foreground. ", "") + "Wide scene, full bleed, no frame: villagers drawn as small flat faceless figures in the village square raising lanterns and laurel wreaths in celebration, "
                 "a huge flat pale-gold sun disc rising behind the cottages. Palette: warm cream, sky blue, pale grey-beige, white and gold."),
    "win_wolf": ("1536x1024", SCENE.replace("No characters in the foreground. ", "") + "Wide scene, full bleed, no frame: a pack of wolves as flat silhouettes on a hill howling at a huge flat ash-white crescent moon, "
                 "below them a dark silent village with no lit windows. Palette: matte black, deep violet, deep crimson accents, dark slate grey and a little gold."),
    "appicon": ("1024x1024", SCENE + "A square app icon, full bleed, no rounded corners and no border: a bold flat wolf head in profile howling upward inside a large flat pale-gold crescent moon, "
                "on a matte black background with a deep violet disc behind it. Very simple, strong silhouette readable at small size, centered."),
}

def _post(url, data, headers):
    req = urllib.request.Request(url, data=data, headers=dict(headers, Authorization="Bearer " + os.environ["OPENAI_API_KEY"]))
    with urllib.request.urlopen(req, timeout=420) as r:
        return base64.b64decode(json.load(r)["data"][0]["b64_json"])

def _multipart(fields, files):
    b = uuid.uuid4().hex; out = []
    for k, v in fields.items():
        out += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"' % k).encode(), b"", str(v).encode()]
    for k, (fn, raw) in files.items():
        out += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"; filename="%s"' % (k, fn)).encode(), b"Content-Type: image/png", b"", raw]
    out += [("--" + b + "--").encode(), b""]
    return b"\r\n".join(out), "multipart/form-data; boundary=" + b

def path_of(name):
    return os.path.join(OUT, "ui", name + ".png") if name in UI else os.path.join(OUT, name + ".png")

def gen(name):
    path = path_of(name)
    if os.path.exists(path) and "--force" not in sys.argv:
        return name, "已存在，跳過"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if name in EDITS:
            src, prompt = EDITS[name]
            if not os.path.exists(path_of(src)):
                return name, "缺參考圖 %s.png，請先產它" % src
            body, ctype = _multipart({"model": MODEL, "prompt": prompt, "size": "1024x1536", "quality": QUALITY},
                                     {"image[]": (src + ".png", open(path_of(src), "rb").read())})
            raw = _post("https://api.openai.com/v1/images/edits", body, {"Content-Type": ctype})
        else:
            size, prompt = UI[name] if name in UI else ("1024x1536", ROLES[name])
            raw = _post("https://api.openai.com/v1/images/generations",
                        json.dumps({"model": MODEL, "prompt": prompt, "size": size, "quality": QUALITY, "n": 1}).encode(), {"Content-Type": "application/json"})
    except urllib.error.HTTPError as e:
        return name, "失敗 %s：%s" % (e.code, e.read().decode()[:300].replace("\n", " "))
    except Exception as e:
        return name, "失敗：%s" % e
    with open(path, "wb") as f:
        f.write(raw)
    return name, "完成（%d KB）" % (len(raw) // 1024)

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    ALL = list(ROLES) + list(UI) + list(EDITS)
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or ALL
    bad = [r for r in want if r not in ALL]
    if bad:
        sys.exit("不認得的名稱：%s（可用：%s）" % (bad, ", ".join(ALL)))
    first = [w for w in want if w not in EDITS]
    with ThreadPoolExecutor(4) as ex:
        for name, msg in ex.map(gen, first):
            print("%-10s %s" % (name, msg), flush=True)
    for name in [w for w in want if w in EDITS]:   # 改畫的要等參考圖產好
        print("%-10s %s" % gen(name), flush=True)
