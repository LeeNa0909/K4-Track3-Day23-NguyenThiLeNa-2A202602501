# Survey of Video and Multimodal Generation

## TL;DR
- The state-of-the-art in video generation has transitioned from U-Net based architectures to scalable Diffusion Transformers (DiT), with Sora demonstrating the potential for minute-long, world-simulative synthesis [1][2][3].
- Unified frameworks (e.g., JavisGPT, JavisDiT++) now integrate video understanding and generation, supporting complex instruction following and interleaved multimodal streams [4][5].
- Precise audio-visual synchronization is achieved through techniques like multi-stream temporal control (MTV), which separates speech, effects, and music, and Temporal-Aligned RoPE (TA-RoPE) [4][6].
- Evaluation is evolving from Fréchet Video Distance (FVD) toward more comprehensive benchmarks that better capture temporal coherence, semantic alignment, and aesthetic quality [7].
- Key open problems include maintaining long-range temporal consistency, modeling complex physical realism, and addressing deepfake-related ethical risks [8][9].

## Background
The field of video generation has evolved rapidly, moving through stages of Generative Adversarial Networks (GANs) and Variational Autoencoders (VAEs) to the current dominance of diffusion-based models. Early foundational work like CogVideo explored large-scale pretraining using Transformers to treat video as discrete tokens [10]. However, the recent shift toward Diffusion Transformers (DiT) has unlocked new levels of scalability and visual fidelity, marked by milestones such as Sora's ability to generate minute-level video sequences [3][9]. Concurrently, the rise of multimodal Large Language Models (LLMs) has enabled a transition from simple text-to-video generation to interactive, instruction-aware systems capable of simultaneous video and audio synthesis [4][5].

## Evolution of Architectures: From U-Net to DiT
The primary architectural shift in recent years is the move from 3D U-Net backbones to Diffusion Transformers (DiTs). Models like CogVideoX and Latte utilize 3D VAEs to compress video into latent representations, which are then processed by transformer blocks that disentangle or joint-process spatial and temporal information [1][2]. While early autoregressive (AR) models like CogVideo treated video frames as discrete tokens [10], contemporary approaches now integrate with diffusion processes to enhance temporal consistency [11]. Recent hybrid models focus on high-speed inference by combining causal attention with distribution matching distillation (DMD) to improve frame rates while maintaining quality [12].

## Multimodal Integration and Instruction Following
Modern video generation is increasingly multimodal, integrating audio synthesis and complex reasoning. Unified frameworks such as JavisGPT and JavisDiT++ bridge comprehension and generation [4][5]. JavisDiT++ is built upon the Wan2.1-1.3B-T2V backbone and utilizes modality-specific MoE (MS-MoE) to refine intra-modal representation while employing joint self-attention for inter-modal interaction [4]. JavisGPT features a SyncFusion module for spatio-temporal audio-video fusion to bridge a pretrained generator [5]. These models facilitate training for diverse scenarios ranging from dialogue to human-centric generation [5].

## Audio-Visual Synchronization and Control
Ensuring temporal alignment between auditory events and visual frames is a critical challenge. The MTV framework addresses this through multi-stream temporal control, disentangling audio into speech, effects, and music to independently guide visual elements like lip motion or environmental mood [6]. To enforce synchronization, researchers employ Temporal-Aligned RoPE (TA-RoPE) for fine-grained audio-video token alignment [4]. By aligning generation with human preferences via techniques like AV-DPO, models improve both audio-video quality and synchronization [4].

## Trends and open problems
A prominent trend is the pursuit of "world-simulative" capabilities, where models like Sora aim to generate minute-long sequences with realistic physics [3][9]. However, significant gaps remain. Models still struggle with physical realism, often violating laws of physics during complex interactions like collisions or fluid dynamics [3][8]. Long-range temporal consistency remains an issue, with models prone to "jitter" and "object morphing" in extended clips [8]. Evaluation is also in flux; while FVD remains a standard quantitative benchmark, it is increasingly criticized for not aligning with human perception, leading to the development of more holistic metrics that evaluate clarity, coherence, and relevance [7]. Finally, ethical considerations regarding deepfakes and copyright infringement necessitate the development of robust "Responsible AI" frameworks [7].

## References
[1] CogVideoX: Text-to-Video Diffusion Models with An Expert Transformer. hf-search. https://huggingface.co/papers/2408.06072 (2024-08-12)
[2] Latte: Latent Diffusion Transformer for Video Generation. arxiv. https://arxiv.org/abs/2401.03048 (2024-01-05)
[3] From Sora What We Can See: A Survey of Text-to-Video Generation. arxiv. https://arxiv.org/abs/2405.10674 (2024-05-16)
[4] JavisDiT++: Unified Modeling and Optimization for Joint Audio-Video Generation. hf-search. https://huggingface.co/papers/2602.19163 (2026-02-22)
[5] Sounding-Video Comprehension and Generation (JavisGPT). web. https://proceedings.neurips.cc/paper_files/paper/2025/file/d1422213c9f2bdd5178b77d166fba86a-Paper-Conference.pdf (2025-12-01)
[6] Audio-Sync Video Generation with Multi-Stream Temporal Control (MTV). web. https://proceedings.neurips.cc/paper_files/paper/2025/file/133239b0506b84c802a12b0e5a764a17-Paper-Conference.pdf (2025-12-01)
[7] Text-to-video generators: a comprehensive survey. web. https://link.springer.com/article/10.1186/s40537-025-01314-3 (2025-11-14)
[8] Video diffusion generation: comprehensive review and open problems. web. https://link.springer.com/article/10.1007/s10462-025-11331-6 (2025-08-20)
[9] The Dawn of Video Generation: Preliminary Explorations with SORA-like Models. arxiv. https://arxiv.org/abs/2410.05227 (2024-10-10)
[10] CogVideo: Large-scale Pretraining for Text-to-Video Generation via Transformers. arxiv. https://arxiv.org/abs/2205.15868 (2022-05-31)
[11] ART-V: Auto-Regressive Text-to-Video Generation with Diffusion Models. arxiv. https://arxiv.org/abs/2311.18834 (2023-11-30)
[12] From Slow Bidirectional to Fast Autoregressive Video Diffusion Models. web. https://openaccess.thecvf.com/content/CVPR2025/papers/Yin_From_Slow_Bidirectional_to_Fast_Autoregressive_Video_Diffusion_Models_CVPR_2025_paper.pdf (2025-06-15)
