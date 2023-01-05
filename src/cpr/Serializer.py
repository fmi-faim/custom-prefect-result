from typing import Any

from prefect.serializers import (
    JSONSerializer,
    prefect_json_object_decoder,
    prefect_json_object_encoder,
)
from prefect.utilities.importtools import from_qualified_name, to_qualified_name

from cpr.Resource import Resource


def target_encoder(obj: Any) -> Any:
    """
    Encoder which takes care of cpr objects.

    Otherwise prefect_json_object_encoder is used.
    """
    if isinstance(obj, Resource):
        return {
            "__class__": to_qualified_name(obj.__class__),
            "data": obj.serialize(),
        }
    else:
        prefect_json_object_encoder(obj)


def target_decoder(result: dict):
    """
    Decoder which takes care of cpr objects.

    Otherwise prefect_json_object_decoder is used.
    """
    if "__class__" in result:
        if result["__class__"].startswith("cpr."):
            clazz = from_qualified_name(result["__class__"])
            return clazz(**result["data"])
        else:
            return prefect_json_object_decoder(result)

    return result


def cpr_serializer(dumps_kwargs={}) -> JSONSerializer:
    """JSONSerializer configured to work with cpr objects."""
    return JSONSerializer(
        object_encoder="cpr.Serializer.target_encoder",
        object_decoder="cpr.Serializer.target_decoder",
        dumps_kwargs=dumps_kwargs,
    )
