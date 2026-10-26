# Earlier injection audit

This was an exploratory experiment before my final two studies. I tested whether misleading notes changed a monitor's answer compared with neutral notes of the same character length.

The design used 192 base cases. Each appeared with no note, twelve misleading notes and twelve neutral controls, giving 4,800 cases. Two methods and two Qwen model sizes produced 19,200 saved predictions. The supplied quality check reports complete coverage, no missing or duplicate predictions, and 16 invalid outputs.

1. [Saved results](results.zip)
2. [Benchmark](hard_benchmark.py)
3. [Analysis](hard_analysis.py)
4. [Modal app](hard_app.py)
5. [Tests](test_audit.py)
6. [Original setup instructions](START_HERE.md)

This reused existing cases and attacks. It is not fresh confirmation of an unchanged research plan. Neutral notes matched character length, not token length or meaning, so a difference alone does not prove the model followed an injected instruction. These results are not pooled with the 28,224 responses in the final report.

The source files and their original instructions are preserved as supplied. No new inference was run to add them here.
