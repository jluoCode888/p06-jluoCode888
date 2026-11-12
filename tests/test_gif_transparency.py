from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from thumbor.config import Config
from thumbor.engines.pil import Engine


def make_transparent_palette_gif():
    img = Image.new("P", (40, 40), 0)
    img.putpalette([255, 0, 0, 0, 0, 255] + [0, 0, 0] * 254)
    for x in range(20, 40):
        for y in range(40):
            img.putpixel((x, y), 1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def test_resized_gif_keeps_transparency_index():
    config = Config()
    config.ALLOW_ANIMATED_GIFS = False
    config.PILLOW_PRESERVE_INDEXED_MODE = True
    engine = Engine(SimpleNamespace(config=config, modules=None))
    engine.extension = ".gif"
    engine.image = engine.create_image(make_transparent_palette_gif())

    engine.resize(20, 20)
    data = engine.read(".gif")

    out = Image.open(BytesIO(data))
    assert "transparency" in out.info
    alpha = out.convert("RGBA").getchannel("A")
    assert alpha.getextrema()[0] == 0
