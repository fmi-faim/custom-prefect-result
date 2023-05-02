from abc import ABC
from typing import Any, Dict, List


class Metadata(ABC):
    """Metadata for an image."""

    metadata: Dict
    resolution: List[Any]
    imagej: bool

    def __init__(
        self,
        metadata: Dict = None,
        resolution: List[Any] = None,
        imagej: bool = True,
        **kwargs
    ):
        """
        Parameters
        ----------
        metadata
            Image metadata, by default None
        resolution
            Resolution metadata, by default None
        imagej
            Save imagej compatible
        """

        self.metadata = metadata
        self.resolution = resolution
        self.imagej = imagej
        super(Metadata, self).__init__(**kwargs)

    def get_metadata(self) -> Dict:
        """Get image metadata.

        Returns
        -------
        Image metadata
        """

        return self.metadata

    def get_resolution(self) -> List[Any]:
        """Get image resolution.

        Returns
        -------
        Image resolution
        """

        return self.resolution
