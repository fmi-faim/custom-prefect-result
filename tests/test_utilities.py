import os
import shutil
from os.path import join
from unittest import TestCase

import numpy as np

from cpr.image.ImageTarget import ImageTarget
from cpr.utilities.utilities import hash_objects


class UtilitiesTest(TestCase):
    def setUp(self) -> None:
        os.makedirs("/tmp/cpr-utilities-test-case", exist_ok=True)
        self.tmp_dir = "/tmp/cpr-utilities-test-case"
        np.random.seed(42)
        self.data = np.random.randint(0, 255, size=(100, 100)).astype(np.uint8)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_hash_objects(self):
        img = ImageTarget.from_path(join(self.tmp_dir, "image.tif"))
        img.set_data(self.data)

        h = hash_objects(img)
        assert h == "2390ea40fa8feefda37bd591daaca846"
