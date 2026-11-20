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
open(SRC, "w", encoding="utf-8").write(s)
body = "\n".join(l for l in s.split("\n") if "claude:viewport-fit-sides" not in l)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(HEAD + body + "\n</html>\n")
print("嵌入 %d 張圖，頁面 %d KB" % (len(art), len(s.encode()) // 1024))
