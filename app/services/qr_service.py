import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer
from PIL import Image
from datetime import datetime
from app.extensions import db
from app.models.qr_code import QRCode
from app.models.user import QuotaUsage


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "qr_codes")

DRAWER_MAP = {
    "square":  SquareModuleDrawer(),
    "rounded": RoundedModuleDrawer(),
    "circle":  CircleModuleDrawer(),
}


def generate_qr_code(user, name: str, target_url: str, style_config: dict) -> tuple:
    """
    Generate a QR code image and save it.
    Returns (QRCode, None) or (None, error_message).
    """
    if not name:
        return None, "Nama QR Code wajib diisi."
    if not target_url:
        return None, "URL target wajib diisi."

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    dot_style   = style_config.get("dot_style", "square")
    fg_color    = style_config.get("fg_color", "#000000")
    bg_color    = style_config.get("bg_color", "#FFFFFF")
    drawer      = DRAWER_MAP.get(dot_style, SquareModuleDrawer())

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    # Use StyledPilImage for the drawer (rounded/circle)
    # but handle colors via our manual recolor for better reliability
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer
    ).convert("RGBA")

    # Manual Recolor (Ensures the colors we picked are exactly applied)
    data = img.getdata()
    fg = _hex_to_rgb(fg_color)
    bg = _hex_to_rgb(bg_color)
    new_data = []
    
    for item in data:
        # StyledPilImage returns pixels where 0 is dark and 255 is light
        # We check the R channel (item[0])
        if item[0] < 128:
            new_data.append(fg + (255,))
        else:
            new_data.append(bg + (255,))
    
    img.putdata(new_data)
    img = img.convert("RGB") # Final save as RGB to keep file small

    # Save PNG
    filename = f"qr_{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    png_path  = os.path.join(UPLOAD_FOLDER, f"{filename}.png")
    img.save(png_path, "PNG")

    # Relative path for DB storage
    rel_png = f"qr_codes/{filename}.png"

    qr_record = QRCode(
        user_id=user.id,
        name=name,
        target_url=target_url,
        style_config=style_config,
        file_path_png=rel_png,
    )
    db.session.add(qr_record)

    # Increment quota
    now = datetime.utcnow()
    quota = QuotaUsage.query.filter_by(user_id=user.id, year=now.year, month=now.month).first()
    if quota:
        quota.qrcodes_used += 1

    db.session.commit()
    return qr_record, None


def _hex_to_rgb(hex_color: str) -> tuple:
    """Helper to convert #RRGGBB or #RGB to (R, G, B)."""
    try:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c*2 for c in hex_color])
        if len(hex_color) != 6:
            return (0, 0, 0) # Fallback to black
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (0, 0, 0) # Fallback to black if anything goes wrong
