#!/usr/bin/env python3
"""新風格試產：新藝術（慕夏）＋琺瑯質感的塔羅牌。白天白金、晚上黑金，外框結構相同。
用法：python3 tools/gen_samples.py        輸出到 art/samples/（不進版控）"""
import base64, json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "samples")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "medium")

FRAME = (
    "Tarot-style character card in Art Nouveau style after Alphonse Mucha, rendered like a cloisonne enamel pin or stained glass: "
    "flat colour fields separated by thin metallic gold outlines, no gradients, no painterly shading, elegant flowing linework. "
    "Composition: a single figure, three-quarter length, centered inside an ornate arched Art Nouveau frame, a large circular halo behind the head, "
    "small round decorative medallions across the top, and an empty ornamental banner plaque at the bottom that is left completely blank. "
    "Symmetrical ornamental border, portrait orientation, full bleed. "
    "Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
)
DAY = ("Palette: ivory white, warm cream and gleaming gold, with soft sky-blue accents. "
       "Motifs: radiant sun halo, laurel branches, lilies, feathered wings; serene, divine, Greek-myth atmosphere.")
NIGHT_A = ("Palette: deep black and antique gold with jewel-like crimson accents. "
           "Motifs: eclipsed crescent-moon halo, thorny briars, roses, dense jewel-like ornament in the manner of Harry Clarke's stained glass; decadent gothic opulence.")
NIGHT_B = ("Palette: black, antique gold and deep violet. "
           "Motifs: an occult magic-circle halo ringed with moon phases, bat wings, coiling serpents, horned demonic ornament, candle flames and curling smoke; dark ritual magic, sinister and lavish.")
SEER = "Subject: a dignified adult seer, a wise oracle woman wearing a modest long-sleeved white and gold ceremonial gown with a laurel crown, holding a softly glowing crystal orb in both hands, calm expression."
WOLF = "Subject: a regal werewolf lord with a wolf's head, glowing red eyes and bared fangs, wearing an ornate high-collared coat, one clawed hand raised; menacing but aristocratic."
# 白天的預言家用原本的寫法會被內容審查擋下，所以試兩種改法：A 不提畫家名字，B 人物不指定性別
FRAME_NO_NAME = FRAME.replace("in Art Nouveau style after Alphonse Mucha", "in the ornate Art Nouveau poster style of 1890s Paris")
SEER_B = "Subject: a wise hooded seer in long layered white and gold ceremonial robes with a laurel crown, holding a softly glowing crystal orb in both hands, calm and solemn."
JOBS = {
    "day_seer": f"{FRAME_NO_NAME} {DAY} {SEER}",
    "day_seer_b": f"{FRAME} {DAY} {SEER_B}",
    "night_wolf_clarke": f"{FRAME} {NIGHT_A} {WOLF}",
    "night_wolf_occult": f"{FRAME} {NIGHT_B} {WOLF}",
}

# ── 第二輪：第一輪太像慕夏的手繪海報，線條太多。改成琺瑯徽章／燙金卡那種極簡平塗 ──
FLAT = (
    "Flat vector illustration designed like a hard-enamel pin or a foil-stamped collectible tarot card. "
    "Extremely clean and simple: large flat colour areas with crisp edges, one uniform thin metallic gold line weight, "
    "no gradients, no shading, no texture, no hatching, no painterly detail, plenty of calm empty space. "
    "Strictly limited palette of only three or four flat colours. "
    "The figure is highly stylised and geometric, built from simplified silhouette shapes, with a blank face that has no facial features. "
    "Composition: a single full-length figure centered inside a simple geometric arch frame drawn with thin lines and circles "
    "(Art Nouveau meets Art Deco), a plain flat circular disc as a halo behind the head, a row of small round medallions with simple icons across the top, "
    "and an empty plain banner plaque at the bottom that is left completely blank. Symmetrical, portrait orientation, full bleed. "
    "Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
)
F_DAY = "Palette: warm ivory and pale beige background, metallic gold lines, and one accent colour only: soft sky blue. Light, calm, divine mood. Simple sun, laurel and lily icons."
F_NIGHT_V = "Palette: matte black background, metallic gold lines, and one accent colour only: deep violet. Dark, occult, elegant mood. Simple moon-phase, bat-wing and serpent icons."
F_NIGHT_R = "Palette: matte black background, metallic gold lines, and one accent colour only: deep crimson. Dark, gothic, elegant mood. Simple crescent-moon, thorn and rose icons."
F_SEER = "Subject: a robed oracle in long simple robes with a laurel crown and a pair of simplified wings, holding a round crystal orb in both hands."
F_WOLF = "Subject: a werewolf lord with a clean wolf-head silhouette, wearing a long high-collared coat, one clawed hand raised; the only facial detail is two small glowing eye shapes."
JOBS.update({
    "v2_day_seer": f"{FLAT} {F_DAY} {F_SEER}",
    "v2_night_wolf_violet": f"{FLAT} {F_NIGHT_V} {F_WOLF}",
    "v2_night_wolf_crimson": f"{FLAT} {F_NIGHT_R} {F_WOLF}",
})

# ── 第三輪：第二輪太空。線條維持簡潔，但把色塊填滿、加一個中間調、服裝和背景加平面紋樣 ──
RICH = (
    "Flat vector illustration designed like a hard-enamel pin or a foil-stamped collectible tarot card. "
    "Clean, crisp and graphic: every area is a filled flat colour block with sharp edges, separated by one uniform thin metallic gold line; "
    "no gradients, no soft shading, no texture, no hatching, no sketchy or painterly lines. "
    "The card is richly filled, not empty: the figure's clothing, hair and accessories are divided into many distinct flat colour blocks, "
    "decorated with simple repeating flat patterns (small circles, diamonds, petals, scallops), and the background inside the frame is filled with large flat ornamental shapes. "
    "Palette of five flat colours: a base colour, a lighter and a darker tone of one accent colour, a neutral mid-tone, and metallic gold for lines and trims. "
    "The figure is stylised and geometric with a dynamic, elegant pose and flowing shapes, and a blank face with no facial features. "
    "Composition: a single full-length figure centered inside an ornamental arch frame built from thin lines, circles and stylised curling plant shapes "
    "(Art Nouveau meets Art Deco), a large flat circular disc as a halo behind the figure, a row of small round medallions with simple icons across the top, "
    "decorative corner pieces, and an ornamental banner plaque at the bottom filled with a flat colour and left completely blank. Symmetrical frame, portrait orientation, full bleed. "
    "Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
)
R_DAY = "Colours: warm ivory base, soft sky blue and deeper azure as the accent tones, pale warm grey-beige as the neutral, metallic gold. Light, divine, serene mood. Icons and ornaments: sun rays, laurel, lilies, feathers."
R_NIGHT_V = "Colours: matte black base, deep violet and lighter amethyst as the accent tones, dark slate grey as the neutral, metallic gold. Dark, occult, lavish mood. Icons and ornaments: moon phases, bat wings, serpents, candle flames."
R_NIGHT_R = "Colours: matte black base, deep crimson and brighter scarlet as the accent tones, dark charcoal grey as the neutral, metallic gold. Dark, gothic, lavish mood. Icons and ornaments: crescent moons, thorns, roses, fangs."
R_SEER = "Subject: a winged oracle in layered flowing robes and a long cape, wearing a laurel crown, lifting a round crystal orb with both hands; long hair flowing to one side."
R_WOLF = "Subject: a werewolf lord with a wolf head and bushy tail, wearing a layered high-collared long coat with patterned lining and a sash, one clawed hand raised, cape sweeping to one side; the only facial detail is two small glowing eye shapes, and the wolf's fur is a grey tone so it stands out from the black background."
JOBS.update({
    "v3_day_seer": f"{RICH} {R_DAY} {R_SEER}",
    "v3_night_wolf_violet": f"{RICH} {R_NIGHT_V} {R_WOLF}",
    "v3_night_wolf_crimson": f"{RICH} {R_NIGHT_R} {R_WOLF}",
})

# ── 第四輪：直接拆解使用者給的範例圖（只取畫法，不取角色），照它的特徵寫 ──
# 範例圖的特徵：
#  1. 每張牌只有一個主色，其餘是大面積的米白、淺灰褐、白；人物本身多半是淺色，主色集中在背景色塊與局部衣飾
#  2. 線條是「同色系的深一階」細線，不是到處都是金線；金屬色只用在少數飾邊
#  3. 上方有一條主色的拱形帶，裡面是交織的緞帶／繩結線條，嵌著 3～5 個小圓章，圓章裡是白色的小花或小圖示
#  4. 人物修長、姿態有動感，會壓到外框上；臉是一塊平塗，沒有五官；頭髮和衣襬是大塊的平面形狀
#  5. 人物背後有一個主色的大圓或大色塊；背景點綴小花、蝴蝶、珠鍊、結晶碎片這類平面小圖案
#  6. 外框是淺褐色的雙細線，圓拱頂；底部是一條主色的橫幅，兩側有小翅膀或葉片裝飾
#  7. 完全平塗，像多層剪紙或琺瑯徽章，沒有漸層、陰影、筆觸
REF = (
    "Flat vector illustration for a collectible tarot-style card, in the look of a layered paper-cut or a soft-enamel pin. "
    "Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or sketchy strokes. "
    "Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. "
    "Colour scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of the costume, "
    "combined with large areas of {base}, {neutral} and {light}. The figure itself is mostly rendered in the pale neutral tones, with the dominant hue as accents. "
    "Figure: tall, slender, elegantly proportioned character in a dynamic graceful pose that overlaps the frame, hair and drapery drawn as big flowing flat shapes, "
    "the face is a single flat blank shape with no facial features at all. "
    "Behind the figure sits one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure ({motifs}). "
    "Frame: a thin double-line border in a muted tan, with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue, "
    "containing interlaced ribbon and knot-work lines and a row of three to five small round medallions, each holding a simple white icon. "
    "At the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left completely blank. "
    "Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
)
def ref(base, neutral, light, motifs, hue, subject):
    return REF.format(base=base, neutral=neutral, light=light, motifs=motifs) + " Dominant hue: " + hue + ". " + subject
X_SEER = "Subject: a winged oracle with a laurel crown and long flowing hair, in layered robes and a cape, lifting a round crystal orb."
X_WOLF = "Subject: a werewolf lord with a wolf head and bushy tail, in a layered high-collared long coat and sweeping cape, one clawed hand raised; the only facial detail is two small glowing eye shapes."
JOBS.update({
    # 白天：照範例圖的淺底
    "v4_day_seer": ref("warm cream", "pale grey-beige", "white", "lilies, feathers, small sunbursts, strings of beads", "sky blue with touches of gold", X_SEER),
    # 晚上：同一套結構，底色換成黑
    "v4_night_wolf_dark": ref("matte black", "dark slate grey", "muted antique gold", "crescent moons, bats, thorn sprigs, crystal shards", "deep violet", X_WOLF),
    # 晚上的另一種可能：像範例圖一樣維持淺底，只靠主色表現陰暗
    "v4_night_wolf_pale": ref("warm cream", "pale grey-beige", "white", "crescent moons, bats, thorn sprigs, crystal shards", "deep crimson with black accents", X_WOLF),
})

# ── 第五輪：第四輪的臉是一顆光滑的蛋。臉仍然不畫五官，但輪廓要有型 ──
FACE_OLD = "the face is a single flat blank shape with no facial features at all. "
FACE_NEW = ("the face has no eyes, no mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-quarter view: "
            "a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow bump on the profile edge, a visible ear, a slender neck, "
            "and layered bangs and loose hair strands overlapping the forehead and cheeks so the head never looks like a plain oval or egg. ")
assert FACE_OLD in REF
REF5 = REF.replace(FACE_OLD, FACE_NEW).replace(
    "Figure: tall, slender, elegantly proportioned character", "Figure: tall, slender, elegantly proportioned character drawn as flat graphic design rather than realistic anatomy,")
def ref5(base, neutral, light, motifs, hue, subject):
    return REF5.format(base=base, neutral=neutral, light=light, motifs=motifs) + " Dominant hue: " + hue + ". " + subject
DAYP = ("warm cream", "pale grey-beige", "white")
NIGHTP = ("matte black", "dark slate grey", "pale ash white")
NIGHT_LINE = " On this dark card, outline dark shapes with a slightly lighter shade of their own colour instead of gold; keep gold for a few trims only."
JOBS.update({
    "v5_day_seer": ref5(*DAYP, "lilies, feathers, small sunbursts, strings of beads", "sky blue with touches of gold", X_SEER),
    "v5_day_hunter": ref5(*DAYP, "pine sprigs, arrows, small stars, falling leaves", "forest green with touches of gold",
                          "Subject: a rugged male hunter in a long travelling coat and wide-brimmed hat, short tousled hair, holding a long rifle upright, cloak blowing to one side."),
    "v5_night_beauty": ref5(*NIGHTP, "roses, thorn sprigs, crescent moons, small hearts", "deep crimson",
                            "Subject: an alluring woman with small wolf ears and a wolf tail, long wavy hair, in an elegant layered gown, holding a single rose, glancing over her shoulder." + NIGHT_LINE),
})

def gen(name):
    path = os.path.join(OUT, name + ".png")
    if os.path.exists(path) and "--force" not in sys.argv:
        return name, "已存在，跳過"
    body = json.dumps({"model": MODEL, "prompt": JOBS[name], "size": "1024x1536", "quality": QUALITY, "n": 1}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=body, headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=400) as r:
            d = json.load(r)["data"][0]
    except urllib.error.HTTPError as e:
        return name, "失敗 %s：%s" % (e.code, e.read().decode()[:300])
    except Exception as e:
        return name, "失敗：%s" % e
    open(path, "wb").write(base64.b64decode(d["b64_json"]))
    return name, "完成"

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    os.makedirs(OUT, exist_ok=True)
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or list(JOBS)
    with ThreadPoolExecutor(3) as ex:
        for name, msg in ex.map(gen, want):
            print("%-20s %s" % (name, msg))
