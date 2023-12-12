from pydantic import AnyUrl, BaseModel, Field


class CreateOriginalURL(BaseModel):
    original_url: AnyUrl = Field(alias='original-url')


class GetShortURL(BaseModel):
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

class Paginator:
    def __init__(self, offset: int = 0, limit: int = 10):
        self.offset = offset
        self.limit = limit

    def __str__(self):
        return "{}: offset: {}, limit: {}".format(
            self.__class__.__name__,
            self.offset,
            self.limit
        )

    async def __call__(self):
        return self
