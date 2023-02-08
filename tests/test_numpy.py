import json
import shutil
import tempfile
from os.path import exists, join
from unittest import TestCase

import numpy as np
from numpy.testing import assert_array_equal

from cpr.numpy.NumpySource import NumpySource
from cpr.numpy.NumpyTarget import NumpyTarget
from cpr.Serializer import cpr_serializer


class NumpyTest(TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        np.random.seed(43)
        self.data = np.random.randint(0, 255, size=(100, 100)).astype(np.uint8)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_numpy_target(self):
        serializer = cpr_serializer()

        nparr: NumpyTarget = NumpyTarget.from_path(join(self.tmp_dir, "data.npy"))

        nparr.set_data(self.data)

        encoded = serializer.dumps(nparr)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.numpy.NumpyTarget.NumpyTarget"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "data"
        assert encoded_dict["data"]["ext"] == ".npy"
        assert encoded_dict["data"]["data_hash"] == "1c4594fe64aab38f"

        assert exists(join(self.tmp_dir, "data-1c4594fe64aab38f.npy"))

        nparr_dec = serializer.loads(encoded)
        assert isinstance(nparr_dec, NumpyTarget)
        assert_array_equal(nparr_dec.get_data(), self.data)
        assert nparr_dec.get_path() == join(self.tmp_dir, "data-1c4594fe64aab38f.npy")
        assert nparr_dec.get_path() == nparr.get_path()
        assert nparr_dec.get_name() == nparr.get_name()

    def test_numpy_source(self):
        path = join(self.tmp_dir, "source_data.npy")
        np.save(path, self.data)

        nparr = NumpySource.from_path(path)

        assert_array_equal(nparr.get_data(), self.data)

        serializer = cpr_serializer()

        encoded = serializer.dumps(nparr)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())
        assert encoded_dict["__class__"] == "cpr.numpy.NumpySource.NumpySource"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "source_data"
        assert encoded_dict["data"]["ext"] == ".npy"
