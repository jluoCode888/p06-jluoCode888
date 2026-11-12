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


class ExtremeAspectCropTestCase(TestCase):
    def get_config(self):
        self.source_root = tempfile.mkdtemp()
        Image.new("RGBA", (1, 1), (255, 0, 0, 255)).save(
            join(self.source_root, "one.png")
        )
        return Config(
            LOADER="thumbor.loaders.file_loader",
            FILE_LOADER_ROOT_PATH=self.source_root,
            ALLOW_UNSAFE_URL=True,
        )

    def tearDown(self):
        shutil.rmtree(self.source_root, ignore_errors=True)
        super().tearDown()

    def test_one_pixel_source_at_extreme_ratio_is_not_empty(self):
        response = self.fetch("/unsafe/50x25/one.png")

        assert response.code == 200, response.code
        image = Image.open(BytesIO(response.body)).convert("RGBA")
        assert image.size == (50, 25), image.size
        center = image.getpixel((25, 12))
        assert center[3] == 255, center
