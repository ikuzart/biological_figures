# BFG (BiologicalFiGures)

BFG annotates the figures in bioRxiv preprints by chaining three pre-trained models. OCR reads the text printed in each figure image, a vision-language model captions the image, and a biomedical named-entity recogniser tags entities in the figure caption, the OCR text and the article abstract, recording which of the three each entity came from. `report.md` is the final report: it describes the design and evaluates it on a 30-figure gold set.

## Requirements

- Python 3.13 (`pyproject.toml` pins `>=3.13,<3.14`)
- [uv](https://docs.astral.sh/uv/), which `scripts/reproduce.sh` uses
- Tesseract OCR on the PATH: `brew install tesseract` (macOS) or `apt install tesseract-ocr` (Linux)

## Install

```bash
./scripts/reproduce.sh
```

This runs `uv sync --extra dev`, installs the scispaCy model with `scripts/install_scispacy.sh`, runs the fast tests and reports which backends are available. The same steps by hand:

```bash
uv sync --extra dev              # Python dependencies, plus pytest
./scripts/install_scispacy.sh    # en_core_sci_lg 0.5.4, installed outside the lock file
```

## Annotate a preprint

```bash
uv run bfg list-stages
uv run bfg annotate path/to/article.meca -o out/article.json
uv run bfg annotate path/to/article.meca --ocr trocr --vision blip --ner scispacy
```

The default backends are Tesseract, ViT-GPT2 and d4data; `bfg list-stages` lists the rest. Model weights are not redistributed: the first run of each backend downloads its checkpoint from the Hugging Face Hub into `hf_models/` (set `BFG_MODEL_CACHE` to use another directory). Without `-o`, the output goes to `data/annotations/<article_id>.json`, and the archive is unpacked under `data/extracted/`. `artefacts/577109_annotation.json` is the output for all eight figures of preprint 577109, and `notebooks/get_data.ipynb` shows how to download the bioRxiv archives.

## Tests

```bash
uv run pytest tests -q --ignore=tests/test_stages_smoke.py    # 31 unit tests, offline
uv run pytest tests/test_stages_smoke.py -q                    # 7 smoke tests, one per backend
```

The smoke tests load every registered backend and run it on a tiny input, so the first run downloads the weights.

## Reproduce the evaluation

`notebooks/evaluation.ipynb` produces every number in Chapter 5 of the report. Open it with the project's virtual environment (`.venv`) as the kernel and run all cells. It reads the gold set in `gold_set/` and the cached model outputs in `eval_results/predictions/`, so it needs neither the bioRxiv archives nor the Hugging Face weights, only `en_core_sci_lg`, whose word vectors score the vision captions. It rewrites Tables 5.1 to 5.6 in `eval_results/` (summarised in `eval_results/summary.md`) and the report figures in `eval_results/figures/`. A figure with no cached output is run through the models again, which needs its archive in `data/May_2026/`.


## Notebooks

| Notebook | Purpose |
| --- | --- |
| `demo.ipynb` | The annotation of preprint 577109: entities by source, a figure next to its annotation, and the evaluation tables |
| `evaluation.ipynb` | The Chapter 5 evaluation on the gold set |
| `annotation_browser.ipynb` | Browse and search the 30 gold annotations next to their images |
| `get_data.ipynb` | Download bioRxiv MECA archives from the requester-pays S3 bucket (needs AWS credentials) |

## Layout

```
src/bfg/         the package: ingest, stages, pipeline, cli
tests/           pytest suite
notebooks/       notebooks above
gold_set/        the 30-figure gold set, its guidelines and agreement reports (see gold_set/README.md)
eval_results/    Tables 5.1 to 5.6 as CSV, summary.md, report figures, cached model outputs
LICENCES.md      licences of the models, the software and the gold-set figures
```
