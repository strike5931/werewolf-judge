#!/usr/bin/env python3
"""把 art/*.png 壓成小張 JPEG 嵌進 werewolf-judge.html，並重建可獨立開啟的 index.html。
沒有圖也能跑（頁面會退回純文字看牌）。用法：python3 tools/build.py"""
import base64, glob, json, os, re, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "werewolf-judge.html")
HEAD = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="狼人殺裁判">
<meta name="theme-color" content="#10162a">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src data:; connect-src https://0.peerjs.com wss://0.peerjs.com; base-uri 'none'; form-action 'none'">
<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
"""
art = {}
live = {}  # 動態牌面的設定（羽毛起點等），寫進頁面的 LIVE
try:
    specs = json.load(open(os.path.join(ROOT, "tools", "live_specs.json"), encoding="utf-8"))
except Exception:
    specs = {}

def plate_banner(png):
    """在「空牌層」上找橫幅。空牌中間大片留白，不能像 banner() 那樣找最長的平坦區（會選到留白）。
    改成把最下方切成一段段「顏色平坦且同色」的區間，取夠高（3% 以上）的區間裡最靠下的那一段：橫幅是外框之前最後一條色帶。"""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(png).convert("RGB"); W, H = im.size
    xs = list(range(int(W * .30), int(W * .42), 5)) + list(range(int(W * .58), int(W * .70), 5))
    rows = []
    for y in range(int(H * .80), int(H * .995)):
        px = [im.getpixel((x, y)) for x in xs]
        mean = [sum(c[i] for c in px) / len(px) for i in range(3)]
        rows.append((y, sum(sum(abs(c[i] - mean[i]) for c in px) / len(px) for i in range(3)), mean))
    runs = []; i = 0
    while i < len(rows):
        if rows[i][1] < 16:
            j = i
            while j + 1 < len(rows) and rows[j + 1][1] < 16 and sum(abs(rows[j + 1][2][c] - rows[i][2][c]) for c in range(3)) < 40:
                j += 1
            runs.append((i, j)); i = j + 1
        else:
            i += 1
    runs = [r for r in runs if (rows[r[1]][0] - rows[r[0]][0]) / H * 100 >= 3]
    if not runs:
        return None
    a, b = runs[-1]; t, bt = rows[a][0] / H * 100, rows[b][0] / H * 100
    r, g, bl = rows[(a + b) // 2][2]
    return round((t + bt) / 2, 1), (0.299 * r + 0.587 * g + 0.114 * bl) > 165

def sway_mask(blobs, pins=(), W=180, H=270):
    """把「哪些部位會飄」畫成一張小圖給著色器用。每個像素三個值：
    R＝擺動幅度（根部 0，越往末端越大）、G＝相位（讓波從根部往末端傳，各部位也不同步）、B＝擺動方向（和部位走向垂直）。"""
    import io, math
    from PIL import Image
    im = Image.new("RGB", (W, H)); px = im.load()
    for y in range(H):
        for x in range(W):
            best = (0.0, 0.0, 0.0); second = 0.0
            for b in blobs:
                rx, ry = b["root"][0] / 100 * W, b["root"][1] / 100 * H
                tx, ty = b["tip"][0] / 100 * W, b["tip"][1] / 100 * H
                ax, ay = tx - rx, ty - ry; L2 = ax * ax + ay * ay
                t = ((x - rx) * ax + (y - ry) * ay) / L2
                if t <= 0 or t > 1.25:
                    continue
                tc = min(t, 1.0); d = math.hypot(x - (rx + ax * tc), y - (ry + ay * tc)); r = b["r"] / 100 * W
                if d >= r:
                    continue
                e = d / r; side = 1.0 if e < 0.55 else 1 - ((e - 0.55) / 0.45) ** 2 * (3 - 2 * ((e - 0.55) / 0.45)) if e < 1 else 0
                w = b["amp"] * (tc ** 1.35) * side
                if w > best[0]:
                    ang = (math.atan2(ay, ax) + math.pi / 2) % math.pi
                    second = best[0]; best = (w, b.get("phase", 0) * 0.5 + (1 - tc) * 0.42, ang / math.pi)
                elif w > second:
                    second = w
            # 兩個部位重疊的地方，方向和相位會突然切換。用「最強減次強」當幅度，交界處剛好是 0，才不會撕裂
            w = best[0] - second
            # 不准動的地方（手、臉、手上的東西）：範圍內歸零，往外 1.7 倍半徑內漸漸放開
            for p in pins:
                ax, ay = p["from"][0] / 100 * W, p["from"][1] / 100 * H; bx, by = p["to"][0] / 100 * W, p["to"][1] / 100 * H
                vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy or 1
                t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2)); d = math.hypot(x - (ax + vx * t), y - (ay + vy * t)); r = p["r"] / 100 * W
                if d < r * 1.7:
                    k = 0.0 if d <= r else (d - r) / (r * 0.7)
                    w *= k * k * (3 - 2 * k)
            px[x, y] = (int(w * 255), int(best[1] * 255), int(best[2] * 255))
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
ban = {}   # 每張牌底部橫幅的中心高度（%）與深淺，網頁疊角色名字時用

def banner(png):
    """量出牌面底部那條留白橫幅在哪裡：回傳 (中心高度 %, 是否為淺色)。量不到回傳 None。
    每張牌是各自產的，橫幅高低會差一兩個百分點，名字要逐張對位才不會偏。"""
    try:
        from PIL import Image
    except ImportError:
        return None
    im = Image.open(png).convert("RGB"); W, H = im.size
    # 取左右兩條直帶（避開正中央的小裝飾），找顏色平坦且連續最長的一段
    xs = list(range(int(W * .27), int(W * .40), 5)) + list(range(int(W * .60), int(W * .73), 5))
    rows = []
    for y in range(int(H * .80), int(H * .99)):
        px = [im.getpixel((x, y)) for x in xs]
        mean = [sum(c[i] for c in px) / len(px) for i in range(3)]
        dev = sum(sum(abs(c[i] - mean[i]) for c in px) / len(px) for i in range(3))
        rows.append((y, dev, mean))
    best = (0, -1); i = 0
    while i < len(rows):
        if rows[i][1] < 14:
            j = i
            while j + 1 < len(rows) and rows[j + 1][1] < 14 and sum(abs(rows[j + 1][2][c] - rows[i][2][c]) for c in range(3)) < 45:
                j += 1
            if j - i > best[1] - best[0]:
                best = (i, j)
            i = j + 1
        else:
            i += 1
    t, b = rows[best[0]][0] / H * 100, rows[best[1]][0] / H * 100
    if b - t < 3.5:
        return None
    r, g, bl = rows[(best[0] + best[1]) // 2][2]
    return round((t + b) / 2, 1), (0.299 * r + 0.587 * g + 0.114 * bl) > 165
with tempfile.TemporaryDirectory() as tmp:
    for png in sorted(glob.glob(os.path.join(ROOT, "art", "*.png"))):
        role = os.path.splitext(os.path.basename(png))[0]
        jpg = os.path.join(tmp, role + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "62", "-Z", "540", png, "--out", jpg],
                       check=True, capture_output=True)
        raw = open(jpg, "rb").read()
        art[role] = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
        m = banner(png)
        if m:
            ban[role] = [m[0], 1 if m[1] else 0]
        print("%-10s %3d KB  橫幅 %s" % (role, len(raw) // 1024, m if m else "量不到，用預設位置"))
    # 動態牌面的分層圖（tools/gen_layers.py 產的）：p_<角色> 是拿掉人物的空牌，f_<角色> 是去背的人物
    for plate in sorted(glob.glob(os.path.join(ROOT, "art", "layers", "*_plate.png"))):
        role = os.path.basename(plate)[:-10]; fig = plate[:-10] + "_fig.png"
        if not os.path.exists(fig):
            continue
        try:
            from PIL import Image
            import io
        except ImportError:
            print("沒有 PIL，略過分層圖"); break
        buf = io.BytesIO(); Image.open(plate).convert("RGB").resize((540, 810), Image.LANCZOS).save(buf, "JPEG", quality=64)
        art["p_" + role] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(); kb = len(buf.getvalue()) // 1024
        im = Image.open(fig).convert("RGBA").resize((540, 810), Image.LANCZOS)
        # 人物的下襬在橫幅上緣之前淡出，才不會蓋住橫幅和上面的名字
        # 動態牌顯示的是「空牌層」，它是 AI 重畫的，橫幅位置和原牌差一點。
        # 所以名字和人物下襬的淡出，都要用空牌層量到的位置（空牌層本身不放大、不位移，名字才對得準）
        pm = plate_banner(plate)
        if pm:
            ban[role] = [pm[0], 1 if pm[1] else 0]
        top = (ban[role][0] - 3.6 if role in ban else 90.0) / 100 * 810; a = im.getchannel("A"); ap = a.load()
        for y in range(int(top - 46), 810):
            k = max(0.0, min(1.0, (top - y) / 46.0))
            for x in range(540):
                ap[x, y] = int(ap[x, y] * k)
        im.putalpha(a); buf = io.BytesIO(); im.save(buf, "WEBP", quality=78, method=6)
        art["f_" + role] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
        print("%-10s 分層：空牌 %d KB、人物 %d KB" % (role, kb, len(buf.getvalue()) // 1024))
        sp = specs.get(role)
        if sp:
            live[role] = {"feathers": 1 if sp.get("feathers") else 0}
            if sp.get("sway"):
                art["m_" + role] = sway_mask(sp["sway"], sp.get("pins", ()))
    # 動態牌面飄落用的羽毛（tools/gen_layers.py --feather 產的），裁掉留白、縮小後存成 _feather
    fp = os.path.join(ROOT, "art", "layers", "feather.png")
    if os.path.exists(fp):
        try:
            from PIL import Image
            import io
            im = Image.open(fp).convert("RGBA"); im = im.crop(im.getbbox()); im.thumbnail((132, 132), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, "WEBP", quality=82, method=6)
            art["_feather"] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
            print("feather    %d KB" % (len(buf.getvalue()) // 1024))
        except ImportError:
            pass
    # 座位上的小徽章：每個角色一枚，存成 i_<角色>
    for png in sorted(glob.glob(os.path.join(ROOT, "art", "icons", "*.png"))):
        role = os.path.splitext(os.path.basename(png))[0]
        jpg = os.path.join(tmp, "i_" + role + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "72", "-Z", "112", png, "--out", jpg], check=True, capture_output=True)
        art["i_" + role] = "data:image/jpeg;base64," + base64.b64encode(open(jpg, "rb").read()).decode()
    # 介面用圖：場景與勝利圖壓成橫幅，卡背同角色卡，主畫面圖示只給 index.html 用
    UIMAP = {"night": ("_night", "800", "55"), "day": ("_day", "800", "55"), "win_good": ("_good", "800", "58"),
             "win_wolf": ("_evil", "800", "58"), "cardback": ("_back", "540", "62")}
    for name, (key, size, q) in UIMAP.items():
        png = os.path.join(ROOT, "art", "ui", name + ".png")
        if not os.path.exists(png):
            continue
        jpg = os.path.join(tmp, name + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", q, "-Z", size, png, "--out", jpg],
                       check=True, capture_output=True)
        raw = open(jpg, "rb").read()
        art[key] = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
        print("%-10s %3d KB" % (name, len(raw) // 1024))
    icon = os.path.join(ROOT, "art", "ui", "appicon.png")
    if os.path.exists(icon):
        out = os.path.join(tmp, "icon.png")
        subprocess.run(["sips", "-Z", "180", icon, "--out", out], check=True, capture_output=True)
        b = base64.b64encode(open(out, "rb").read()).decode()
        HEAD += '<link rel="apple-touch-icon" href="data:image/png;base64,%s">\n<link rel="icon" href="data:image/png;base64,%s">\n' % (b, b)
s = open(SRC, encoding="utf-8").read()
s, n = re.subn(r"const ART=.*?;/\*ART\*/", lambda m: "const ART=" + json.dumps(art, separators=(",", ":")) + ";/*ART*/", s, count=1, flags=re.S)
assert n == 1, "找不到 ART 標記"
s, n = re.subn(r"const BAN=.*?;/\*BAN\*/", lambda m: "const BAN=" + json.dumps(ban, separators=(",", ":")) + ";/*BAN*/", s, count=1, flags=re.S)
assert n == 1, "找不到 BAN 標記"
s, n = re.subn(r"const LIVE=.*?;/\*LIVE\*/", lambda m: "const LIVE=" + json.dumps(live, separators=(",", ":")) + ";/*LIVE*/", s, count=1, flags=re.S)
assert n == 1, "找不到 LIVE 標記"
open(SRC, "w", encoding="utf-8").write(s)
body = "\n".join(l for l in s.split("\n") if "claude:viewport-fit-sides" not in l)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(HEAD + body + "\n</html>\n")
print("嵌入 %d 張圖，頁面 %d KB" % (len(art), len(s.encode()) // 1024))
