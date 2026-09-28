# BFG evaluation results

RQ1 to RQ3 use the 30 of 30 gold figures marked done, with 455 unique gold names, 390 of them in the caption and 65 only in the image text. RQ4 uses all 30 figures. Intervals are 95% percentile intervals from 2000 figure-level bootstrap resamples (seed 1234).

## Table 5.1: OCR against the gold image text (RQ1)

| backend   |   N |   CER |   CER_lo |   CER_hi |   WER |   WER_lo |   WER_hi |   word_recall |   word_recall_lo |   word_recall_hi |   word_precision |   word_precision_lo |   word_precision_hi |
|:----------|----:|------:|---------:|---------:|------:|---------:|---------:|--------------:|-----------------:|-----------------:|-----------------:|--------------------:|--------------------:|
| tesseract |  30 | 0.658 |    0.625 |    0.691 | 0.893 |    0.835 |    0.952 |         0.367 |            0.298 |            0.446 |            0.425 |               0.351 |               0.502 |
| trocr     |  30 | 0.997 |    0.996 |    0.998 | 1.000 |    0.999 |    1.000 |         0.000 |            0.000 |            0.001 |            0.033 |               0.000 |               0.100 |

## Table 5.2: d4data on the caption alone and on the caption with the OCR text (RQ2)

| backend                   | context          | match   |   N |     P |   P_lo |   P_hi |     R |   R_lo |   R_hi |    F1 |   F1_lo |   F1_hi |   TP |   FP |   FN |   OCR_only_TP |   strings_per_fig |
|:--------------------------|:-----------------|:--------|----:|------:|-------:|-------:|------:|-------:|-------:|------:|--------:|--------:|-----:|-----:|-----:|--------------:|------------------:|
| d4data-biomedical-ner-all | caption_only     | exact   |  30 | 0.234 |  0.191 |  0.280 | 0.396 |  0.316 |  0.468 | 0.294 |   0.245 |   0.338 |  180 |  589 |  275 |             0 |            25.633 |
| d4data-biomedical-ner-all | caption_plus_ocr | exact   |  30 | 0.131 |  0.100 |  0.164 | 0.530 |  0.457 |  0.592 | 0.210 |   0.167 |   0.253 |  241 | 1602 |  214 |            50 |            61.433 |
| d4data-biomedical-ner-all | caption_only     | overlap |  30 | 0.469 |  0.402 |  0.528 | 0.633 |  0.536 |  0.720 | 0.539 |   0.473 |   0.591 |  288 |  408 |  167 |             0 |            25.633 |
| d4data-biomedical-ner-all | caption_plus_ocr | overlap |  30 | 0.270 |  0.227 |  0.319 | 0.767 |  0.692 |  0.829 | 0.400 |   0.347 |   0.453 |  349 | 1345 |  106 |            50 |            61.433 |

## Table 5.2b: Paired change from adding the OCR text, exact rule

| metric   |   delta |     lo |     hi |
|:---------|--------:|-------:|-------:|
| P        |  -0.103 | -0.131 | -0.077 |
| R        |   0.134 |  0.087 |  0.182 |
| F1       |  -0.084 | -0.114 | -0.049 |

## Table 5.3: The three NER models on the caption with the OCR text (RQ3)

| backend                   | context          | match   |   N |     P |   P_lo |   P_hi |     R |   R_lo |   R_hi |    F1 |   F1_lo |   F1_hi |   TP |   FP |   FN |   OCR_only_TP |   strings_per_fig |
|:--------------------------|:-----------------|:--------|----:|------:|-------:|-------:|------:|-------:|-------:|------:|--------:|--------:|-----:|-----:|-----:|--------------:|------------------:|
| d4data-biomedical-ner-all | caption_plus_ocr | exact   |  30 | 0.131 |  0.100 |  0.164 | 0.530 |  0.457 |  0.592 | 0.210 |   0.167 |   0.253 |  241 | 1602 |  214 |            50 |            61.433 |
| bert-base-ner             | caption_plus_ocr | exact   |  30 | 0.386 |  0.287 |  0.504 | 0.112 |  0.081 |  0.148 | 0.174 |   0.130 |   0.221 |   51 |   81 |  404 |             5 |             4.400 |
| scispacy                  | caption_plus_ocr | exact   |  30 | 0.164 |  0.135 |  0.194 | 0.662 |  0.616 |  0.701 | 0.263 |   0.223 |   0.302 |  301 | 1534 |  154 |            31 |            61.167 |
| d4data-biomedical-ner-all | caption_plus_ocr | overlap |  30 | 0.270 |  0.227 |  0.319 | 0.767 |  0.692 |  0.829 | 0.400 |   0.347 |   0.453 |  349 | 1345 |  106 |            50 |            61.433 |
| bert-base-ner             | caption_plus_ocr | overlap |  30 | 0.621 |  0.504 |  0.752 | 0.207 |  0.158 |  0.265 | 0.310 |   0.247 |   0.376 |   94 |   50 |  361 |             5 |             4.400 |
| scispacy                  | caption_plus_ocr | overlap |  30 | 0.301 |  0.258 |  0.342 | 0.912 |  0.876 |  0.942 | 0.453 |   0.402 |   0.497 |  415 | 1282 |   40 |            31 |            61.167 |

## Table 5.3b: Paired change against d4data on the caption with the OCR text, exact rule

| backend       | metric   |   delta |     lo |     hi |
|:--------------|:---------|--------:|-------:|-------:|
| bert-base-ner | P        |   0.256 |  0.167 |  0.360 |
| bert-base-ner | R        |  -0.418 | -0.496 | -0.321 |
| bert-base-ner | F1       |  -0.036 | -0.097 |  0.026 |
| scispacy      | P        |   0.033 |  0.010 |  0.057 |
| scispacy      | R        |   0.132 |  0.072 |  0.200 |
| scispacy      | F1       |   0.053 |  0.021 |  0.086 |

## Table 5.4: Generated captions against their own and the other paper captions (RQ4)

| backend   | metric   |   matched |   shuffled |    gap |   gap_lo |   gap_hi |   top1 |   N |
|:----------|:---------|----------:|-----------:|-------:|---------:|---------:|-------:|----:|
| vit-gpt2  | cosine   |     0.389 |      0.383 |  0.006 |   -0.028 |    0.036 |      1 |  30 |
| vit-gpt2  | jaccard  |     0.004 |      0.006 | -0.002 |   -0.004 |    0.002 |      0 |  30 |
| blip      | cosine   |     0.367 |      0.368 | -0.001 |   -0.029 |    0.028 |      2 |  30 |
| blip      | jaccard  |     0.004 |      0.005 | -0.001 |   -0.004 |    0.005 |      1 |  30 |

## Table 5.5: Gold entity types and the labels of the two typed models

| source                                      | label                |   share |   n |
|:--------------------------------------------|:---------------------|--------:|----:|
| gold                                        | gene_or_protein      |   0.382 | 174 |
| gold                                        | cell_or_tissue       |   0.251 | 114 |
| gold                                        | chemical             |   0.187 |  85 |
| gold                                        | technique            |   0.097 |  44 |
| gold                                        | other                |   0.040 |  18 |
| gold                                        | organism             |   0.040 |  18 |
| gold                                        | disease              |   0.004 |   2 |
| d4data-biomedical-ner-all                   | Diagnostic_procedure |   0.425 | 832 |
| d4data-biomedical-ner-all                   | Lab_value            |   0.377 | 738 |
| d4data-biomedical-ner-all                   | Detailed_description |   0.098 | 191 |
| d4data-biomedical-ner-all                   | Coreference          |   0.037 |  73 |
| d4data-biomedical-ner-all                   | Sign_symptom         |   0.025 |  49 |
| d4data-biomedical-ner-all                   | Biological_structure |   0.015 |  29 |
| d4data-biomedical-ner-all (correct strings) | Diagnostic_procedure |   0.677 | 189 |
| d4data-biomedical-ner-all (correct strings) | Lab_value            |   0.093 |  26 |
| d4data-biomedical-ner-all (correct strings) | Detailed_description |   0.072 |  20 |
| d4data-biomedical-ner-all (correct strings) | Coreference          |   0.050 |  14 |
| d4data-biomedical-ner-all (correct strings) | Biological_structure |   0.047 |  13 |
| d4data-biomedical-ner-all (correct strings) | Sign_symptom         |   0.029 |   8 |
| bert-base-ner                               | MISC                 |   0.458 |  66 |
| bert-base-ner                               | ORG                  |   0.340 |  49 |
| bert-base-ner                               | PER                  |   0.125 |  18 |
| bert-base-ner                               | LOC                  |   0.076 |  11 |
| bert-base-ner (correct strings)             | MISC                 |   0.579 |  33 |
| bert-base-ner (correct strings)             | ORG                  |   0.316 |  18 |
| bert-base-ner (correct strings)             | PER                  |   0.070 |   4 |
| bert-base-ner (correct strings)             | LOC                  |   0.035 |   2 |

## Median per-figure scores by figure type

| figure_type   |   figures |   gold_words |   tesseract_CER |   tesseract_word_recall |   trocr_CER |   trocr_word_recall |   gold_names |   d4data-biomedical-ner-all_found |   bert-base-ner_found |   scispacy_found |
|:--------------|----------:|-------------:|----------------:|------------------------:|------------:|--------------------:|-------------:|----------------------------------:|----------------------:|-----------------:|
| diagram       |         4 |       21.000 |           0.301 |                   0.679 |       0.981 |               0.000 |        8.500 |                             1.500 |                 1.500 |            6.500 |
| micrograph    |         2 |       65.500 |           0.641 |                   0.283 |       1.000 |               0.000 |       17.000 |                             9.000 |                 2.500 |           12.500 |
| mixed         |        20 |      122.000 |           0.656 |                   0.445 |       0.999 |               0.000 |       15.000 |                             7.500 |                 1.500 |            9.000 |
| plot          |         4 |      161.000 |           0.678 |                   0.259 |       0.997 |               0.000 |       10.000 |                             4.500 |                 0.500 |            8.000 |
