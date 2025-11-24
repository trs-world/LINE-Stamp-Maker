from PIL import Image
import os
import sys

# デフォルトの入力ファイル名（引数未指定時に使用）
DEFAULT_INPUT_FILE = "1.png"
# 出力フォルダ
OUTPUT_DIR = "output_stamps"

# グリッドの行・列（3×4）
ROWS = 3
COLS = 4

# 背景とみなす色（ユーザー指定の #0ED728）
BACKGROUND_COLOR = (0x0E, 0xD7, 0x28)

# 多少の色ブレを許容する閾値（数値を大きくすると背景として判定される範囲が広がる）
# 緑の輪郭を強めに消したいので、かなり広めに設定
COLOR_TOLERANCE = 35  # 完全に背景として消すしきい値
FADE_TOLERANCE = 45   # この距離までは徐々にアルファを下げる


def is_grayish(r: int, g: int, b: int, max_diff: int = 15) -> bool:
    return abs(r - g) <= max_diff and abs(g - b) <= max_diff and abs(r - b) <= max_diff


def color_distance(pixel: tuple, base_color: tuple) -> int:
    r, g, b, a = pixel
    br, bg, bb = base_color
    return max(abs(r - br), abs(g - bg), abs(b - bb))


def estimate_background_color(img: Image.Image) -> tuple:
    # 現在はユーザー指定の背景色を優先的に使い、
    # 推定はフォールバック用途として保持する
    img = img.convert("RGBA")
    w, h = img.size
    edge_pixels = []

    for x in range(w):
        edge_pixels.append(img.getpixel((x, 0)))
        edge_pixels.append(img.getpixel((x, h - 1)))
    for y in range(h):
        edge_pixels.append(img.getpixel((0, y)))
        edge_pixels.append(img.getpixel((w - 1, y)))

    rs: list[int] = []
    gs: list[int] = []
    bs: list[int] = []
    for r, g, b, a in edge_pixels:
        if a > 0:
            rs.append(r)
            gs.append(g)
            bs.append(b)

    if rs and gs and bs:
        est = (sum(rs) // len(rs), sum(gs) // len(gs), sum(bs) // len(bs))
        # 推定値と指定背景色が大きく違わなければ指定色を優先
        if color_distance((est[0], est[1], est[2], 255), BACKGROUND_COLOR) <= 25:
            return BACKGROUND_COLOR
        return est
    return BACKGROUND_COLOR


def make_background_transparent(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    base_color = estimate_background_color(img)
    datas = list(img.getdata())

    # 1stパス: 色ベースで背景・強い緑を透明/半透明にする
    new_data = []
    for pixel in datas:
        dist = color_distance(pixel, base_color)
        r, g, b, a = pixel

        # 強い緑輪郭の専用判定（少し緩めて、薄い緑も拾う）
        strong_green = (
            g > 80
            and g - max(r, b) > 25
        )

        if strong_green:
            new_data.append((r, g, b, 0))
        elif dist <= COLOR_TOLERANCE:
            new_data.append((r, g, b, 0))
        elif dist <= FADE_TOLERANCE:
            ratio = (dist - COLOR_TOLERANCE) / (FADE_TOLERANCE - COLOR_TOLERANCE)
            new_alpha = int(a * ratio)
            new_data.append((r, g, b, new_alpha))
        else:
            new_data.append(pixel)

    img.putdata(new_data)

    # 2ndパス: 透明ピクセルに隣接する、背景色にかなり近いピクセルを追加で削る（1pxエッジ除去）
    w, h = img.size
    px = img.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue

            # 近傍に透明ピクセルがあるかチェック
            has_transparent_neighbor = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        nr, ng, nb, na = px[nx, ny]
                        if na == 0:
                            has_transparent_neighbor = True
                            break
                if has_transparent_neighbor:
                    break

            if not has_transparent_neighbor:
                continue

            # 背景色にそこそこ近いエッジはすべて削る（かなり強め）
            dist_bg = max(
                abs(r - BACKGROUND_COLOR[0]),
                abs(g - BACKGROUND_COLOR[1]),
                abs(b - BACKGROUND_COLOR[2]),
            )
            if dist_bg <= 90:
                px[x, y] = (r, g, b, 0)

    return img


def add_white_outline(img: Image.Image, thickness: int = 2) -> Image.Image:
    """透過済み画像の非透過領域の周囲に白い縁取りを追加する"""
    img = img.convert("RGBA")
    w, h = img.size

    for _ in range(thickness):
        src = img.copy()
        src_px = src.load()
        dst_px = img.load()

        for y in range(h):
            for x in range(w):
                r, g, b, a = dst_px[x, y]
                if a != 0:
                    continue

                has_opaque_neighbor = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            nr, ng, nb, na = src_px[nx, ny]
                            if na > 0:
                                has_opaque_neighbor = True
                                break
                    if has_opaque_neighbor:
                        break

                if has_opaque_neighbor:
                    dst_px[x, y] = (255, 255, 255, 255)

    return img


def check_even_output(start_index: int, count: int = ROWS * COLS) -> None:
    all_even = True
    for idx in range(start_index, start_index + count):
        filename = f"{idx:02d}.png"
        path = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(path):
            print(f"[SIZE CHECK] Missing file: {path}")
            all_even = False
            continue

        try:
            with Image.open(path) as im:
                w, h = im.size
                if (w % 2 != 0) or (h % 2 != 0):
                    print(f"[SIZE CHECK] NG: {path} -> {w}x{h} (odd size)")
                    all_even = False
                else:
                    print(f"[SIZE CHECK] OK: {path} -> {w}x{h}")
        except Exception as e:
            print(f"[SIZE CHECK] Error reading {path}: {e}")
            all_even = False

    if all_even:
        print("[SIZE CHECK] All output stamp images have even width and height.")
    else:
        print("[SIZE CHECK] There are output images with odd sizes or missing files.")


def split_to_stamps(input_file: str, start_index: int = 1) -> None:
    """入力ファイルを読み込み、背景透過 + 3×4 に分割して PNG で保存

    start_index によって出力ファイル名の開始番号を制御する。
    例: start_index=1  -> 01.png〜12.png
        start_index=13 -> 13.png〜24.png
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} が見つかりません。このスクリプトと同じフォルダに配置してください。")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    img = Image.open(input_file)

    width, height = img.size
    cell_w = width // COLS
    cell_h = height // ROWS

    index = start_index
    for row in range(ROWS):
        for col in range(COLS):
            left = col * cell_w
            upper = row * cell_h
            right = left + cell_w
            lower = upper + cell_h

            crop = img.crop((left, upper, right, lower))
            crop = make_background_transparent(crop)
            crop = add_white_outline(crop, thickness=2)
            out_path = os.path.join(OUTPUT_DIR, f"{index:02d}.png")
            crop.save(out_path, format="PNG")
            print(f"saved: {out_path}")
            index += 1

    check_even_output(start_index, ROWS * COLS)


if __name__ == "__main__":
    # 使い方:
    #   python split_line_stamp.py                -> 1.png を 01〜12.png で出力
    #   python split_line_stamp.py 2.png         -> 2.png を 01〜12.png で出力
    #   python split_line_stamp.py 2.png 2       -> 2.png を 13〜24.png で出力

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        input_file = DEFAULT_INPUT_FILE

    # 第2引数が "2" のときだけ、13〜24番で出力する
    if len(sys.argv) >= 3 and sys.argv[2] == "2":
        start_index = 13
    else:
        start_index = 1

    split_to_stamps(input_file, start_index=start_index)
