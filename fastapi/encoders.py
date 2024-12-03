import dataclasses
import datetime
from collections import defaultdict, deque
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network
from pathlib import Path, PurePath
from re import Pattern
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from uuid import UUID
from fastapi.types import IncEx
from pydantic import BaseModel
from pydantic.color import Color
from pydantic.networks import AnyUrl, NameEmail
from pydantic.types import SecretBytes, SecretStr
from typing_extensions import Annotated, Doc
from ._compat import PYDANTIC_V2, UndefinedType, Url, _model_dump

def decimal_encoder(dec_value: Decimal) -> Union[int, float]:
    """
    Encodes a Decimal as int of there's no exponent, otherwise float

    This is useful when we use ConstrainedDecimal to represent Numeric(x,0)
    where a integer (but not int typed) is used. Encoding this as a float
    results in failed round-tripping between encode and parse.
    Our Id type is a prime example of this.

    >>> decimal_encoder(Decimal("1.0"))
    1.0

    >>> decimal_encoder(Decimal("1"))
    1
    """
    if dec_value.as_tuple().exponent == 0:
        return int(dec_value)
    else:
        return float(dec_value)
ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {bytes: lambda o: o.decode(), Color: str, datetime.date: isoformat, datetime.datetime: isoformat, datetime.time: isoformat, datetime.timedelta: lambda td: td.total_seconds(), Decimal: decimal_encoder, Enum: lambda o: o.value, frozenset: list, deque: list, GeneratorType: list, IPv4Address: str, IPv4Interface: str, IPv4Network: str, IPv6Address: str, IPv6Interface: str, IPv6Network: str, NameEmail: str, Path: str, Pattern: lambda o: o.pattern, SecretBytes: str, SecretStr: str, set: list, UUID: str, Url: str, AnyUrl: str}
encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)

def jsonable_encoder(obj: Annotated[Any, Doc('\n            The input object to convert to JSON.\n            ')], include: Annotated[Optional[IncEx], Doc("\n            Pydantic's `include` parameter, passed to Pydantic models to set the\n            fields to include.\n            ")]=None, exclude: Annotated[Optional[IncEx], Doc("\n            Pydantic's `exclude` parameter, passed to Pydantic models to set the\n            fields to exclude.\n            ")]=None, by_alias: Annotated[bool, Doc("\n            Pydantic's `by_alias` parameter, passed to Pydantic models to define if\n            the output should use the alias names (when provided) or the Python\n            attribute names. In an API, if you set an alias, it's probably because you\n            want to use it in the result, so you probably want to leave this set to\n            `True`.\n            ")]=True, exclude_unset: Annotated[bool, Doc("\n            Pydantic's `exclude_unset` parameter, passed to Pydantic models to define\n            if it should exclude from the output the fields that were not explicitly\n            set (and that only had their default values).\n            ")]=False, exclude_defaults: Annotated[bool, Doc("\n            Pydantic's `exclude_defaults` parameter, passed to Pydantic models to define\n            if it should exclude from the output the fields that had the same default\n            value, even when they were explicitly set.\n            ")]=False, exclude_none: Annotated[bool, Doc("\n            Pydantic's `exclude_none` parameter, passed to Pydantic models to define\n            if it should exclude from the output any fields that have a `None` value.\n            ")]=False, custom_encoder: Annotated[Optional[Dict[Any, Callable[[Any], Any]]], Doc("\n            Pydantic's `custom_encoder` parameter, passed to Pydantic models to define\n            a custom encoder.\n            ")]=None, sqlalchemy_safe: Annotated[bool, Doc("\n            Exclude from the output any fields that start with the name `_sa`.\n\n            This is mainly a hack for compatibility with SQLAlchemy objects, they\n            store internal SQLAlchemy-specific state in attributes named with `_sa`,\n            and those objects can't (and shouldn't be) serialized to JSON.\n            ")]=True) -> Any:
    """
    Convert any object to something that can be encoded in JSON.

    This is used internally by FastAPI to make sure anything you return can be
    encoded as JSON before it is sent to the client.

    You can also use it yourself, for example to convert objects before saving them
    in a database that supports only JSON.

    Read more about it in the
    [FastAPI docs for JSON Compatible Encoder](https://fastapi.tiangolo.com/tutorial/encoder/).
    """
    if custom_encoder is None:
        custom_encoder = {}
    
    if is_dataclass(obj):
        obj_dict = dataclasses.asdict(obj)
        return jsonable_encoder(
            obj_dict,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            custom_encoder=custom_encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "json_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = _model_dump(
            obj,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        return jsonable_encoder(
            obj_dict,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    
    if isinstance(obj, Enum):
        return obj.value
    
    if isinstance(obj, PurePath):
        return str(obj)
    
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if isinstance(key, bytes):
                encoded_key = key.decode("utf-8")
            else:
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            encoded_value = jsonable_encoder(
                value,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_none=exclude_none,
                custom_encoder=custom_encoder,
                sqlalchemy_safe=sqlalchemy_safe,
            )
            encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        return [
            jsonable_encoder(
                item,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                custom_encoder=custom_encoder,
                sqlalchemy_safe=sqlalchemy_safe,
            )
            for item in obj
        ]
    
    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    
    for encoder, classes in encoders_by_class_tuples:
        if isinstance(obj, classes):
            return encoder(obj)
    
    try:
        data = dict(obj)
    except Exception:
        pass
    else:
        return jsonable_encoder(
            data,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            custom_encoder=custom_encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    
    raise ValueError(f"Object of type {type(obj)} is not JSON serializable")
