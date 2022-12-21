from os.path import exists

from tifffile import imread

from cpr.Resource import Resource


class ImageSource(Resource):
    def get_data(self):
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = imread(self.get_path())

        return self._data
