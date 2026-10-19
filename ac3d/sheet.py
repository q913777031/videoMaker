"""把若干静帧拼成一行联系表：python3 ac3d/sheet.py 输出.png 帧1.png 帧2.png ..."""
import sys
from PIL import Image

out, files = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).convert("RGB").resize((360, 640)) for f in files]
sheet = Image.new("RGB", (360 * len(ims), 640), "white")
for i, im in enumerate(ims):
    sheet.paste(im, (i * 360, 0))
sheet.save(out)
