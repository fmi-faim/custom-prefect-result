import json
import shutil
import tempfile
from os.path import exists, join
from unittest import TestCase

import pandas as pd

from cpr.csv.CSVSource import CSVSource
from cpr.csv.CSVTarget import CSVTarget
from cpr.Serializer import cpr_serializer


class CSVTest(TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        self.data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_csv_target(self):
        serializer = cpr_serializer()

        csv = CSVTarget.from_path(join(self.tmp_dir, "test.csv"))
        csv.set_data(self.data)

        encoded = serializer.dumps(csv)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())

        assert encoded_dict["__class__"] == "cpr.csv.CSVTarget.CSVTarget"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "test"
        assert encoded_dict["data"]["ext"] == ".csv"
        assert encoded_dict["data"]["data_hash"] == "b44f1e9ba85e9b4d"

        assert exists(join(self.tmp_dir, "test-b44f1e9ba85e9b4d.csv"))

        csv_dec = serializer.loads(encoded)
        assert isinstance(csv_dec, CSVTarget)
        assert all(csv_dec.get_data() == self.data)
        assert csv_dec.get_path() == join(self.tmp_dir, "test-b44f1e9ba85e9b4d.csv")
        assert csv_dec.get_path() == csv.get_path()
        assert csv_dec.get_name() == csv.get_name()

    def test_csv_source(self):
        path = join(self.tmp_dir, "source_table.csv")
        self.data.to_csv(path, index=True)

        csv = CSVSource.from_path(path)

        assert all(csv.get_data() == self.data)
        serializer = cpr_serializer()

        encoded = serializer.dumps(csv)

        assert isinstance(encoded, bytes)

        encoded_dict = json.loads(encoded.decode())

        assert encoded_dict["__class__"] == "cpr.csv.CSVSource.CSVSource"
        assert encoded_dict["data"]["location"] == self.tmp_dir
        assert encoded_dict["data"]["name"] == "source_table"
        assert encoded_dict["data"]["ext"] == ".csv"

        assert exists(join(self.tmp_dir, "source_table.csv"))

        csv_dec = serializer.loads(encoded)
        assert isinstance(csv_dec, CSVSource)
        assert all(csv_dec.get_data() == self.data)
        assert csv_dec.get_path() == join(self.tmp_dir, "source_table.csv")
        assert csv_dec.get_path() == csv.get_path()
        assert csv_dec.get_name() == csv.get_name()
