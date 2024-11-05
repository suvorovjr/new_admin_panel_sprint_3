from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any
from uuid import UUID


class UUIDMixin(BaseModel):
    id: UUID


class PersonDetail(UUIDMixin):
    name: str = Field(alias='full_name')


class FilmWork(UUIDMixin):
    imdb_rating: Optional[float] = None
    genres: List[str]
    title: str
    description: Optional[str] = None

    directors_names: str = Field(default_factory=str)
    actors_names: str = Field(default_factory=str)
    writers_names: str = Field(default_factory=str)

    directors: List[PersonDetail] = Field(default_factory=list)
    actors: List[PersonDetail] = Field(default_factory=list)
    writers: List[PersonDetail] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def distribute_person_details(cls, data: dict[str, Any]):
        person_details = data.get('person_details', [])

        roles = {
            'director': ('directors', 'directors_names'),
            'actor': ('actors', 'actors_names'),
            'writer': ('writers', 'writers_names'),
        }

        for detail_list, name_list in roles.values():
            data[detail_list] = []
            data[name_list] = ''

        for person in person_details:
            role = person.get('role')
            if role is not None:
                role = role.lower()
                if role in roles:
                    detail_list, name_list = roles[role]
                    data[detail_list].append(PersonDetail(**person))

                    if data[name_list]:
                        data[name_list] += ', ' + person['full_name']
                    else:
                        data[name_list] = person['full_name']
        return data
