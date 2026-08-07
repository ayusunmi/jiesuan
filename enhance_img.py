"""提高二维码图片清晰度并更新到 index.html"""
import base64
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

ROOT = Path(__file__).parent
SRC_IMG = ROOT / "qr_payment.jpg"
ORIG_IMG = Path(r"D:\段娅楠\D\微信\jilu\xwechat_files\wxid_rge5st6wr13512_3db2\temp\RWTemp\2026-08\收银码.jpg")
HTML_FILE = ROOT / "index.html"

# 优先使用原始图片（清晰度更高），否则用现有 qr_payment.jpg
src = ORIG_IMG if ORIG_IMG.exists() else SRC_IMG
print(f"Using source image: {src}")
print(f"Source exists: {src.exists()}")

if not src.exists():
    print("ERROR: No source image found")
    sys.exit(1)

# 打开原图，转 RGB
img = Image.open(src).convert("RGB")
print(f"Original size: {img.size}")

# 保存为高质量 JPEG（quality=95，保留较高清晰度，subsampling=0 禁用色度子采样以保留细节）
buf = Path(ROOT) / "qr_payment_hq.jpg"
img.save(buf, "JPEG", quality=95, subsampling=0, optimize=True)
print(f"Saved high-quality image: {buf}")
print(f"File size: {buf.stat().st_size} bytes")

# 转 base64
b64 = base64.b64encode(buf.read_bytes()).decode("ascii")
print(f"Base64 length: {len(b64)}")

# 读取 HTML
html = HTML_FILE.read_text(encoding="utf-8")

# 通过唯一的前缀和后缀定位现有 src
prefix = '<img class="qr-img" src="data:image/jpeg;base64,'
suffix = '" alt="收银码">'
start = html.find(prefix)
if start == -1:
    print("ERROR: qr-img tag not found")
    sys.exit(1)
end = html.find(suffix, start)
if end == -1:
    print("ERROR: closing alt tag not found")
    sys.exit(1)

old_tag = html[start:end + len(suffix)]
new_tag = prefix + b64 + suffix
html = html[:start] + new_tag + html[end + len(suffix):]

HTML_FILE.write_text(html, encoding="utf-8")
print("HTML updated successfully")
