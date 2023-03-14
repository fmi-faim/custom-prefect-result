from os.path import exists
from typing import Any, Dict, List, Tuple

import xxhash
from numpy._typing import ArrayLike
from tifffile import imread, imwrite

from cpr.image.Metadata import Metadata
from cpr.Target import Target


class ImageTarget(Target, Metadata):
    """Persists image data and serializes a JSON serializable dictionary.

    An ImageTarget must have a file-location, -name and -extension. With
    set_data a numpy array can be provided to the ImageTarget. This call
    will compute a unique data_hash for the provided data.

    When serialize() is called on an ImageTarget the data is written to
    location/name-{data_hash}.ext.

    When get_data() is called the data is retrieved from its location and
    hash_data is compared to the hash of the loaded data.
    """

    def __init__(
        self,
        location: str,
        name: str,
        ext: str,
        metadata: Dict = None,
        resolution: List[Any] = None,
        data_hash: str = None,
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
        metadata
            Image metadata passed on to tifffile, by default None
        resolution
            Resolution metadata passed on to tifffile, by default None
        data_hash
            Image data hash, by default None

        Example
        -------
        img = ImageTarget(
            location="/path/to/dir",
            name="image_file",
            ext="tif",
            metadata={
                'axes': 'YX',
                'PhysicalSizeX': 0.134,
                'PhysicalSizeXUnit': 'micron',
                'PhysicalSizeY': 0.134,
                'PhysicalSizeYUnit': 'micron',
            },
            resolution=[1e4 / 0.134, 1e4 / 0.134],
        )
        img.set_data(np.random.rand(0, 255, (100, 100)))
        img.get_data()
        """
        super(ImageTarget, self).__init__(
            location=location,
            name=name,
            ext=ext,
            data_hash=data_hash,
            metadata=metadata,
            resolution=resolution,
        )

    @classmethod
    def from_path(cls, path: str, metadata: Dict = None, resolution: List[Any] = None):
        """Create new instance from file-path.

        Parameters
        ----------
        path
            Default file-path where the image is stored.
        metadata
            Image metadata passed on to tifffile, by default None
        resolution
            Image resolution metadata passed on to tifffile, by default None

        Returns
        -------
        A new image target

        Example
        -------
        img = ImageTarget.from_path(
            path="/path/to/dir/image_file.tif",
            metadata={
                'axes': 'YX',
                'PhysicalSizeX': 0.134,
                'PhysicalSizeXUnit': 'micron',
                'PhysicalSizeY': 0.134,
                'PhysicalSizeYUnit': 'micron',
            },
            resolution=[1e4 / 0.134, 1e4 / 0.134],
        )
        img.set_data(np.random.rand(0, 255, (100, 100)))
        img.get_data()
        """
        img = super(ImageTarget, cls).from_path(path=path)
        img.metadata = metadata
        img.resolution = resolution
        return img

    def set_metadata(self, metadata: Dict):
        """Set image metadata.

        Parameters
        ----------
        metadata
            Image metadata passed on to tifffile during serialization
        """

        self.metadata = metadata

    def set_resolution(self, resolution: Tuple[float, ...]):
        """Set resolution metadata.

        Parameters
        ----------
        resolution
            Pixel resolution of the image data
        """

        self.resolution = resolution

    def get_data(self) -> ArrayLike:
        """Access image data.

        The image data is cached by this function.

        Returns
        -------
        Image data as numpy array
        """

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

    def _write_data(self):
        if self._data is not None and not exists(self.get_path()):
            if (self.metadata is not None) and (self.resolution is not None):
                # Save with metadata and resolution information
                imwrite(
                    self.get_path(),
                    self._data,
                    compression="zlib",
                    resolution=tuple(self.resolution),
                    resolutionunit="CENTIMETER",
                    metadata=self.metadata,
                )
            elif self.metadata is not None:
                # Save with metadata
                imwrite(
                    self.get_path(),
                    self._data,
                    compression="zlib",
                    resolution=(1.0,) * len(self._data.shape),
                    resolutionunit="CENTIMETER",
                    metadata=self.metadata,
                )
            elif self.resolution is not None:
                # Save with resolution information
                imwrite(
                    self.get_path(),
                    self._data,
                    compression="zlib",
                    resolution=tuple(self.resolution),
                    resolutionunit="CENTIMETER",
                )
            else:
                # Save without metadata
                imwrite(self.get_path(), self._data, compression="zlib")

    def serialize(self):
        """Persist image and serialize to JSON serializable dict."""
        d = super(ImageTarget, self).serialize()
        d["resolution"] = self.resolution
        d["metadata"] = self.metadata
        return d
