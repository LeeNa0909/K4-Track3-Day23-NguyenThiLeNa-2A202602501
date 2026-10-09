# Survey on Efficient Inference and Small Language Models

## TL;DR
- Optimized architectures for Small Language Models (SLMs) achieve up to 42% greater inference throughput and 2.1% higher accuracy compared to LLaMA-3.2 under equal training budgets [1].
- Fine-grained Mixture-of-Experts (MoE) routing outperforms dense Transformers, with the efficiency gap widening as models scale [2].
- QServe's W4A8KV4 quantization and system co-design improve maximum serving throughput by up to 3.5x for Qwen1.5-72B on L40S GPUs compared to TensorRT-LLM [3].
- TinyLlama (1.1B) shows that pretraining on approximately 1 trillion tokens for three epochs enables compact models to outperform others of comparable size [4].
- Pruning laws provide a framework to predict performance degradation and identify critical thresholds for model compression across diverse architectures [5].

## Background
The rapid growth of Large Language Models (LLMs) has led to significant challenges in deployment, particularly regarding memory and compute costs [3]. This has spurred research into Small Language Models (SLMs) and inference optimization. SLMs aim to maintain competitive capabilities with reduced parameter counts to facilitate deployment on resource-constrained hardware [4][6]. Techniques like quantization and pruning are further employed to reduce the footprint of existing models while preserving accuracy [5][7].

## Architectural Innovations and Scaling Laws
Traditional scaling laws are being refined into "conditional scaling laws" that account for architectural factors such as Grouped-Query Attention (GQA) and MLP-to-attention ratios [1]. Research suggests that optimized architectures can achieve up to 42% greater inference throughput and 2.1% higher accuracy compared to LLaMA-3.2 when trained under the same budget [1]. Furthermore, Mixture-of-Experts (MoE) is no longer exclusive to massive models; fine-grained MoE architectures outperform dense Transformers, and this performance advantage increases with model scale [2].

## Quantization and Weight Compression
Quantization remains a primary method for enabling SLM deployment on consumer hardware. Activation-aware Weight Quantization (AWQ) protects salient weights for 4-bit regimes [7]. Beyond weights, KV cache optimization is critical for long-context efficiency. The QServe system employs W4A8KV4 quantization to improve serving throughput by up to 3.5x for Qwen1.5-72B on L40S GPUs compared to TensorRT-LLM [3]. Additionally, SAW-INT4 utilizes block-diagonal Hadamard rotation to achieve near-lossless 4-bit KV-cache quantization while maintaining serving efficiency [8].

## Training Efficiency and Knowledge Distillation
SLM performance is increasingly driven by high-quality training curricula and extended token counts. TinyLlama, a 1.1B parameter model, was pretrained on around 1 trillion tokens for up to three epochs, demonstrating performance gains over existing open-source models of comparable size [4]. Data quality and post-training also play central roles; models like Phi-4 (14B) achieve strong reasoning performance through improved data curriculum and post-training refinement, moving beyond simple teacher-student distillation [6]. To further accelerate inference, student models can be trained to predict tokens for larger teachers, lowering rejection rates in speculative decoding [9].

## Parameter Pruning and Model Sparsity
Pruning offers an alternative to quantization by removing redundant parameters. Scaling laws for parameter pruning, or "pruning laws," provide a predictive framework to estimate post-pruning performance based on the unpruned model and pruning ratio [5]. Across multiple models, these laws achieve high accuracy in quantifying degradation and identifying critical thresholds beyond which recovery is infeasible, providing a principled method for efficient deployment under compute constraints [5].

## Trends and open problems
The trend in SLMs is moving toward inference-aware training, where hardware constraints like GQA and hidden size are considered during architectural search [1]. A key challenge remains the trade-off between accuracy and serving efficiency in low-bit KV-cache quantization [8]. Research into improved data curricula and synthetic data generation, as seen in the Phi-4 model, suggests that data quality is as vital as parameter scaling for reasoning tasks [6].

## References
[1] Scaling Laws Meet Model Architecture: Toward Inference-Efficient LLMs. arxiv. https://arxiv.org/abs/2510.18245 (2025-10-21)
[2] Scaling Laws for Fine-Grained Mixture of Experts. arxiv. https://arxiv.org/abs/2402.07871 (2024-02-12)
[3] QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving. hf-daily. https://huggingface.co/papers/2405.04532 (2024-05-07)
[4] TinyLlama: An Open-Source Small Language Model. arxiv. https://arxiv.org/abs/2401.02385 (2024-01-04)
[5] Scaling Laws for Parameter Pruning in LLMs. web. https://openreview.net/forum?id=1m4cKCr0vx (2024-01-01)
[6] Phi-4 Technical Report. arxiv. https://arxiv.org/abs/2412.08905 (2024-12-12)
[7] LLM Quantization: GPTQ, AWQ, and GGUF for Efficient Deployment. web. https://calmops.com/algorithms/llm-quantization-gptq-awq-gguf/ (2026-03-19)
[8] SAW-INT4: System-Aware 4-Bit KV-Cache Quantization for Real-World LLM Serving. hf-daily. https://huggingface.co/papers/2604.19157 (2026-04-21)
[9] DistillSpec: Improving Speculative Decoding via Knowledge Distillation. web. https://proceedings.iclr.cc/paper_files/paper/2024/file/8766fbc68e1ed1cdef712ce273e0a363-Paper-Conference.pdf (2024-05-01)
