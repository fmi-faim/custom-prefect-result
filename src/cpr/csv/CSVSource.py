from os.path import exists

import pandas as pd

from cpr.Resource import Resource


class CSVSource(Resource):
    """Provides access to a csv file."""

    def __init__(
        self,
        location: str,
        name: str,
        ext: str = ".csv",
    ):
        """
        Parameters
        ----------
        location
            Where the csv is stored
        name
            Name of the csv file
        ext
            File extension, must be csv
        """
        assert ext == ".csv", "Extension must be .csv."
        super(CSVSource, self).__init__(
            location=location,
            name=name,
            ext=ext,
        )

    def get_data(self):
        """Access DataFrame.

        The DataFrame is cached by this call.

        Returns
        -------
        DataFrame
        """
        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            self._data = pd.read_csv(self.get_path())

        return self._data
