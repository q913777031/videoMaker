"""把一期的逐镜静帧拼成联系表：python3 make_sheet.py 04 [起] [止]"""
import sys
import PIL.Image as I
S = "out/stills/"
k = sys.argv[1]; a = int(sys.argv[2]); b = int(sys.argv[3])
ims = [I.open(f"{S}s{k}_{i:02d}.png").resize((540, 960)) for i in range(a, b)]
n = len(ims); cols = 3; rows = (n + cols - 1) // cols
sheet = I.new("RGB", (540 * cols, 960 * rows), "white")
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * 540, (i // cols) * 960))
sheet.save(f"{S}sheet_{k}_{a}.png")
