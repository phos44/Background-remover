from dataclasses import dataclass


@dataclass(frozen=True)
class BackgroundRemovalOptions:
    alpha_matting: bool = False
    post_process_mask: bool = True
    alpha_matting_foreground_threshold: int = 240
    alpha_matting_background_threshold: int = 10
    alpha_matting_erode_size: int = 10

