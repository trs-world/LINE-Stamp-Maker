from __future__ import annotations

import os
from pathlib import Path

from make_resized_image import make_resized_image, parse_background


BASE_DIR = Path(__file__).resolve().parent
MAIN_TAB_DIR = BASE_DIR / "main-tab"


def main() -> None:
    if not MAIN_TAB_DIR.exists():
        raise FileNotFoundError(f"{MAIN_TAB_DIR} が見つかりません。main-tab フォルダを作成してください。")

    src_main = MAIN_TAB_DIR / "01.png"
    src_tab = MAIN_TAB_DIR / "02.png"

    if not src_main.exists():
        raise FileNotFoundError(f"{src_main} が見つかりません。01.png を main-tab フォルダに置いてください。")
    if not src_tab.exists():
        raise FileNotFoundError(f"{src_tab} が見つかりません。02.png を main-tab フォルダに置いてください。")

    # 背景は透過（"" を渡すと parse_background が (0,0,0,0) になる）
    background = parse_background("")

    # main.png: 240x240
    out_main = MAIN_TAB_DIR / "main.png"
    make_resized_image(
        input_path=str(src_main),
        output_path=str(out_main),
        target_width=240,
        target_height=240,
        background=background,
    )

    # tab.png: 96x74
    out_tab = MAIN_TAB_DIR / "tab.png"
    make_resized_image(
        input_path=str(src_tab),
        output_path=str(out_tab),
        target_width=96,
        target_height=74,
        background=background,
    )


if __name__ == "__main__":
    main()
