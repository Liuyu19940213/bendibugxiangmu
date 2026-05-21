"""
Material library for dynamic few-shot rewrite

Stores rewrite results as plain-text files grouped by book name,
and provides deduplicated selection of reference articles for
few-shot prompting.
"""

import hashlib
import random
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


def _content_hash(text: str) -> str:
    """Generate a content-based hash for deduplication."""
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def _normalize(text: str) -> str:
    """Normalize text by collapsing all whitespace for comparison."""
    return re.sub(r"\s+", "", text or "")


def _safe_dirname(name: str) -> str:
    """Sanitize a book name into a safe directory name."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .") or "未命名"


class MaterialLibrary:
    """File-based material library for storing and retrieving rewrite results.

    Each book gets its own subdirectory under the root. Articles are stored
    as timestamped .txt files with SHA-256 deduplication.

    Attributes:
        root: Root directory path for all material storage.
    """

    def __init__(self, root: str = "./materials") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _book_dir(self, book_name: str) -> Path:
        """Get (and create if needed) the directory for a specific book."""
        path = self.root / _safe_dirname(book_name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, book_name: str, text: str) -> bool:
        """Save a rewrite result for a book.

        Performs deduplication via content hash and sequence similarity.
        Already-existing near-duplicates are silently skipped.

        Args:
            book_name: The book name used as grouping key.
            text: The article text to save.

        Returns:
            True if the article was saved, False if it was a duplicate.
        """
        folder = self._book_dir(book_name)
        new_hash = _content_hash(text)

        for existing in folder.glob("*.txt"):
            try:
                existing_text = existing.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            if _content_hash(existing_text) == new_hash:
                return False

            similarity = SequenceMatcher(
                None, _normalize(text), _normalize(existing_text)
            ).ratio()
            if similarity >= 0.92:
                return False

        filename = f"{datetime.now():%Y-%m-%d_%H%M%S}.txt"
        (folder / filename).write_text(text, encoding="utf-8")
        return True

    def select_references(
        self, book_name: str, max_count: int = 4
    ) -> list[str]:
        """Select up to max_count reference articles for a book.

        If fewer articles exist than max_count, returns all available.
        Otherwise, randomly samples max_count articles.

        Args:
            book_name: The book name to look up.
            max_count: Maximum number of references to return.

        Returns:
            List of article text strings (may be empty).
        """
        folder = self._book_dir(book_name)
        paths = list(folder.glob("*.txt"))
        if len(paths) <= max_count:
            selected = paths
        else:
            selected = random.sample(paths, max_count)
        return [p.read_text(encoding="utf-8") for p in selected]

    def count(self, book_name: str) -> int:
        """Return the number of stored articles for a book."""
        return len(list(self._book_dir(book_name).glob("*.txt")))
