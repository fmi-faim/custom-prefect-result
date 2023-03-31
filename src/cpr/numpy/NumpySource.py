import numpy as np

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

    def _read_data(self):
        return np.load(self.get_path())
