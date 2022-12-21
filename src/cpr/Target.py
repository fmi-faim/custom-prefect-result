from os.path import join

from cpr.Resource import Resource


class Target(Resource):
    data_hash: str

    def __init__(self, location: str, name: str, ext: str, data_hash: str = None):
        super(Target, self).__init__(location=location, name=name, ext=ext)
        self.data_hash = data_hash

    def compute_data_hash(self):
        self.data_hash = self._hash_data(self._data)

    def set_data(self, data):
        self._data = data
        self.compute_data_hash()

    def _hash_data(self, a) -> str:
        ...

    def serialize(self):
        d = super(Target, self).serialize()
        d["data_hash"] = self.data_hash
        return d

    def get_path(self):
        assert self.data_hash is not None, (
            "Data hash is None. Please call " "set_data first."
        )
        return join(self.location, f"{self.name}-{self.data_hash}{self.ext}")
