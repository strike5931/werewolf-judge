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

# 介面用圖：一律拿產好的牌當參考圖（走 images/edits），畫法才會和牌面是同一套：
# 單一主色＋米白或黑底、同色系細線勾邊、繩結拱帶、嵌白色小圖示的圓章。
STYLE_REF = (
    "Use the attached card image(s) only as a style reference. Match their look exactly: completely flat fills with crisp edges, thin tone-on-tone outlines, "
    "a nearly monochrome scheme built on one dominant hue, the same interlaced ribbon knot-work bands, the same small round medallions holding simple white icons, "
    "the same thin double-line tan border, and a few scattered small flat motifs. No gradients, no shading, no texture, no paper-cut depth or drop shadows. "
    "Do not copy the character from the reference. " + NO_TEXT + " Now create a new image: "
)
DAY_PAL = "Palette: warm cream base, sky blue as the single dominant hue, pale grey-beige and white, with a few touches of gold."
NIGHT_PAL = "Palette: matte black base, deep violet as the single dominant hue, dark slate grey and pale ash white, with a few touches of gold. Outline dark shapes in a slightly lighter shade of their own colour."
UI = {
    "day": ("1536x1024", ["seer"], STYLE_REF + "a wide landscape banner, full bleed. A small medieval village of simple flat cottages and one church spire on gentle hills, "
            "drawn as large calm flat shapes with thin tone-on-tone outlines. A big flat sun disc sits behind the village, ringed by a thin knot-work band. "
            "An arched knot-work band with five small round medallions (sun, laurel, lily, feather, star icons) runs across the top edge. Lilies and laurel sprigs at the lower corners, tiny sunbursts in the sky. "
            "No people. Lots of calm empty sky. " + DAY_PAL),
    "night": ("1536x1024", ["wolf"], STYLE_REF + "a wide landscape banner, full bleed. The same small medieval village of simple flat cottages and one church spire on gentle hills at night, "
              "drawn as large calm flat shapes clearly visible against the sky, with a few small lit windows. A big flat deep-violet disc sits behind the village with a pale ash-white crescent moon inside it, ringed by a thin knot-work band. "
              "An arched knot-work band with five small round medallions (crescent moon, bat, wolf head, pine tree, star icons) runs across the top edge. Thorn sprigs and pine silhouettes at the lower corners, tiny stars and crystal shards in the sky. "
              "No people. The hills and village must stay readable, not swallowed by black. " + NIGHT_PAL),
    "cardback": ("1024x1536", ["seer", "wolf"], STYLE_REF + "the ornamental back of this tarot deck, portrait, full bleed, perfectly symmetrical, with no character and no banner. "
                 "Keep the same thin double-line tan border and rounded arch. In the centre, one large round medallion ringed by knot-work: its left half is a sky-blue sun with short rays, its right half is a deep-violet crescent moon, "
                 "and a white wolf paw print sits in the middle where they meet. Above and below it, mirrored arched knot-work bands each carry three small round medallions with simple white icons (star, laurel, crescent). "
                 "Fill the rest with a calm repeating pattern of small flat diamonds and four-point stars. "
                 "Palette: warm cream base, muted antique gold-tan as the dominant hue for the bands and pattern, with sky blue and deep violet only inside the central medallion."),
    "win_good": ("1536x1024", ["seer"], STYLE_REF + "a wide celebration banner, full bleed. A row of tall, slender, faceless villagers in simple robes, drawn exactly like the card figure (blank faces with shaped outlines, flowing flat hair and drapery), "
                 "raising lanterns and laurel wreaths in the village square. A huge flat sun disc rises behind them, ringed by a knot-work band. An arched knot-work band with five small round medallions runs across the top edge. "
                 "Lilies, feathers and tiny sunbursts scattered around. " + DAY_PAL),
    "win_wolf": ("1536x1024", ["wolf"], STYLE_REF + "a wide triumph banner, full bleed. Three werewolves drawn exactly like the card figure (stylised wolf heads, only two small glowing eye shapes, flowing flat fur and tattered coats) "
                 "stand on a hill howling, above a small silent village with no lit windows. A huge flat deep-violet disc with a pale ash-white crescent moon rises behind them, ringed by a knot-work band. "
                 "An arched knot-work band with five small round medallions runs across the top edge. Bats, thorn sprigs and crystal shards scattered around, with a few deep crimson accents. " + NIGHT_PAL),
    "appicon": ("1024x1024", ["wolf"], STYLE_REF + "a square app icon, full bleed, no rounded corners and no outer border. One large round medallion fills the square: a bold white wolf head in profile howling upward, "
                "inside a pale-gold crescent moon, on a flat deep-violet disc, ringed by a single knot-work band with four tiny round medallions at the compass points. Matte black corners. "
                "Very simple and bold so it reads at small size; thin tone-on-tone outlines, a little gold on the ring only."),
}

# 座位上的小頭像：不從牌面裁頭（淺色無臉的人物縮小後認不出來），改成每個角色一枚徽章。
# 主色圓底＋一個白色符號，和牌面頂部那排圓章同一套語彙。拿該角色自己的牌當參考圖，顏色才會一致。
ICON_PROMPT = (
    "Use the attached card only as a colour and style reference. Create a round emblem icon in the same style as the small round medallions on that card: "
    "a square image filled edge to edge by one flat disc in the card's dominant hue, with a thin lighter knot-work ring just inside the edge, "
    "and in the centre one single bold, simple, solid white symbol: {symbol}. "
    "The symbol is large, fills most of the disc, and is extremely simple so it stays readable at 24 pixels. Completely flat, no gradients, no shading, no texture, "
    "no small details, no extra ornaments, no character, no face. " + NO_TEXT
)
ICONS = {
    "seer": "a crystal ball on a small stand with a four-point star inside", "witch": "a round-bottomed potion bottle with a cork",
    "hunter": "a rifle scope crosshair", "guard": "a kite shield with a plain cross", "idiot": "a two-pointed jester's cap with bells",
    "knight": "an upright longsword", "merchant": "a pair of balance scales", "villager": "a sheaf of wheat",
    "wolf": "a wolf head facing forward", "wolfbro": "a large wolf paw print", "wolfyb": "a small hooded cloak hood with two pointed wolf ears poking through",
    "wolfyb2": "a snarling wolf head in profile with open jaws and sharp fangs, with one small crimson eye", "wolfking": "a jagged crown",
    "whitewolf": "an eight-point starburst explosion", "beauty": "a rose seen from above",
}

def _post(url, data, headers):
    req = urllib.request.Request(url, data=data, headers=dict(headers, Authorization="Bearer " + os.environ["OPENAI_API_KEY"]))
    with urllib.request.urlopen(req, timeout=420) as r:
        return base64.b64decode(json.load(r)["data"][0]["b64_json"])

def path_of(name):
    if name.startswith("icon_"):
        return os.path.join(OUT, "icons", name[5:] + ".png")
    return os.path.join(OUT, "ui", name + ".png") if name in UI else os.path.join(OUT, name + ".png")

def gen(name):
    path = path_of(name)
    if os.path.exists(path) and "--force" not in sys.argv:
        return name, "已存在，跳過"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if name in EDITS or name in UI or name.startswith("icon_"):
            if name.startswith("icon_"):
                refs, size, prompt = [name[5:]], "1024x1024", ICON_PROMPT.format(symbol=ICONS[name[5:]])
            elif name in EDITS:
                src, prompt = EDITS[name]; refs, size = [src], "1024x1536"
            else:
                size, refs, prompt = UI[name]
            miss = [r for r in refs if not os.path.exists(path_of(r))]
            if miss:
                return name, "缺參考圖 %s，請先產它" % miss
            body = b""; b = uuid.uuid4().hex; parts = []
            for k, v in {"model": MODEL, "prompt": prompt, "size": size, "quality": QUALITY}.items():
                parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"' % k).encode(), b"", str(v).encode()]
            for r in refs:   # 可以附多張參考圖
                parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="image[]"; filename="%s.png"' % r).encode(), b"Content-Type: image/png", b"", open(path_of(r), "rb").read()]
            parts += [("--" + b + "--").encode(), b""]
            raw = _post("https://api.openai.com/v1/images/edits", b"\r\n".join(parts), {"Content-Type": "multipart/form-data; boundary=" + b})
        else:
            raw = _post("https://api.openai.com/v1/images/generations",
                        json.dumps({"model": MODEL, "prompt": ROLES[name], "size": "1024x1536", "quality": QUALITY, "n": 1}).encode(), {"Content-Type": "application/json"})
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
    ALL = list(ROLES) + list(UI) + list(EDITS) + ["icon_" + k for k in ICONS]
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or ALL
    bad = [r for r in want if r not in ALL]
    if bad:
        sys.exit("不認得的名稱：%s（可用：%s）" % (bad, ", ".join(ALL)))
    first = [w for w in want if w in ROLES]
    with ThreadPoolExecutor(4) as ex:
        for name, msg in ex.map(gen, first):
            print("%-10s %s" % (name, msg), flush=True)
    later = [w for w in want if w not in ROLES]   # 介面圖和改畫的都要等參考用的牌產好
    with ThreadPoolExecutor(4) as ex:
        for name, msg in ex.map(gen, later):
            print("%-10s %s" % (name, msg), flush=True)
