from collections import deque
from copy import copy
from dataclasses import dataclass, is_dataclass
from enum import Enum
from typing import Any, Callable, Deque, Dict, FrozenSet, List, Mapping, Sequence, Set, Tuple, Type, Union
from fastapi.exceptions import RequestErrorModel
from fastapi.types import IncEx, ModelNameMap, UnionType
from pydantic import BaseModel, create_model
from pydantic.version import VERSION as P_VERSION
from starlette.datastructures import UploadFile
from typing_extensions import Annotated, Literal, get_args, get_origin
PYDANTIC_VERSION = P_VERSION
PYDANTIC_V2 = PYDANTIC_VERSION.startswith('2.')
sequence_annotation_to_type = {Sequence: list, List: list, list: list, Tuple: tuple, tuple: tuple, Set: set, set: set, FrozenSet: frozenset, frozenset: frozenset, Deque: deque, deque: deque}
sequence_types = tuple(sequence_annotation_to_type.keys())
if PYDANTIC_V2:
    from pydantic import PydanticSchemaGenerationError as PydanticSchemaGenerationError
    from pydantic import TypeAdapter
    from pydantic import ValidationError as ValidationError
    from pydantic._internal._schema_generation_shared import GetJsonSchemaHandler as GetJsonSchemaHandler
    from pydantic._internal._typing_extra import eval_type_lenient
    from pydantic._internal._utils import lenient_issubclass as lenient_issubclass
    from pydantic.fields import FieldInfo
    from pydantic.json_schema import GenerateJsonSchema as GenerateJsonSchema
    from pydantic.json_schema import JsonSchemaValue as JsonSchemaValue
    from pydantic_core import CoreSchema as CoreSchema
    from pydantic_core import PydanticUndefined, PydanticUndefinedType
    from pydantic_core import Url as Url
    try:
        from pydantic_core.core_schema import with_info_plain_validator_function as with_info_plain_validator_function
    except ImportError:
        from pydantic_core.core_schema import general_plain_validator_function as with_info_plain_validator_function
    Required = PydanticUndefined
    Undefined = PydanticUndefined
    UndefinedType = PydanticUndefinedType
    evaluate_forwardref = eval_type_lenient
    Validator = Any

    class BaseConfig:
        pass

    class ErrorWrapper(Exception):
        pass

    @dataclass
    class ModelField:
        field_info: FieldInfo
        name: str
        mode: Literal['validation', 'serialization'] = 'validation'

        def __post_init__(self) -> None:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(Annotated[self.field_info.annotation, self.field_info])

        def __hash__(self) -> int:
            return hash((self.name, self.mode, id(self.field_info)))
else:
    from fastapi.openapi.constants import REF_PREFIX as REF_PREFIX
    from pydantic import AnyUrl as Url
    from pydantic import BaseConfig as BaseConfig
    from pydantic import ValidationError as ValidationError
    from pydantic.class_validators import Validator as Validator
    from pydantic.error_wrappers import ErrorWrapper as ErrorWrapper
    from pydantic.errors import MissingError
    from pydantic.fields import SHAPE_FROZENSET, SHAPE_LIST, SHAPE_SEQUENCE, SHAPE_SET, SHAPE_SINGLETON, SHAPE_TUPLE, SHAPE_TUPLE_ELLIPSIS
    from pydantic.fields import FieldInfo as FieldInfo
    from pydantic.fields import ModelField as ModelField
    from pydantic.fields import Required as Required
    from pydantic.fields import Undefined as Undefined
    from pydantic.fields import UndefinedType as UndefinedType
    from pydantic.schema import field_schema, get_flat_models_from_fields, get_model_name_map, model_process_schema
    from pydantic.schema import get_annotation_from_field_info as get_annotation_from_field_info
    from pydantic.typing import evaluate_forwardref as evaluate_forwardref
    from pydantic.utils import lenient_issubclass as lenient_issubclass
    GetJsonSchemaHandler = Any
    JsonSchemaValue = Dict[str, Any]
    CoreSchema = Any
    sequence_shapes = {SHAPE_LIST, SHAPE_SET, SHAPE_FROZENSET, SHAPE_TUPLE, SHAPE_SEQUENCE, SHAPE_TUPLE_ELLIPSIS}
    sequence_shape_to_type = {SHAPE_LIST: list, SHAPE_SET: set, SHAPE_TUPLE: tuple, SHAPE_SEQUENCE: list, SHAPE_TUPLE_ELLIPSIS: list}

    @dataclass
    class GenerateJsonSchema:
        ref_template: str

    class PydanticSchemaGenerationError(Exception):
        pass
