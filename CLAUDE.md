# 狼人殺裁判台

給裁判用的單頁工具，一個 HTML 檔，發佈在 GitHub Pages。使用者是裁判本人，不寫程式。

動手前先讀：

- [docs/HANDOFF.md](docs/HANDOFF.md)：程式怎麼組成、怎麼改、怎麼驗證、踩過的坑、還沒做的事。
- [README.md](README.md)：三種玩法的流程和這一桌的規則。規則以這裡為準，不是網路上的通用版。
- [docs/ART.md](docs/ART.md)：牌面畫法和產圖提示詞。只有動到圖才需要看。

## 一定要遵守

- 回覆用繁體中文。
- 只改 `werewolf-judge.html`。`index.html` 是建置產物，改完跑 `python3 tools/build.py`。
- `werewolf-judge.html` 有一行 1.9 MB 的圖檔資料（`const ART=`）。不要整檔讀取；用 `grep -n` 定位、用 Python 做完全相符的字串取代。做法在 HANDOFF 的「原始檔怎麼編輯」。
- 改完程式要跑無頭測試：`cd tools/e2e && node run.mjs`。新功能要加斷言。
- **使用者說「推上去」才提交和推送。** 在那之前只發佈私人預覽，並說清楚驗證了什麼、沒驗證到什麼。
- 提交用 noreply 信箱：`git -c user.email="35601322+strike5931@users.noreply.github.com" commit ...`
- OpenAI 金鑰只從 `OPENAI_API_KEY` 環境變數讀，不寫進檔案、不出現在對話。產圖會花使用者的錢，整批產之前先確認。
- 規則有疑問先問使用者。他常附群組對話截圖，截圖裡的結論就是規格。
- 不要在使用者的預覽分頁清 `localStorage`，會弄丟他正在進行的一局。

## 常用指令

```bash
python3 tools/build.py
```

```bash
cd tools/e2e && node run.mjs
```

```bash
python3 -m http.server 8765
```

## 位置

- 公開網站：https://strike5931.github.io/werewolf-judge/
- 儲存庫：https://github.com/strike5931/werewolf-judge
