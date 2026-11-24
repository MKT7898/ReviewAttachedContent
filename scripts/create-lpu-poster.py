"""Create matching, vector-based A4 PDF and editable SVG poster files."""

from html import escape
from pathlib import Path

WIDTH, HEIGHT = 595.276, 841.89
NAVY = "#102849"
BLUE = "#C5DFFF"
INK = "#173453"
MUTED = "#485D73"
PALE = "#F0F6FD"
WHITE = "#FFFFFF"
pdf = []
svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" '
    'viewBox="0 0 595.276 841.89" role="img" aria-labelledby="title description">',
    "<title>LPU Smart Lost and Found System — campus poster</title>",
    "<desc>A4 poster with a non-scannable QR placeholder, instructions for reporting "
    "and searching items, and a reminder to hand valuables to campus security.</desc>",
]


def rgb(color):
    return " ".join(f"{int(color[i:i + 2], 16) / 255:.4f}" for i in (1, 3, 5))


def rect(x, y, w, h, fill, stroke=None):
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
        + (f' stroke="{stroke}" stroke-width="1"' if stroke else "")
        + "/>"
    )
    pdf.append(f"q {rgb(fill)} rg")
    if stroke:
        pdf.append(f"{rgb(stroke)} RG 1 w")
    pdf.append(f"{x} {HEIGHT - y - h:.3f} {w} {h} re {'B' if stroke else 'f'} Q")


def line(x1, y1, x2, y2, color, weight=1):
    svg.append(
        f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" '
        f'stroke="{color}" stroke-width="{weight}"/>'
    )
    pdf.append(
        f"q {rgb(color)} RG {weight} w {x1} {HEIGHT-y1:.3f} m "
        f"{x2} {HEIGHT-y2:.3f} l S Q"
    )


def text(x, y, content, size=14, color=INK, bold=False, center=False):
    # Helvetica metrics cover the ASCII text used in this print master.
    widths = {
        " ": 278, ".": 278, ",": 278, ":": 278, "-": 333, "/": 278,
        "?": 611 if bold else 556, "&": 722 if bold else 667,
    }
    narrow = "ijlIft"
    wide = "mwMW"
    total = 0
    # Exact centering is handled by SVG; these standard metrics center PDF text.
    regular = [
        667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
        722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611,
    ]
    heavy = [
        722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833,
        722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611,
    ]
    lower = [
        556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
        556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500,
    ]
    for char in content:
        if "A" <= char <= "Z":
            total += (heavy if bold else regular)[ord(char) - 65]
        elif "a" <= char <= "z":
            total += lower[ord(char) - 97]
        else:
            total += widths.get(char, 556)
    actual_x = x - total * size / 2000 if center else x
    assert actual_x >= 0 and actual_x + total * size / 1000 < WIDTH, content
    svg.append(
        f'<text x="{x}" y="{y}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}"'
        f' text-anchor="{"middle" if center else "start"}">{escape(content)}</text>'
    )
    escaped = content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    pdf.append(
        f"BT /{'F2' if bold else 'F1'} {size} Tf {rgb(color)} rg "
        f"1 0 0 1 {actual_x:.3f} {HEIGHT-y:.3f} Tm ({escaped}) Tj ET"
    )


rect(0, 0, WIDTH, HEIGHT, WHITE)
rect(0, 0, WIDTH, 251, NAVY)
rect(0, 0, WIDTH, 7, BLUE)
rect(40, 34, 35, 35, WHITE)
text(57.5, 56, "LPU", 12, NAVY, True, True)
text(87, 47, "LPU SMART LOST AND FOUND SYSTEM", 12, WHITE, True)
text(87, 64, "LOVELY PROFESSIONAL UNIVERSITY", 9, BLUE)
text(40, 124, "LOST SOMETHING?", 39, WHITE, True)
text(40, 172, "FOUND SOMETHING?", 39, BLUE, True)
text(42, 215, "Report it. Search it. Return it.", 20, WHITE)

text(WIDTH / 2, 284, "ONE CAMPUS. LOOKING OUT FOR EACH OTHER.", 10, MUTED, True, True)
rect(204, 302, 187, 174, PALE, "#C8D8EB")
# A deliberately blank panel: no QR-like modules, finder marks, or barcode.
text(WIDTH / 2, 375, "QR CODE", 20, NAVY, True, True)
text(WIDTH / 2, 399, "PLACEHOLDER", 17, NAVY, True, True)
text(WIDTH / 2, 429, "Non-scannable", 11, MUTED, False, True)
text(WIDTH / 2, 460, "Replace with your verified website QR", 9, MUTED, False, True)
text(WIDTH / 2, 511, "Scan here to report a lost item", 18, INK, True, True)
text(WIDTH / 2, 535, "or submit a found item.", 18, INK, True, True)
line(40, 560, WIDTH - 40, 560, "#D9E3EE")
text(40, 588, "THREE SIMPLE STEPS TO A SAFE RETURN", 10, MUTED, True)

for x, number, title, detail in [
    (40, "01", "SCAN", ["Scan the QR code."]),
    (215, "02", "REPORT OR SEARCH", ["Report or search", "for the item."]),
    (390, "03", "VERIFY & COLLECT", ["Verify ownership", "and collect the item."]),
]:
    rect(x, 606, 31, 29, PALE)
    text(x + 15.5, 626, number, 13, NAVY, True, True)
    text(x, 656, title, 11, NAVY, True)
    for index, row in enumerate(detail):
        text(x, 677 + index * 18, row, 12, MUTED)

rect(40, 722, WIDTH - 80, 78, NAVY)
text(57, 746, "FOUND SOMETHING VALUABLE?", 11, BLUE, True)
text(57, 767, "For valuable belongings, please hand them over", 13, WHITE)
text(57, 785, "to authorised campus security staff.", 13, WHITE)
text(WIDTH / 2, 824, "A little care. A safe return. A stronger campus community.", 10, MUTED, False, True)
svg.append("</svg>")

stream = "\n".join(pdf).encode("ascii")
objects = [
    b"<< /Type /Catalog /Pages 2 0 R >>",
    b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    (
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {WIDTH} {HEIGHT}] "
        "/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
    ).encode("ascii"),
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
    f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
    b"<< /Title (LPU Smart Lost and Found - A4 Campus Poster) "
    b"/Subject (Print at actual size on A4. QR placeholder is non-scannable.) >>",
]
output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
offsets = [0]
for index, obj in enumerate(objects, 1):
    offsets.append(len(output))
    output.extend(f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")
xref = len(output)
output.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
for offset in offsets[1:]:
    output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
output.extend(
    f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R /Info 7 0 R >>\n"
    f"startxref\n{xref}\n%%EOF\n".encode("ascii")
)
destination = Path("public")
destination.mkdir(exist_ok=True)
(destination / "lpu-lost-found-poster.pdf").write_bytes(output)
(destination / "lpu-lost-found-poster.svg").write_text("\n".join(svg), encoding="utf-8")
print("Created A4 vector PDF and SVG (210 x 297 mm), one page, with non-scannable QR placeholder.")
