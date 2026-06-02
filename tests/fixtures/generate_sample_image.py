"""Create a small test leaf image for vision tests (no external download)."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Install Pillow: pip install Pillow")

OUT = Path(__file__).parent / "images" / "sample_leaf.jpg"
OUT.parent.mkdir(parents=True, exist_ok=True)

img = Image.new("RGB", (400, 300), color=(34, 120, 50))
draw = ImageDraw.Draw(img)
draw.ellipse([80, 60, 320, 240], fill=(180, 200, 60), outline=(100, 140, 40))
draw.ellipse([150, 120, 200, 170], fill=(139, 90, 43))
img.save(OUT, "JPEG", quality=85)
print(f"Created {OUT}")
