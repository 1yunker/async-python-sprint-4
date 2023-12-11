from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class CreateOriginalURL(BaseModel):
    original_url: AnyUrl = Field(alias='original-url')


class GetShortURL(BaseModel):
    # model_config = ConfigDict(from_attributes=True)

    id: int = Field(serialization_alias='short-id')
    short_url: str = Field(serialization_alias='short-url')
    # type: public|private = public
    # is_active: bool
    # clicks: int

    # class Config:
    #     orm_mode = True


# class URLInfo(URL):
#     url: str
#     admin_url: str
