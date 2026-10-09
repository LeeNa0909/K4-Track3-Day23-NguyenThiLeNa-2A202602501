Source audit for `survey-about-efficient-inference-and-small-language-models`:

1. In Background, remove the fixed “approximately 1B to over 10B parameters” definition. The source set does not establish a fixed SLM size range. Keep the definition qualitative and cite sources that support deployment or compression claims.
2. Keep citations in Background and Trends and open problems. Cite only claims supported by the referenced paper: [1] architecture-aware inference, [6] Phi-4 data/curriculum, and [8] low-bit KV-cache trade-offs.
3. Remove the final forecast about “unified compression frameworks” and “efficient performance on a wider range of edge devices”; it is not supported by the source registry. Do not replace it with another prediction.
4. Inspect every sentence in those sections for unsupported numbers or claims. Delete or narrow any claim that cannot be verified from the existing source pages; do not treat a validator pass as evidence of factual support.
5. Preserve the five cited TL;DR bullets, at least three source families, and all required headings. Run the citation finalizer and validator inside the sandbox after editing.
