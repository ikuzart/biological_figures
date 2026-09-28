# Annotation guidelines for the gold set

These are the rules for annotating the 30 figures in `gold_set/images/`. The annotation is done in `notebooks/annotate_gold_set.ipynb`, which shows each figure next to a form and saves the answers to `gold_set/annotations/<key>.json`. The same rules apply to every figure, so that the reference the models are scored against is consistent from one figure to the next.

Annotate each figure before looking at any model output for it. Seeing what the OCR or NER models returned first would pull the reference towards them.

## What is recorded

Every figure gets a figure type, the text printed in the image, a list of entities, and optional notes. The OCR models are scored against the image text and the NER models against the entities. The figure type and the entity types only describe the set and are not used for scoring, so when a case is unclear, pick the closest option and move on.

## Figure type

Pick one type for the whole figure.

| Type | Use it for |
| --- | --- |
| `plot` | charts and graphs only, such as bar, line, scatter and box plots, and heat maps |
| `micrograph` | microscope images only (light, fluorescence or electron), with or without labels |
| `blot_or_gel` | western blots, gels and similar membranes only |
| `diagram` | drawings such as models, pathways, schemes, workflows and timelines |
| `mixed` | panels of more than one of the kinds above, which covers most figures with several panels |
| `other` | anything else, such as photographs, sequence alignments, 3D structures or tables drawn as images |

## Image text

The image text is a transcription of all the printed text that can be read in the image. It is the reference for the OCR models, so it should hold what a perfect OCR engine would return, and nothing more.

**What to include.** Every legible word, number and symbol printed in the image. That covers panel letters, titles, axis labels, tick labels, legends, labels on micrographs and blots, scale bar labels, and significance marks such as `*`, `**` and `n.s.`. A word printed several times is written each time it appears.

**What to leave out.** Drawn shapes are not text, so arrows, lines, brackets, colour bars and the symbols in legend keys are skipped. Letters that belong to a drawing, such as the atoms of a chemical structure, are skipped too and mentioned in the notes. Nothing that is not printed is added, so no panel markers of your own and no descriptions of what the image shows.

**Order.** Go panel by panel in the order of the panel letters. A figure without panel letters counts as one panel. Inside a panel, go from top to bottom, and from left to right for text at the same height. Each printed line goes on its own line in the text box, and labels that sit apart go on separate lines even when they are level with each other. Rotated text, such as a y axis label, is written as a normal line and placed by the height of its middle. An empty line between panels is allowed and makes the text easier to check. The exact order inside a busy panel is often a judgement call, so do not spend long on it. The evaluation reports a word score that ignores order next to the character error rate for this reason.

**Characters.** Type the text as printed, keeping the capital letters and the spelling, even where the figure has a typo. Greek letters and symbols are typed as the character itself (α, β, µ, ±, °, ×). On a Mac, the Character Viewer (Control, Command and Space together) finds them by name. Superscripts and subscripts are typed inline, so Ca²⁺ becomes `Ca2+` and CO₂ becomes `CO2`. Minus signs and dashes are typed as the ordinary hyphen.

**Legibility.** Include text that can be read with confidence at full size. If some text is too small or blurred to read, leave it out rather than guess, and name the panel in the notes. A figure with no legible text at all gets an empty text box and a note saying so.

**An example.** Suppose a figure has two panels. Panel A shows two micrographs side by side with the titles `DMSO` and `Rapamycin` above them, the rotated row label `GFP-LC3` on the left, and `10 µm` next to the scale bar in the second image. Panel B is a bar chart with `**` above the second bar at the top of the plot, the ticks 0, 10 and 20, the rotated y axis label `Puncta per cell` level with the 10, and two bars labelled `WT` and `ATG5 KO`. The image text is

```
A
DMSO
Rapamycin
GFP-LC3
10 µm

B
**
20
Puncta per cell
10
0
WT
ATG5 KO
```

## Entities

An entity is the name of a specific biomedical thing that appears in the caption or in the image text. The list is the reference for the NER models, which read the same caption together with the text the OCR finds in the image.

| Type | Use it for | Examples |
| --- | --- | --- |
| `gene_or_protein` | genes, proteins and protein complexes, including tagged or mutant forms written as one name | ATG5, p53, GFP-LC3, E-cadherin |
| `chemical` | small molecules, drugs, dyes, stains and buffers | rapamycin, DMSO, DAPI, MitoTracker |
| `disease` | diseases and disorders | Alzheimer's disease, tauopathy |
| `organism` | species and strains | mouse, zebrafish, Drosophila, S. cerevisiae |
| `cell_or_tissue` | cell types, cell lines, tissues, organs and parts of the cell | HeLa, neurons, liver, lysosome |
| `technique` | methods, assays and instruments | confocal microscopy, western blot, FRAP, flow cytometry |
| `other` | a biomedical name that fits none of the types above | |

The rules for choosing the names are these.

1. **Only names that appear in the caption or the image text.** The article can be opened from the link in the form, for example to check what an abbreviation stands for, but a name that is only in the article is not listed. The form checks this rule when saving.
2. **Copy the name exactly as printed**, with the same spelling, hyphens and Greek letters. Capital letters do not matter, because the evaluation ignores them.
3. **Keep just the name.** Leave out generic words around it, such as cells, protein, gene, KO, siRNA, fibrils, staining and treatment. So `HeLa cells` becomes `HeLa` and `ATG5 KO` becomes `ATG5`. A tag or mutation joined to the name, as in `GFP-LC3`, stays part of it.
4. **List each name once**, however often it appears. Names that differ only in capital letters count as the same name.
5. **List both the full name and the abbreviation** when both appear, for example `glial fibrillary acidic protein` and `GFAP`.
6. **Leave out** numbers, units, statistics and statistical tests (p values, ANOVA, t test), and words that do not name a specific thing, such as control, sample, treatment or image.
7. **Names found only in the image text count as much as those in the caption.** They are what the OCR stage can add, so read through the image text for them once it is typed.

In the form, write one entity per line as the name, a vertical bar and the type, for example `DMSO | chemical`. For the example figure above, with the caption "GFP-LC3 puncta in HeLa cells treated with DMSO or rapamycin", the entity box is

```
GFP-LC3 | gene_or_protein
HeLa | cell_or_tissue
DMSO | chemical
rapamycin | chemical
ATG5 | gene_or_protein
```

`Rapamycin` in the image and `rapamycin` in the caption are the same name, so it is listed once. `ATG5` appears only in the image text.

## Notes

The notes are for anything that affected the annotation: text too small to read, words you were unsure of, letters inside a chemical structure that were left out, or the use of a copying aid. Notes are not scored.

## Copying aid

Typing out a dense figure takes a long time. Text may be copied out of the image with an OCR tool that is not one of the models being evaluated, for example Live Text in the macOS Preview app, as a starting point. Every line must then be checked against the image and corrected by hand, the order fixed to follow these rules, and the notes must say so, for example `text copied with Live Text, then checked by hand`. Never start from the output of Tesseract or TrOCR, since those are the models being scored.

## Done

Tick done when the figure type is chosen and both the image text and the entity list are complete. The form keeps a figure as not done while any check fails, and the evaluation scores only the figures marked done. A finished figure can be reopened and changed at any time, after which the evaluation notebook should be run again.
