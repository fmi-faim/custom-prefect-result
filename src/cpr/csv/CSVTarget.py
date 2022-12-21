from os.path import exists

import pandas as pd
import xxhash
from pandas.core.util.hashing import hash_pandas_object

from cpr.Target import Target


class CSVTarget(Target):
    def get_data(self):
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = pd.read_csv(self.get_path(), index_col=0)
            assert self._hash_data(self._data) == self.data_hash, (
                "Loaded csv has a different hash. This data is either "
                "from a different run or corrupted."
            )

        return self._data

    def _hash_data(self, a):
        return xxhash.xxh3_64(hash_pandas_object(a).values.tobytes()).hexdigest()

    def serialize(self):
        if self._data is not None:
            self._data.to_csv(self.get_path())

        return super(CSVTarget, self).serialize()
