"""
Generate high-quality multi-resolution Windows Icon (.ico) for Universal Paper Downloader.
Built by Hans x Gravi
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_app_icon(output_path="app_icon.ico"):
    size = 256
    # Create RGBA image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base Squircle / Rounded Background (Deep Royal Blue Gradient-ish)
    bg_color = (15, 23, 42, 255)       # Slate 900
    border_color = (56, 189, 248, 255) # Sky 400
    accent_blue = (30, 58, 138, 255)   # Blue 900
    
    # Draw rounded rect backplate
    draw.rounded_rectangle([12, 12, size - 12, size - 12], radius=48, fill=bg_color, outline=border_color, width=5)

    # Subtle inner glow / gradient plate
    draw.rounded_rectangle([20, 20, size - 20, size - 20], radius=40, fill=accent_blue)

    # 2. Document / Paper Sheet (White / Light Slate with folded corner)
    # Paper bounds: left=60, top=45, right=180, bottom=205
    # Fold corner at top right: corner size = 32
    p_left, p_top, p_right, p_bottom = 64, 48, 192, 208
    fold = 36

    paper_fill = (248, 250, 252, 255) # Slate 50
    paper_shadow = (203, 213, 225, 255) # Slate 300
    
    # Paper polygon with folded corner
    paper_coords = [
        (p_left, p_top),
        (p_right - fold, p_top),
        (p_right, p_top + fold),
        (p_right, p_bottom),
        (p_left, p_bottom)
    ]
    draw.polygon(paper_coords, fill=paper_fill)

    # Fold flap (top right triangle)
    flap_coords = [
        (p_right - fold, p_top),
        (p_right - fold, p_top + fold),
        (p_right, p_top + fold)
    ]
    draw.polygon(flap_coords, fill=paper_shadow, outline=(148, 163, 184, 255), width=2)

    # 3. Text lines on Paper
    line_color = (100, 116, 139, 255) # Slate 500
    header_color = (2, 132, 199, 255) # Sky 600
    
    # Title line
    draw.rounded_rectangle([p_left + 16, p_top + 22, p_right - fold - 8, p_top + 30], radius=3, fill=header_color)

    # Article text lines
    draw.rounded_rectangle([p_left + 16, p_top + 54, p_right - 18, p_top + 60], radius=2, fill=line_color)
    draw.rounded_rectangle([p_left + 16, p_top + 70, p_right - 18, p_top + 76], radius=2, fill=line_color)
    draw.rounded_rectangle([p_left + 16, p_top + 86, p_right - 28, p_top + 92], radius=2, fill=line_color)
    draw.rounded_rectangle([p_left + 16, p_top + 102, p_right - 18, p_top + 108], radius=2, fill=line_color)

    # 4. Vibrant Download Badge / Academic Emblem in bottom-right quadrant
    # Circle badge
    badge_center = (180, 180)
    badge_radius = 42
    b_x1 = badge_center[0] - badge_radius
    b_y1 = badge_center[1] - badge_radius
    b_x2 = badge_center[0] + badge_radius
    b_y2 = badge_center[1] + badge_radius

    # Outer badge circle with glowing outline
    draw.ellipse([b_x1, b_y1, b_x2, b_y2], fill=(14, 165, 233, 255), outline=(255, 255, 255, 255), width=4) # Sky 500

    # Down Arrow inside Badge
    arrow_color = (255, 255, 255, 255)
    # Stem
    draw.rectangle([badge_center[0] - 6, badge_center[1] - 22, badge_center[0] + 6, badge_center[1] + 6], fill=arrow_color)
    # Head
    draw.polygon([
        (badge_center[0] - 18, badge_center[1] + 4),
        (badge_center[0] + 18, badge_center[1] + 4),
        (badge_center[0], badge_center[1] + 24)
    ], fill=arrow_color)

    # Horizontal tray line under arrow
    draw.rounded_rectangle([badge_center[0] - 20, badge_center[1] + 24, badge_center[0] + 20, badge_center[1] + 28], radius=2, fill=arrow_color)

    # Save as multi-resolution ICO file
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(output_path, format="ICO", sizes=sizes)
    print(f"[*] Icon successfully created at {output_path} with sizes {sizes}")

if __name__ == "__main__":
    create_app_icon()
