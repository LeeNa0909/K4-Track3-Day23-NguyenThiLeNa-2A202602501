Source audit for `survey-about-video-and-multimodal-generation`:

1. Correct the TL;DR claim that groups JavisGPT and JavisDiT++ as both integrating video understanding and generation. JavisGPT [5] covers sounding-video comprehension and generation; JavisDiT++ [4] is a joint audio-video generation model. State that distinction plainly and cite each clause accurately.
2. The “minute-long” Sora statement in TL;DR is supported by the Sora survey [3], not by CogVideoX [1] or Latte [2]. Remove [1][2] from that clause; cite [3] (and [9] only if it independently supports the same statement).
3. Retain the verified JavisDiT++ details: TA-RoPE and AV-DPO are described by [4], while the MTV multi-stream separation of speech, effects, and music is described by [6]. Keep citations attached to the matching method.
4. Review all other quantitative or model-specific claims against the source pages using `web_fetch`. Remove or narrow unsupported statements, especially where one citation is being used to support multiple unrelated methods.
5. Preserve 3–5 cited TL;DR bullets, at least three source families, and the report template. Run the citation finalizer and validator in the sandbox after edits.
