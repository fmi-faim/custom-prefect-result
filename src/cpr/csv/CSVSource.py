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

    def _read_data(self):
        return pd.read_csv(self.get_path(), index_col=0)
