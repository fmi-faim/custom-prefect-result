from os.path import exists

import pandas as pd

from cpr.Resource import Resource


class CSVSource(Resource):
    def get_data(self):
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = pd.read_csv(self.get_path())

        return self._data
