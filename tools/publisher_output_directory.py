"""Create publisher-source output directories without following filesystem links.

Ingesters operate on locally captured private source material.  Directory
creation must obey the same fail-closed boundary as their descriptor-pinned
atomic file writes, including when an ancestor is replaced by a symlink.
"""

from __future__ import annotations

import os
from pathlib import Path


def ensure_directory(root: Path, relative: Path) -> None:
    """Ensure a directory beneath a pinned, symlink-free checkout root.

    Every existing component is opened with O_DIRECTORY | O_NOFOLLOW; each
    missing component is made relative to the already-open parent descriptor.
    This never calls Path.mkdir through an unchecked ancestor.  On platforms
    without these primitives, ingestion fails before changing any directory.
    """
    root = Path(root)
    relative = Path(relative)
    if (not root.is_absolute() or not relative.parts or relative.is_absolute() or
            any(part in (".", "..", "") for part in relative.parts)):
        raise ValueError("unsafe publisher source directory path")
    if (not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY") or
            os.open not in os.supports_dir_fd or os.mkdir not in os.supports_dir_fd):
        raise ValueError("platform lacks safe no-follow directory primitives")

    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(root.anchor, flags)
    try:
        # The checkout root must already exist. Never create its ancestors.
        for part in root.parts[1:]:
            if part in (".", "..", ""):
                raise ValueError("unsafe checkout path component")
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        for part in relative.parts:
            try:
                os.mkdir(part, dir_fd=descriptor)
            except FileExistsError:
                pass
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    finally:
        os.close(descriptor)
