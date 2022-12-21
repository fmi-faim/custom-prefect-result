from os.path import exists

import xxhash
from tifffile import imread, imwrite

from cpr.Target import Target


class ImageTarget(Target):
    def get_data(self):
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = imread(self.get_path())
            assert self._hash_data(self._data) == self.data_hash, (
                "Loaded image has a different hash. This data is either "
                "from a different run or corrupted."
            )

        return self._data

    def _hash_data(self, a):
        data = bytes()
        data += str(a.dtype).encode("ascii")
        data += b","
        data += str(a.shape).encode("ascii")
        data += b","
        data += a.tobytes()
        return xxhash.xxh3_64(data).hexdigest()

    def serialize(self):
        if self._data is not None:
            imwrite(self.get_path(), self._data, compression="zlib")

        return super(ImageTarget, self).serialize()
