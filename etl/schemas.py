from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


class UUIDMixin(BaseModel):
    id: UUID


class Genre(UUIDMixin):
    name: str


class Person(UUIDMixin):
    name: str


class NestedPerson(UUIDMixin):
    name: str = Field(..., alias="full_name")


class FilmWork(UUIDMixin):
    imdb_rating: Optional[float] = Field(None, alias="rating")
    genres: List[str]
    title: str
    description: Optional[str] = None
    directors_names: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    directors: Optional[List[NestedPerson]] = None
    actors: Optional[List[NestedPerson]] = None
    writers: Optional[List[NestedPerson]] = None

    class Config:
        allow_population_by_field_name = True
