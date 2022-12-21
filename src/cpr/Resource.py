from abc import ABC
from os.path import join, split, splitext
from typing import Any


class Resource(ABC):
    location: str
    name: str
    ext: str
    _data: Any

    def __init__(self, location: str, name: str, ext: str):
        super(Resource, self).__init__()
        self.location = location
        self.name = name
        self.ext = ext
        self._data = None

    @classmethod
    def from_path(cls, path: str):
        location, file_name = split(path)
        name, ext = splitext(file_name)
        return cls(location=location, name=name, ext=ext)

    def get_data(self):
        ...

    def get_name(self):
        return self.name

    def serialize(self):
        return {
            "location": self.location,
            "name": self.name,
            "ext": self.ext,
        }

    def get_path(self):
        return join(self.location, f"{self.name}{self.ext}")
