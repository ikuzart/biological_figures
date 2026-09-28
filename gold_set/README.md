# Gold set

This folder holds the gold set used to evaluate BFG. It has 30 figures from Cell Biology preprints on bioRxiv, each with a hand annotation of its figure type, the text printed in the image, and the biomedical entities named in its caption and image text. The OCR stages are scored against the image text and the NER stages against the entities.

## How the figures were chosen

The figures were drawn from the bioRxiv monthly dump for May 2026 by `notebooks/sample_gold_set.ipynb`. The notebook read the metadata of all 7,132 archives and kept the Cell Biology preprints released under CC BY 4.0 or CC0 1.0, taking only the latest version of each. It then kept their main figures that have both an image and a caption, and from the 132 preprints left it drew 30 with a fixed seed and one main figure from each. The licence filter keeps the set shareable in a public repository, and taking one figure per preprint stops any single paper from dominating it.

![Sampling funnel from the May 2026 dump to the gold set](sampling_funnel.png)

| Step | Preprints | Figures |
| --- | ---: | ---: |
| All archives in the dump | 7,132 | 54,418 |
| Cell Biology | 424 | 3,463 |
| CC BY 4.0 or CC0 1.0 | 140 | 1,166 |
| Latest version of each preprint | 133 | 1,102 |
| Main figures with an image and a caption | 132 | 779 |
| Drawn for the gold set, one figure each | 30 | 30 |

Running the sampling notebook again on the same dump draws the same 30 figures. `sample.json` records the seed, a fingerprint of the archive list and the full list of figures, so a different dump would be noticed.

## Files

| Path | Contents |
| --- | --- |
| `images/<key>.png` | the figure at its published size, converted from the TIFF in its archive without scaling or cropping |
| `annotations/<key>.json` | the annotation of the figure |
| `sample.json` | how the sample was drawn, and the list of the 30 figures |
| `attribution.md` | the source, authors and licence of every figure |
| `guidelines.md` | the annotation rules |
| `sampling_funnel.png` | the chart above |

A key such as `722904v2_fig7` names the preprint, its version, and the id the figure has in the preprint's JATS XML.

## Annotation files

Each annotation file has three parts. `key` names the figure, `paper` holds the article details and the caption copied from the JATS XML, and `gold` holds the hand annotation. A file for a figure that has not been annotated yet looks like this, with the caption shortened here.

```json
{
  "key": "722904v2_fig7",
  "paper": {
    "preprint": "722904v2",
    "doi": "10.64898/2026.05.05.722904",
    "title": "An aPKC rheostat induces apical contraction in response to epithelial stretching",
    "authors": "Doerflinger et al.",
    "licence": "CC BY 4.0",
    "figure_label": "Figure 7.",
    "caption": "A model showing how cell stretching could activate a compensatory apical contraction. ..."
  },
  "gold": {
    "figure_type": "",
    "ocr_text": "",
    "entities": [],
    "notes": "",
    "done": false
  }
}
```

| Field in `gold` | Meaning |
| --- | --- |
| `figure_type` | one of `plot`, `micrograph`, `blot_or_gel`, `diagram`, `mixed` and `other` |
| `ocr_text` | all the legible printed text in the image, one printed line per line, in the order set out in `guidelines.md` |
| `entities` | a list of `{"text": ..., "type": ...}` entries, each name written as it appears in the caption or the image text |
| `notes` | anything that affected the annotation, not scored |
| `done` | true once the figure is finished. The evaluation scores only the figures marked done |

## Licences

Every image and caption stays under the licence its authors chose, which is CC BY 4.0 for 28 figures and CC0 1.0 for 2. `attribution.md` credits the authors of each figure, as CC BY requires. The images were converted from TIFF to PNG and not changed in any other way.
