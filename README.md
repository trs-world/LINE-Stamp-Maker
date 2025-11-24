# LINEスタンプ自動生成ツールの使い方

このプロジェクトでは、1枚のLINEスタンプシート画像から

- 12種類のスタンプ画像
- メイン画像 (240x240)
- タブ画像 (96x74)

を半自動で生成できます。

---

## 1. 事前準備

1. Python と `Pillow` をインストール

   ```powershell
   cd "c:\Users\PC_User\CascadeProjects\LINE-stamp"
   pip install pillow
   ```

2. 元画像を用意

   - 3×4 = 12コマのスタンプが並んだ画像を `1.png` / `2.png` / `3.png` などとして
     プロジェクト直下に置いておきます。
   - 背景はできるだけ単色（例: 緑 `#0ED728`）にしておくときれいに透過できます。

---

## 2. スタンプ画像を12種類に分割する

`split_line_stamp.py` を使って、指定した1枚の画像を
背景透過＋白フチ付きの12枚に分割します。

```powershell
cd "c:\Users\PC_User\CascadeProjects\LINE-stamp"

# 例: 2.png を処理する場合
python split_line_stamp.py 2.png
```

- `output_stamps` フォルダに、
  
  ```text
  01.png
  02.png
  ...
  12.png
  ```
  
  の12枚が生成されます。

※ 背景色やフチの調整は `split_line_stamp.py` 内の定数を変更することでカスタマイズできます。

---

## 3. メイン画像・タブ画像を選ぶ

12枚のスタンプ画像の中から、メイン画像とタブ画像に使いたいものを選びます。

1. プロジェクト直下に `main-tab` フォルダを作成（既にある場合はそのまま）

2. 選んだスタンプ画像をコピーして配置

   - メイン画像にしたいもの → `main-tab/01.png`
   - タブ画像にしたいもの → `main-tab/02.png`

   例:

   ```text
   LINE-stamp/
     output_stamps/
       01.png
       02.png
       ...
       12.png
     main-tab/
       01.png  # メイン用に選んだ画像
       02.png  # タブ用に選んだ画像
   ```

---

## 4. メイン画像 (240x240) とタブ画像 (96x74) を生成

`make_main_tab.py` を実行すると、

- `main-tab/01.png` から `main.png` (240x240)
- `main-tab/02.png` から `tab.png` (96x74)

が自動生成されます。

```powershell
cd "c:\Users\PC_User\CascadeProjects\LINE-stamp"
python make_main_tab.py
```

- 実行後の `main-tab` フォルダ:

  ```text
  main-tab/
    01.png      # 元のメイン候補
    02.png      # 元のタブ候補
    main.png    # 出力された240x240メイン画像
    tab.png     # 出力された96x74タブ画像
  ```

※ 背景はデフォルトで透過になっています。白背景にしたい場合は、
  `make_main_tab.py` 内の `background = parse_background("")` を
  `background = parse_background("#FFFFFF")` に変更してください。

---

## 5. ZIPファイルにまとめる

LINEスタンプ登録用に、

- 12種類のスタンプ画像 (`output_stamps/01.png`〜`12.png`)
- メイン画像 (`main-tab/main.png`)
- タブ画像 (`main-tab/tab.png`)

を1つのZIPにまとめます。

例として、`dist` フォルダにZIPを作る場合:

1. 必要なファイルを一時フォルダにコピー

   ```powershell
   cd "c:\Users\PC_User\CascadeProjects\LINE-stamp"

   mkdir dist  -Force
   mkdir dist\stamp -Force

   # 12種類のスタンプ画像
   copy .\output_stamps\*.png .\dist\stamp\

   # メイン画像とタブ画像
   copy .\main-tab\main.png .\dist\stamp\
   copy .\main-tab\tab.png  .\dist\stamp\
   ```

2. ZIPに圧縮（PowerShellの場合）

   ```powershell
   Compress-Archive -Path .\dist\stamp\* -DestinationPath .\dist\line-stamp.zip -Force
   ```

- 最終的に `dist/line-stamp.zip` が作成されます。
- このZIPをLINEスタンプ登録時の素材として利用できます。

---

## 補足: 背景を単色に揃えたい場合

背景が白で透過が難しい場合は、`recolor_background.py` を使って
背景だけを一旦緑などの単色に変えてから `split_line_stamp.py` をかけることもできます。

```powershell
# 例: 3.png の外周の白背景だけを緑(#0ED728)に変える
python recolor_background.py 3.png 3-g.png

# その後、3-g.png を分割
python split_line_stamp.py 3-g.png
```

これにより、キャラ内部の白は保ったまま、背景だけを透過処理しやすい色に揃えられます。
