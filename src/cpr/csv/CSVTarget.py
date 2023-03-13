from os.path import exists

import pandas as pd
import xxhash
from pandas.core.util.hashing import hash_pandas_object

from cpr.Target import Target


class CSVTarget(Target):
    """Persists tabular data to csv and serializes a JSON serializable
    dictionary.

    A CSVTarget must have a file-location, -name and -extension (extenstion
    must be csv). With set_data a pandas.DataFrame can be provided. This
    will compute a unique data_hash for the provided DataFrame.

    When serialize() is called on a CSVTarget the DataFrame is saved as csv to
    location/name-{data_hash}.ext.

    When get_data() is called the data is retrieved from its location and
    hash_data is compared to the hash of the loaded data.
    """

    def __init__(
        self,
        location: str,
        name: str,
        ext: str = ".csv",
        data_hash: str = None,
    ):
        """
        Parameters
        ----------
        location
            Where the csv is stored
        name
            Name of the csv file
        ext
            File extension, must be csv
        data_hash
            DataFrame hash, by default None
        """
        assert ext == ".csv", "Extension must be .csv."
        super(CSVTarget, self).__init__(
            location=location,
            name=name,
            ext=ext,
            data_hash=data_hash,
        )

    def get_data(self) -> pd.DataFrame:
        """Access DataFrame.

        The DataFrame is cached by this call.

        Returns
        -------
        DataFrame
        """
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

    def _write_data(self):
        if self._data is not None:
            self._data.to_csv(self.get_path(), mode="w")
