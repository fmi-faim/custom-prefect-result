from os.path import exists, split, splitext
from typing import Dict, List

import zarr
from numpy._typing import ArrayLike
from ome_zarr.io import parse_url

from cpr.Resource import Resource


class ZarrSource(Resource):
    """Provides access to an zarr file.

    If `slices_start` and `slices_stop` are empty, the zarr-group is
    returned on `get_data()` and no actual data is loaded from storage.

    If `slices_start` and `slices_stop` indicate a ROI this ROI is loaded
    from storage and cached on `get_data()`.
    """

    def __init__(
        self,
        location: str,
        name: str,
        ext: str,
        group: str,
        slices_start: List[int],
        slices_stop: List[int],
        mode: str = "r",
    ):
        """
        Parameters
        ----------
        location
            Where the image file is stored
        name
            Name of the image file
        ext
            File extension
        group
            Index into zarr-group
        slices_start
            Start indices of slices used to access the data
        slices_stop
            Stop indices of slices used to access the data
        mode
            How to open the zarr container.
        """

        super(ZarrSource, self).__init__(
            location=location,
            name=name,
            ext=ext,
        )
        self._group = group
        if len(slices_start) > 0:
            slices = []
            for s, e in zip(slices_start, slices_stop):
                slices.append(slice(s, e))
            self._slices = tuple(slices)
        else:
            self._slices = None

        self._mode = mode

    @classmethod
    def from_path(
        cls,
        path: str,
        group: str = "0",
        slices_start: List[int] = [],
        slices_stop: List[int] = [],
        mode: str = "r",
    ):
        """Create new instance from file-path.

        Parameters
        ----------
        path
            Path to the image file
        group
            Index into zarr-group
        slices_start
            Start indices of slices used to access the data
        slices_stop
            Stop indices of slices used to access the data
        mode
            How to open the zarr container.

        Returns
        -------
        A new zarr source to read from
        """
        location, file_name = split(path)
        name, ext = splitext(file_name)
        return cls(
            location=location,
            name=name,
            ext=ext,
            group=group,
            slices_start=slices_start,
            slices_stop=slices_stop,
            mode=mode,
        )

    def get_data(self) -> ArrayLike:
        """Access zarr data.

        The zarr data is loaded and cached iff `slices_start` and
        `slices_end` is provided.

        Returns
        -------
        Either the zarr group or the actual data.
        """

        if self._data is None:
            assert exists(self.get_path()), f"{self.get_path()} does not " f"exist."

            store = parse_url(path=self.get_path(), mode=self._mode).store
            zdata = zarr.group(store=store)
            if self._slices is None:
                self._data = zdata[self._group]
            else:
                self._data = zdata[self._group][self._slices]

        return self._data

    def serialize(self) -> Dict:
        """Serialize to JSON serializable dict."""
        d = super(ZarrSource, self).serialize()
        d["group"] = self._group
        starts, stops = [], []
        if self._slices is not None:
            for sl in self._slices:
                starts.append(sl.start)
                stops.append(sl.stop)
        d["slices_start"] = starts
        d["slices_stop"] = stops
        d["mode"] = self._mode
        return d
