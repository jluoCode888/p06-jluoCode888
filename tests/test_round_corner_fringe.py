# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image
from tornado.testing import gen_test

from thumbor.config import Config
from thumbor.context import Context, RequestParameters
from thumbor.importer import Importer
from thumbor.testing import FilterTestCase
from thumbor.transformer import Transformer


class RoundCornerFringeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_round_corner_has_no_dark_fringe(self):
        config = Config(
            FILTERS=["thumbor.filters.round_corner"],
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=self.get_fixture_root_path(),
        )
        importer = Importer(config)
        importer.import_modules()

        context = Context(config=config, importer=importer)
        context.request = RequestParameters()
        context.request.engine = context.modules.engine
        context.request.width = 100
        context.request.height = 100
        context.transformer = Transformer(context)

        source = Image.new("RGB", (100, 100), (200, 200, 200))
        buffer = BytesIO()
        source.save(buffer, "PNG")
        context.request.engine.load(buffer.getvalue(), ".png")

        round_corner_cls = importer.filters[0]
        round_corner_cls.pre_compile()

        # radius 30, fill white, transparent corners
        await round_corner_cls("round_corner(30,255,255,255,1)", context=context).run()

        image = context.request.engine.image.convert("RGBA")

        # Outside the arc at the corner: fully transparent.
        assert image.getpixel((0, 0))[3] == 0, image.getpixel((0, 0))
        # Inside the picture: source color, fully opaque.
        assert image.getpixel((50, 50)) == (200, 200, 200, 255), image.getpixel(
            (50, 50)
        )

        corner = [
            image.getpixel((x, y)) for x in range(30) for y in range(30)
        ]
        visible = [p for p in corner if p[3] > 0]

        # No pixel on the arc may be darkened toward black.
        darkest = min(min(p[:3]) for p in visible)
        assert darkest >= 180, darkest

        # The arc is smoothed through alpha: some edge pixels are partly
        # transparent rather than fully opaque.
        partial = [p for p in visible if p[3] < 255]
        assert partial, "no partially transparent pixels on the arc"
