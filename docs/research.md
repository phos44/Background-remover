# Research and SOTA analysis

## Problem

Background removal is usually a binary foreground extraction problem with an alpha-matte output. The production result should preserve object edges, hair, translucent regions and holes while keeping inference latency and memory use predictable.

## Classical methods

Classical methods are useful as historical baselines or for constrained scenes, but they are brittle for general user uploads.

| Approach | Strengths | Weaknesses |
| --- | --- | --- |
| Chroma key / color thresholding | Very fast, CPU-only, deterministic | Requires controlled background color and lighting |
| GrabCut / graph cuts | Good for simple objects with user hints | Needs initialization, weak with hair and low contrast |
| Watershed / edge-based segmentation | Interpretable and cheap | Over-segments textured images |
| Traditional matting with trimap | Accurate when a trimap is available | User interaction or upstream trimap generation is required |

## Deep learning families

| Family | Examples | Best use |
| --- | --- | --- |
| Salient object detection | U^2-Net, IS-Net | Generic single/few foreground object extraction |
| Portrait matting | MODNet, P3M-Net | Real-time human portrait/video matting |
| Dichotomous image segmentation | DIS/IS-Net, FP-DIS, MVANet, BiRefNet, DCENet | Category-agnostic high-detail foreground masks |
| Foundation/interactive matting | SAM-based matting, SAMA, ZIM | Promptable or zero-shot workflows where compute budget is higher |
| Commercial/source-available background models | BRIA RMBG 1.4/2.0 | Product/e-commerce quality, license must be checked |

## Recent SOTA notes

- DIS5K formalized high-accuracy dichotomous image segmentation for category-agnostic foreground extraction and positioned it as directly useful for image background removal.
- U^2-Net introduced a nested U-structure for salient object detection that captures multi-scale context while keeping compute moderate.
- MODNet is trimap-free and real-time for portraits; it is excellent for humans but narrower than generic product/object uploads.
- FP-DIS adds frequency priors to recover fine boundaries on DIS5K.
- MVANet uses multi-view aggregation and reports strong accuracy/speed on DIS-style foreground extraction.
- BiRefNet targets high-resolution dichotomous segmentation with localization and reconstruction modules plus bilateral references; public weights are available on Hugging Face.
- BRIA RMBG 1.4/2.0 are practical background-removal models trained for broad commercial image categories. RMBG 1.4 has a compact 44.1M parameter model card; RMBG 2.0 is exposed through BRIA/FAL endpoints and Hugging Face demos, with commercial licensing constraints.
- SAMA and ZIM show the research direction: unified segmentation and matting or zero-shot matting on top of foundation segmentation models. They are promising, but heavier and less convenient for a simple self-hosted app.

## Model comparison

| Model | Accuracy | Speed/cost | Maturity | Fit for this project |
| --- | --- | --- | --- | --- |
| GrabCut | Low-medium | Very low CPU | Stable | Baseline only |
| MODNet | High for portraits | Very fast | Mature | Too domain-specific |
| U^2-Net via rembg | Good general quality | Moderate CPU, good ONNX deployment | Very mature Python package | Best default for a local production assignment |
| IS-Net / DIS | Higher boundary quality | Higher cost | Research-oriented | Good future adapter |
| BiRefNet | SOTA-level DIS quality | Higher memory/latency, larger model | Strong open weights | Best quality candidate when GPU is available |
| BRIA RMBG 1.4/2.0 | Very high practical quality | Higher dependency/licensing complexity | Mature model cards/services | Good enterprise option; license-sensitive |
| SAMA/ZIM | Very high/promptable | Heavy | Emerging 2025-2026 research | Not ideal for first production release |

## Selected model

The application uses `rembg` with `u2net` by default.

Rationale:

- stable Python integration with ONNX Runtime;
- works on CPU, so the app is usable on developer machines without CUDA;
- good quality for generic foreground extraction;
- smaller operational risk than wiring a large research repository into the request path;
- clean adapter boundary allows replacing the model with BiRefNet, RMBG, or a hosted inference service without changing the API or UI.

For a GPU production deployment focused on maximum quality, the next recommended adapter is BiRefNet or BRIA RMBG 2.0 after confirming license and latency requirements.

## Sources

- U^2-Net paper: https://huggingface.co/papers/2005.09007
- DIS project and DIS5K: https://xuebinqin.github.io/dis/
- BiRefNet paper/model: https://huggingface.co/ZhengPeng7/BiRefNet-DIS5K
- BiRefNet repository: https://github.com/ZhengPeng7/BiRefNet
- BRIA RMBG 1.4 model card: https://huggingface.co/briaai/RMBG-1.4
- BRIA RMBG 2.0 demo/model card entry: https://huggingface.co/briaai/RMBG-2.0
- MODNet repository: https://github.com/ZHKKKe/MODNet
- DCENet paper: https://www.sciencedirect.com/science/article/pii/S1077314224002030
- SAMA AAAI 2026: https://ojs.aaai.org/index.php/AAAI/article/view/37382
- ZIM ICCV 2025: https://openaccess.thecvf.com/content/ICCV2025/html/Kim_ZIM_Zero-Shot_Image_Matting_for_Anything_ICCV_2025_paper.html

