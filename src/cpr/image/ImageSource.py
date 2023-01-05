from os.path import exists
from typing import Any, Dict, Tuple

from numpy._typing import ArrayLike
from tifffile import imread

from cpr.image.Metadata import Metadata
from cpr.Resource import Resource


class ImageSource(Resource, Metadata):
    """Provides access to an image file and its metadata."""

    def __init__(
        self,
        location: str,
        name: str,
        ext: str,
        metadata: Dict = None,
        resolution: Tuple[Any, Any] = None,
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

        Example
        -------
        img = ImageSource(
            location="/path/to/dir",
            name="image_file",
            ext="tif",
            metadata={
                'axes': 'YX',
                'spacing': 0.134,
                'unit': 'micron'
            },
            resolution=(1/0.134, 1/0.134),
        )
        img.get_data()
        """

        super(ImageSource, self).__init__(
            location=location,
            name=name,
            ext=ext,
            metadata=metadata,
            resolution=resolution,
        )

    @classmethod
    def from_path(
        cls, path: str, metadata: Dict = None, resolution: Tuple[Any, Any] = None
    ):
        """Create new instance from file-path.

        Parameters
        ----------
        path
            Path to the image file
        metadata
            Image metadata passed on to tifffile, by default None
        resolution
            Image resolution passed on to tifffile, by default None

        Returns
        -------
        A new image source to read from

        Example
        -------
        img = ImageSource.from_path(
            path="/path/to/dir/image_file.tif",
            metadata={
                'axes': 'YX',
                'spacing': 0.134,
                'unit': 'micron'
            },
            resolution=(1/0.134, 1/0.134),
        )
        img.get_data()
        """

        img = super(ImageSource, cls).from_path(path=path)
        img.metadata = metadata
        img.resolution = resolution
        return img

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

        return self._data

    def serialize(self) -> Dict:
        """Serialize to JSON serializable dict."""
        d = super(ImageSource, self).serialize()
        d["metadata"] = self.metadata
        d["resolution"] = self.resolution
        return d
