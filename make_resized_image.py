from __future__ import annotations

from PIL import Image
import argparse
import os
from typing import Tuple


def parse_background(code: str) -> Tuple[int, int, int, int]:
    """"#RRGGBB" or "#RRGGBBAA" を (R, G, B, A) に変換。空文字なら完全透過。"""
    if code == "":
        return 0, 0, 0, 0
    if not code.startswith("#"):
        raise ValueError("background color must start with '#'")
    if len(code) == 7:
        r = int(code[1:3], 16)
        g = int(code[3:5], 16)
        b = int(code[5:7], 16)
        return r, g, b, 255
    if len(code) == 9:
        r = int(code[1:3], 16)
        g = int(code[3:5], 16)
        b = int(code[5:7], 16)
        a = int(code[7:9], 16)
        return r, g, b, a
    raise ValueError("background color must be #RRGGBB or #RRGGBBAA")


def make_resized_image(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    background: Tuple[int, int, int, int],
) -> None:
    """元画像の縦横比を保ったまま、指定サイズのキャンバスに中央配置して出力する"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"{input_path} が見つかりません")

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # 縦横比を維持しながら、指定サイズ内に収まる最大サイズにリサイズ
    scale = min(target_width / w, target_height / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # 指定サイズのキャンバスを作成して中央に貼り付け
    canvas = Image.new("RGBA", (target_width, target_height), background)
    offset_x = (target_width - new_w) // 2
    offset_y = (target_height - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y), resized)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.save(output_path, format="PNG")
    print(f"saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "指定した画像をリサイズしてキャンバスに中央配置して出力するスクリプト\n"
            "デフォルトは240x240（LINEメイン画像想定）"
        )
    )
    parser.add_argument("input", help="入力PNGファイルパス")
    parser.add_argument("output", help="出力PNGファイルパス")
    parser.add_argument(
        "--width",
        type=int,
        default=240,
        help="出力画像の幅（デフォルト: 240）",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=240,
        help="出力画像の高さ（デフォルト: 240）",
    )
    parser.add_argument(
        "--background",
        default="",  # 空文字なら完全透過
        help="背景色 #RRGGBB または #RRGGBBAA（デフォルト: 透過）",
    )

    args = parser.parse_args()
    bg = parse_background(args.background)

    make_resized_image(
        input_path=args.input,
        output_path=args.output,
        target_width=args.width,
        target_height=args.height,
        background=bg,
    )


if __name__ == "__main__":
    main()
