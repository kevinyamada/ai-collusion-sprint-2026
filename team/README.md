# Our team project

## Auditing Conditional Failures in Dolos

**Team Toronto: Gaven Ren, Barry Wu, Louis Mandela Brown, Kevin Yamada and Dongho Park**

This folder contains the team files Kevin supplied. The report studies a conditional JSON error in Dolos and tests how internal activations affect the model's next token. It does not establish the hidden objective that was deliberately trained into the model.

1. [Team report](Dolos_Submission_Report.pdf)
2. [Editable report](Dolos_Submission_Report.docx)
3. [Evidence package sizes and checksums](archive_manifest.json)

## Complete research archive

The evidence ZIPs in this folder are independent archives. Download all of them and extract them into the same directory. They share the original `Dolos_Continued_Audit_20261025` folder structure. You do not need to join the ZIP files together.

Every file from the supplied archive is preserved byte for byte across these packages. The split only makes the download easier to manage. The archive includes old drafts and checkpoint notes as well as the final report. Some historical notes say the project has not been submitted; those notes describe the state when they were written.

Start with `submission_20261025/START_HERE.md` inside the extracted archive. The main evidence locations are:

1. `submission_20261025/final_confirmation/` for the final panel, saved outputs and scores
2. `sustained_discovery/tool_activation_interchange/` for the activation experiments
3. `sustained_discovery/tool_prefix_reachability/` for the decoding path checks
4. `devin_review_20261025/` for the separate code monitor analysis and its limitations

The original runners include machine specific paths and pinned environments. They are preserved research records, not a portable installer. Reading the saved evidence does not require loading model weights.

## Credit and scope

This is shared team work. Kevin's solo pricing monitor study is [in the solo folder](../solo/). It is a separate project with a different experiment and report. The team report credits the organizer's models, external trigger leads and AI assistance. Those credits still apply to this copy.
