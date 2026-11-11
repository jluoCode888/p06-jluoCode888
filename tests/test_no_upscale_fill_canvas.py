# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import shutil
import tempfile
from io import BytesIO
from os.path import join

from PIL import Image

from tests.base import TestCase
from thumbor.config import Config


class NoUpscaleFillCanvasTestCase(TestCase):
    def get_config(self):
        self.source_root = tempfile.mkdtemp()
        Image.new("RGB", (80, 50), (0, 0, 255)).save(
            join(self.source_root, "small.png")
        )
        return Config(
            FILTERS=[
                "thumbor.filters.fill",
                "thumbor.filters.no_upscale",
            ],
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=self.source_root,
            ALLOW_UNSAFE_URL=True,
        )

    def tearDown(self):
        shutil.rmtree(self.source_root, ignore_errors=True)
        super().tearDown()

    def test_fill_with_no_upscale_keeps_fit_in_canvas(self):
        response = self.fetch(
            "/unsafe/fit-in/300x300/filters:fill(red):no_upscale()/small.png"
        )

        assert response.code == 200, response.code
        image = Image.open(BytesIO(response.body)).convert("RGB")
        assert image.size == (300, 300), image.size
        assert image.getpixel((0, 0)) == (255, 0, 0), image.getpixel((0, 0))
