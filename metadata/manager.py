from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class MetadataError(RuntimeError):
    """Raised when metadata operations fail."""


@dataclass
class UnifiedMetadata:
    """Unified user-facing metadata model for Explorer-compatible fields."""

    title: str | None = None
    subject: str | None = None
    tags: list[str] = field(default_factory=list)
    rating: int | None = None
    comments: str | None = None
    author: str | None = None
    copyright_text: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "UnifiedMetadata":
        tags = value.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        return cls(
            title=_clean_text(value.get("title")),
            subject=_clean_text(value.get("subject")),
            tags=[t for t in (_clean_text(t) for t in tags) if t],
            rating=_normalize_rating(value.get("rating")),
            comments=_clean_text(value.get("comments")),
            author=_clean_text(value.get("author") or value.get("artist")),
            copyright_text=_clean_text(value.get("copyright") or value.get("copyright_text")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subject": self.subject,
            "tags": list(self.tags),
            "rating": self.rating,
            "comments": self.comments,
            "author": self.author,
            "copyright": self.copyright_text,
        }


class MetadataManager:
    """Read/write metadata using ExifTool with cross-platform tag redundancy."""

    def __init__(self, exiftool_path: str | Path | None = None):
        self.exiftool_path = self._resolve_exiftool(exiftool_path)

    @property
    def available(self) -> bool:
        return self.exiftool_path is not None

    def ensure_available(self) -> None:
        if self.exiftool_path is None:
            raise MetadataError(
                "ExifTool executable not found. Expected exiftool in PATH, "
                "or bundled at tools/exiftool.exe for Windows builds."
            )

    def read_metadata(self, image_path: str | Path) -> UnifiedMetadata:
        self.ensure_available()
        path = Path(image_path)
        if not path.exists():
            raise MetadataError(f"File not found: {path}")

        payload = self._run(["-j", "-n", "-G1", str(path)])
        try:
            row = json.loads(payload)[0]
        except Exception as exc:  # pragma: no cover - defensive
            raise MetadataError(f"Failed to parse metadata output: {exc}") from exc

        xmp_subject = _to_list(self._pick(row, ["XMP-dc:Subject", "XMP:Subject"]))
        windows_subject = _clean_text(self._pick(row, ["IFD0:XPSubject", "EXIF:XPSubject"]))
        windows_keywords = _to_list(self._pick(row, ["IFD0:XPKeywords", "EXIF:XPKeywords"]))

        title = _clean_text(
            self._pick(
                row,
                [
                    "XMP-dc:Title",
                    "XMP:Title",
                    "IFD0:XPTitle",
                    "EXIF:ImageDescription",
                    "EXIF:XPTitle",
                ],
            )
        )

        # Windows keeps Subject and Keywords separate, while many Linux tools
        # display XMP:Subject as keywords. Prefer keyword-style fields for tags.
        tags = xmp_subject or windows_keywords
        subject = windows_subject
        if not subject and xmp_subject and not windows_keywords and len(xmp_subject) == 1:
            subject = xmp_subject[0]

        return UnifiedMetadata(
            title=title,
            subject=subject,
            tags=tags,
            rating=_normalize_rating(self._pick(row, ["XMP-xmp:Rating", "XMP:Rating", "IFD0:Rating", "EXIF:Rating"])),
            comments=_clean_text(self._pick(row, ["IFD0:XPComment", "EXIF:XPComment", "ExifIFD:UserComment", "EXIF:UserComment"])),
            author=_clean_text(self._pick(row, ["XMP-dc:Creator", "IFD0:Artist", "EXIF:Artist", "IFD0:XPAuthor", "EXIF:XPAuthor"])),
            copyright_text=_clean_text(self._pick(row, ["XMP-dc:Rights", "IFD0:Copyright", "EXIF:Copyright"])),
        )

    def get_raw_metadata(self, image_path: str | Path) -> dict[str, Any]:
        """Return full grouped metadata row from ExifTool for diagnostics."""
        self.ensure_available()
        path = Path(image_path)
        if not path.exists():
            raise MetadataError(f"File not found: {path}")

        payload = self._run(["-j", "-n", "-G1", str(path)])
        try:
            rows = json.loads(payload)
            return rows[0] if rows else {}
        except Exception as exc:  # pragma: no cover - defensive
            raise MetadataError(f"Failed to parse metadata output: {exc}") from exc

    def write_metadata(
        self,
        image_path: str | Path,
        metadata: UnifiedMetadata | dict[str, Any],
        output_path: str | Path | None = None,
    ) -> Path:
        self.ensure_available()
        path = Path(image_path)
        if not path.exists():
            raise MetadataError(f"File not found: {path}")

        data = metadata if isinstance(metadata, UnifiedMetadata) else UnifiedMetadata.from_dict(metadata)
        args = ["-P"]

        if data.title is not None:
            args.extend([
                f"-XMP-dc:Title={data.title}",
                f"-XMP-dc:Description={data.title}",
                f"-IFD0:ImageDescription={data.title}",
                f"-IFD0:XPTitle={data.title}",
            ])

        if data.subject is not None:
            args.extend([
                f"-IFD0:XPSubject={data.subject}",
                f"-XMP-photoshop:Headline={data.subject}",
                f"-IPTC:ObjectName={data.subject}",
            ])

        unique_tags = []
        for tag in data.tags:
            if tag not in unique_tags:
                unique_tags.append(tag)

        # Keep XMP Subject for keywords/tags so Linux viewers match Windows edits.
        if unique_tags:
            args.append("-XMP-dc:Subject=")
            for value in unique_tags:
                args.append(f"-XMP-dc:Subject+={value}")

            args.append("-IPTC:Keywords=")
            for value in unique_tags:
                args.append(f"-IPTC:Keywords+={value}")
        elif data.subject:
            args.extend([
                "-XMP-dc:Subject=",
                f"-XMP-dc:Subject+={data.subject}",
            ])

        if unique_tags:
            args.append(f"-IFD0:XPKeywords={';'.join(unique_tags)}")
            args.append(f"-XMP-microsoft:LastKeywordXMP={unique_tags[-1]}")

        if data.author is not None:
            args.extend([
                f"-XMP-dc:Creator={data.author}",
                f"-IFD0:Artist={data.author}",
                f"-IFD0:XPAuthor={data.author}",
            ])

        if data.comments is not None:
            args.extend([
                f"-ExifIFD:UserComment={data.comments}",
                f"-IFD0:XPComment={data.comments}",
            ])

        if data.rating is not None:
            percent = _rating_to_percent(data.rating)
            args.extend([
                f"-XMP-xmp:Rating={data.rating}",
                f"-XMP:Rating={data.rating}",
                f"-IFD0:Rating={data.rating}",
                f"-IFD0:RatingPercent={percent}",
                f"-XMP-microsoft:RatingPercent={percent}",
            ])

        if data.copyright_text is not None:
            args.extend([
                f"-XMP-dc:Rights={data.copyright_text}",
                f"-IFD0:Copyright={data.copyright_text}",
            ])

        if not args or args == ["-P"]:
            return path if output_path is None else Path(output_path)

        if output_path:
            out_path = Path(output_path)
            args.extend(["-o", str(out_path)])
        else:
            out_path = path
            args.append("-overwrite_original")

        args.append(str(path))
        self._run(args)
        return out_path

    def _run(self, args: list[str]) -> str:
        if self.exiftool_path is None:
            raise MetadataError("ExifTool path is not configured.")

        cmd = [self.exiftool_path, "-charset", "filename=utf8", *args]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout).strip()
            raise MetadataError(err or f"ExifTool failed with exit code {result.returncode}")
        return result.stdout

    @staticmethod
    def _pick(row: dict[str, Any], candidates: list[str]) -> Any:
        if not row:
            return None
        lower = {k.lower(): v for k, v in row.items()}
        for candidate in candidates:
            value = lower.get(candidate.lower())
            if value not in (None, "", []):
                return value
        return None

    @staticmethod
    def _resolve_exiftool(custom_path: str | Path | None) -> str | None:
        candidates: list[Path] = []
        if custom_path:
            candidates.append(Path(custom_path))

        env_path = os.environ.get("EXIFTOOL_PATH")
        if env_path:
            candidates.append(Path(env_path))

        if getattr(sys, "frozen", False):
            meipass = Path(getattr(sys, "_MEIPASS", Path.cwd()))
            candidates.extend(
                [
                    meipass / "tools" / "exiftool.exe",
                    meipass / "exiftool.exe",
                ]
            )

        base = Path(__file__).resolve().parent.parent
        candidates.extend(
            [
                base / "tools" / "exiftool.exe",
                base / "exiftool.exe",
            ]
        )

        if os.name == "nt":
            candidates.append(Path.home() / "AppData" / "Local" / "Programs" / "ExifTool" / "ExifTool.exe")

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return str(candidate)

        for binary_name in ("exiftool", "exiftool.exe"):
            found = shutil.which(binary_name)
            if found:
                return found

        return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    text = str(value).strip()
    return text or None


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [v.strip() for v in (str(x) for x in value) if v.strip()]

    text = str(value).strip()
    if not text:
        return []

    for sep in (";", ",", "|"):
        if sep in text:
            return [item.strip() for item in text.split(sep) if item.strip()]
    return [text]


def _normalize_rating(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        rating = int(float(value))
    except (TypeError, ValueError):
        return None
    if rating < 1:
        return 1
    if rating > 5:
        return 5
    return rating


def _rating_to_percent(rating: int) -> int:
    mapping = {1: 1, 2: 25, 3: 50, 4: 75, 5: 99}
    return mapping.get(rating, 0)
