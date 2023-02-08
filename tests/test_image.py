import json
import shutil
import tempfile
from os.path import exists, join
from unittest import TestCase

import numpy as np
from numpy.testing import assert_array_equal
from tifffile import imwrite

from cpr.image.ImageSource import ImageSource
from cpr.image.ImageTarget import ImageTarget
from cpr.Serializer import cpr_serializer


class ImageTest(TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        np.random.seed(42)
        self.data = np.random.randint(0, 255, size=(100, 100)).astype(np.uint8)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_image_target(self):
        serializer = cpr_serializer()
        metadata = {"axes": "YX", "spacing": 0.134, "unit": "micron"}
        resolution = [1 / 0.134, 1 / 0.134]

        img: ImageTarget = ImageTarget.from_path(join(self.tmp_dir, "image.tif"))
        img.set_data(self.data)
        img.set_metadata(metadata)
        img.set_resolution(resolution)

        encoded = serializer.dumps(img)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.image.ImageTarget.ImageTarget"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "image"
        assert encoded_dict["data"]["ext"] == ".tif"
        assert encoded_dict["data"]["metadata"] == metadata
        print(type(encoded_dict["data"]["resolution"]))
        assert encoded_dict["data"]["resolution"] == resolution
        assert encoded_dict["data"]["data_hash"] == "9e9bc5323bce7d43"

        assert exists(join(self.tmp_dir, "image-9e9bc5323bce7d43.tif"))

        img_dec = serializer.loads(encoded)
        assert isinstance(img_dec, ImageTarget)
        assert_array_equal(img_dec.get_data(), self.data)
        assert img_dec.get_path() == join(self.tmp_dir, "image-9e9bc5323bce7d43.tif")
        assert img_dec.get_path() == img.get_path()
        assert img_dec.get_name() == img.get_name()
        assert img_dec.get_metadata() == img.get_metadata()
        assert img_dec.get_resolution() == img.get_resolution()

    def test_image_source(self):
        path = join(self.tmp_dir, "source_img.tif")
        imwrite(path, self.data, compression="zlib")

        img = ImageSource.from_path(path)

        assert_array_equal(img.get_data(), self.data)

        serializer = cpr_serializer()

        encoded = serializer.dumps(img)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.image.ImageSource.ImageSource"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "source_img"
        assert encoded_dict["data"]["ext"] == ".tif"

        assert exists(join(self.tmp_dir, "source_img.tif"))

        img_dec = serializer.loads(encoded)
        assert isinstance(img_dec, ImageSource)
        assert_array_equal(img_dec.get_data(), self.data)
        assert img_dec.get_path() == join(self.tmp_dir, "source_img.tif")
        assert img_dec.get_path() == img.get_path()
        assert img_dec.get_name() == img.get_name()
