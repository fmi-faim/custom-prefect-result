# Custom Prefect Result (CPR)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Custom Prefect Result (CPR) enables task-run result caching in Prefect, while keeping the result data in any file-format e.g. tiff-file for image data or csv-file for tabular data.
This works by providing a custom `object_encoder` and `object_decoder` to `prefect.serializers.JSONSerializer`, which takes care of serializing all objects of type `cpr.Resource.Resource`.

A `cpr.Resource.Resource` is an object with four fields (`location`, `name`, `ext`, `_data`) and serializes only the first three fields i.e. the full path to a file.
One can call `get_data` on a resource, which will load the file dependent on the specific implementation.
This type should be used for files which already exist and are not generated by a task-run.

For results generated by a task the `cpr.Target.Target` type should be used, which has a `set_data` method.
During `set_data` a data-hash is computed uniquely identifying the given data.
When a target gets serialized it will write the data and only serialize the `location`, `name`, `ext` and `data_hash`.

With this approach Prefect can keep track of slim task-run results serialized to JSON, while the computed output can be saved anywhere and be accessed in its native form.
To ensure that a loaded task-run result is still correct, the `data_hash` is computed and compared to the serialized hash once the data is loaded back into memory.

## Support Data Types
### Source
* Tiff-Image via `cpr.image.ImageSource.ImageSource` provides access to a tif-file and returns a numpy array.
* CSV via `cpr.csv.CSVSource.CSVSource` provides access to a csv-file and returns a pandas DataFrame.

### Target
* Tiff-Image via `cpr.image.ImageTarget.ImageTarget` wraps a numpy array and saves the numpy array to compressed tif-file.
* CSV via `cpr.csv.CSVTarget.CSVTarget` wraps a pandas DataFrame and saves it to a csv file.

## Usage
To use CPR in your workflow with result caching you must set the task `cache_key_fn` to `cpr.utilities.utilities.task_input_hash`, which ensures that any `cpr.Resource.Resource` is cached correctly.
Furthermore, the flow `result_serializer` must be set to `cpr.Serializer.cpr_serializer`, which returns the default Prefect `JSONSerializer` but configured with custom `target_encoder` and `target_decoder`.

Now you can use CPR resources and targets to cache and save custom data types.

```python
from glob import glob
from os import makedirs
from os.path import join, exists

from cpr.Resource import Resource
from cpr.Serializer import cpr_serializer
from cpr.image import ImageSource
from cpr.image.ImageTarget import ImageTarget
from cpr.utilities.utilities import task_input_hash
from prefect import flow, task
from prefect_dask import DaskTaskRunner

from scipy.ndimage import gaussian_filter


@task()
def list_files(input_data_dir):
    images = []
    for f in glob(join(input_data_dir, "*.tif")):
        images.append(ImageSource.from_path(f))

    return images


@task(cache_key_fn=task_input_hash) # Use cpr.utilities.utilities.task_input_hash to hash cpr.Resource.Resource input parameters correctly
def denoise_image(result_dir,
                  image: Resource,
                  sigma):
    output = ImageTarget.from_path(
        path=join(result_dir, f"{image.get_name()}.tif"))

    output.set_data(gaussian_filter(image.get_data(), sigma))

    return output

@task(cache_key_fn=task_input_hash)
def segment_image(result_dir: str,
                  denoised: Resource,
                  threshold: float):
    output = ImageTarget.from_path(
        path=join(result_dir, f"{denoised.get_name()}.tif"))

    output.set_data(denoised.get_data() > threshold)

    return output


task_runner = DaskTaskRunner(
    cluster_class="dask.distributed.LocalCluster",
    cluster_kwargs={
        "n_workers": 8,
        "processes": True,
        "threads_per_worker": 1,
    }
)


@flow(name="Example",
      cache_result_in_memory=False,
      persist_result=True,
      result_serializer=cpr_serializer(), # Use CPR serializer to catch cpr.Resource.Resource objects.
      task_runner=task_runner)
def measure_flow(
        input_data_dir: str = "/home/tibuch/Data/broad/nuclei_U2OS/images/",
        result_root_dir: str = "/home/tibuch/Data/broad/nuclei_U2OS/",
        denoise_sigma: float = 2,
        threshold: float = 400):

    assert exists(result_root_dir), "Output directory does not exist."

    denoising_results = join(result_root_dir, "denoised")
    segmentation_results = join(result_root_dir, "segmented")
    makedirs(denoising_results, exist_ok=True)
    makedirs(segmentation_results, exist_ok=True)

    img_files = list_files.submit(input_data_dir).result()

    for file in img_files:
        denoised = denoise_image.submit(denoising_results, file,
                                        denoise_sigma)

        segmented = segment_image.submit(segmentation_results, denoised,
                                         threshold)

if __name__ == "__main__":
    measure_flow(input_data_dir="/home/tibuch/Data/broad/nuclei_U2OS/images/",
                 result_root_dir="/home/tibuch/Data/broad/nuclei_U2OS/",
                 denoise_sigma=2,
                 threshold=400, )
```
