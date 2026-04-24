"""Generate a styled QR code linking to the resume URL declared in the config.

CLI:
    uv run python scripts/generate_qr_code.py --config options.yml --project-root .
"""

import argparse
import sys
from pathlib import Path

import PIL
import qrcode
import requests
from PIL import Image, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options

CORNER_RADIUS = 100
DOWNLOADS_SUBDIR = "assets/downloads"  # relative to project_root, fetched images land here
ROUNDED_LOGO_FILENAME = "rounded-logo.png"


def add_corners(im: Image.Image, rad: int) -> Image.Image:
    """Add rounded corners to an image (in-place alpha mask)."""
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def style_inner_eyes(img: Image.Image) -> Image.Image:
    """Mask for the inner finder-pattern squares."""
    img_size = img.size[0]
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((60, 60, 90, 90), fill=255)
    draw.rectangle((img_size - 90, 60, img_size - 60, 90), fill=255)
    draw.rectangle((60, img_size - 90, 90, img_size - 60), fill=255)
    return mask


def style_outer_eyes(img: Image.Image) -> Image.Image:
    """Mask for the outer finder-pattern rings."""
    img_size = img.size[0]
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((40, 40, 110, 110), fill=255)
    draw.rectangle((img_size - 110, 40, img_size - 40, 110), fill=255)
    draw.rectangle((40, img_size - 110, 110, img_size - 40), fill=255)
    draw.rectangle((60, 60, 90, 90), fill=0)
    draw.rectangle((img_size - 90, 60, img_size - 60, 90), fill=0)
    draw.rectangle((60, img_size - 90, 90, img_size - 60), fill=0)
    return mask


def fetch_remote_image(url: str, dest: Path) -> None:
    """Download an image from url to dest (creating parents)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    dest.write_bytes(response.content)


def prepare_logo(image_source: str, project_root: Path) -> Path:
    """Resolve the logo: local path or remote URL. Returns path to the rounded-corner logo."""
    if image_source.startswith(("http://", "https://")):
        downloads = project_root / DOWNLOADS_SUBDIR
        downloaded = downloads / Path(image_source).name
        fetch_remote_image(image_source, downloaded)
        source_img = downloaded
        rounded = downloads / ROUNDED_LOGO_FILENAME
    else:
        source_img = project_root / image_source
        rounded = source_img.parent / ROUNDED_LOGO_FILENAME

    im = Image.open(source_img)
    im = im.crop((0, 0, min(im.size), min(im.size)))  # square-crop
    im = add_corners(im, CORNER_RADIUS)
    im.save(rounded)
    return rounded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate styled QR code for the resume URL.")
    parser.add_argument("--config", default="options.yml")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)

    # PIL.Image.Resampling compat shim for older Pillow
    if not hasattr(PIL.Image, "Resampling"):
        PIL.Image.Resampling = PIL.Image

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)

    logo_path = prepare_logo(cfg["image_source"], project_root)
    color_panel = tuple(cfg["color_panel"])
    resume_url = cfg["resume_url"]
    qr_output = project_root / cfg["paths"]["qr_output"]
    qr_output.parent.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(resume_url)

    # qrcode 8.x wraps the PIL image; unwrap via .get_image() for PIL ops below.
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path=str(logo_path),
    ).get_image()
    qr_inner = qr.make_image(
        image_factory=StyledPilImage,
        eye_drawer=RoundedModuleDrawer(radius_ratio=0.9),
        color_mask=SolidFillColorMask(front_color=color_panel),
    ).get_image()
    qr_outer = qr.make_image(
        image_factory=StyledPilImage,
        eye_drawer=RoundedModuleDrawer(radius_ratio=0.9),
    ).get_image()

    intermediate = Image.composite(qr_inner, qr_img, style_inner_eyes(qr_img))
    final = Image.composite(qr_outer, intermediate, style_outer_eyes(qr_img))
    final.save(qr_output)

    print(f"QR code → {qr_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
