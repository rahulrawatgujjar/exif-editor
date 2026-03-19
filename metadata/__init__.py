"""Metadata abstraction layer for EXIF/XMP/Windows compatibility."""

from .manager import MetadataError, MetadataManager, UnifiedMetadata

__all__ = ["MetadataError", "MetadataManager", "UnifiedMetadata"]
