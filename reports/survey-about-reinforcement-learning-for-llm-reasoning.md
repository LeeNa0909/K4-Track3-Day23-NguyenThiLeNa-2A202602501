# Reinforcement Learning for LLM Reasoning: Algorithmic Foundations and Scaling Trends

## TL;DR
* **Algorithmic Shift**: Transition from global preference alignment to step-level credit assignment using methods like Group Relative Policy Optimization (GRPO) and MCTS-guided search [1][2].
* **Reward Engineering**: Integration of process-based rewards and formal verification (e.g., SMT solvers) to provide dense signals and mitigate "reward hacking" in reasoning chains [3][4][5].
* **Scaling Behavior**: Reasoning performance improves with increased reinforcement learning training compute and test-time computation (thinking tokens) [6][7].
* **Benchmark Evolution**: As datasets like GSM8K reach saturation, new frontiers like AIME, GPQA, and Codeforces demonstrate the efficacy of specialized reasoning models [6][8].
* **Verifiable Reasoning**: Success in math and coding is driven by verifiable rewards; however, generalized reasoning in non-verifiable domains remains an open challenge [6][9].

## Background
Reasoning in Large Language Models (LLMs) refers to the ability to decompose complex problems into multi-step "chains of thought" (CoT). Traditional Supervised Fine-Tuning (SFT) often fails to capture the trial-and-error nature of high-level problem solving. Reinforcement Learning (RL) has emerged as a critical paradigm to bridge this gap by treating reasoning as a sequential decision process. Recent breakthroughs, exemplified by OpenAI's o1, have demonstrated that RL can foster emergent self-correction and strategic planning, with performance scaling as a function of both training and test-time compute [6][7].

## Algorithmic Frameworks for Reasoning
The landscape of RL for reasoning has evolved beyond standard Proximal Policy Optimization (PPO). While PPO remains a foundation, its reliance on a learned critic network can present challenges for step-level credit assignment in reasoning-heavy tasks [2].
* **Group Relative Policy Optimization (GRPO)**: Popularized by DeepSeek, GRPO eliminates the value function critic. It estimates relative advantage by comparing a response to a group of sampled outputs, reducing memory overhead and improving stability for mathematical tasks [1].
* **Search-Guided RL**: Monte Carlo Tree Search (MCTS) is increasingly used as a policy improvement operator. Frameworks like AlphaZero-style MCTS allow models to collect granular step-level signals, which can then be used to update the policy via Direct Preference Optimization (DPO) [10].
* **Sampling-Based Alternatives**: Methods like TreeBoN integrate speculative tree-search with Best-of-N sampling, using token-level rewards from DPO models to guide tree expansion and prune low-quality partial paths [11].

## Reward Signal Design and Process Supervision
A core difficulty in RL for reasoning is the sparsity of outcome-based rewards.
* **Outcome vs. Process Rewards**: Outcome-based Reward Models (ORM) provide reliable but sparse feedback. In contrast, Process-based Reward Models (PRM) offer dense step-by-step guidance but are susceptible to "reward hacking," where models learn to repeat redundant but correct steps to inflate scores [9][5].
* **Formal Verification**: Recent work uses formal verification tools to provide automated, error-free step-level labels. The FoVer method uses tools like Z3 and Isabelle to automatically annotate error labels for PRM training [4]. Similarly, the SPRING framework utilizes SMT solvers to reward "novel reasoning steps" that are logically valid and not already implied by previous context [3].
* **Refinement Techniques**: To address reward hacking from redundant correct steps, studies have proposed "Clipping" and "Delta" reward refinements to ensure the accumulative reward of a trajectory remains upper-bounded [5].

## Scaling Laws and Inference-Time Compute
A defining trend is the shift from pre-training scaling to inference-time and RL-time scaling.
* **Scaling Trends**: OpenAI's o1 demonstrates that performance on math and coding benchmarks improves smoothly with both RL training compute and the number of "thinking tokens" generated at test-time [6].
* **Emergent Behaviors**: Through large-scale RL, models develop behaviors such as self-correction, backtracking, and trial-and-error [6]. The o3 model demonstrated state-of-the-art proficiency by achieving gold medal status at the 2024 International Olympiad in Informatics (IOI) and a Codeforces rating comparable to elite human competitors [8].
* **Open-Source Scaling**: Models like T1 demonstrate that RL can bridge performance gaps by scaling inference-time compute through synthesized CoT data and oversampling, outperforming models like QwQ-32B-Preview on benchmarks such as AIME2024 [12].

## Benchmarks and Performance Metrics
As reasoning models improve, traditional benchmarks like GSM8K have reached saturation and are no longer effective at differentiating frontier models [6].
* **Advanced Benchmarks**: AIME (math), GPQA (science), and Codeforces (competitive programming) have become the new standard for evaluating reasoning capability [6][8].
* **Performance Gains**: Reasoning-optimized models show dramatic improvements; for instance, o1 reached 83% on the 2024 AIME with consensus sampling (64 samples), compared to just 12% for GPT-4o [6]. The o3 model further demonstrated these gains by achieving a gold medal at the 2024 IOI [8].

## Trends and open problems
The future of RL for reasoning is centered on generalizing success beyond verifiable domains.
* **Verifiable vs. Non-Verifiable Domains**: Current successes are concentrated in math and code where rewards are easily verified. Scaling these benefits to subjective reasoning or creative writing remains an open challenge [6][9].
* **Inference Efficiency**: While scaling "thinking tokens" improves accuracy, it increases latency and cost. Adaptive scaling, where models decide when to stop "thinking" based on confidence, is an active area of research [6][13].
* **Distribution Shift**: A key challenge in test-time scaling is ensuring that search strategies remain effective as the search budget grows, avoiding pitfalls where the model might exploit weaknesses in the reward signal [7][13].
* **Data Synthesis**: In data-constrained environments, the synthesis of high-quality "trial-and-error" data and self-verification chains is critical for further RL progress [12][13].

## References
[1] Reinforcement Learning for LLM Post-Training: A Survey. web. https://arxiv.org/abs/2407.16216 (2024-07-23)
[2] A Technical Survey of Reinforcement Learning Techniques for Large Language Models. web. https://arxiv.org/abs/2507.04136 (2025-07-05)
[3] Rewarding Novel Deductions: Solver-guided Process Supervision for Logical Reasoning. arxiv. https://arxiv.org/abs/2609.34660 (2026-09-28)
[4] Training Step-Level Reasoning Verifiers with Formal Verification Tools. hf-search. https://huggingface.co/papers/2505.15960 (2025-05-21)
[5] On Designing Effective RL Reward at Training Time for LLM Reasoning. hf-search. https://huggingface.co/papers/2410.15115 (2024-10-19)
[6] Learning to reason with LLMs (OpenAI o1). web. https://openai.com/index/learning-to-reason-with-llms/ (2024-09-12)
[7] Scaling of Search and Learning: A Roadmap to Reproduce o1. arxiv. https://arxiv.org/abs/2412.14135 (2024-12-14)
[8] Competitive Programming with Large Reasoning Models. arxiv. https://arxiv.org/abs/2502.06807 (2025-02-03)
[9] Enhancing Large Language Model Reasoning with Reward Models: An Analytical Survey. hf-search. https://huggingface.co/papers/2510.01925 (2025-10-02)
[10] Monte Carlo Tree Search Boosts Reasoning via Iterative Preference Learning. web. https://arxiv.org/abs/2405.00451 (2024-05-01)
[11] TreeBoN: Enhancing Inference-Time Alignment with Speculative Tree-Search and Best-of-N Sampling. web. https://arxiv.org/abs/2410.16033 (2024-10-18)
[12] Advancing Language Model Reasoning through Reinforcement Learning and Inference Scaling (T1). hf-search. https://huggingface.co/papers/2501.11651 (2025-01-20)
[13] Inference-Time Scaling for Complex Tasks: Where We Stand and What Lies Ahead. arxiv. https://arxiv.org/abs/2504.00294 (2025-03-31)
