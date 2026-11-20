# 美術風格與提示詞

這份文件記錄牌面和介面圖的畫法、實際使用的提示詞，以及試產過程學到的事。之後要加新角色、重產某一張，照這裡做就能維持同一套風格。

提示詞的**實際來源是 [`tools/gen_art.py`](../tools/gen_art.py)**，這份文件是從它整理出來的；兩邊不一致時以程式為準。試產五輪的完整提示詞留在 [`tools/gen_samples.py`](../tools/gen_samples.py)。

## 風格是什麼

**平塗的塔羅牌，像多層剪紙或琺瑯徽章。** 版式和裝飾語彙來自新藝術（Art Nouveau），但畫法是現代的平面設計稿，不是慕夏那種手繪海報。

七個特徵，缺一個就會走樣：

1. **一張牌一個主色**，其餘是大面積的底色、中間調和淺色。人物本身偏淺，主色集中在背景色塊和局部衣飾。
2. **線條是同色系深一階的細線**（或白線），不是黑線，也不是到處金線。金色只用在少數飾邊。
3. **上方一條主色的拱形帶**，裡面是交織的緞帶繩結，嵌著 3 到 5 個小圓章，圓章裡是白色小圖示。
4. **人物修長、姿態有動感**，會壓到外框上。頭髮、毛、衣襬是大塊的平面形狀。
5. **臉不畫五官，但輪廓要有型**：四分之三側臉、下顎收到尖下巴、看得到耳朵、瀏海和髮絲蓋住額頭臉頰。不能是一顆蛋。
6. **人物背後有一個主色大圓**，周圍點綴幾個平面小圖案。
7. **外框是淺褐色雙細線加圓拱頂**，底部一條主色橫幅，兩側有小翅膀或葉片，**橫幅留白**。

完全平塗：沒有漸層、陰影、紙紋、筆觸。

## 白天與晚上

外框結構完全相同，只換底色，所以放在一起是同一副牌。

| | 底色 | 中間調 | 淺色 | 用在 |
|---|---|---|---|---|
| 白天 | 暖米白 | 淺灰褐 | 白 | 好人牌、白天背景、好人勝利 |
| 晚上 | 消光黑 | 深石板灰 | 灰白 | 狼人牌、晚上背景、狼人勝利 |

晚上的牌另外加一句：深色的形狀用「自己顏色淺一階」勾邊，不要用金線，否則黑底配金會太花。

### 各牌主色

| 好人（淺底） | 主色 | | 狼人（黑底） | 主色 |
|---|---|---|---|---|
| 預言家 | 天藍 | | 狼人 | 暗紫 |
| 女巫 | 翠綠 | | 狼兄 | 暗紫 |
| 獵人 | 森林綠 | | 狼弟 | 淡紫 |
| 守衛 | 海軍藍 | | 狼王 | 深紅 |
| 白痴 | 橘 | | 白狼王 | 深紅 |
| 騎士 | 玫瑰粉 | | 狼美人 | 深紅 |
| 黑市商人 | 琥珀 | |  |  |
| 平民 | 麥黃 | |  |  |

一般狼人用暗紫，狼王、白狼王、狼美人這類特殊狼用深紅，用顏色區分階級。好人牌都帶一點金。

## 角色牌的提示詞

每張牌的提示詞＝**共用模板**＋**主色**＋**小圖案**＋**人物描述**。

### 共用模板

`{base}`、`{neutral}`、`{light}` 填白天或晚上的三個顏色；`{motifs}` 填這張牌的小圖案；`{face}` 填下面的人臉或狼臉段落。

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of {base}, {neutral} and {light}. The figure itself is mostly rendered
in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly proportioned
character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose that overlaps
the frame, hair, fur and drapery drawn as big flowing flat shapes. {face}Behind the figure sits one large flat
disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure ({motifs}). Frame: a
thin double-line border in a muted tan, with a rounded arch at the top. Across the top runs an arched band
filled with the dominant hue, containing interlaced ribbon and knot-work lines and a row of three to five
small round medallions, each holding a simple white icon. At the bottom is a horizontal banner filled with the
dominant hue, flanked by small wing or leaf ornaments, and left completely blank. Portrait orientation, full
bleed. Absolutely no text, letters, runes, glyphs, numbers, logos or watermarks anywhere in the image.
```

### 臉的寫法

人形角色：

```text
The face has no eyes, no mouth and no drawn features, but its outline is carefully shaped like a stylish anime
character seen in three-quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a
subtle nose and brow bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair
strands overlapping the forehead and cheeks so the head never looks like a plain oval or egg.
```

狼形角色（狼頭只留兩個發光的眼睛）：

```text
The head is a clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with
tufts of fur at the cheeks; the only facial detail is two small glowing eye shapes, no other features.
```

### 晚上的牌多加一句

```text
On this dark card, outline dark shapes with a slightly lighter shade of their own colour instead of gold; keep
gold for a few trims only.
```

### 各角色完整提示詞

直接可用，貼給產圖模型就會得到那張牌（尺寸 1024×1536）。

<details><summary>預言家（seer）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (lilies,
feathers, small sunbursts, strings of beads). Frame: a thin double-line border in a muted tan, with a rounded
arch at the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon
and knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At
the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and
left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers,
logos or watermarks anywhere in the image. Dominant hue: sky blue with touches of gold. Subject: a winged
oracle with a laurel crown and long flowing hair, in layered robes and a cape, lifting a round crystal orb.
```

</details>

<details><summary>女巫（witch）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (herb sprigs,
small bottles, drifting bubbles, tiny stars). Frame: a thin double-line border in a muted tan, with a rounded
arch at the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon
and knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At
the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and
left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers,
logos or watermarks anywhere in the image. Dominant hue: jade teal with touches of gold. Subject: a witch in a
wide-brimmed pointed hat and a layered travelling dress, long braided hair, holding up one small potion bottle
while a second bottle hangs at her belt.
```

</details>

<details><summary>獵人（hunter）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (pine sprigs,
arrows, small stars, falling leaves). Frame: a thin double-line border in a muted tan, with a rounded arch at
the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon and
knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At the
bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left
completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos
or watermarks anywhere in the image. Dominant hue: forest green with touches of gold. Subject: a rugged male
hunter in a long travelling coat and wide-brimmed hat, short tousled hair, holding a long rifle upright, cloak
blowing to one side.
```

</details>

<details><summary>守衛（guard）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (small shields,
lanterns, oak leaves, chain links). Frame: a thin double-line border in a muted tan, with a rounded arch at
the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon and
knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At the
bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left
completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos
or watermarks anywhere in the image. Dominant hue: navy blue with touches of gold. Subject: a steadfast
guardian in light plate armour and a long tabard, short neat hair, bracing a large kite shield in front and
holding a spear upright, cape billowing.
```

</details>

<details><summary>白痴（idiot）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (juggling
balls, playing cards, small bells, ribbons). Frame: a thin double-line border in a muted tan, with a rounded
arch at the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon
and knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At
the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and
left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers,
logos or watermarks anywhere in the image. Dominant hue: marigold orange with touches of gold. Subject: a
cheerful fool in a two-pointed jester's cap with bells and a patchwork tunic, balancing on one foot and
tossing playing cards into the air.
```

</details>

<details><summary>騎士（knight）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (roses, crossed
swords, small banners, laurel leaves). Frame: a thin double-line border in a muted tan, with a rounded arch at
the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon and
knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At the
bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left
completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos
or watermarks anywhere in the image. Dominant hue: dusty rose with touches of gold. Subject: a noble knight in
elegant plate armour with a long cape and a plume, shoulder-length hair, raising a longsword in a duelling
salute.
```

</details>

<details><summary>黑市商人（merchant）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (coins, small
keys, vials, dangling charms). Frame: a thin double-line border in a muted tan, with a rounded arch at the
top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon and knot-
work lines and a row of three to five small round medallions, each holding a simple white icon. At the bottom
is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left
completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos
or watermarks anywhere in the image. Dominant hue: amber ochre with touches of gold. Subject: a shrewd
travelling merchant in a hooded patchwork cloak, hair hidden by the hood, holding one side of the cloak open
to show a small crystal orb, a vial and an old pistol hanging inside.
```

</details>

<details><summary>平民（villager）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of warm cream, pale grey-beige and white. The figure itself is mostly
rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender, elegantly
proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic graceful pose
that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no eyes, no
mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen in three-
quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose and brow
bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands overlapping
the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits one large
flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure (wheat stalks,
small cottages, daisies, sparrows). Frame: a thin double-line border in a muted tan, with a rounded arch at
the top. Across the top runs an arched band filled with the dominant hue, containing interlaced ribbon and
knot-work lines and a row of three to five small round medallions, each holding a simple white icon. At the
bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf ornaments, and left
completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes, glyphs, numbers, logos
or watermarks anywhere in the image. Dominant hue: wheat yellow with touches of gold. Subject: an ordinary
young villager in a simple tunic and wool cloak, short hair, holding up a candle lantern and looking back over
one shoulder.
```

</details>

<details><summary>狼人（wolf）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The head is a
clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at
the cheeks; the only facial detail is two small glowing eye shapes, no other features. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(crescent moons, bats, pine silhouettes, crystal shards). Frame: a thin double-line border in a muted tan,
with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue, containing
interlaced ribbon and knot-work lines and a row of three to five small round medallions, each holding a simple
white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf
ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes,
glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: deep violet. Subject: a lean
werewolf in a ragged long villager's coat, bushy tail, crouched forward with one clawed hand reaching out. On
this dark card, outline dark shapes with a slightly lighter shade of their own colour instead of gold; keep
gold for a few trims only.
```

</details>

<details><summary>狼兄（wolfbro）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The head is a
clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at
the cheeks; the only facial detail is two small glowing eye shapes, no other features. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(crescent moons, wolf-tooth charms, thorn sprigs, pine silhouettes). Frame: a thin double-line border in a
muted tan, with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue,
containing interlaced ribbon and knot-work lines and a row of three to five small round medallions, each
holding a simple white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by
small wing or leaf ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text,
letters, runes, glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: deep violet.
Subject: a tall, broad-shouldered werewolf elder brother in a worn long leather coat with a wolf-tooth
pendant, bushy tail, one arm held out protectively to the side. On this dark card, outline dark shapes with a
slightly lighter shade of their own colour instead of gold; keep gold for a few trims only.
```

</details>

<details><summary>狼弟（wolfyb）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The head is a
clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at
the cheeks; the only facial detail is two small glowing eye shapes, no other features. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(small crescent moons, falling leaves, tiny stars, thorn sprigs). Frame: a thin double-line border in a muted
tan, with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue,
containing interlaced ribbon and knot-work lines and a row of three to five small round medallions, each
holding a simple white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by
small wing or leaf ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text,
letters, runes, glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: muted lavender
violet. Subject: a young, slender werewolf with pale fur wrapped in an oversized hooded villager's cloak, the
hood up and one paw holding the cloak over his muzzle, timid posture. On this dark card, outline dark shapes
with a slightly lighter shade of their own colour instead of gold; keep gold for a few trims only.
```

</details>

<details><summary>狼王（wolfking）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The head is a
clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at
the cheeks; the only facial detail is two small glowing eye shapes, no other features. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(crowns, crescent moons, thorn sprigs, small flames). Frame: a thin double-line border in a muted tan, with a
rounded arch at the top. Across the top runs an arched band filled with the dominant hue, containing
interlaced ribbon and knot-work lines and a row of three to five small round medallions, each holding a simple
white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf
ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes,
glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: deep crimson. Subject: a commanding
werewolf king wearing a jagged crown and a fur-trimmed mantle over a long coat, bushy tail, aiming an old
flintlock pistol with one outstretched arm. On this dark card, outline dark shapes with a slightly lighter
shade of their own colour instead of gold; keep gold for a few trims only.
```

</details>

<details><summary>白狼王（whitewolf）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The head is a
clean, stylised wolf head with pointed ears and a defined muzzle in three-quarter view, with tufts of fur at
the cheeks; the only facial detail is two small glowing eye shapes, no other features. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(sparks, small starbursts, crescent moons, shattered crystal shards). Frame: a thin double-line border in a
muted tan, with a rounded arch at the top. Across the top runs an arched band filled with the dominant hue,
containing interlaced ribbon and knot-work lines and a row of three to five small round medallions, each
holding a simple white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by
small wing or leaf ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text,
letters, runes, glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: deep crimson.
Subject: a white-furred werewolf king with a jagged crown and a tattered cape, bushy white tail, both clawed
hands flung wide as sparks burst around him. On this dark card, outline dark shapes with a slightly lighter
shade of their own colour instead of gold; keep gold for a few trims only.
```

</details>

<details><summary>狼美人（beauty）</summary>

```text
A collectible tarot-style character card. Flat vector illustration in the look of a layered paper-cut or a
soft-enamel pin. Completely flat fills with crisp edges; no gradients, no shading, no texture, no painterly or
sketchy strokes. Outlines are thin and tone-on-tone: each shape is outlined in a slightly darker shade of its
own colour, or in white, rather than black; metallic gold appears only on a few trims and ornaments. Colour
scheme is nearly monochrome: one single dominant hue used for large background blocks and selected parts of
the costume, combined with large areas of matte black, dark slate grey and pale ash white. The figure itself
is mostly rendered in the pale neutral tones, with the dominant hue as accents. Figure: tall, slender,
elegantly proportioned character drawn as flat graphic design rather than realistic anatomy, in a dynamic
graceful pose that overlaps the frame, hair, fur and drapery drawn as big flowing flat shapes. The face has no
eyes, no mouth and no drawn features, but its outline is carefully shaped like a stylish anime character seen
in three-quarter view: a defined jawline tapering to a pointed chin, a clear cheekbone curve, a subtle nose
and brow bump on the profile edge, a visible ear, a slender neck, and layered bangs and loose hair strands
overlapping the forehead and cheeks so the head never looks like a plain oval or egg. Behind the figure sits
one large flat disc or bold shape in the dominant hue. Scatter a few small flat motifs around the figure
(roses, thorn sprigs, crescent moons, small hearts). Frame: a thin double-line border in a muted tan, with a
rounded arch at the top. Across the top runs an arched band filled with the dominant hue, containing
interlaced ribbon and knot-work lines and a row of three to five small round medallions, each holding a simple
white icon. At the bottom is a horizontal banner filled with the dominant hue, flanked by small wing or leaf
ornaments, and left completely blank. Portrait orientation, full bleed. Absolutely no text, letters, runes,
glyphs, numbers, logos or watermarks anywhere in the image. Dominant hue: deep crimson. Subject: an alluring
woman with small wolf ears and a wolf tail, long wavy hair, in an elegant layered gown, holding a single rose,
glancing over her shoulder. On this dark card, outline dark shapes with a slightly lighter shade of their own
colour instead of gold; keep gold for a few trims only.
```

</details>

### 同一個角色的另一個形態：用參考圖改畫

覺醒狼弟不是重新產的，而是把產好的狼弟牌當參考圖，走 `images/edits` 改畫，才會是同一隻狼、同一件斗篷。只寫文字描述的話會變成另一個角色。

```text
Redraw this same card as the character's awakened, enraged form. Keep exactly the same flat paper-cut
illustration style, the same black card, the same frame, top band with medallions and blank bottom banner, and
the same young slender pale-furred werewolf and cloak. Changes: the hood is thrown back, he no longer hides
his muzzle, his jaws are open in a snarl with fangs showing, fur bristling, one clawed hand raised, his two
eye shapes now glow bright crimson red, and the dominant hue shifts from lavender violet to a hotter violet
with crimson accents. The bottom banner stays completely blank. Absolutely no text, letters, runes, glyphs,
numbers, logos or watermarks anywhere in the image.
```

## 介面圖的提示詞

牌背、背景、勝利圖、app 圖示**一律附上產好的牌當參考圖**（白天的附預言家、晚上的附狼人、牌背兩張都附），走 `images/edits`。只用文字描述「同一套美術」是不夠的，第一次這樣做的結果是有陰影的剪紙風景畫，和牌面對不起來。

### 共用開頭

```text
Use the attached card image(s) only as a style reference. Match their look exactly: completely flat fills with
crisp edges, thin tone-on-tone outlines, a nearly monochrome scheme built on one dominant hue, the same
interlaced ribbon knot-work bands, the same small round medallions holding simple white icons, the same thin
double-line tan border, and a few scattered small flat motifs. No gradients, no shading, no texture, no paper-
cut depth or drop shadows. Do not copy the character from the reference. Absolutely no text, letters, runes,
glyphs, numbers, logos or watermarks anywhere in the image. Now create a new image:
```

白天配色：

```text
Palette: warm cream base, sky blue as the single dominant hue, pale grey-beige and white, with a few touches
of gold.
```

晚上配色：

```text
Palette: matte black base, deep violet as the single dominant hue, dark slate grey and pale ash white, with a
few touches of gold. Outline dark shapes in a slightly lighter shade of their own colour.
```

### 各張的內容描述

接在共用開頭後面。

<details><summary>白天背景（day，1536x1024，參考圖：預言家）</summary>

```text
a wide landscape banner, full bleed. A small medieval village of simple flat cottages and one church spire on
gentle hills, drawn as large calm flat shapes with thin tone-on-tone outlines. A big flat sun disc sits behind
the village, ringed by a thin knot-work band. An arched knot-work band with five small round medallions (sun,
laurel, lily, feather, star icons) runs across the top edge. Lilies and laurel sprigs at the lower corners,
tiny sunbursts in the sky. No people. Lots of calm empty sky. Palette: warm cream base, sky blue as the single
dominant hue, pale grey-beige and white, with a few touches of gold.
```

</details>

<details><summary>晚上背景（night，1536x1024，參考圖：狼人）</summary>

```text
a wide landscape banner, full bleed. The same small medieval village of simple flat cottages and one church
spire on gentle hills at night, drawn as large calm flat shapes clearly visible against the sky, with a few
small lit windows. A big flat deep-violet disc sits behind the village with a pale ash-white crescent moon
inside it, ringed by a thin knot-work band. An arched knot-work band with five small round medallions
(crescent moon, bat, wolf head, pine tree, star icons) runs across the top edge. Thorn sprigs and pine
silhouettes at the lower corners, tiny stars and crystal shards in the sky. No people. The hills and village
must stay readable, not swallowed by black. Palette: matte black base, deep violet as the single dominant hue,
dark slate grey and pale ash white, with a few touches of gold. Outline dark shapes in a slightly lighter
shade of their own colour.
```

</details>

<details><summary>牌背（cardback，1024x1536，參考圖：預言家、狼人）</summary>

```text
the ornamental back of this tarot deck, portrait, full bleed, perfectly symmetrical, with no character and no
banner. Keep the same thin double-line tan border and rounded arch. In the centre, one large round medallion
ringed by knot-work: its left half is a sky-blue sun with short rays, its right half is a deep-violet crescent
moon, and a white wolf paw print sits in the middle where they meet. Above and below it, mirrored arched knot-
work bands each carry three small round medallions with simple white icons (star, laurel, crescent). Fill the
rest with a calm repeating pattern of small flat diamonds and four-point stars. Palette: warm cream base,
muted antique gold-tan as the dominant hue for the bands and pattern, with sky blue and deep violet only
inside the central medallion.
```

</details>

<details><summary>好人勝利（win_good，1536x1024，參考圖：預言家）</summary>

```text
a wide celebration banner, full bleed. A row of tall, slender, faceless villagers in simple robes, drawn
exactly like the card figure (blank faces with shaped outlines, flowing flat hair and drapery), raising
lanterns and laurel wreaths in the village square. A huge flat sun disc rises behind them, ringed by a knot-
work band. An arched knot-work band with five small round medallions runs across the top edge. Lilies,
feathers and tiny sunbursts scattered around. Palette: warm cream base, sky blue as the single dominant hue,
pale grey-beige and white, with a few touches of gold.
```

</details>

<details><summary>狼人勝利（win_wolf，1536x1024，參考圖：狼人）</summary>

```text
a wide triumph banner, full bleed. Three werewolves drawn exactly like the card figure (stylised wolf heads,
only two small glowing eye shapes, flowing flat fur and tattered coats) stand on a hill howling, above a small
silent village with no lit windows. A huge flat deep-violet disc with a pale ash-white crescent moon rises
behind them, ringed by a knot-work band. An arched knot-work band with five small round medallions runs across
the top edge. Bats, thorn sprigs and crystal shards scattered around, with a few deep crimson accents.
Palette: matte black base, deep violet as the single dominant hue, dark slate grey and pale ash white, with a
few touches of gold. Outline dark shapes in a slightly lighter shade of their own colour.
```

</details>

<details><summary>app 圖示（appicon，1024x1024，參考圖：狼人）</summary>

```text
a square app icon, full bleed, no rounded corners and no outer border. One large round medallion fills the
square: a bold white wolf head in profile howling upward, inside a pale-gold crescent moon, on a flat deep-
violet disc, ringed by a single knot-work band with four tiny round medallions at the compass points. Matte
black corners. Very simple and bold so it reads at small size; thin tone-on-tone outlines, a little gold on
the ring only.
```

</details>

## 座位頭像的徽章

座位上的小頭像不是從牌面裁出來的。這個畫法的人物是淺色、沒有五官，縮成小圓後好人牌幾乎都是一團米白，認不出來。所以每個角色另外產一枚徽章：主色圓底加一個白色符號，和牌面頂部那排圓章是同一套。

產的時候附上**該角色自己的牌**當參考圖，徽章的顏色才會和牌一致。`{symbol}` 填下表的符號。

```text
Use the attached card only as a colour and style reference. Create a round emblem icon in the same style as
the small round medallions on that card: a square image filled edge to edge by one flat disc in the card's
dominant hue, with a thin lighter knot-work ring just inside the edge, and in the centre one single bold,
simple, solid white symbol: {symbol}. The symbol is large, fills most of the disc, and is extremely simple so
it stays readable at 24 pixels. Completely flat, no gradients, no shading, no texture, no small details, no
extra ornaments, no character, no face. Absolutely no text, letters, runes, glyphs, numbers, logos or
watermarks anywhere in the image.
```

| 角色 | 符號 |
|---|---|
| 預言家 | a crystal ball on a small stand with a four-point star inside |
| 女巫 | a round-bottomed potion bottle with a cork |
| 獵人 | a rifle scope crosshair |
| 守衛 | a kite shield with a plain cross |
| 白痴 | a two-pointed jester's cap with bells |
| 騎士 | an upright longsword |
| 黑市商人 | a pair of balance scales |
| 平民 | a sheaf of wheat |
| 狼人 | a wolf head facing forward |
| 狼兄 | a large wolf paw print |
| 狼弟 | a small hooded cloak hood with two pointed wolf ears poking through |
| 狼弟・覺醒 | a snarling wolf head in profile with open jaws and sharp fangs, with one small crimson eye |
| 狼王 | a jagged crown |
| 白狼王 | an eight-point starburst explosion |
| 狼美人 | a rose seen from above |

```bash
python3 tools/gen_art.py icon_角色代號
```

符號要挑輪廓單純、彼此差異大的，因為實際只顯示 28 像素左右。

## 換姿勢、修局部

不滿意某張牌的動作時，不要直接重產覆蓋，先產候選圖比較。做法在 [`tools/gen_poses.py`](../tools/gen_poses.py)，候選圖存到 `art/samples/`，不會動到現用的圖。

- **換整個姿勢**：重新寫人物描述，走一般產圖。挑姿勢的原則是輪廓要斜、有方向感，要有大片會飄的東西（披風、斗篷、尾巴），手不要壓在會飄的布料上。
- **只改一個地方**：拿現有的圖當參考圖走 `images/edits`，提示詞開頭寫「只改一處、其他完全不變」，再具體描述要改的東西。這樣人物、外框、配色幾乎不會動。守衛就是這樣一步步改出來的：先定姿勢，再改槍的長度和方向，再改盾牌的拿法，最後修燈籠的鍊子。
- **只是要左右相反**：直接把圖鏡射就好，不用花錢重產。
- 定案後把最終的描述寫回 `gen_art.py`，並在註解註明現用的圖是哪一張候選，因為照描述重產不會得到一模一樣的圖。

產完要放大檢查邊角的小東西。AI 常在背景的小裝飾上出錯，例如鍊子斷掉懸空、外框的角沒畫滿。

## 動態牌面

牌面可以做成有視差、部位會飄的動態版本。15 張都做了。

**分層**：[`tools/gen_layers.py`](../tools/gen_layers.py) 拿牌自己當參考圖，產兩張圖存到 `art/layers/`：

- `<角色>_plate.png`：拿掉人物的空牌。
- `<角色>_fig.png`：只有人物。這個模型不支援透明背景，所以是請它畫在純色底上（好人牌用洋紅、狼人牌用亮綠），再由腳本去背。

**部位飄動**：不把頭髮、袖子真的切開，而是在 [`tools/live_specs.json`](../tools/live_specs.json) 標出哪些部位會飄：

- `sway`：每個部位給根部和末端的座標、粗細、強度。根部不動，越往末端擺越大。
- `pins`：不准動的地方，通常是手、臉、手上拿的東西。飄動的部位常會圈到旁邊的手，要靠它擋掉。
- `feathers`：這張牌要不要有羽毛飄落。

`build.py` 把這些畫成一張權重圖嵌進頁面，瀏覽器用 WebGL 即時變形。標座標時，用 `python3 tools/layer_grid.py 角色代號` 把人物層疊上百分比格線，再看圖填。

去背不乾淨（細鍊子、髮絲邊緣殘留底色）時，調 `gen_layers.py` 裡 `cut()` 的參數，再跑 `python3 tools/gen_layers.py --recut 角色代號`，會用留著的原圖重新去背，不用重產。

**限制**：只能讓部位在原地彎曲擺動，做不到換姿勢、轉頭、眨眼。幅度不能大，否則被推開的地方後面沒有東西可以補。

## 怎麼加一張新牌

1. 在 `tools/gen_art.py` 的 `ROLES` 加一行，照現有的寫法給：白天或晚上（`DAY`／`NIGHT`）、人臉或狼臉、主色、四種小圖案、人物描述。
2. 主色挑一個還沒用過的。好人牌結尾加 `with touches of gold`。
3. 人物描述寫服裝、髮型、手上拿什麼、姿勢。不要寫年紀和身材。
4. 產圖、重建：

```bash
python3 tools/gen_art.py 新角色代號
```

```bash
python3 tools/build.py
```

5. 在 `tools/gen_art.py` 的 `ICONS` 加上這個角色的符號，產一枚徽章（見上一節），座位上的小頭像會用它。
6. 底部橫幅的位置不用手動量，`build.py` 會從圖上量出來，名字自動對位。

金鑰從 `OPENAI_API_KEY` 環境變數讀，不要寫進任何檔案。

## 試產學到的事

定案前試了五輪，每一輪錯在哪裡：

| 輪 | 做法 | 結果 |
|---|---|---|
| 1 | 提示詞寫「Alphonse Mucha 風格」 | 太像手繪海報，線條密、有寫實的臉 |
| 2 | 改成極簡平塗、金色細線 | 太空，幾乎只有線稿 |
| 3 | 加回色塊和平面紋樣 | 太花，而且到處金線 |
| 4 | 逐項拆解參考圖的特徵再寫 | 方向對了，但臉是一顆蛋 |
| 5 | 臉不畫五官但描述輪廓 | 定案 |

幾個具體的坑：

- **不要寫畫家的名字。** 寫了就會被拉向那位畫家的招牌畫法。改成描述看得到的特徵（線怎麼勾、顏色幾種、框長怎樣）。
- **「不畫五官」要搭配「輪廓怎麼畫」。** 只說 blank face 會得到光滑的橢圓。
- **「金色線條」會被放大。** 一提到金線就整張都是。要寫明「只用在少數飾邊」，並指定其餘線條用同色系。
- **要統一風格就附參考圖。** 文字描述不夠精確，同一段話每次畫出來的質感都不同。
- **底部橫幅一定要寫「留白」**，並在結尾重複一次不要任何文字。模型產的字是亂碼，名字由網頁疊上去。
- **內容審查會擋某些人物描述。** 遇過的是「young … priestess」加上長袍的組合。改成不提年紀、把服裝寫得端莊具體就過了。被擋時先換人物描述的用詞，不要動畫法的部分。
- **每張牌的橫幅高低會差一兩個百分點**，所以名字不能用固定位置，要逐張量。
- **不要從牌面裁頭像。** 人物是淺色又沒有五官，縮小後好人牌幾乎都是一團米白。改成每個角色一枚專屬徽章才認得出來。

## 圖檔放哪裡

| 位置 | 內容 |
|---|---|
| `art/*.png`、`art/ui/*.png`、`art/icons/*.png` | 現用的原圖（牌、介面圖、徽章）。不進版控，只在本機 |
| `art/layers/` | 動態牌面的分層圖和羽毛 |
| `art/v2_replaced/` | 換姿勢時被換掉的舊圖 |
| `art/v1/` | 第一版（手繪水粉風）的舊圖 |
| `art/v2_ui_first/` | 第二版最初那批介面圖（和牌面不一致，已換掉） |
| `art/samples/` | 五輪試產的樣張 |
| `werewolf-judge.html` 裡的 `ART` | 壓縮後嵌進頁面的版本，由 `build.py` 產生 |

原圖沒有備份在 GitHub。換電腦或要保存的話，記得另外複製 `art/` 資料夾。
