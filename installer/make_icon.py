"""Generate PNG icons for OpenArchieve from a simple vector-like drawing."""
import os
from PIL import Image, ImageDraw, ImageFont

DARK = (30, 31, 34)
GOLD = (240, 178, 50)
WHITE = (242, 243, 245)
DIM = (181, 186, 193)


def font(size):
    for name in ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def make(size, path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = size * 0.18
    # background rounded rect
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=DARK)
    # gold top bar
    bar_h = size * 0.23
    d.rounded_rectangle([0, 0, size - 1, bar_h], radius=r, fill=GOLD)
    d.rectangle([0, bar_h * 0.5, size - 1, bar_h], fill=GOLD)
    # "OA" text
    f = font(int(size * 0.34))
    text = "OA"
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] + size * 0.07), text, fill=WHITE, font=f)
    # gold progress bar near bottom
    bw = size * 0.56
    bh = size * 0.09
    bx = (size - bw) / 2
    by = size * 0.78
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh / 2, fill=GOLD)
    d.rounded_rectangle([bx + bw * 0.08, by + bh * 0.3, bx + bw * 0.5, by + bh * 0.7], radius=bh * 0.2, fill=DARK)
    img.save(path)
    print(f"saved {path} ({size}x{size})")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..")
    for s in (16, 32, 48, 64, 128, 256):
        make(s, os.path.join(out, f"icon_{s}.png"))
    make(256, os.path.join(out, "icon.png"))
    # Multi-resolution .ico for Windows (Inno Setup requires .ico)
    try:
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        imgs = [Image.open(os.path.join(out, f"icon_{s}.png")) for s, _ in sizes]
        imgs[0].save(
            os.path.join(out, "icon_256.ico"),
            format="ICO",
            sizes=sizes,
            append_images=imgs[1:],
        )
        print("saved icon_256.ico (multi-res)")
    except Exception as e:
        print(f"ICO generation skipped: {e}")
