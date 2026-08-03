from io import BytesIO

from PIL import Image

from app.infrastructure.image_preprocessor import prepare_for_inference


def test_flattens_rgba_onto_white_background() -> None:
    source = Image.new("RGBA", (32, 32), (255, 0, 0, 128))
    prepared = prepare_for_inference(source)

    assert prepared.mode == "RGB"
    pixel = prepared.getpixel((0, 0))
    assert pixel[0] > 200
    assert pixel[1] < 180


def test_keeps_rgb_unchanged_mode() -> None:
    source = Image.new("RGB", (16, 16), (0, 128, 255))
    prepared = prepare_for_inference(source)

    assert prepared.mode == "RGB"
    assert prepared.getpixel((0, 0)) == (0, 128, 255)


def test_accepts_bytes_like_pipeline_input() -> None:
    image = Image.new("RGB", (8, 8), "green")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    loaded = Image.open(BytesIO(buffer.getvalue()))
    prepared = prepare_for_inference(loaded)

    assert prepared.size == (8, 8)
