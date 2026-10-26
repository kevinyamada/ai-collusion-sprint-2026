# Checking Actions to Audit Explicit Price Agreements

Author: Kevin Yamada, University of Toronto.

This project tests AI monitors on scripted records of price agreements and actions. It is a separate study from Team Toronto’s Dolos audit.

## Main finding

Extracting evidence and checking it with code improved the main comparison on clean prose. Smaller models often failed the required output format on JSON inputs. The report includes those failures. Perfect results on some scripted conditions do not establish a universal collusion detector.

Download and extract `Monitoring_Submission_Package.zip` for the code, raw results, editable report and figures listed below.

## Files

1. Monitoring_Report.pdf: final report, six pages including references and appendices.
2. Monitoring_Report.docx: editable report.
3. final-two-b200.zip: frozen source code, tests and launch instructions for both studies.
4. FINAL_RESULTS.zip: two nested result archives containing saved prompts and predictions, cases, metrics and runtime records.
5. Figure1_Primary_Results.png and Figure2_Format_Failures.png: figures used in the report.
6. ABSTRACT.txt: submission abstract.
7. verified_tables.json: selected results used for the report figures and tables.

## Inspect the evidence

Extract FINAL_RESULTS.zip and both result ZIPs inside it. Read analysis/quality_checks.json, metrics.csv, paired_effects.csv and counterfactual_pairs.csv. Raw predictions are saved in per model batch_*.jsonl files. cases_with_labels.json contains the generated cases.

The two studies contain 16,128 and 12,096 actual model calls, for 28,224 total. Reviewing the saved results does not require any additional Modal spending.

## Reproduction

Extract final-two-b200.zip and follow its START_HERE.md. The code for the two studies is in test1/ and test2/. Each includes hard_app.py, hard_benchmark.py, hard_analysis.py and tests. Exact model revisions and runtime settings are listed in Appendix B of the report. All data are fictional. No model weights or credentials are included.

## AI assistance

ChatGPT/Codex assisted with experiment design, code, checks, interpretation and writing. Kevin ran the experiments and supplied the saved results. The report describes the limits of automated verification.
