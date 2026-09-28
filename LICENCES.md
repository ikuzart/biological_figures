# BFG licences

This file records the licence of every model the pipeline can load, of the main Python dependencies, and of every figure in the gold set. Table 3.1 of the report refers to the model table. The BFG code itself was written by the author for the CM3070 final project.

## Models

Model weights are not redistributed. Each backend downloads its checkpoint from the Hugging Face Hub on first use and caches it in the git-ignored `hf_models/` directory. The snapshot column gives the commit of each checkpoint the evaluation used.

| Modality | Registry key | Model | Licence | Source | Snapshot |
| --- | --- | --- | --- | --- | --- |
| OCR | `tesseract` | Tesseract 5, LSTM engine | Apache-2.0 | https://github.com/tesseract-ocr/tesseract | system binary, 5.5.3 for the evaluation |
| OCR | `trocr` | microsoft/trocr-base-printed | MIT | https://huggingface.co/microsoft/trocr-base-printed | `93450be3f1ed40a930690d951ef3932687cc1892` |
| Vision | `vit-gpt2` | nlpconnect/vit-gpt2-image-captioning | Apache-2.0 | https://huggingface.co/nlpconnect/vit-gpt2-image-captioning | `dc68f91c06a1ba6f15268e5b9c13ae7a7c514084` |
| Vision | `blip` | Salesforce/blip-image-captioning-base | BSD-3-Clause | https://huggingface.co/Salesforce/blip-image-captioning-base | `82a37760796d32b1411fe092ab5d4e227313294b` |
| NER | `d4data-biomedical-ner-all` | d4data/biomedical-ner-all: DistilBERT (distilbert-base-uncased) fine-tuned on the MACCROBAT clinical case reports | Apache-2.0 | https://huggingface.co/d4data/biomedical-ner-all | `015a4050c9ac99722e61c547aa9b4282bcbedc7f` |
| NER | `bert-base-ner` | dslim/bert-base-NER: BERT-base fine-tuned on CoNLL-2003 news | MIT | https://huggingface.co/dslim/bert-base-NER | `d1a3e8f13f8c3566299d95fcfc9a8d2382a9affc` |
| NER | `scispacy` | scispaCy 0.6.2 with the en_core_sci_lg 0.5.4 pipeline | Apache-2.0 (scispaCy code), CC BY-SA 3.0 (en_core_sci_lg) | https://allenai.github.io/scispacy/ | release 0.5.4, installed by `scripts/install_scispacy.sh` |

en_core_sci_lg also supplies the word vectors that the evaluation uses to score the vision captions. Its CC BY-SA 3.0 licence, taken from the model's own metadata, is the only share-alike licence in the table. It applies to the model files, which this repository does not contain.

Two domain-aware vision models were investigated and not integrated. `microsoft/BiomedVLP-BioViL-T` is a dual encoder that produces retrieval embeddings, not captions, so it cannot stand in for a captioning stage. LLaVA-Med is released as weight differences against a Llama base model and was not downloaded. Section 3.4 of the report gives the details.

## Python dependencies

The versions below are those in `uv.lock`, and the licences are taken from each package's metadata.

| Package | Version | Licence |
| --- | --- | --- |
| transformers | 4.57.6 | Apache-2.0 |
| torch | 2.14.0 | Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT (bundled components) |
| huggingface-hub | 0.36.2 | Apache-2.0 |
| sentencepiece | 0.2.2 | Apache-2.0 |
| spacy | 3.8.16 | MIT |
| scispacy | 0.6.2 | Apache-2.0 |
| pytesseract | 0.3.13 | Apache-2.0 |
| pillow | 12.3.0 | MIT-CMU |
| numpy | 1.26.4 | BSD-3-Clause |
| pandas | 3.0.6 | BSD-3-Clause |
| pyarrow | 25.0.1 | Apache-2.0 |
| matplotlib | 3.11.2 | Matplotlib licence (PSF-based) |
| jiwer | 4.0.0 | Apache-2.0 |
| tabulate | 0.10.0 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| certifi | 2026.7.22 | MPL-2.0 |
| python-dotenv | 1.2.3 | BSD-3-Clause |
| ipykernel | 7.3.0 | BSD-3-Clause |
| pandas-stubs | 3.0.5.260914 | BSD-3-Clause |

## Gold-set figures

The 30 images in `gold_set/images/`, and the caption text in the annotation files, come from bioRxiv preprints posted by openRxiv. Each stays under the licence its authors chose, recorded in the `<permissions>` element of the preprint's JATS XML. The images were converted from the archive's TIFF files to PNG and, where the original was wider than 1,800 pixels, scaled down to that width. The entity lists, types, OCR transcriptions and notes in the annotation files are the project's own work.

| Archive | Figures | Preprint DOI | First author | Licence |
| --- | --- | --- | --- | --- |
| `02f55356` | fig1 | 10.64898/2026.05.01.722121 | Wongtrakul-Kish | All rights reserved |
| `09572f18` | figs2 | 10.64898/2026.04.28.721503 | Buglak | CC0 1.0 (US Government work) |
| `141a6f66` | fig1 | 10.1101/2025.11.24.690135 | Babu | All rights reserved |
| `1b75fa43` | fig6 | 10.64898/2026.05.05.722904 (version 1) | Doerflinger | CC BY 4.0 |
| `2ee6298a` | fig5 | 10.64898/2026.04.29.721565 | Van Zundert | All rights reserved |
| `3f22fcad` | fig4 | 10.64898/2026.04.30.721919 | Silva-Almeida | All rights reserved |
| `7c04bff4` | fig1 | 10.64898/2026.05.17.724675 | Sahasrabudhe | CC BY-NC-ND 4.0 |
| `7d56ba33` | fig3 | 10.64898/2026.05.06.723184 | Nonaka | All rights reserved |
| `86194590` | fig3 | 10.1101/2025.07.17.665028 | Robb | All rights reserved |
| `872c8f8c` | fig4 | 10.64898/2026.05.04.722602 | Szafranska | CC BY-NC 4.0 |
| `8c6a0945` | fig4 | 10.1101/2024.07.25.605133 | Cheng | CC BY-NC-ND 4.0 |
| `8fdbda91` | fig2, fig3 | 10.64898/2026.04.18.710733 | Xiong | All rights reserved |
| `9581c585` | fig6 | 10.1101/2024.01.24.577109 | Kumar | CC0 1.0 (US Government work) |
| `9bf82375` | fig3 | 10.64898/2026.05.18.725821 | Naaz | CC BY-NC 4.0 |
| `a796e3d6` | fig7 | 10.64898/2026.05.18.725837 | Pan | CC BY 4.0 |
| `aa15c000` | fig5 | 10.1101/2023.02.01.526449 | Ettelt | CC BY-NC-ND 4.0 |
| `acea6d6b` | fig6 | 10.64898/2026.05.15.725580 | Judge | CC BY 4.0 |
| `b6325477` | fig1 | 10.64898/2026.05.05.722904 (version 2) | Doerflinger | CC BY 4.0 |
| `b8eeda89` | fig2, fig3 | 10.64898/2026.05.12.724245 | Rafiq | CC BY 4.0 |
| `c9894bbb` | fig5 | 10.64898/2026.05.18.725568 | Ewachiw | All rights reserved |
| `d66b0cb1` | fig3 | 10.1101/2025.11.17.683537 | Salmond | CC BY-NC-ND 4.0 |
| `dde1772b` | fig3 | 10.64898/2026.05.28.728554 | Weyerhäuser | All rights reserved |
| `dede990f` | fig5 | 10.64898/2026.05.24.727551 | Kadzik | CC BY-NC-ND 4.0 |
| `eaa39a84` | fig5 | 10.1101/2025.03.20.644150 | Mohammed | All rights reserved |
| `eadbf8b8` | fig1 | 10.64898/2026.05.15.725367 | Chen | CC BY-NC-ND 4.0 |
| `f1aa0d75` | fig1 | 10.64898/2026.05.22.727240 | Uhrig | CC BY-NC-ND 4.0 |
| `f20a3c81` | fig6 | 10.64898/2026.05.05.723108 | Sbalchiero | CC BY-NC-ND 4.0 |
| `fbdff998` | fig3 | 10.64898/2026.05.02.722362 | Tariq | CC0 1.0 (public domain dedication) |

The archive column is the first eight characters of the MECA archive name, which prefixes the file names in `gold_set/`. Eleven figures from ten preprints are marked all rights reserved: bioRxiv's statement for them reads "The material may not be redistributed, re-used or adapted without the author's permission."
