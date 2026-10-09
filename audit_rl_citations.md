Source audit for `survey-about-reinforcement-learning-for-llm-reasoning`:

1. Correct the first TL;DR bullet. It currently groups GRPO and MCTS as methods for step-level credit assignment. GRPO [1] is described as group-relative policy optimization; MCTS-guided preference learning [10] is the source that decomposes instance-level reward into step-level signals. State those as distinct approaches and cite each clause accurately.
2. Check that all named algorithms, numerical benchmark claims, and solver details are supported by the exact cited sources. Keep o1 AIME figures attached to [6], and the o3 IOI/Codeforces claim attached to [8]. Narrow unsupported claims.
3. Preserve the report structure, 3–5 cited TL;DR bullets, and at least three source families. Run the citation finalizer and validator in the sandbox after editing.
