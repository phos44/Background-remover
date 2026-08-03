from PIL import Image, ImageOps


def prepare_for_inference(image: Image.Image) -> Image.Image:
    """Normalize image before segmentation to avoid alpha-channel artifacts."""
    image = ImageOps.exif_transpose(image)

    if image.mode in {"RGBA", "LA", "PA"}:
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        flattened = Image.alpha_composite(background, image.convert("RGBA"))
        return flattened.convert("RGB")

    if image.mode != "RGB":
        return image.convert("RGB")

    return image
