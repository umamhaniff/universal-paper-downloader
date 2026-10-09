"""
Generate bespoke, premium, high-end Logo & Icon for Universal Paper Downloader.
Concept: 'The Scholarly Nexus' - An abstract geometric crystalline manuscript
fused with an orbital celestial portal in cyber-cyan & electric violet.
Supersampled at 1024x1024 and downscaled with Lanczos for razor-sharp fidelity.
Built by Hans x Gravi
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

def create_premium_branding():
    # 1. Supersampled rendering canvas
    CANVAS_SIZE = 1024
    img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = CANVAS_SIZE / 2
    
    # --- A. BACKGROUND CONTAINER (Luxury Obsidian Squircle) ---
    margin = 56
    radius = 210
    bg_box = [margin, margin, CANVAS_SIZE - margin, CANVAS_SIZE - margin]
    
    # Outer ambient glow
    glow_img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.rounded_rectangle(bg_box, radius=radius, fill=(56, 189, 248, 80))
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(35))
    img.paste(glow_img, (0, 0), glow_img)

    # Base dark container
    draw.rounded_rectangle(bg_box, radius=radius, fill=(11, 15, 26, 255), outline=(56, 189, 248, 200), width=10)
    
    # Inner border contour
    inner_box = [margin + 16, margin + 16, CANVAS_SIZE - margin - 16, CANVAS_SIZE - margin - 16]
    draw.rounded_rectangle(inner_box, radius=radius - 12, outline=(99, 102, 241, 100), width=4)

    # --- B. UNIVERSAL ORBITAL CELESTIAL RINGS ---
    # Large tilted dynamic ellipse ring
    ring_img = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring_img)
    
    # Elliptical orbit 1 (cyan accent)
    ring_bbox = [center - 360, center - 200, center + 360, center + 200]
    ring_draw.ellipse(ring_bbox, outline=(56, 189, 248, 180), width=8)
    
    # Elliptical orbit 2 (violet accent, intersecting angle)
    ring_bbox_2 = [center - 220, center - 350, center + 220, center + 350]
    ring_draw.ellipse(ring_bbox_2, outline=(168, 85, 247, 140), width=6)

    # Orbit nodes / planetary particles
    nodes = [
        (center + 340, center - 60, (56, 189, 248, 255), 14),
        (center - 310, center + 100, (14, 165, 233, 255), 12),
        (center + 120, center + 320, (192, 132, 252, 255), 16),
        (center - 140, center - 310, (244, 114, 182, 255), 12),
    ]
    for nx, ny, ncolor, nr in nodes:
        ring_draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=ncolor, outline=(255, 255, 255, 255), width=3)

    img = Image.alpha_composite(img, ring_img)
    draw = ImageDraw.Draw(img)

    # --- C. CORE ICON: ISOMETRIC GEOMETRIC WINGS OF KNOWLEDGE (OPEN MANUSCRIPT PORTAL) ---
    # Left wing (Cyber Cyan Gradient Facet)
    # Right wing (Electric Violet/Indigo Facet)
    # Center spine / Prism Zenith
    
    y_shift = 15
    spine_x = center
    spine_top = center - 160 + y_shift
    spine_bottom = center + 180 + y_shift
    
    # Wing Left Outer
    wing_l_outer = (center - 250, center - 40 + y_shift)
    wing_l_mid = (center - 180, center + 140 + y_shift)
    wing_l_bottom = (center - 40, spine_bottom - 20)
    
    # Wing Left Main Facet (Cyan Blue)
    draw.polygon([
        (spine_x, spine_top),
        wing_l_outer,
        wing_l_mid,
        (spine_x, spine_bottom)
    ], fill=(14, 165, 233, 240), outline=(224, 242, 254, 255))
    
    # Wing Left Shadow / Fold Sub-Facet
    draw.polygon([
        wing_l_mid,
        (spine_x, spine_bottom),
        (spine_x - 30, spine_bottom + 45),
        wing_l_mid
    ], fill=(3, 105, 161, 240))

    # Wing Right Outer
    wing_r_outer = (center + 250, center - 40 + y_shift)
    wing_r_mid = (center + 180, center + 140 + y_shift)
    
    # Wing Right Main Facet (Electric Violet)
    draw.polygon([
        (spine_x, spine_top),
        wing_r_outer,
        wing_r_mid,
        (spine_x, spine_bottom)
    ], fill=(139, 92, 246, 240), outline=(243, 232, 255, 255))
    
    # Wing Right Shadow / Fold Sub-Facet
    draw.polygon([
        wing_r_mid,
        (spine_x, spine_bottom),
        (spine_x + 30, spine_bottom + 45),
        wing_r_mid
    ], fill=(91, 33, 182, 240))

    # --- D. INNER KINETIC LIGHT LAYERS (Transparent Geometric Pages) ---
    # Inner Left Page (Lighter Cyan)
    draw.polygon([
        (spine_x, spine_top + 45),
        (center - 180, center - 10 + y_shift),
        (center - 130, center + 120 + y_shift),
        (spine_x, spine_bottom - 10)
    ], fill=(56, 189, 248, 220), outline=(255, 255, 255, 220))

    # Inner Right Page (Lighter Violet/Magenta)
    draw.polygon([
        (spine_x, spine_top + 45),
        (center + 180, center - 10 + y_shift),
        (center + 130, center + 120 + y_shift),
        (spine_x, spine_bottom - 10)
    ], fill=(168, 85, 247, 220), outline=(255, 255, 255, 220))

    # --- E. ZENITH PORTAL APEX (Glowing Prism Star / Diamond Core) ---
    # Radiant Diamond at Zenith
    d_size = 54
    d_cy = spine_top - 65
    diamond_coords = [
        (center, d_cy - d_size),
        (center + d_size * 0.75, d_cy),
        (center, d_cy + d_size),
        (center - d_size * 0.75, d_cy)
    ]
    # Diamond Glow
    for d_offset in [16, 8]:
        draw.polygon([
            (center, d_cy - d_size - d_offset),
            (center + d_size * 0.75 + d_offset, d_cy),
            (center, d_cy + d_size + d_offset),
            (center - d_size * 0.75 - d_offset, d_cy)
        ], outline=(254, 240, 138, 90), width=3)

    # Core Diamond (Golden Beacon of Knowledge)
    draw.polygon(diamond_coords, fill=(250, 204, 21, 255), outline=(255, 255, 255, 255))
    
    # Inner Diamond Facet
    draw.polygon([
        (center, d_cy - d_size),
        (center + d_size * 0.75, d_cy),
        (center, d_cy + d_size * 0.3)
    ], fill=(254, 240, 138, 255))

    # Vertical light ray beam from diamond into book spine
    draw.line([(center, d_cy + d_size), (center, spine_top + 40)], fill=(255, 255, 255, 220), width=6)

    # --- F. EXPORT HIGH-RES ASSETS ---
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 1. High-Res PNG (512x512 with high-quality Lanczos downsampling)
    logo_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
    logo_png_path = assets_dir / "logo.png"
    logo_512.save(logo_png_path, "PNG")
    print(f"[*] High-res logo saved at: {logo_png_path.resolve()}")

    # 2. Multi-Resolution Windows ICO
    ico_path = Path("app_icon.ico")
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    logo_512.save(ico_path, format="ICO", sizes=sizes)
    print(f"[*] Multi-res app_icon.ico saved at: {ico_path.resolve()} with sizes {sizes}")

if __name__ == "__main__":
    create_premium_branding()
