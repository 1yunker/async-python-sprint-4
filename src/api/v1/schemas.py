from pydantic import AnyUrl, BaseModel, Field


class OriginalURL(BaseModel):
    original_url: AnyUrl = Field(alias='original-url')


class ShortURL(BaseModel):
    short_id: str = Field(serialization_alias='short-id')
    short_url: AnyUrl = Field(serialization_alias='short-url')


class FullURL(ShortURL):
    original_url: AnyUrl = Field(serialization_alias='original-url')
    is_active: bool
    clicks: int
    # type: public|private = public
