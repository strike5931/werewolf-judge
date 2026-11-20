#!/usr/bin/env python3
"""把人物層疊上百分比格線，方便看圖在 tools/live_specs.json 填部位座標。
用法：python3 tools/layer_grid.py wolf [witch ...]   輸出到 art/preview/grid_<角色>.jpg"""
import os, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 720, 1080
for role in sys.argv[1:]:
    fig = Image.open(os.path.join(ROOT, "art", "layers", role + "_fig.png")).convert("RGBA").resize((W, H))
    bg = Image.new("RGB", (W, H), "#3c5a46"); bg.paste(fig, (0, 0), fig); d = ImageDraw.Draw(bg)
    for k in range(1, 20):
        c = (255, 0, 255) if k % 2 == 0 else (0, 255, 255)
        d.line([(W * k // 20, 0), (W * k // 20, H)], fill=c, width=1); d.line([(0, H * k // 20), (W, H * k // 20)], fill=c, width=1)
        if k % 2 == 0:
            d.text((W * k // 20 + 2, 2), str(k * 5), fill="yellow"); d.text((2, H * k // 20 + 2), str(k * 5), fill="yellow")
    out = os.path.join(ROOT, "art", "preview", "grid_%s.jpg" % role); os.makedirs(os.path.dirname(out), exist_ok=True)
    bg.save(out, quality=82); print(out)
