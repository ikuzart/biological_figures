from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import IO


@dataclass
class FigureRef:
    fig_id: str
    label: str
    caption: str
    href: str | None


@dataclass
class ParsedJATS:
    title: str
    abstract: str
    figures: list[FigureRef]


_WS_RE = re.compile(r"\s+")


def _text_of(node: ET.Element | None) -> str:
    if node is None:
        return ""
    parts = list(node.itertext())
    return _WS_RE.sub(" ", " ".join(p for p in parts if p)).strip()


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _iter_local(root: ET.Element, name: str):
    for el in root.iter():
        if _localname(el.tag) == name:
            yield el


def _first_local(root: ET.Element, name: str) -> ET.Element | None:
    for el in _iter_local(root, name):
        return el
    return None


def parse_jats(source: Path | str | IO[bytes]) -> ParsedJATS:
    """Extract title, abstract and figure captions from a JATS XML file.

    The bioRxiv .meca archive ships JATS tagged XML. We match by localname
    to be tolerant of the assorted namespaces used across versions.
    The source can be a path or an open binary file, so XML read straight
    out of an archive works without unpacking it first.
    """

    root = ET.parse(source).getroot()

    title = _text_of(_first_local(root, "article-title"))
    abstract = _text_of(_first_local(root, "abstract"))

    figures: list[FigureRef] = []
    for fig in _iter_local(root, "fig"):
        fig_id = fig.attrib.get("id", "").strip()
        label = _text_of(_first_local(fig, "label"))
        caption = _text_of(_first_local(fig, "caption"))
        href = None
        graphic = _first_local(fig, "graphic")
        if graphic is not None:
            for k, v in graphic.attrib.items():
                if _localname(k) == "href":
                    href = v
                    break
        figures.append(
            FigureRef(fig_id=fig_id, label=label, caption=caption, href=href)
        )

    return ParsedJATS(title=title, abstract=abstract, figures=figures)
