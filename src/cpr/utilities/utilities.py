from typing import Any, Dict, Optional

from cloudpickle import cloudpickle
from prefect.context import TaskRunContext
from prefect.utilities.hashing import _md5, stable_hash

from cpr.Serializer import cpr_serializer


def hash_objects(*args, hash_algo=_md5, **kwargs) -> Optional[str]:
    try:
        serializer = cpr_serializer(dumps_kwargs={"sort_keys": True})
        return stable_hash(serializer.dumps((args, kwargs)), hash_algo=hash_algo)
    except Exception:
        pass

    try:
        return stable_hash(cloudpickle.dumps((args, kwargs)), hash_algo=hash_algo)
    except Exception:
        pass

    return None


def task_input_hash(
    context: "TaskRunContext", arguments: Dict[str, Any]
) -> Optional[str]:
    return hash_objects(
        context.task.task_key,
        context.task.fn.__code__.co_code.hex(),
        arguments,
    )
