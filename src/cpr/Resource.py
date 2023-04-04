from abc import ABC
from os.path import exists, join, split, splitext
from typing import Any


class Resource(ABC):
    """Base class for Sources and Targets."""

    location: str
    name: str
    ext: str
    _data: Any

    def __init__(self, location: str, name: str, ext: str, **kwargs):
        """
        Parameters
        ----------
        location
            Where the data is stored
        name
            File name of the data
        ext
            File extension of the data
        kwargs
        """
        self.location = location
        self.name = name
        self.ext = ext
        self._data = None
        super(Resource, self).__init__(**kwargs)

    @classmethod
    def from_path(cls, path: str):
        """Create new instance form file-path.

        Parameters
        ----------
        path
            Path to the file

        Returns
        -------
        A new instance
        """
        location, file_name = split(path)
        name, ext = splitext(file_name)
        return cls(location=location, name=name, ext=ext)

    def get_data(self, cache=False):
        """Access the data."""
        assert exists(self.get_path()), (
            f"Result does not exist at " f"{self.get_path()}."
        )
        if cache:
            self._data = self._read_data()
            return self._data
        else:
            return self._read_data()

    def _read_data(self):
        ...

    def get_name(self) -> str:
        """Get file name.

        Returns
        -------
        File name without extension
        """
        return self.name

    def serialize(self):
        """Serialize to JSON serializable dict."""
        return {
            "location": self.location,
            "name": self.name,
            "ext": self.ext,
        }

    def get_path(self) -> str:
        """Get full file-path.

        Returns
        -------
        location/name.ext
        """
        return join(self.location, f"{self.name}{self.ext}")
