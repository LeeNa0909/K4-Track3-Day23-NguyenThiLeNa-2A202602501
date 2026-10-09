# Survey of Video and Multimodal Generation

## TL;DR
- The state-of-the-art in video generation has transitioned from U-Net based architectures to scalable Diffusion Transformers (DiT), with Sora demonstrating the potential for minute-long, world-simulative synthesis [1].
- New unified frameworks address multimodal tasks: JavisGPT integrates sounding-video comprehension and generation [2], while JavisDiT++ focuses on joint audio-video generation with enhanced synchronization [3].
- Precise audio-visual synchronization is achieved through techniques like multi-stream temporal control (MTV), which separates speech, effects, and music to guide visual elements [4], and Temporal-Aligned RoPE (TA-RoPE) for fine-grained token alignment [3].
- Evaluation is evolving from Fréchet Video Distance (FVD) toward more comprehensive benchmarks that better capture temporal coherence, semantic alignment, and aesthetic quality [5].
- Key open problems include maintaining long-range temporal consistency, modeling complex physical realism, and addressing deepfake-related ethical risks [6][7].

## Background
The field of video generation has evolved rapidly, moving through stages of Generative Adversarial Networks (GANs) and Variational Autoencoders (VAEs) to the current dominance of diffusion-based models. Early foundational work like CogVideo explored large-scale pretraining using Transformers to treat video as discrete tokens [8]. However, the recent shift toward Diffusion Transformers (DiT) has unlocked new levels of scalability and visual fidelity, marked by milestones such as Sora's ability to generate one-minute sequences [1][7]. Concurrently, the rise of multimodal Large Language Models (LLMs) has enabled a transition from simple text-to-video generation to interactive, instruction-aware systems. JavisGPT, for instance, supports sounding-video comprehension alongside generation [2], while JavisDiT++ optimizes joint audio-video synthesis [3].

## Evolution of Architectures: From U-Net to DiT
The primary architectural shift in recent years is the move from 3D U-Net backbones to Diffusion Transformers (DiTs). Models like CogVideoX and Latte utilize 3D VAEs to compress video into latent representations, which are then processed by transformer blocks that disentangle or joint-process spatial and temporal information [9][10]. While early autoregressive (AR) models like CogVideo treated video frames as discrete tokens [8], contemporary approaches now integrate with diffusion processes to enhance temporal consistency [11]. Recent hybrid models focus on high-speed inference by combining causal attention with distribution matching distillation (DMD) to improve frame rates while maintaining quality [12].

## Multimodal Integration and Instruction Following
Modern video generation is increasingly multimodal, integrating audio synthesis and complex reasoning. JavisGPT is a unified multimodal LLM featuring a SyncFusion module for spatio-temporal audio-video fusion, enabling both comprehension and generation from multimodal instructions [2]. In contrast, JavisDiT++ is a dedicated joint audio-video generation (JAVG) model built upon the Wan2.1-1.3B-T2V backbone [3]. It utilizes modality-specific MoE (MS-MoE) to refine intra-modal representation while employing joint self-attention for inter-modal interaction [3]. These models facilitate diverse scenarios ranging from dialogue to proactive multimodal conversations [2].

## Audio-Visual Synchronization and Control
Ensuring temporal alignment between auditory events and visual frames is a critical challenge. The MTV framework addresses this through multi-stream temporal control, disentangling audio into speech, effects, and music to independently guide visual elements like lip motion, event timing, or environmental mood [4]. To enforce synchronization at the token level, JavisDiT++ employs Temporal-Aligned RoPE (TA-RoPE) for fine-grained audio-video synchronization [3]. By aligning generation with human preferences via techniques like AV-DPO, models improve both audio-video quality and synchronization [3].

## Trends and open problems
A prominent trend is the pursuit of "world-simulative" capabilities, where models like Sora aim to generate minute-long sequences with realistic physics [1][7]. However, significant gaps remain. Models still struggle with physical realism, often violating laws of physics during complex interactions like collisions or fluid dynamics [1][6]. Long-range temporal consistency remains an issue, with models prone to "jitter" and "object morphing" in extended clips [6]. Evaluation is also in flux; while FVD remains a standard quantitative benchmark, it is increasingly criticized for not aligning with human perception, leading to the development of more holistic metrics that evaluate clarity, coherence, and relevance [5]. Finally, ethical considerations regarding deepfakes and copyright infringement necessitate the development of robust "Responsible AI" frameworks [5].

## References
[1] From Sora What We Can See: A Survey of Text-to-Video Generation. arxiv. https://arxiv.org/abs/2405.10674 (2024-05-16)
[2] Sounding-Video Comprehension and Generation (JavisGPT). web. https://proceedings.neurips.cc/paper_files/paper/2025/file/d1422213c9f2bdd5178b77d166fba86a-Paper-Conference.pdf (2025-12-01)
[3] JavisDiT++: Unified Modeling and Optimization for Joint Audio-Video Generation. hf-search. https://huggingface.co/papers/2602.19163 (2026-02-22)
[4] Audio-Sync Video Generation with Multi-Stream Temporal Control (MTV). web. https://proceedings.neurips.cc/paper_files/paper/2025/file/133239b0506b84c802a12b0e5a764a17-Paper-Conference.pdf (2025-12-01)
[5] Text-to-video generators: a comprehensive survey. web. https://link.springer.com/article/10.1186/s40537-025-01314-3 (2025-11-14)
[6] Video diffusion generation: comprehensive review and open problems. web. https://link.springer.com/article/10.1007/s10462-025-11331-6 (2025-08-20)
[7] The Dawn of Video Generation: Preliminary Explorations with SORA-like Models. arxiv. https://arxiv.org/abs/2410.05227 (2024-10-10)
[8] CogVideo: Large-scale Pretraining for Text-to-Video Generation via Transformers. arxiv. https://arxiv.org/abs/2205.15868 (2022-05-31)
[9] CogVideoX: Text-to-Video Diffusion Models with An Expert Transformer. hf-search. https://huggingface.co/papers/2408.06072 (2024-08-12)
[10] Latte: Latent Diffusion Transformer for Video Generation. arxiv. https://arxiv.org/abs/2401.03048 (2024-01-05)
[11] ART-V: Auto-Regressive Text-to-Video Generation with Diffusion Models. arxiv. https://arxiv.org/abs/2311.18834 (2023-11-30)
[12] From Slow Bidirectional to Fast Autoregressive Video Diffusion Models. web. https://openaccess.thecvf.com/content/CVPR2025/papers/Yin_From_Slow_Bidirectional_to_Fast_Autoregressive_Video_Diffusion_Models_CVPR_2025_paper.pdf (2025-06-15)
