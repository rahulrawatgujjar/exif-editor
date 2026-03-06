#!/usr/bin/env python3
"""
Image EXIF / Metadata Editor
-----------------------------
View, edit, clear, copy, export, and import EXIF metadata for JPEG images.

Usage:
  python exif_editor.py view   image.jpg
  python exif_editor.py edit   image.jpg [--field value ...]
  python exif_editor.py clear  image.jpg [--output out.jpg]
  python exif_editor.py copy   source.jpg target.jpg
  python exif_editor.py export image.jpg  [-o metadata.json]
  python exif_editor.py import image.jpg  -i metadata.json  [-o out.jpg]
  python exif_editor.py gps    image.jpg  --lat LAT --lon LON [--alt ALT]

Requires:
  pip install Pillow piexif
"""

import argparse
import json
import random
import sys
import struct
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

try:
    from PIL import Image
    import piexif
    from piexif import TAGS
except ImportError:
    print("Missing dependencies. Install with:\n  pip install Pillow piexif")
    sys.exit(1)

from camera_presets import CAMERA_PRESETS


# ---------------------------------------------------------------------------
# Tag name lookups (human-readable name -> (IFD, tag_id))
# ---------------------------------------------------------------------------

EDITABLE_TAGS = {
    # 0th IFD (image/camera info)
    "make":               ("0th",  piexif.ImageIFD.Make),
    "model":              ("0th",  piexif.ImageIFD.Model),
    "orientation":        ("0th",  piexif.ImageIFD.Orientation),
    "software":           ("0th",  piexif.ImageIFD.Software),
    "datetime":           ("0th",  piexif.ImageIFD.DateTime),
    "artist":             ("0th",  piexif.ImageIFD.Artist),
    "copyright":          ("0th",  piexif.ImageIFD.Copyright),
    "image_description":  ("0th",  piexif.ImageIFD.ImageDescription),
    "x_resolution":       ("0th",  piexif.ImageIFD.XResolution),
    "y_resolution":       ("0th",  piexif.ImageIFD.YResolution),
    # Exif IFD
    "datetime_original":  ("Exif", piexif.ExifIFD.DateTimeOriginal),
    "datetime_digitized": ("Exif", piexif.ExifIFD.DateTimeDigitized),
    "user_comment":       ("Exif", piexif.ExifIFD.UserComment),
    "image_unique_id":    ("Exif", piexif.ExifIFD.ImageUniqueID),
    "lens_make":          ("Exif", piexif.ExifIFD.LensMake),
    "lens_model":         ("Exif", piexif.ExifIFD.LensModel),
    "iso":                ("Exif", piexif.ExifIFD.ISOSpeedRatings),
    "focal_length":       ("Exif", piexif.ExifIFD.FocalLength),
    "f_number":           ("Exif", piexif.ExifIFD.FNumber),
    "exposure_time":      ("Exif", piexif.ExifIFD.ExposureTime),
    "flash":              ("Exif", piexif.ExifIFD.Flash),
    "color_space":        ("Exif", piexif.ExifIFD.ColorSpace),
    "pixel_x_dimension":  ("Exif", piexif.ExifIFD.PixelXDimension),
    "pixel_y_dimension":  ("Exif", piexif.ExifIFD.PixelYDimension),
}

# Tags that store plain text (ASCII / bytes)
STRING_TAGS = {
    "make", "model", "software", "datetime", "artist", "copyright",
    "image_description", "datetime_original", "datetime_digitized",
    "image_unique_id", "lens_make", "lens_model",
}

# Tags that store a single integer
INT_TAGS = {"orientation", "iso", "flash", "color_space",
            "pixel_x_dimension", "pixel_y_dimension"}

# Tags that store a rational (numerator, denominator) tuple
RATIONAL_TAGS = {"focal_length", "f_number", "exposure_time",
                 "x_resolution", "y_resolution"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_exif(image_path: Path) -> dict:
    """Load EXIF dict from a JPEG, return empty scaffold if none exists."""
    try:
        exif_bytes = Image.open(image_path).info.get("exif", b"")
        if exif_bytes:
            return piexif.load(exif_bytes)
    except Exception:
        pass
    return {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}


def save_exif(image_path: Path, exif_dict: dict, output_path: Path | None = None):
    """Write the modified EXIF back into the image (in-place or to output_path)."""
    target = output_path or image_path
    img = Image.open(image_path)
    exif_bytes = piexif.dump(exif_dict)
    img.save(target, exif=exif_bytes)
    print(f"Saved: {target}")


def decode_value(val):
    """Return a human-readable Python object from a raw piexif value."""
    if isinstance(val, bytes):
        # UserComment has a charset prefix (8 bytes)
        if len(val) > 8 and val[:8] in (b"ASCII\x00\x00\x00", b"UNICODE\x00", b"\x00" * 8):
            return val[8:].decode("utf-8", errors="replace").rstrip("\x00")
        return val.decode("utf-8", errors="replace").rstrip("\x00")
    if isinstance(val, tuple):
        if len(val) == 2 and all(isinstance(v, int) for v in val):
            return f"{val[0]}/{val[1]}"  # rational
        return list(val)
    return val


def tag_name(ifd_name: str, tag_id: int) -> str:
    """Return the tag name string, falling back to the numeric ID."""
    try:
        return TAGS[ifd_name][tag_id]["name"]
    except (KeyError, TypeError):
        return str(tag_id)


def encode_string(value: str) -> bytes:
    return value.encode("utf-8")


def encode_user_comment(value: str) -> bytes:
    return b"ASCII\x00\x00\x00" + value.encode("utf-8")


def parse_rational(value: str) -> tuple:
    """Parse '1/100' or '3.5' into a (num, denom) rational tuple."""
    if "/" in value:
        num, denom = value.split("/", 1)
        return (int(num.strip()), int(denom.strip()))
    f = float(value)
    # Convert float to a reasonable rational
    denom = 1000
    return (int(f * denom), denom)


def decdeg_to_dms_rational(dd: float) -> list:
    """Convert decimal degrees to [(deg,1),(min,1),(sec*100,100)] rationals."""
    dd = abs(dd)
    degrees = int(dd)
    minutes = int((dd - degrees) * 60)
    seconds = round(((dd - degrees) * 60 - minutes) * 60 * 100)
    return [(degrees, 1), (minutes, 1), (seconds, 100)]




def random_datetime(days_back: int = 365) -> str:
    """Return a random EXIF datetime string within the last N days."""
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(6, 20),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    dt = datetime.now() - delta
    return dt.strftime("%Y:%m:%d %H:%M:%S")


# Extensions treated as JPEG-compatible by piexif
JPEG_EXTS = {".jpg", ".jpeg", ".jpe", ".jfif"}


def geocode_city(city_name: str) -> tuple[float, float]:
    """
    Return (lat, lon) for a city/place name using OpenStreetMap Nominatim.
    No API key required; respects the 1-req/s usage policy.
    """
    query = urllib.parse.urlencode({"q": city_name, "format": "json", "limit": "1"})
    url   = f"https://nominatim.openstreetmap.org/search?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "exif_editor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        sys.exit(f"Geocoding failed: {e}")
    if not data:
        sys.exit(f"Location not found: {city_name!r}")
    return float(data[0]["lat"]), float(data[0]["lon"])


def jitter_coords(lat: float, lon: float, max_meters: float = 500) -> tuple[float, float]:
    """
    Add a small random offset to coordinates so each image in a batch
    appears to be taken at a slightly different spot within the city.
    Default spread: ±500 m  (~0.0045°)
    """
    import math
    delta_deg = max_meters / 111_000          # rough metres-per-degree
    lat += random.uniform(-delta_deg, delta_deg)
    lon += random.uniform(-delta_deg, delta_deg) / max(math.cos(math.radians(lat)), 0.01)
    return round(lat, 6), round(lon, 6)


def _apply_fake_to_file(src: Path, dst: Path, args, p: dict,
                         lat: float | None = None,
                         lon: float | None = None) -> dict:
    """
    Core helper: build fake EXIF from preset `p` and write it into `src`,
    saving the result to `dst`.  Returns a dict with the applied values
    so the caller can print a summary.
    lat/lon override args.lat/args.lon when provided.
    """
    exif = load_exif(src)

    # --- Pick lens (always random so each image in a batch differs) ---
    lens_name, focal_mm, base_fnumber, fnumber_pool = random.choice(p["lenses"])

    # --- Exposure settings ---
    if args.random:
        iso     = random.choice(p["iso_pool"])
        shutter = random.choice(p["shutter_pool"])
        fnumber = random.choice(fnumber_pool)
    else:
        iso     = p["iso_pool"][len(p["iso_pool"]) // 2]
        shutter = (1, 250)
        fnumber = base_fnumber

    # --- Timestamp (always per-file random unless --datetime was fixed) ---
    ts = args.datetime or random_datetime(days_back=args.days_back)

    # --- 0th IFD ---
    exif["0th"] = {
        piexif.ImageIFD.Make:             encode_string(p["make"]),
        piexif.ImageIFD.Model:            encode_string(p["model"]),
        piexif.ImageIFD.Orientation:      1,
        piexif.ImageIFD.XResolution:      (72, 1),
        piexif.ImageIFD.YResolution:      (72, 1),
        piexif.ImageIFD.ResolutionUnit:   2,
        piexif.ImageIFD.Software:         encode_string(p["software"]),
        piexif.ImageIFD.DateTime:         encode_string(ts),
        piexif.ImageIFD.YCbCrPositioning: 1,
    }
    if args.artist:
        exif["0th"][piexif.ImageIFD.Artist]          = encode_string(args.artist)
    if args.copyright:
        exif["0th"][piexif.ImageIFD.Copyright]        = encode_string(args.copyright)
    if args.title:
        exif["0th"][piexif.ImageIFD.ImageDescription] = encode_string(args.title)

    # --- Exif IFD ---
    exif["Exif"] = {
        piexif.ExifIFD.ExposureTime:      shutter,
        piexif.ExifIFD.FNumber:           fnumber,
        piexif.ExifIFD.ISOSpeedRatings:   iso,
        piexif.ExifIFD.DateTimeOriginal:  encode_string(ts),
        piexif.ExifIFD.DateTimeDigitized: encode_string(ts),
        piexif.ExifIFD.ShutterSpeedValue: shutter,
        piexif.ExifIFD.ApertureValue:     fnumber,
        piexif.ExifIFD.Flash:             0,
        piexif.ExifIFD.FocalLength:       (focal_mm, 1),
        piexif.ExifIFD.ColorSpace:        1,
        piexif.ExifIFD.LensMake:          encode_string(p["lens_make"]),
        piexif.ExifIFD.LensModel:         encode_string(lens_name),
    }
    if args.comment:
        exif["Exif"][piexif.ExifIFD.UserComment] = encode_user_comment(args.comment)
    if args.description:
        exif["Exif"][piexif.ExifIFD.UserComment] = encode_user_comment(args.description)

    # --- GPS IFD (optional) ---
    # Prefer explicit lat/lon args passed to this function, fall back to CLI args
    _lat = lat if lat is not None else args.lat
    _lon = lon if lon is not None else args.lon
    if _lat is not None and _lon is not None:
        lat, lon = _lat, _lon
        gps = {
            piexif.GPSIFD.GPSVersionID:   (2, 3, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef:  b"N" if lat >= 0 else b"S",
            piexif.GPSIFD.GPSLatitude:     decdeg_to_dms_rational(lat),
            piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
            piexif.GPSIFD.GPSLongitude:    decdeg_to_dms_rational(lon),
        }
        if args.alt is not None:
            alt_v = float(args.alt)
            gps[piexif.GPSIFD.GPSAltitudeRef] = 0 if alt_v >= 0 else 1
            gps[piexif.GPSIFD.GPSAltitude]    = (int(abs(alt_v) * 100), 100)
        exif["GPS"] = gps

    save_exif(src, exif, dst)
    return {"lens": lens_name, "iso": iso, "shutter": shutter,
            "fnumber": fnumber, "ts": ts,
            "lat": _lat, "lon": _lon}


def _resolve_preset(preset_key: str) -> tuple[str, dict]:
    """Return (key, preset_dict). If key is 'random', pick one at random."""
    if preset_key == "random":
        preset_key = random.choice(list(CAMERA_PRESETS.keys()))
    elif preset_key not in CAMERA_PRESETS:
        sys.exit(f"Unknown preset '{preset_key}'. "
                 f"Available: random, {', '.join(CAMERA_PRESETS)}.")
    return preset_key, CAMERA_PRESETS[preset_key]


def cmd_fake(args):
    """Apply a full fake camera EXIF profile — single file or whole folder."""
    input_path = Path(args.image)
    use_random_preset = (args.preset == "random")

    # Validate preset name early (unless it's 'random')
    if not use_random_preset and args.preset not in CAMERA_PRESETS:
        sys.exit(f"Unknown preset '{args.preset}'. "
                 f"Available: random, {', '.join(CAMERA_PRESETS)}.")

    # ----------------------------------------------------------------- coords
    # Priority: --lat/--lon  >  --city  >  no GPS
    base_lat = base_lon = None
    if args.lat is not None and args.lon is not None:
        base_lat, base_lon = args.lat, args.lon
    elif args.city:
        print(f"Geocoding '{args.city}' ...", flush=True)
        base_lat, base_lon = geocode_city(args.city)
        print(f"  → {base_lat:.6f}, {base_lon:.6f}")

    # ------------------------------------------------------------------ batch
    if input_path.is_dir():
        out_dir = Path(args.output_dir) if args.output_dir else input_path / "output"
        out_dir.mkdir(parents=True, exist_ok=True)

        images = sorted(
            f for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in JPEG_EXTS
        )
        if not images:
            sys.exit(f"No JPEG images found in: {input_path}")

        print(f"Preset  : {args.preset}")
        print(f"Input   : {input_path}  ({len(images)} images)")
        print(f"Output  : {out_dir}")
        if base_lat is not None:
            print(f"Location: {base_lat:.6f}, {base_lon:.6f}  (±500 m jitter per image)")
        print("-" * 60)

        ok, skipped = 0, 0
        for i, src in enumerate(images, 1):
            dst = out_dir / src.name
            chosen_key, p = _resolve_preset(args.preset)
            # Apply small random offset so each image has a unique nearby GPS point
            img_lat = img_lon = None
            if base_lat is not None:
                img_lat, img_lon = jitter_coords(base_lat, base_lon)
            try:
                info = _apply_fake_to_file(src, dst, args, p,
                                           lat=img_lat, lon=img_lon)
                gps_str = (f"  GPS={info['lat']:.5f},{info['lon']:.5f}"
                           if info["lat"] is not None else "")
                print(f"  [{i:>3}/{len(images)}] {src.name}")
                print(f"         camera={p['make']} {p['model']}  "
                      f"lens={info['lens']}  ISO={info['iso']}  "
                      f"1/{info['shutter'][1]}s  "
                      f"f/{info['fnumber'][0]/info['fnumber'][1]:.1f}  "
                      f"{info['ts']}{gps_str}")
                ok += 1
            except Exception as e:
                print(f"  [{i:>3}/{len(images)}] SKIP {src.name}  ({e})")
                skipped += 1

        print("-" * 60)
        print(f"Done: {ok} processed, {skipped} skipped.")
        return

    # ----------------------------------------------------------------- single
    if not input_path.exists():
        sys.exit(f"File not found: {input_path}")

    chosen_key, p = _resolve_preset(args.preset)

    if args.output_dir and not args.output:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / input_path.name
    elif args.output:
        dst = Path(args.output)
    else:
        dst = None   # overwrite in place

    info = _apply_fake_to_file(input_path, dst or input_path, args, p,
                                lat=base_lat, lon=base_lon)
    print(f"  Preset    : {chosen_key}")
    print(f"  Camera    : {p['make']} {p['model']}")
    print(f"  Lens      : {info['lens']}")
    print(f"  ISO       : {info['iso']}")
    print(f"  Shutter   : 1/{info['shutter'][1]}s")
    print(f"  Aperture  : f/{info['fnumber'][0]/info['fnumber'][1]:.1f}")
    print(f"  Timestamp : {info['ts']}")
    if info["lat"] is not None:
        print(f"  GPS       : {info['lat']:.6f}, {info['lon']:.6f}")
    if args.title:
        print(f"  Title     : {args.title}")
    if args.description:
        print(f"  Desc      : {args.description}")
    if args.artist:
        print(f"  Artist    : {args.artist}")


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def cmd_view(args):
    """Print all EXIF metadata in a readable format."""
    path = Path(args.image)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    exif = load_exif(path)
    ifd_labels = {
        "0th":    "Image IFD (0th)",
        "Exif":   "Exif IFD",
        "GPS":    "GPS IFD",
        "Interop":"Interoperability IFD",
        "1st":    "Thumbnail IFD (1st)",
    }

    print(f"\n{'='*55}")
    print(f"  EXIF Metadata: {path.name}")
    print(f"{'='*55}")

    found_any = False
    for ifd_key, label in ifd_labels.items():
        ifd_data = exif.get(ifd_key, {})
        if not ifd_data:
            continue
        found_any = True
        print(f"\n[{label}]")
        for tag_id, raw_val in ifd_data.items():
            name = tag_name(ifd_key, tag_id)
            display = decode_value(raw_val)
            print(f"  {name:<35} {display}")

    if not found_any:
        print("\n  (No EXIF metadata found)")
    print()


def cmd_edit(args):
    """Set one or more EXIF fields by name."""
    path = Path(args.image)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    exif = load_exif(path)
    updates = vars(args)  # all parsed args as a dict

    changed = 0
    for field, (ifd, tag_id) in EDITABLE_TAGS.items():
        value = updates.get(field)
        if value is None:
            continue

        if field in STRING_TAGS:
            encoded = encode_string(value)
        elif field == "user_comment":
            encoded = encode_user_comment(value)
        elif field in INT_TAGS:
            encoded = int(value)
        elif field in RATIONAL_TAGS:
            encoded = parse_rational(value)
        else:
            encoded = value  # fallback: pass as-is

        exif[ifd][tag_id] = encoded
        print(f"  Set [{ifd}] {field} = {value!r}")
        changed += 1

    if changed == 0:
        print("No fields specified. Use --help to see available options.")
        return

    output = Path(args.output) if args.output else None
    save_exif(path, exif, output)


def cmd_clear(args):
    """Remove all EXIF metadata from the image."""
    path = Path(args.image)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    empty_exif = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}
    output = Path(args.output) if args.output else None
    save_exif(path, empty_exif, output)
    print("All EXIF metadata cleared.")


def cmd_copy(args):
    """Copy all EXIF metadata from source image to target image."""
    src = Path(args.source)
    dst = Path(args.target)
    for p in (src, dst):
        if not p.exists():
            sys.exit(f"File not found: {p}")

    exif = load_exif(src)
    save_exif(dst, exif)
    print(f"EXIF copied from {src.name} → {dst.name}")


def cmd_export(args):
    """Export EXIF metadata to a JSON file."""
    path = Path(args.image)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    exif = load_exif(path)
    output_path = Path(args.output) if args.output else path.with_suffix(".exif.json")

    # Build a serialisable dict
    serial = {}
    for ifd_key, ifd_data in exif.items():
        serial[ifd_key] = {}
        for tag_id, raw_val in ifd_data.items():
            name = tag_name(ifd_key, tag_id)
            serial[ifd_key][name] = decode_value(raw_val)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serial, f, indent=2, ensure_ascii=False)
    print(f"Exported metadata to: {output_path}")


def cmd_import(args):
    """
    Import EXIF metadata from a JSON file previously exported by this tool.
    Only the string/integer fields in EDITABLE_TAGS are restored.
    """
    path = Path(args.image)
    json_path = Path(args.input)
    for p in (path, json_path):
        if not p.exists():
            sys.exit(f"File not found: {p}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    exif = load_exif(path)

    # Build reverse lookup: tag name -> (ifd, tag_id, type)
    reverse = {}
    for field, (ifd, tag_id) in EDITABLE_TAGS.items():
        name = tag_name(ifd, tag_id)
        reverse[name] = (ifd, tag_id, field)

    for ifd_key, tags in data.items():
        for tag_name_str, value in tags.items():
            if tag_name_str not in reverse:
                continue
            ifd, tag_id, field = reverse[tag_name_str]
            if field in STRING_TAGS:
                exif[ifd][tag_id] = encode_string(str(value))
            elif field == "user_comment":
                exif[ifd][tag_id] = encode_user_comment(str(value))
            elif field in INT_TAGS:
                exif[ifd][tag_id] = int(value)
            elif field in RATIONAL_TAGS:
                exif[ifd][tag_id] = parse_rational(str(value))

    output = Path(args.output) if args.output else None
    save_exif(path, exif, output)
    print(f"Imported metadata from: {json_path}")


def cmd_gps(args):
    """Embed GPS coordinates (and optional altitude) into the image."""
    path = Path(args.image)
    if not path.exists():
        sys.exit(f"File not found: {path}")

    lat, lon = args.lat, args.lon
    exif = load_exif(path)

    gps = {
        piexif.GPSIFD.GPSVersionID:  (2, 3, 0, 0),
        piexif.GPSIFD.GPSLatitudeRef:  b"N" if lat >= 0 else b"S",
        piexif.GPSIFD.GPSLatitude:     decdeg_to_dms_rational(lat),
        piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
        piexif.GPSIFD.GPSLongitude:    decdeg_to_dms_rational(lon),
    }

    if args.alt is not None:
        alt = float(args.alt)
        gps[piexif.GPSIFD.GPSAltitudeRef] = 0 if alt >= 0 else 1
        gps[piexif.GPSIFD.GPSAltitude]    = (int(abs(alt) * 100), 100)

    exif["GPS"] = gps

    output = Path(args.output) if args.output else None
    save_exif(path, exif, output)

    ref_lat = "N" if lat >= 0 else "S"
    ref_lon = "E" if lon >= 0 else "W"
    print(f"GPS set: {abs(lat):.6f}°{ref_lat}, {abs(lon):.6f}°{ref_lon}"
          + (f", alt {args.alt}m" if args.alt is not None else ""))


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exif_editor.py",
        description="View and modify EXIF/metadata of JPEG images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- view ---
    p_view = sub.add_parser("view", help="Print all EXIF metadata")
    p_view.add_argument("image", help="Path to the image")

    # --- edit ---
    p_edit = sub.add_parser("edit", help="Set specific EXIF fields")
    p_edit.add_argument("image", help="Path to the image")
    p_edit.add_argument("-o", "--output", metavar="OUT", help="Save to a new file instead of overwriting")
    # Dynamically add one --flag per editable field
    for field in EDITABLE_TAGS:
        flag = f"--{field.replace('_', '-')}"
        p_edit.add_argument(flag, dest=field, metavar="VALUE",
                            help=f"Set the {field} tag")

    # --- clear ---
    p_clear = sub.add_parser("clear", help="Remove all EXIF metadata")
    p_clear.add_argument("image", help="Path to the image")
    p_clear.add_argument("-o", "--output", metavar="OUT", help="Save to a new file")

    # --- copy ---
    p_copy = sub.add_parser("copy", help="Copy EXIF from source to target image")
    p_copy.add_argument("source", help="Image to copy metadata FROM")
    p_copy.add_argument("target", help="Image to copy metadata TO")

    # --- export ---
    p_export = sub.add_parser("export", help="Export metadata to JSON")
    p_export.add_argument("image", help="Path to the image")
    p_export.add_argument("-o", "--output", metavar="JSON", help="Output JSON file (default: <image>.exif.json)")

    # --- import ---
    p_import = sub.add_parser("import", help="Import metadata from a JSON file")
    p_import.add_argument("image", help="Path to the image")
    p_import.add_argument("-i", "--input", required=True, metavar="JSON", help="JSON file to read metadata from")
    p_import.add_argument("-o", "--output", metavar="OUT", help="Save to a new file")

    # --- gps ---
    p_gps = sub.add_parser("gps", help="Set GPS coordinates")
    p_gps.add_argument("image", help="Path to the image")
    p_gps.add_argument("--lat", type=float, required=True, help="Latitude  in decimal degrees (negative = South)")
    p_gps.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees (negative = West)")
    p_gps.add_argument("--alt", type=float, default=None, help="Altitude in meters (optional)")
    p_gps.add_argument("-o", "--output", metavar="OUT", help="Save to a new file")

    # --- fake ---
    preset_list = ", ".join(CAMERA_PRESETS.keys())
    p_fake = sub.add_parser(
        "fake",
        help="Apply a full fake camera EXIF profile",
        description=f"Apply a realistic fake EXIF profile.\nAvailable presets: {preset_list}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_fake.add_argument("image",
        help="Path to the image (or glob pattern with --batch)")
    p_fake.add_argument("-p", "--preset", default="random", metavar="PRESET",
        help=f"Camera preset: random (default), or one of: {preset_list}")
    p_fake.add_argument("-r", "--random", action="store_true",
        help="Randomize exposure settings within the preset's realistic ranges")
    p_fake.add_argument("--days-back", type=int, default=365, metavar="N",
        help="Random timestamp within last N days (default: 365)")
    p_fake.add_argument("--datetime", metavar="YYYY:MM:DD HH:MM:SS",
        help="Fix timestamp instead of randomizing")
    p_fake.add_argument("--title",      metavar="TEXT",  help="Image title (stored as ImageDescription)")
    p_fake.add_argument("--description",metavar="TEXT",  help="Image description (stored as UserComment)")
    p_fake.add_argument("--artist",     metavar="NAME",  help="Photographer name")
    p_fake.add_argument("--copyright",  metavar="TEXT",  help="Copyright string")
    p_fake.add_argument("--comment",    metavar="TEXT",  help="UserComment field (use --description instead)")
    loc_group = p_fake.add_mutually_exclusive_group()
    loc_group.add_argument("--city", metavar="NAME",
        help="City/place name to geocode into GPS coordinates "
             "(e.g. 'Paris', 'New York', 'Tokyo'). "
             "In batch mode each image gets a unique nearby point (±500 m).")
    loc_group.add_argument("--lat", type=float, default=None,
        help="GPS latitude (use with --lon)")
    p_fake.add_argument("--lon",  type=float, default=None, help="GPS longitude (use with --lat)")
    p_fake.add_argument("--alt",  type=float, default=None, help="GPS altitude in meters")
    p_fake.add_argument("-o", "--output", metavar="OUT",
        help="(Single file) save to a new file instead of overwriting")
    p_fake.add_argument("-d", "--output-dir", metavar="DIR",
        help="Output folder for batch mode (default: <input_dir>/output). "
             "Also works for single files.")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "view":   cmd_view,
        "edit":   cmd_edit,
        "clear":  cmd_clear,
        "copy":   cmd_copy,
        "export": cmd_export,
        "import": cmd_import,
        "gps":    cmd_gps,
        "fake":   cmd_fake,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
