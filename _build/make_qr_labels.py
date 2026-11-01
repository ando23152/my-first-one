"""Print QR reorder labels for every catalog part.

Usage: python3 make_qr_labels.py [SITE_URL] [out.pdf]
  SITE_URL defaults to the current site address. Re-run with the real domain once it's live,
  e.g. python3 make_qr_labels.py https://truepartfabrication.com

Layout: Avery 5160 / 8160 (30 labels per US Letter sheet, 1 x 2-5/8 in).
Each label: QR code to the part page (with ?ref=qr, which shows a reorder note),
part name, part number it replaces, and the phone number.
"""
import json, sys, io
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

sys.path.insert(0, "/home/claude/site_src")
import build as B
import parts_pages

SITE = (sys.argv[1] if len(sys.argv) > 1 else B.BASE).rstrip("/")
OUT = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/TPF_Part_QR_Labels.pdf"
PHONE = "(209) 554-4800"

items = parts_pages.assign_slugs(B.CAT["items"])
W, H = letter
LW, LH = 2.625 * inch, 1.0 * inch
LEFT, TOP, GAP = 0.1875 * inch, 0.5 * inch, 0.125 * inch

def wrap(c, text, font, size, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
            if len(lines) == max_lines:
                break
    if len(lines) < max_lines and cur:
        lines.append(cur)
    if len(lines) == max_lines and " ".join(lines) != text:
        while c.stringWidth(lines[-1] + "…", font, size) > width and " " in lines[-1]:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] += "…"
    return lines

c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("True Part Fabrication QR reorder labels"); c.setAuthor("True Part Fabrication LLC")
for n, it in enumerate(items):
    i = n % 30
    if n and i == 0:
        c.showPage()
    col, row = i % 3, i // 3
    x = LEFT + col * (LW + GAP); y = H - TOP - (row + 1) * LH
    url = f"{SITE}/parts/{it['slug']}/?ref=qr"
    q = qrcode.QRCode(border=1, box_size=6, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(url); q.make(fit=True)
    buf = io.BytesIO(); q.make_image(fill_color="black", back_color="white").save(buf, format="PNG"); buf.seek(0)
    qs = 0.82 * inch
    c.drawImage(ImageReader(buf), x + 0.08 * inch, y + (LH - qs) / 2, qs, qs)
    tx = x + 0.08 * inch + qs + 0.08 * inch; tw = LW - (tx - x) - 0.1 * inch
    c.setFont("Helvetica-Bold", 6.2); c.setFillColorRGB(0.84, 0.12, 0.16)
    c.drawString(tx, y + LH - 0.2 * inch, "TRUE PART FABRICATION")
    c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 7.4)
    ty = y + LH - 0.34 * inch
    for line in wrap(c, it["n"], "Helvetica-Bold", 7.4, tw, 2):
        c.drawString(tx, ty, line); ty -= 0.115 * inch
    c.setFont("Helvetica", 6.4)
    for line in wrap(c, B.rp(it), "Helvetica", 6.4, tw, 1):
        c.drawString(tx, ty, line); ty -= 0.1 * inch
    c.setFont("Helvetica", 6.2)
    c.drawString(tx, y + 0.1 * inch, f"Scan to reorder · {PHONE}")
c.save()
print(f"{len(items)} labels, {(len(items) + 29) // 30} sheets -> {OUT} (links to {SITE})")
