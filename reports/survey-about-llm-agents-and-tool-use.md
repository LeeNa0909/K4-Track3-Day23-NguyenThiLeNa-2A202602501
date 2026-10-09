# Survey of LLM Agents and Tool Use Architectures

## TL;DR
*   LLM agent architectures have transitioned from static prompting to modular systems integrating planning, memory, and active tool orchestration [1][2].
*   Tool-use mechanisms are categorized into three primary triggers: in-generation monitoring, iterative reasoning-action loops (ReAct), and confidence-based thresholding [1][3].
*   Modern planning strategies employ search-based methods like Tree-of-Thoughts (ToT) and Monte Carlo Tree Search (MCTS) or delegate to external symbolic solvers like PDDL [4][5].
*   The "Tool Maker" paradigm allows agents to autonomously generate code-based APIs (e.g., CREATOR, LATM) when existing toolsets are insufficient [5][3][6].
*   Security remains a critical bottleneck, with prompt injection and tool-mediated hijacking dominating threat surfaces, often evaluated via Attack Success Rate (ASR) [7][8].

## Background
The evolution of Large Language Models (LLMs) from passive text predictors to autonomous agents marks a paradigm shift in artificial intelligence. Early efforts focused on in-context learning and zero-shot reasoning, but these were limited by the "closed-world" nature of model weights. To overcome this, researchers developed architectures that allow LLMs to interact with external environments. This integration, often referred to as "tool learning," enables models to invoke APIs, execute code, and retrieve real-time information, effectively transforming them into agentic cores capable of goal-directed behavior [2][3][6].

## Core Architectures and Planning Frameworks
Modern LLM agents are typically structured around four modular pillars: Profile Definition, Memory, Planning, and Action Execution [2][5]. Within this structure, planning has emerged as a diverse field ranging from feedback-free strategies like Chain-of-Thought (CoT) to complex, feedback-based search methods [2][4].

*   **Decomposition and Search:** Systems like Tree-of-Thoughts (ToT) and Graph-of-Thoughts (GoT) enable agents to explore multiple reasoning paths [1][4]. More recent approaches, such as HyperAgent, utilize tool-schema hypergraphs to model complex tool relationships directly at the schema level [9].
*   **External Solver Integration:** Frameworks like LLM+P and LLM+PDDL bridge the gap between neural and symbolic AI by converting natural language goals into formal Planning Domain Definition Language (PDDL), which is then solved by classical external planners to ensure plan feasibility [4].
*   **Self-Reflection:** Iterative loops (e.g., Reflexion, Self-Refine) allow agents to evaluate their own previous actions or tool outputs to correct errors and refine subsequent plans [4].

## Tool-Use Paradigms and API Integration
The shift from static Retrieval-Augmented Generation (RAG) to active tool orchestration is governed by a multi-stage operational pipeline: planning, selection, execution, and feedback processing [1][6].

*   **Invocation Mechanisms:** Active tool use is triggered via three main methods: in-generation triggers (monitoring tokens for stop sequences), reasoning-acting cycles (e.g., ReAct), and confidence-based invocation where a tool is called only when model certainty falls below a threshold [1][3].
*   **Tool Learning and Creation:** While early methods relied on fine-tuning (e.g., Toolformer), recent work emphasizes zero-shot use through detailed API documentation [3]. In the "Tool Maker" paradigm (e.g., LATM, CREATOR), agents act as creators by synthesizing their own executable code or APIs to solve novel tasks that lack pre-defined tools [5][6].
*   **Scaling and Standardization:** Research has shown models like Gorilla can be grounded in documentation to interact with large repositories of RESTful APIs [2]. Emerging standards like the Model Context Protocol (MCP) aim to provide secure, interoperable links between LLMs and external data [10].

## Evaluation Benchmarks and Metrics
Evaluation has matured from rule-based synthetic tasks to "live," interactive environments that test long-horizon reasoning.

*   **Benchmarks:** Early benchmarks like ToolBench have been superseded by more complex suites such as GAIA (multi-step reasoning) and SWE-bench (software engineering) [10]. Modern interactive benchmarks like Agent-SafetyBench reveal that current models still struggle with safety in dynamic tool environments [8].
*   **Metrics:** There is a significant imbalance in current evaluation practices. While Attack Success Rate (ASR) is widely reported (cited in 129 papers in one meta-analysis), deployment-critical metrics like Utility, Latency, and Cost are rarely prioritized [7].

## Trends and open problems
The field is moving toward multi-agent coordination and multimodal tool use to resolve ambiguities in natural language intent [2][3]. A major trend is the development of "prospective" safety benchmarks (e.g., SafeToolBench) that attempt to detect irreversible harms, such as property damage or privacy leaks, before a tool is executed [7]. Open problems include the lack of standardized abstraction layers for universal APIs, high token costs in long-horizon planning, and the vulnerability of agents to persistent state corruption and multi-agent threat propagation [6][7].

## References
[1] A Review of Prominent Paradigms for LLM-Based Agents: Tool Use, Planning, and Feedback Learning. web. https://arxiv.org/abs/2406.05804 (2024-06-10)
[2] From Language to Action: A Review of Large Language Models as Autonomous Agents and Tool Users. hf-search. https://huggingface.co/papers/2508.17281 (2025-08-17)
[3] LLM-Based Agents for Tool Learning: A Survey. web. https://link.springer.com/article/10.1007/s41019-025-00296-9 (2025-06-26)
[4] Understanding the planning of LLM agents: A survey. arxiv. https://arxiv.org/abs/2402.02716 (2024-02-05)
[5] Large Language Model Agent: A Survey on Methodology, Applications and Challenges. web. https://arxiv.org/abs/2503.21460 (2025-03-01)
[6] Tool learning with language models: a comprehensive survey of methods, pipelines, and benchmarks. web. https://link.springer.com/article/10.1007/s44336-025-00024-x (2025-11-27)
[7] Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation. arxiv. https://arxiv.org/abs/2606.10749 (2026-06-15)
[8] Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents. hf-search. https://huggingface.co/papers/2410.02644 (2024-10-03)
[9] HyperAgent: Planning and Acting over Tool-Schema Hypergraphs. hf-search. https://huggingface.co/papers/2608.02650 (2026-07-31)
[10] Evaluation and Benchmarking of LLM Agents: A Survey. web. https://dl.acm.org/doi/10.1145/3711896.3736570 (2025-08-03)
