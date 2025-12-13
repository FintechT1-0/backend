from pydantic import BaseModel, HttpUrl

class NewsItem(BaseModel):
    url: HttpUrl
    thumbnail: HttpUrl
    image: HttpUrl
    title: str
    content: str
    date: str
    excerpt: str
    lang: str
    category: str

    class Config:
        from_attributes = True