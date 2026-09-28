from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from bfg.config import Config
from bfg.ingest.meca import extract_meca
from bfg.pipeline.annotator import annotate_article, write_annotation
from bfg.stages.registry import REGISTRY, specs_for_modality


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="bfg",
        description=(
            "BFG: orchestrate OCR plus vision language plus biomedical NER "
            "over figures in a bioRxiv .meca preprint."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    annotate = sub.add_parser(
        "annotate", help="Annotate every figure in a .meca archive."
    )
    annotate.add_argument("meca", type=Path, help="Path to a bioRxiv .meca file.")
    annotate.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (defaults to data/annotations/<id>.json).",
    )
    annotate.add_argument("--extract-dir", type=Path, default=Path("data/extracted"))
    annotate.add_argument("--ocr", default=None, help="OCR backend key.")
    annotate.add_argument("--vision", default=None, help="Vision backend key.")
    annotate.add_argument("--ner", default=None, help="NER backend key.")
    annotate.add_argument("--cache", type=Path, default=None, help="Model cache dir.")
    annotate.add_argument("-v", "--verbose", action="store_true")

    sub.add_parser("list-stages", help="List available stage backends.")

    return p


def _config_from_args(args: argparse.Namespace) -> Config:
    cfg = Config()
    if getattr(args, "ocr", None):
        cfg.ocr_backend = args.ocr
    if getattr(args, "vision", None):
        cfg.vision_backend = args.vision
    if getattr(args, "ner", None):
        cfg.ner_backend = args.ner
    if getattr(args, "cache", None):
        cfg.model_cache = args.cache
    return cfg


def _cmd_annotate(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    log = logging.getLogger("bfg")

    cfg = _config_from_args(args)
    cfg.ensure_cache()

    log.info("Extracting %s into %s", args.meca, args.extract_dir)
    article = extract_meca(args.meca, args.extract_dir)
    log.info(
        "Parsed article '%s' with %d figures",
        article.article_id,
        len(article.figures),
    )

    log.info(
        "Backends: ocr=%s vision=%s ner=%s",
        cfg.ocr_backend, cfg.vision_backend, cfg.ner_backend,
    )
    annotation = annotate_article(article, cfg=cfg)

    out = args.out or Path("data/annotations") / f"{article.article_id}.json"
    write_annotation(annotation, out)
    log.info("Wrote annotation to %s", out)
    return 0


def _cmd_list_stages(_: argparse.Namespace) -> int:
    for modality in ("ocr", "vision", "ner"):
        print(f"[{modality}]")
        for spec in specs_for_modality(modality):
            print(f"  - {spec.key}: {spec.description}")
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "annotate":
        return _cmd_annotate(args)
    if args.command == "list-stages":
        return _cmd_list_stages(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
