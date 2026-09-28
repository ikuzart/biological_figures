from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from bfg.ingest.jats import ParsedJATS, parse_jats


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".gif"}


@dataclass
class Figure:
    fig_id: str
    label: str
    caption: str
    image_path: Path


@dataclass
class ExtractedArticle:
    """Article and figures pulled out of a bioRxiv .meca archive."""

    article_id: str
    title: str
    abstract: str
    figures: list[Figure] = field(default_factory=list)
    extract_dir: Path | None = None


def _find_jats_xml(root: Path) -> Path:
    candidates = [p for p in root.rglob("*.xml") if p.is_file()]
    if not candidates:
        raise FileNotFoundError(f"No XML file found in {root}")

    def score(p: Path) -> tuple[int, int]:
        name = p.name.lower()
        parts = [x.lower() for x in p.parts]
        content_dir_bonus = 1 if any("content" in x for x in parts) else 0
        jats_bonus = 1 if "jats" in name or "article" in name else 0
        return (content_dir_bonus + jats_bonus, -len(p.parts))

    candidates.sort(key=score, reverse=True)
    return candidates[0]


def _match_figure_asset(root: Path, jats_href: str | None, fig_id: str) -> Path | None:
    images = [p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES]
    if not images:
        return None
    if jats_href:
        target = Path(jats_href).name
        target_stem = Path(target).stem.lower()
        for p in images:
            if p.name.lower() == target.lower():
                return p
        for p in images:
            if p.stem.lower() == target_stem:
                return p
    if fig_id:
        fid = fig_id.lower()
        for p in images:
            if fid in p.stem.lower():
                return p
    return None


def _promote_figures(jats: ParsedJATS, extract_dir: Path) -> list[Figure]:
    figures: list[Figure] = []
    for ref in jats.figures:
        img = _match_figure_asset(extract_dir, ref.href, ref.fig_id)
        if img is None:
            continue
        figures.append(
            Figure(
                fig_id=ref.fig_id or img.stem,
                label=ref.label,
                caption=ref.caption,
                image_path=img,
            )
        )
    return figures


def extract_meca(meca_path: Path | str, out_dir: Path | str) -> ExtractedArticle:
    """Unzip a .meca archive and parse its JATS XML plus figure images.

    .meca is just a ZIP with a JATS XML manifest plus figure assets.
    """

    meca = Path(meca_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    extract_root = out / meca.stem
    extract_root.mkdir(parents=True, exist_ok=True)

    # Only unpack members that are not on disk yet, so re runs reuse an
    # earlier extraction instead of rewriting it.
    with zipfile.ZipFile(meca) as zf:
        missing = [n for n in zf.namelist() if not (extract_root / n).exists()]
        if missing:
            zf.extractall(extract_root, members=missing)

    xml_path = _find_jats_xml(extract_root)
    jats = parse_jats(xml_path)
    figures = _promote_figures(jats, extract_root)

    return ExtractedArticle(
        article_id=meca.stem,
        title=jats.title,
        abstract=jats.abstract,
        figures=figures,
        extract_dir=extract_root,
    )
