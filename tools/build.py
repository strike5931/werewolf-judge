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
<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>
"""
art = {}
with tempfile.TemporaryDirectory() as tmp:
    for png in sorted(glob.glob(os.path.join(ROOT, "art", "*.png"))):
        role = os.path.splitext(os.path.basename(png))[0]
        jpg = os.path.join(tmp, role + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "62", "-Z", "540", png, "--out", jpg],
                       check=True, capture_output=True)
        raw = open(jpg, "rb").read()
        art[role] = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
        print("%-10s %3d KB" % (role, len(raw) // 1024))
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
open(SRC, "w", encoding="utf-8").write(s)
body = "\n".join(l for l in s.split("\n") if "claude:viewport-fit-sides" not in l)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(HEAD + body + "\n</html>\n")
print("嵌入 %d 張圖，頁面 %d KB" % (len(art), len(s.encode()) // 1024))
