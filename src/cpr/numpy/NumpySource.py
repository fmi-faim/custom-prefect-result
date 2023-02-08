from os.path import exists

import numpy as np
from numpy._typing import ArrayLike

from cpr.Resource import Resource


class NumpySource(Resource):
    """Provides access to a numpy array file."""

    def __init__(self, location: str, name: str, ext: str):
        """
        Parameters
        ----------
        location
            Where the image file is stored
        name
            Name of the image file
        ext
            File extension
        """
        assert ext in [".npz", ".npy"], "Extension must be .npz or .npy."
        super(NumpySource, self).__init__(
            location=location,
            name=name,
            ext=ext,
        )

    def get_data(self) -> ArrayLike:
        """Access numpy array data.

        The data is cached by this function.

        Returns
        -------
        Array data
        """

        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not exist."

            self._data = np.load(self.get_path())

        return self._data
