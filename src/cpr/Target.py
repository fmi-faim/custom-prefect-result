import gc
from os.path import join

from cpr.Resource import Resource


class Target(Resource):
    """Base class for Targets.

    A target has an additional data_hash attribute, which is used to track
    data uniqueness.
    """

    data_hash: str

    def __init__(
        self, location: str, name: str, ext: str, data_hash: str = None, **kwargs
    ):
        """
        Parameters
        ----------
        location
            Where the data is stored
        name
            File name of the data
        ext
            File extension of the data
        data_hash
            Data hash, by default None
        """
        self.data_hash = data_hash
        super(Target, self).__init__(location=location, name=name, ext=ext, **kwargs)

    def compute_data_hash(self):
        """Compute and set current data_hash."""
        if self._data is not None:
            self.data_hash = self._hash_data(self._data)

    def set_data(self, data):
        """Set data and compute data_hash.

        Parameters
        ----------
        data
            Data stored with this Target
        """
        self._data = data

    def _hash_data(self, data) -> str:
        ...

    def _write_data(self):
        ...

    def serialize(self):
        """Persist data and serialize to JSON serializable dict."""
        self.compute_data_hash()
        self._write_data()
        del self._data
        gc.collect()
        self._data = None
        d = super(Target, self).serialize()
        d["data_hash"] = self.data_hash
        return d

    def get_path(self):
        """Get unique file-path.

        This file-path is unique because the data_hash is inserted. This
        allows to reuse this Target with different data. Everytime the
        Target gets serialized a new file is persisted.

        Returns
        -------
        location/name-data_hash.ext
        """
        assert (
            self.data_hash is not None
        ), "Data hash is None. Please call set_data first."
        return join(self.location, f"{self.name}-{self.data_hash}{self.ext}")
