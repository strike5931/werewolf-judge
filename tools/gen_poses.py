#!/usr/bin/env python3
"""重產動作用的候選圖：同一張牌換幾種姿勢，產到 art/samples/ 給人挑，不會覆蓋現用的圖。
挑定後把該姿勢的描述寫回 tools/gen_art.py 的 ROLES（或 EDITS），再用 gen_art.py --force 正式重產。
用法：python3 tools/gen_poses.py [名稱...] [--force]"""
import base64, json, os, sys, uuid, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_art as g

OUT = os.path.join(g.ROOT, "art", "samples")
# 挑姿勢的原則：輪廓要斜、要有方向感（不要正面直立）；要有大片會飄的東西（披風、斗篷、尾巴）方便之後做動態；
# 手和手上拿的東西不要壓在會飄的布料上，否則飄動時會被一起拉歪。
GUARD = dict(pal=g.DAY, face=g.FACE_HUMAN, hue="navy blue with touches of gold", motifs="small shields, lanterns, oak leaves, chain links")
POSES = {
    # 守衛 A：護人。側身前傾、盾牌斜舉在前，另一隻手向後張開擋住身後，披風整片往後飛
    "guard_a": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour and a long tabard, short neat hair, caught mid-motion in a wide braced stance leaning forward on a strong diagonal: "
        "a large kite shield thrust out in front at an angle, the other arm flung out behind with an open hand as if shielding someone, "
        "a long cape and the tabard streaming far out behind in big sweeping shapes, head turned to look over the shield.")),
    # 守衛 B：橫槍。回頭、長槍橫擋在身前，披風大幅翻捲
    "guard_b": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour and a long tabard, short neat hair, turning sharply with the body twisted: "
        "a long spear held horizontally across the body in both hands to bar the way, a kite shield slung on the back, "
        "a long cape whipping around in a wide swirl, head turned back over the shoulder, weight on the back foot.")),
    # 守衛 C、D：使用者指定「槍要很長」，參考的是長槍斜貫整個畫面的持槍姿勢。槍比人高很多，從牌的一角斜到對角
    "guard_c": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour and a long tabard, short neat hair, in a low ready stance with the body turned side-on and one knee bent: "
        "he grips an extremely long lance in both hands, far longer than he is tall, held diagonally across his body so that it runs from the lower-left corner of the card up to the upper-right corner, "
        "both ends reaching past the frame; the lance has a long slender leaf-shaped blade with small wing-like guards at its base and a pointed butt spike. "
        "A kite shield is slung on his back, a long cape whips out behind him in a wide swirl, head turned toward the lance tip.")),
    "guard_d": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour and a long tabard, short neat hair, standing guard side-on with his weight on the back foot and the front leg lifted slightly: "
        "one hand holds an extremely long lance, far longer than he is tall, angled steeply so that it crosses the whole card from the lower-left corner to the upper-right corner with both ends reaching past the frame; "
        "the lance has a long slender leaf-shaped blade with small wing-like guards at its base and a pointed butt spike. "
        "His other arm braces a large kite shield at his side, a long cape streams out behind him in big sweeping shapes, head turned to look ahead along the lance.")),
    # 守衛 E：使用者選了 D，但要槍改成「\」方向（左上到右下）。拿 D 當參考圖改畫，人物朝向不變，只換槍的角度
    "guard_e": ("edit_s", "pose_guard_d",
        "Redraw this same card with one change: the direction of the long lance. Keep exactly the same flat illustration style, colours, frame, top band with medallions, blank bottom banner, "
        "and the same guardian facing the same way with the same armour, fur collar, cape and kite shield. "
        "Change: the extremely long lance now slants the other way, like a backslash: its blade tip points to the upper-left corner of the card and its butt end reaches the lower-right corner, "
        "crossing the whole card with both ends past the frame. Adjust his grip and arm naturally so he holds it that way; the shield stays braced at his side and the cape still streams out behind. "
        "The bottom banner stays completely blank. " + g.NO_TEXT),
    # 守衛 F、G：使用者要「槍往下拿」。槍尖朝下指向左下角，槍桿從身側往右上斜出去，身體前傾、一腳抬起，像蓄勢待發
    "guard_f": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour with a fur collar and a long tabard, short neat hair, in a poised battle-ready stance seen side-on facing left: body leaning forward, "
        "weight on one straight leg with the other knee raised as if about to spring. He holds an extremely long lance, far longer than he is tall, low at his side with the blade pointing DOWN: "
        "the long slender leaf-shaped blade aims at the lower-left corner of the card, and the shaft rises behind his hip and shoulder toward the upper-right corner, both ends reaching past the frame; "
        "small wing-like guards at the base of the blade and a pointed butt spike. His rear hand grips the shaft near his hip, his other arm carries a kite shield tucked close to his body, "
        "a long cape streams out behind him in big sweeping shapes, head lowered and turned toward where the blade points.")),
    "guard_g": ("gen", g.card(GUARD["pal"], GUARD["face"], GUARD["hue"], GUARD["motifs"],
        "a steadfast guardian in light plate armour with a fur collar and a long tabard, short neat hair, in a low poised battle-ready stance seen side-on facing left: body leaning forward with one knee raised. "
        "He grips an extremely long lance in both hands, far longer than he is tall, angled with the blade pointing DOWN and forward: "
        "the long slender leaf-shaped blade aims at the lower-left corner of the card, and the shaft rises past his shoulder toward the upper-right corner, both ends reaching past the frame; "
        "small wing-like guards at the base of the blade and a pointed butt spike. A kite shield is slung on his back, "
        "a long cape whips out behind him in a wide swirl, head lowered and turned toward where the blade points.")),
    # 守衛 H：使用者指定以 D（面向右、槍是「/」）為底，只把槍頭尾對調，變成槍尖朝下
    "guard_h": ("edit_s", "pose_guard_d",
        "Redraw this same card with one change: turn the long lance end for end so that its blade points DOWN. Keep exactly the same flat illustration style, colours, frame, top band with medallions, "
        "blank bottom banner, and the same guardian in the same pose facing the same way, with the same armour, fur collar, cape, kite shield and the same grip on the shaft. "
        "The lance keeps the same slant and the same position across the card, but reversed: the long slender leaf-shaped blade with its small wing-like guards is now at the lower-left end, "
        "aiming down toward the lower-left corner of the card, and the plain pointed butt spike is now at the upper-right end. Both ends still reach past the frame. "
        "The bottom banner stays completely blank. " + g.NO_TEXT),
    # 守衛 I、J：使用者選回 D（槍尖在右上），但盾牌角度怪——原圖的盾是正面平貼、直立浮在身側，看不出是怎麼拿的
    "guard_i": ("edit_s", "pose_guard_d",
        "Redraw this same card with one change: the kite shield. Keep exactly the same flat illustration style, colours, frame, top band with medallions, blank bottom banner, "
        "and the same guardian in the same pose facing the same way, with the same armour, fur collar, cape and the same long lance in the same position with its blade at the upper right. "
        "Change: the shield is now worn naturally on his forearm, with his arm visibly passing behind it through the straps and his hand gripping it. "
        "It is tilted, not upright: its top edge leans in toward his chest and its pointed bottom swings outward and down, at roughly a thirty degree angle, "
        "and it is drawn in a slight three-quarter view so it looks narrower and turned partly away from the viewer rather than flat-on. It overlaps his hip and thigh, held close and ready. "
        "The bottom banner stays completely blank. " + g.NO_TEXT),
    "guard_j": ("edit_s", "pose_guard_d",
        "Redraw this same card with one change: the kite shield. Keep exactly the same flat illustration style, colours, frame, top band with medallions, blank bottom banner, "
        "and the same guardian in the same pose facing the same way, with the same armour, fur collar, cape and the same long lance in the same position with its blade at the upper right. "
        "Change: the shield now rests on the ground beside his front leg, standing on its pointed bottom and leaning slightly against his leg, "
        "with his free hand resting on its top edge. It is turned at a three-quarter angle so it looks narrower rather than flat-on to the viewer, and it sits lower in the picture than before. "
        "The bottom banner stays completely blank. " + g.NO_TEXT),
    # 守衛 K：J 定案後使用者指出右邊的燈有瑕疵——鍊子彎彎曲曲、上端懸空沒接到拱帶。只修這一處
    "guard_k": ("edit_s", "pose_guard_j",
        "Redraw this same card with one small fix and nothing else changed. Keep exactly the same flat illustration style, colours, frame, top band with medallions, blank bottom banner, "
        "and the same guardian, lance, cape and the shield resting on the ground under his hand, all in exactly the same positions. "
        "Fix: the hanging lantern on the right side. Its chain is currently wavy and its top end floats loose in mid-air. Redraw it so the chain hangs perfectly straight and vertical, "
        "attached at the top to the underside of the arched top band, exactly mirroring the lantern on the left side: same straight chain, same length, same lantern design, same height. "
        "The bottom banner stays completely blank. " + g.NO_TEXT),
    # 狼弟覺醒 A：掙脫。仰頭嚎叫、雙臂向後張開，斗篷被撕開往兩側飛散
    "wolfyb2_a": ("edit", "wolfyb",
        "Redraw this same card as the character's awakening moment, in a completely new and much more dynamic pose. Keep exactly the same flat illustration style, the same black card, "
        "the same frame, top band with medallions and blank bottom banner, and the same young slender pale-furred werewolf. "
        "New pose: he throws his head back and howls at the sky with jaws wide open and fangs showing, chest pushed forward, both arms flung out and back with claws spread, "
        "his hooded cloak ripping apart and flying off behind him in several large torn pieces, tail lashing, fur bristling. Strong diagonal silhouette, not a straight standing pose. "
        "His two eye shapes glow bright crimson red, and the dominant hue shifts from lavender violet to a hotter violet with crimson accents. The bottom banner stays completely blank. " + g.NO_TEXT),
    # 狼弟覺醒 B：撲擊。壓低前衝、單爪前伸，斗篷和尾巴往後拖
    "wolfyb2_b": ("edit", "wolfyb",
        "Redraw this same card as the character's awakened, enraged form, in a completely new and much more dynamic pose. Keep exactly the same flat illustration style, the same black card, "
        "the same frame, top band with medallions and blank bottom banner, and the same young slender pale-furred werewolf. "
        "New pose: he lunges forward and low on a steep diagonal, one clawed arm reaching far out toward the viewer's side, the other arm drawn back, jaws open in a snarl with fangs showing, "
        "hood thrown back, his torn cloak and bushy tail streaming out behind him in long sweeping shapes. Not a straight standing pose. "
        "His two eye shapes glow bright crimson red, and the dominant hue shifts from lavender violet to a hotter violet with crimson accents. The bottom banner stays completely blank. " + g.NO_TEXT),
}

def run(name):
    path = os.path.join(OUT, "pose_" + name + ".png")
    if os.path.exists(path) and "--force" not in sys.argv:
        return name, "已存在，跳過"
    spec = POSES[name]
    try:
        if spec[0] == "gen":
            raw = g._post("https://api.openai.com/v1/images/generations",
                          json.dumps({"model": g.MODEL, "prompt": spec[1], "size": "1024x1536", "quality": g.QUALITY, "n": 1}).encode(), {"Content-Type": "application/json"})
        else:
            src = os.path.join(OUT, spec[1] + ".png") if spec[0] == "edit_s" else g.path_of(spec[1])   # edit_s：參考圖是另一張候選圖
            b = uuid.uuid4().hex; parts = []
            for k, v in {"model": g.MODEL, "prompt": spec[2], "size": "1024x1536", "quality": g.QUALITY}.items():
                parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="%s"' % k).encode(), b"", str(v).encode()]
            parts += [("--" + b).encode(), ('Content-Disposition: form-data; name="image[]"; filename="%s.png"' % spec[1]).encode(), b"Content-Type: image/png", b"",
                      open(src, "rb").read(), ("--" + b + "--").encode(), b""]
            raw = g._post("https://api.openai.com/v1/images/edits", b"\r\n".join(parts), {"Content-Type": "multipart/form-data; boundary=" + b})
    except urllib.error.HTTPError as e:
        return name, "失敗 %s：%s" % (e.code, e.read().decode()[:300].replace("\n", " "))
    except Exception as e:
        return name, "失敗：%s" % e
    open(path, "wb").write(raw)
    return name, "完成"

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("找不到 OPENAI_API_KEY 環境變數。")
    os.makedirs(OUT, exist_ok=True)
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or list(POSES)
    with ThreadPoolExecutor(4) as ex:
        for name, msg in ex.map(run, want):
            print("%-12s %s" % (name, msg), flush=True)
