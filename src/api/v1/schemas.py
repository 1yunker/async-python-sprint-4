from pydantic import BaseModel, AnyUrl, Field


class CreateOriginalURL(BaseModel):
    original_url: AnyUrl = Field(alias='original-url')


class GetShortURL(BaseModel):
    short_id: int = Field(alias='short-id')
    short_url: AnyUrl = Field(alias='short-url')
    # type: public|private = public
    # is_active: bool
    # clicks: int

    class Config:
        orm_mode = True


# class URLInfo(URL):
#     url: str
#     admin_url: str
