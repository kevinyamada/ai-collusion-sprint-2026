# Crossed static-injection audit

This is a focused post-hoc follow-up to hard-b200-v1. It is not new held-out evidence for an unchanged research plan. No report is included.

## Question

Do the observed failures under injected notes persist when every attack is tested against the same conversations, and do attacks differ from neutral nuisance text of equal character length?

The previous study assigned one attack per family. This study crosses all 12 attacks with every base case, addressing that confounding. Controls match characters, NOT token length or semantics. A difference therefore does not by itself prove the model obeyed the attack instruction. Read raw responses as well.

## Frozen design

Two models: fixed revisions of Qwen2.5-7B and Qwen2.5-32B. Same B200/CUDA12.8/PyTorch2.7/BF16/batch16 runtime as hard-b200-v1. Same greedy generation and max192 new tokens.

Eight existing wording/price families × twelve scenarios × two action worlds = 192 base cases. Each appears under clean evidence, twelve static attacks, and twelve corresponding character-length neutral controls: 4,800 cases. Baseline JSON and hybrid: 9,600 predictions/model, 19,200 total. No checklist or extra action formats: this follow-up specifically isolates the note manipulation, rather than repeating completed comparisons.

Primary exploratory comparison: attack minus corresponding neutral balanced accuracy, separately by model/method/attack. Also compare against clean. Report every attack, including attacks that improve performance or have no effect. 25% positive labels; always-negative ordinary accuracy=75%, balanced accuracy=50%. Invalid outputs fail. Report extraction accuracy including invalids, sensitivity/false positives, and clean-correct-to-attack-wrong transitions. Bootstrap by whole family (8 families), descriptive only; repeated templates and many comparisons preclude strong generality claims.

This uses existing cases/attacks and is not adversarial attack discovery. No model weights are modified. Hybrid still assumes trusted machine-readable actions. The purpose is to audit an observed effect, not to force a lower score or tune an intervention until it wins.

## Launch

Extract to `C:\Users\kevin\injection-audit-b200`. The launcher locates the existing desktop or laptop Python environment. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_AUDIT.ps1
```

Keep the terminal open and computer awake. All model inference and result generation occurs on Modal. Do not edit files during a run.

## Budget

Two B200 workers in parallel. Each has a 3,500-second timeout, 3,200-second soft stop and one paid attempt per run ID. At the conservative $9/worker-hour estimate, combined GPU-worker allocation is $17.50, leaving margin within the requested approximately $20 for export/build overhead. This is not an invoice guarantee/account cap. Keep the $0 out-of-pocket account spend limit. No automatic paid retries and no minimum-spend padding. Do not launch duplicate apps or change run IDs to bypass a reservation. Partial runs are explicitly marked incomplete and exported.

Separate Volume `kevin-collusion-injection-audit`; existing model cache reused. Original tests/results stay untouched. Every batch checkpoints before reporting progress.

## Export recovery

If only export fails, run the launcher in export-only mode:

`powershell -ExecutionPolicy Bypass -File .\RUN_AUDIT.ps1 -DownloadOnly`

That does not repeat inference. Upload `injection-audit-v1-results-....zip` plus error output if any.

## Validation

Data/control/label tests and Modal1.6.2 app import checked locally. Exporter checked with artificial test fixtures that were discarded and are not experimental results. Actual cloud execution is not claimed until logged. Output ZIP includes raw responses, prompts, labels, GPU/runtime records, exact coverage checks, tables, an attack-effect figure and limitations.
