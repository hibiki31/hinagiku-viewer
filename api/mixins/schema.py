from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        # Pydantic v2でのalias警告を抑制
        use_attribute_docstrings=False,
    )
