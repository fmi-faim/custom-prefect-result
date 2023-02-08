from os.path import exists

import numpy as np
import xxhash
from numpy._typing import ArrayLike

from cpr.Target import Target


class NumpyTarget(Target):
    """Persists numpy array data and serializes a JSON serializable dictionary.

    An NumpyTarget must have a file-location, -name and -extension. With
    set_data a numpy array can be provided to the NumpyTarget. This call
    will compute a unique data_hash for the provided data.

    When serialize() is called on an NumpyTarget the data is written to
    location/name-{data_hash}.npz.

    When get_data() is called the data is retrieved from its location and
    hash_data is compared to the hash of the loaded data.
    """

    def __init__(
        self,
        location: str,
        name: str,
        ext: str,
        data_hash: str = None,
    ):
        """
        Parameters
        ----------
        location
            Where the image file is stored
        name
            Name of the image file
        ext
            File extension must be .npy
        """
        assert ext == ".npy", "`ext` must be .npy."
        super(NumpyTarget, self).__init__(
            location=location,
            name=name,
            ext=ext,
            data_hash=data_hash,
        )

    def get_data(self) -> ArrayLike:
        """Access numpy array data.

        The data is cached by this function.

        Returns
        -------
        Array data.
        """
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = np.load(self.get_path())
            assert self._hash_data(self._data) == self.data_hash, (
                "Loaded data has a different hash. This data is either "
                "from a different run or corrupted."
            )

        return self._data

    def _hash_data(self, a) -> str:
        data = bytes()
        data += str(a.dtype).encode("ascii")
        data += b","
        data += str(a.shape).encode("ascii")
        data += b","
        data += a.tobytes()
        return xxhash.xxh3_64(data).hexdigest()

    def _write_data(self):
        if self._data is not None:
            np.save(self.get_path(), self._data)
