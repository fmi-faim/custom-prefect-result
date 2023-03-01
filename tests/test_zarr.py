import json
import shutil
import tempfile
from os.path import join
from unittest import TestCase

import numpy as np
import zarr
from numpy.testing import assert_array_equal
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image

from cpr.Serializer import cpr_serializer
from cpr.zarr.ZarrSource import ZarrSource


class ZarrTest(TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        np.random.seed(43)
        self.data = np.random.randint(0, 255, size=(3, 100, 100)).astype(np.uint8)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_zarr_source(self):
        path = join(self.tmp_dir, "test.zarr")

        store = parse_url(path=path, mode="w").store
        zdata = zarr.group(store=store)
        write_image(
            self.data,
            group=zdata,
            axes=[
                {"name": "z", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
                {"name": "x", "type": "space", "unit": "micrometer"},
            ],
        )

        z1 = ZarrSource.from_path(path, "0", [1, 10], [2, -10])

        assert_array_equal(z1.get_data(), self.data[1:2, 10:-10])

        serializer = cpr_serializer()

        encoded = serializer.dumps(z1)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.zarr.ZarrSource.ZarrSource"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "test"
        assert encoded_dict["data"]["ext"] == ".zarr"
        assert encoded_dict["data"]["group"] == "0"
        assert encoded_dict["data"]["slices_start"] == [1, 10]
        assert encoded_dict["data"]["slices_stop"] == [2, -10]

    def test_zarr_source_empty_slice(self):
        path = join(self.tmp_dir, "test.zarr")

        store = parse_url(path=path, mode="w").store
        zdata = zarr.group(store=store)
        write_image(
            self.data,
            group=zdata,
            axes=[
                {"name": "z", "type": "space", "unit": "micrometer"},
                {"name": "y", "type": "space", "unit": "micrometer"},
                {"name": "x", "type": "space", "unit": "micrometer"},
            ],
        )

        z1 = ZarrSource.from_path(path, "0")
        serializer = cpr_serializer()

        encoded = serializer.dumps(z1)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.zarr.ZarrSource.ZarrSource"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "test"
        assert encoded_dict["data"]["ext"] == ".zarr"
        assert encoded_dict["data"]["group"] == "0"
        assert encoded_dict["data"]["slices_start"] == []
        assert encoded_dict["data"]["slices_stop"] == []
        assert z1._data is None
        assert isinstance(z1.get_data(), zarr.core.Array)
        assert z1._data is not None
