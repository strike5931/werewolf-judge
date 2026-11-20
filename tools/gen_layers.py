#!/usr/bin/env python3
"""把一張牌拆成兩層，給動態牌面（視差＋待機動態）用。目前是原型，只試過預言家。

每張牌拿它自己當參考圖，請 OpenAI 各畫一張：
  <角色>_plate.png  拿掉人物的空牌（外框、拱帶、背景圓盤、小圖案、橫幅）
  <角色>_fig.png    只有人物，透明背景，位置和大小與原牌相同
輸出到 art/layers/（不進版控）。用法：python3 tools/gen_layers.py seer [--force]
"""
import base64, json, os, sys, uuid, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "art", "layers")
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "medium")
NO_TEXT = "Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image."
PLATE = (
    "Recreate this exact card with the character completely removed. Keep everything else identical and in the same place: the thin double-line border, "
    "the arched knot-work band with its round medallions at the top, the blank banner with its side ornaments at the bottom, the large flat disc or shape behind where the character stood, "
    "the flat background colour and the small scattered motifs. Where the character was, continue the background disc and flat colour cleanly. "
    "No character, no silhouette, no ghost outline, no leftover hands, hair, cloth or held objects. Same completely flat style, same colours, no gradients, no shading. The banner stays blank. " + NO_TEXT
)
FIG = (
    "Extract only the character from this card and redraw it identically: the same figure, same pose, same proportions, same size and same position within the image, "
    "including everything the character wears, holds or has attached (hair, wings, tail, cape, weapon, orb and so on), in the same completely flat style and colours with the same thin tone-on-tone outlines. "
    "Remove everything else: no border, no top band, no medallions, no banner, no background disc, no scattered motifs, no background colour. "
    "Place the figure on a perfectly uniform, flat, solid pure {key} background ({hex}) that fills the whole image edge to edge, with no gradient, no shadow and no texture. "
    "Do not use that {key} colour anywhere on the figure. Clean crisp edges with no halo or glow around the figure. " + NO_TEXT
)

FEATHER = (
    "Use the attached card only as a style reference for its feathers and wings. Draw one single elegant bird feather, large, filling most of the image, placed diagonally with the quill at the lower left and the tip at the upper right. "
    "A graceful slightly curved shape with a soft tapered tip, a fine central shaft, a few delicate barb lines and two or three small natural splits along the edge, with a little downy fluff near the quill. "
    "Completely flat style: warm white and pale cream fills, thin tone-on-tone outlines in pale tan, no black lines, no gradients, no shading, no texture. "
    "Place it on a perfectly uniform, flat, solid pure magenta background (#FF00FF) that fills the whole image edge to edge. Do not use magenta on the feather. No other objects. " + NO_TEXT
)

def feather():
    """產一片羽毛的圖（動態牌面飄落用），去背後存成 art/layers/feather.png"""
    path = os.path.join(OUT, "feather.png")
    if os.path.exists(path) and "--force" not in sys.argv:
        return path, "已存在，跳過"
    b = uuid.uuid4().hex; parts = []
    for k, v in {"model": MODEL, "prompt": FEATHER, "size": "1024x1024", "quality": QUALITY}.items():
        parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"' % k).encode(), b"", str(v).encode()]
    parts += [("--" + b).encode(), b'Content-Disposition: form-data; name="image[]"; filename="seer.png"', b"Content-Type: image/png", b"",
              open(os.path.join(ROOT, "art", "seer.png"), "rb").read(), ("--" + b + "--").encode(), b""]
    req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"\r\n".join(parts), headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "multipart/form-data; boundary=" + b})
    try:
        with urllib.request.urlopen(req, timeout=420) as r:
            open(path, "wb").write(base64.b64decode(json.load(r)["data"][0]["b64_json"]))
    except urllib.error.HTTPError as e:
        return path, "失敗 %s：%s" % (e.code, e.read().decode()[:300].replace("\n", " "))
    cut(path, (255, 0, 255))
    return path, "完成"

NIGHT_ROLES = {"wolf", "wolfbro", "wolfyb", "wolfyb2", "wolfking", "whitewolf", "beauty"}

def cut(path, key):
    """去背：離底色越近越透明，邊緣留一點半透明避免鋸齒，並把邊緣沾到的底色抽掉。原圖另存一份 _raw。"""
    from PIL import Image
    im = Image.open(path).convert("RGB"); im.save(path[:-4] + "_raw.png")
    px = im.load(); W, H = im.size
    out = Image.new("RGBA", (W, H)); op = out.load()
    LO, HI = 70.0, 150.0   # 色差小於 LO 全透明，大於 HI 全不透明
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            d = ((r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2) ** 0.5
            a = 0.0 if d <= LO else 1.0 if d >= HI else (d - LO) / (HI - LO)
            if 0 < a < 1:   # 半透明的邊緣像素：把混進來的底色扣掉
                r, g, b = [max(0, min(255, int((c - key[i] * (1 - a)) / a))) for i, c in enumerate((r, g, b))]
            op[x, y] = (r, g, b, int(a * 255))
    out.save(path)

def call(role, kind):
    path = os.path.join(OUT, "%s_%s.png" % (role, kind))
    if os.path.exists(path) and "--force" not in sys.argv:
        return path, "已存在，跳過"
    b = uuid.uuid4().hex; parts = []
    # 這個模型不支援透明背景，所以人物畫在純色底上，再用 cut() 把底色去掉。
    # 淺底的好人牌用洋紅當底，黑底紫紅色系的狼人牌用亮綠，避免和牌上的顏色撞
    key = ("green", "#00FF00") if role in NIGHT_ROLES else ("magenta", "#FF00FF")
    fields = {"model": MODEL, "prompt": PLATE if kind == "plate" else FIG.format(key=key[0], hex=key[1]), "size": "1024x1536", "quality": QUALITY}
    for k, v in fields.items():
        parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"' % k).encode(), b"", str(v).encode()]
    parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="image[]"; filename="%s.png"' % role).encode(), b"Content-Type: image/png", b"",
              open(os.path.join(ROOT, "art", role + ".png"), "rb").read(), ("--" + b + "--").encode(), b""]
    req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"\r\n".join(parts), headers={
        "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "multipart/form-data; boundary=" + b})
    try:
        with urllib.request.urlopen(req, timeout=420) as r:
            raw = base64.b64decode(json.load(r)["data"][0]["b64_json"])
    except urllib.error.HTTPError as e:
        return path, "失敗 %s：%s" % (e.code, e.read().decode()[:300].replace("\n", " "))
    except Exception as e:
        return path, "失敗：%s" % e
    open(path, "wb").write(raw)
    if kind == "fig":
        cut(path, (0, 255, 0) if role in NIGHT_ROLES else (255, 0, 255))
    return path, "完成（%d KB）" % (os.path.getsize(path) // 1024)

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    os.makedirs(OUT, exist_ok=True)
    if "--feather" in sys.argv:
        print("%-28s %s" % ("feather.png", feather()[1])); sys.exit()
    roles = [a for a in sys.argv[1:] if not a.startswith("--")] or sys.exit("請指定角色代號，例如 seer；或 --feather 產羽毛")
    jobs = [(r, k) for r in roles for k in ("plate", "fig")]
    with ThreadPoolExecutor(4) as ex:
        for path, msg in ex.map(lambda j: call(*j), jobs):
            print("%-28s %s" % (os.path.basename(path), msg), flush=True)
