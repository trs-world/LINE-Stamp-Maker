from __future__ import annotations

from PIL import Image
import argparse
import os
from typing import Tuple, List


def parse_color(code: str) -> Tuple[int, int, int]:
    """"#RRGGBB" 形式のカラーコードを (R, G, B) に変換"""
    if not code.startswith("#") or len(code) != 7:
        raise ValueError("color code must be like #RRGGBB")
    r = int(code[1:3], 16)
    g = int(code[3:5], 16)
    b = int(code[5:7], 16)
    return r, g, b


def recolor_background(
    input_path: str,
    output_path: str,
    from_color: Tuple[int, int, int],
    to_color: Tuple[int, int, int],
    tolerance: int = 20,
) -> None:
    """指定した色付近の「外周と繋がった背景」だけを別の1色に塗り替える"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"{input_path} が見つかりません")

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    px = img.load()
    fr, fg, fb = from_color

    def is_from_color(r: int, g: int, b: int) -> bool:
        return (
            abs(r - fr) <= tolerance
            and abs(g - fg) <= tolerance
            and abs(b - fb) <= tolerance
        )

    # フラッドフィル用マスク（True: 外周と繋がった背景として塗り替える）
    visited: List[List[bool]] = [[False] * w for _ in range(h)]
    stack: List[Tuple[int, int]] = []

    # 画像の四辺からスタート
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h):
            continue
        if visited[y][x]:
            continue

        r, g, b, a = px[x, y]
        if not is_from_color(r, g, b):
            continue

        visited[y][x] = True

        # 4近傍を探索
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    # visited=True のところだけ背景色を塗り替える
    tr, tg, tb = to_color
    for y in range(h):
        for x in range(w):
            if visited[y][x]:
                r, g, b, a = px[x, y]
                px[x, y] = (tr, tg, tb, a)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, format="PNG")
    print(f"saved: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="背景を1色に塗り替えるスクリプト")
    parser.add_argument("input", help="入力PNGファイルパス")
    parser.add_argument("output", help="出力PNGファイルパス")
    parser.add_argument(
        "--from-color",
        default="#FFFFFF",
        help="元の背景色（デフォルト: #FFFFFF）",
    )
    parser.add_argument(
        "--to-color",
        default="#0ED728",
        help="塗り替え後の背景色（デフォルト: #0ED728）",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=20,
        help="元色とみなす許容誤差（デフォルト: 20）",
    )

    args = parser.parse_args()

    from_color = parse_color(args.from_color)
    to_color = parse_color(args.to_color)

    recolor_background(
        input_path=args.input,
        output_path=args.output,
        from_color=from_color,
        to_color=to_color,
        tolerance=args.tolerance,
    )


if __name__ == "__main__":
    main()
