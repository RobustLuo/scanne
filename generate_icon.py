"""
图标生成器：为超级骆狗工具箱生成 .ico 图标和 logo 图片
运行: python3 generate_icon.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIZE = 256
MARGIN = 24


def create_icon(size=256):
    """生成盾牌 + 扫描线 图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = int(size * 0.10)

    # === 渐变背景圆 ===
    center = size // 2
    radius = size // 2 - pad
    for r in range(radius, 0, -1):
        t = r / radius
        r_val = int(30 + (1 - t) * 40)
        g_val = int(100 + (1 - t) * 130)
        b_val = int(180 + (1 - t) * 75)
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(r_val, g_val, b_val, 255),
        )

    # === 盾牌形状 ===
    shield_w = int(size * 0.45)
    shield_h = int(size * 0.62)
    shield_x = center - shield_w // 2
    shield_y = int(size * 0.16)

    # 盾牌多边形坐标：顶部宽 → 腰部收窄 → 底部尖角
    points = [
        (shield_x, shield_y),                                    # 左上
        (shield_x + shield_w, shield_y),                         # 右上
        (shield_x + shield_w, shield_y + int(shield_h * 0.55)),  # 右腰
        (center, shield_y + shield_h),                           # 底尖
        (shield_x, shield_y + int(shield_h * 0.55)),             # 左腰
    ]
    draw.polygon(points, fill=(240, 245, 255, 255), outline=(60, 120, 200), width=3)

    # === 盾牌内：扫描圆圈 ===
    scan_cx = center
    scan_cy = shield_y + int(shield_h * 0.32)
    scan_r = int(shield_w * 0.25)
    line_w = 3

    # 外圈
    draw.ellipse(
        [scan_cx - scan_r, scan_cy - scan_r, scan_cx + scan_r, scan_cy + scan_r],
        outline=(50, 130, 220, 255), width=line_w,
    )

    # 扫描线（水平）
    draw.line(
        [scan_cx - int(scan_r * 0.7), scan_cy, scan_cx + int(scan_r * 0.7), scan_cy],
        fill=(50, 130, 220, 255), width=line_w,
    )

    # 中心点
    dot_r = 5
    draw.ellipse(
        [scan_cx - dot_r, scan_cy - dot_r, scan_cx + dot_r, scan_cy + dot_r],
        fill=(50, 130, 220, 255),
    )

    # === 盾牌内：√ 勾 ===
    check_x = center
    check_y = shield_y + int(shield_h * 0.55)
    check_size = int(shield_w * 0.22)
    draw.line(
        [
            check_x - check_size, check_y,
            check_x - int(check_size * 0.35), check_y + int(check_size * 0.65),
        ],
        fill=(34, 197, 94, 255), width=5,
    )
    draw.line(
        [
            check_x - int(check_size * 0.35), check_y + int(check_size * 0.65),
            check_x + int(check_size * 0.55), check_y - int(check_size * 0.3),
        ],
        fill=(34, 197, 94, 255), width=5,
    )

    # === 保存多尺寸 .ico ===
    sizes = [256, 128, 64, 48, 32, 16]
    ico_path = os.path.join(BASE_DIR, "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"[OK] 图标已生成: {ico_path}  (尺寸: {sizes})")

    # === 保存 PNG logo ===
    png_path = os.path.join(BASE_DIR, "logo.png")
    img.save(png_path, format="PNG")
    print(f"[OK] Logo 已生成: {png_path}  ({size}x{size})")

    return img


if __name__ == "__main__":
    create_icon()
    print("\n生成完毕！PyInstaller 打包时使用 --icon=icon.ico 即可。")
