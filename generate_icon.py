"""
Generate high-end 3D Modern Hardcover Academic Journal Book icon & logo.
Concept: Hardcover Research Tome in deep midnight blue with multi-layered pages,
embossed golden crest, and a silky golden bookmark ribbon.
Supersampled at 1024x1024, downscaled via Lanczos.
Built by Hans x Gravi
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math

def draw_3d_journal_tome():
    CANVAS_SIZE = 1024
    img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base App Squircle Container (iOS / macOS Dark Luxury Style)
    margin = 60
    radius = 210
    squircle_box = [margin, margin, CANVAS_SIZE - margin, CANVAS_SIZE - margin]

    # Outer ambient drop shadow of squircle
    shadow_img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.rounded_rectangle([margin + 10, margin + 25, CANVAS_SIZE - margin - 10, CANVAS_SIZE - margin + 25],
                                  radius=radius, fill=(0, 0, 0, 160))
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(30))
    img.paste(shadow_img, (0, 0), shadow_img)

    # Dark background plate (Deep Obsidian Blue)
    draw.rounded_rectangle(squircle_box, radius=radius, fill=(13, 19, 33, 255), outline=(56, 189, 248, 120), width=6)
    
    # Inner subtle rim highlight
    draw.rounded_rectangle([margin + 10, margin + 10, CANVAS_SIZE - margin - 10, CANVAS_SIZE - margin - 10],
                           radius=radius - 8, outline=(255, 255, 255, 25), width=2)

    # 2. Drop Shadow of the 3D Book
    book_shadow = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    bs_draw = ImageDraw.Draw(book_shadow)
    # Shadow ellipse under the book
    bs_draw.ellipse([210, 660, 830, 840], fill=(0, 0, 0, 180))
    book_shadow = book_shadow.filter(ImageFilter.GaussianBlur(32))
    img.paste(book_shadow, (0, 0), book_shadow)
    draw = ImageDraw.Draw(img)

    # 3. 3D BOOK GEOMETRY (Isometric Perspective)
    # Book is resting at a 3D perspective angle:
    # Top Cover (Front):
    #   p_tl: Top-Left  (near spine)
    #   p_tr: Top-Right (outer top)
    #   p_br: Bottom-Right (outer bottom)
    #   p_bl: Bottom-Left (near spine bottom)
    
    # Thickness / extrusion offsets
    thickness_y = 110  # page block height
    thickness_x = 0

    # Cover points (top surface)
    c_tl = (270, 310)  # Top Left
    c_tr = (710, 230)  # Top Right
    c_br = (780, 560)  # Bottom Right
    c_bl = (340, 640)  # Bottom Left

    # Back cover / Bottom points
    b_tl = (c_tl[0], c_tl[1] + thickness_y)
    b_tr = (c_tr[0], c_tr[1] + thickness_y)
    b_br = (c_br[0], c_br[1] + thickness_y)
    b_bl = (c_bl[0], c_bl[1] + thickness_y)

    # --- A. SPINE (Left Edge) ---
    # Spine polygon
    spine_coords = [c_tl, c_bl, b_bl, b_tl]
    # Deep navy spine with gradient-like tones
    draw.polygon(spine_coords, fill=(15, 23, 42, 255), outline=(30, 41, 59, 255))
    # Spine vertical highlight ridges (book binding grooves)
    draw.line([(c_tl[0] + 12, c_tl[1] + 15), (c_bl[0] + 12, c_bl[1] + 15)], fill=(51, 65, 85, 255), width=4)
    draw.line([(c_tl[0] + 24, c_tl[1] + 30), (c_bl[0] + 24, c_bl[1] + 30)], fill=(71, 85, 105, 255), width=2)

    # --- B. PAGE BLOCK (Bottom Edge - Paper Layers) ---
    # Bottom page rim
    draw.polygon([c_bl, c_br, b_br, b_bl], fill=(226, 232, 240, 255), outline=(148, 163, 184, 255))
    # Horizontal page striations (simulating dense book pages)
    for step in range(12, thickness_y - 12, 14):
        p1 = (c_bl[0], c_bl[1] + step)
        p2 = (c_br[0], c_br[1] + step)
        draw.line([p1, p2], fill=(203, 213, 225, 255), width=2)

    # --- C. PAGE BLOCK (Right Edge - Paper Layers) ---
    draw.polygon([c_tr, c_br, b_br, b_tr], fill=(241, 245, 249, 255), outline=(148, 163, 184, 255))
    # Striations along right edge
    for step in range(10, thickness_y - 10, 14):
        p1 = (c_tr[0], c_tr[1] + step)
        p2 = (c_br[0], c_br[1] + step)
        draw.line([p1, p2], fill=(203, 213, 225, 255), width=2)

    # Bottom Cover lip (Hardcover overhang)
    lip = 8
    draw.polygon([
        (b_bl[0], b_bl[1]),
        (b_br[0] + lip, b_br[1] + lip // 2),
        (b_br[0] + lip, b_br[1] + lip // 2 + 10),
        (b_bl[0], b_bl[1] + 10)
    ], fill=(15, 23, 42, 255))

    # --- D. TOP COVER (Front Hardcover Face) ---
    # Rich Midnight Royal Blue
    cover_coords = [c_tl, c_tr, c_br, c_bl]
    draw.polygon(cover_coords, fill=(29, 78, 216, 255), outline=(96, 165, 250, 255), width=3) # Blue 700

    # Inner embossed golden filigree border
    def lerp_pt(p1, p2, t):
        return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

    def inset_quad(pts, margin_t):
        # Center of quad
        cx = sum(p[0] for p in pts) / 4
        cy = sum(p[1] for p in pts) / 4
        return [(lerp_pt(p, (cx, cy), margin_t)) for p in pts]

    inner_gold_quad = inset_quad(cover_coords, 0.12)
    draw.polygon(inner_gold_quad, outline=(251, 191, 36, 230), width=4) # Amber 400 gold

    # Second fine gold hairline
    inner_gold_quad2 = inset_quad(cover_coords, 0.15)
    draw.polygon(inner_gold_quad2, outline=(253, 230, 138, 140), width=2)

    # --- E. EMBOSSED GOLDEN SCHOLARLY EMBLEM ON COVER ---
    # Center of front cover
    cov_cx = sum(p[0] for p in cover_coords) / 4
    cov_cy = sum(p[1] for p in cover_coords) / 4

    # Academic Laurel / Compass Monogram
    # Central Gold Diamond
    diam_r = 44
    draw.polygon([
        (cov_cx, cov_cy - diam_r),
        (cov_cx + diam_r * 0.9, cov_cy),
        (cov_cx, cov_cy + diam_r),
        (cov_cx - diam_r * 0.9, cov_cy)
    ], fill=(245, 158, 11, 240), outline=(254, 240, 138, 255), width=3)

    # Four-pointed academic star inside diamond
    star_inner = 14
    star_outer = 32
    star_pts = []
    for i in range(8):
        angle = i * (math.pi / 4)
        r = star_outer if i % 2 == 0 else star_inner
        star_pts.append((cov_cx + r * math.cos(angle), cov_cy + r * math.sin(angle) * 0.85))
    draw.polygon(star_pts, fill=(254, 243, 199, 255))

    # Embossed Title Lines on Cover (Simulating Gold Lettering)
    for line_y_offset in [-110, -85]:
        t_l = (cov_cx - 105, cov_cy + line_y_offset)
        t_r = (cov_cx + 105, cov_cy + line_y_offset)
        draw.line([t_l, t_r], fill=(252, 211, 77, 210), width=6)

    # --- F. SILKY GOLDEN BOOKMARK RIBBON ---
    # Ribbon flows out from inside the pages and drapes down past the bottom edge
    # Points defining ribbon
    r_width = 38
    r_top_left = (540, 480)
    r_mid_left = (555, 660)
    r_bottom_left = (565, 760)

    r_top_right = (r_top_left[0] + r_width, r_top_left[1] - 8)
    r_mid_right = (r_mid_left[0] + r_width, r_mid_left[1] - 6)
    r_bottom_right = (r_bottom_left[0] + r_width, r_bottom_left[1] - 4)

    # Notch tip at end of ribbon (classic V-cut)
    v_notch = (r_bottom_left[0] + r_width / 2, r_bottom_left[1] - 22)

    # Ribbon drop shadow
    ribbon_shadow = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    rs_draw = ImageDraw.Draw(ribbon_shadow)
    rs_coords = [
        (r_mid_left[0] + 8, r_mid_left[1] + 12),
        (r_mid_right[0] + 8, r_mid_right[1] + 12),
        (r_bottom_right[0] + 8, r_bottom_right[1] + 12),
        (v_notch[0] + 8, v_notch[1] + 12),
        (r_bottom_left[0] + 8, r_bottom_left[1] + 12)
    ]
    rs_draw.polygon(rs_coords, fill=(0, 0, 0, 100))
    ribbon_shadow = ribbon_shadow.filter(ImageFilter.GaussianBlur(10))
    img.paste(ribbon_shadow, (0, 0), ribbon_shadow)
    draw = ImageDraw.Draw(img)

    # Ribbon body
    ribbon_coords = [
        r_top_left,
        r_top_right,
        r_bottom_right,
        v_notch,
        r_bottom_left
    ]
    # Rich Golden Silk gradient fill
    draw.polygon(ribbon_coords, fill=(245, 158, 11, 255), outline=(254, 243, 199, 255), width=2) # Amber 500

    # Ribbon highlight sheen (vertical light streak along ribbon)
    sheen_left = (r_top_left[0] + 8, r_top_left[1])
    sheen_bottom = (r_bottom_left[0] + 8, r_bottom_left[1] - 22)
    draw.line([sheen_left, sheen_bottom], fill=(254, 240, 138, 200), width=4)

    # --- G. SAVE EXPORT ASSETS ---
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # 1. High-Res PNG (512x512 via Lanczos)
    logo_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    png_path = assets_dir / "logo.png"
    logo_512.save(png_path, "PNG")
    print(f"[*] High-res 3D tome logo saved at: {png_path.resolve()}")

    # 2. Multi-Resolution Windows ICO
    ico_path = Path("app_icon.ico")
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    logo_512.save(ico_path, format="ICO", sizes=sizes)
    print(f"[*] Multi-res 3D tome app_icon.ico saved at: {ico_path.resolve()}")

if __name__ == "__main__":
    draw_3d_journal_tome()
