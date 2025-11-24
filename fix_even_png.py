import os
from pathlib import Path
from PIL import Image

# 対象フォルダ
BASE_DIR = Path(r"c:\Users\PC_User\CascadeProjects\LINE-stamp\Release")

def make_even_by_crop(img: Image.Image) -> Image.Image:
    width, height = img.size
    new_width = width - (width % 2)   # 奇数なら -1
    new_height = height - (height % 2)

    # すでに偶数ならそのまま
    if new_width == width and new_height == height:
        return img

    # 右端・下端を切り捨ててクロップ
    return img.crop((0, 0, new_width, new_height))


def process_pngs(base_dir: Path):
    count_total = 0
    count_changed = 0

    for root, _, files in os.walk(base_dir):
        for name in files:
            if not name.lower().endswith(".png"):
                continue

            file_path = Path(root) / name
            count_total += 1

            try:
                with Image.open(file_path) as im:
                    w, h = im.size
                    new_im = make_even_by_crop(im)

                    if new_im.size != (w, h):
                        # 上書き保存
                        new_im.save(file_path)
                        count_changed += 1
                        print(f"Fixed: {file_path}  {w}x{h} -> {new_im.size[0]}x{new_im.size[1]}")
                    else:
                        # 既に偶数
                        print(f"OK   : {file_path}  {w}x{h} (already even)")
            except Exception as e:
                print(f"Error: {file_path} ({e})")

    print("-----")
    print(f"Total PNG files : {count_total}")
    print(f"Changed (cropped to even): {count_changed}")


if __name__ == "__main__":
    if not BASE_DIR.exists():
        print(f"Directory not found: {BASE_DIR}")
    else:
        print(f"Scanning: {BASE_DIR}")
        process_pngs(BASE_DIR)
