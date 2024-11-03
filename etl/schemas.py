from pydantic import BaseModel, Field
from uuid import UUID
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict


class UUIDMixin(BaseModel):
    id: UUID


class Genre(UUIDMixin):
    name: str


class Person(UUIDMixin):
    name: str


class FilmWork(BaseModel):
    pass


class PersonFilmWork(BaseModel):
    pass


class GenreFilmWork(BaseModel):
    pass


@dataclass
class BaseDataclass:
    def to_pg_dict(self, mapping: Dict[str, str]) -> Dict[str, Any]:
        pg_dict = {}
        for field, value in self.__dict__.items():
            pg_dict[mapping.get(field, field)] = value
        return pg_dict

    def __post_init__(self) -> None:
        pass

    def validate_fields(self, fields_mapping: Dict[str, Any]) -> None:
        for field_name, validator in fields_mapping.items():
            current_value = getattr(self, field_name)
            validated_value = validator(current_value) if isinstance(current_value, str) else current_value
            setattr(self, field_name, validated_value)

    @classmethod
    def from_dict(cls, data: dict[str:Any], field_mapping: dict[str:Any] = None):
        field_mapping = field_mapping or {}
        normalized_data = {}
        for field_name in cls.__dict__.get('__dataclass_fields__'):
            source_field = field_mapping.get(field_name, field_name)
            if source_field in data:
                normalized_data[field_name] = data[source_field]
        return cls(**normalized_data)


@dataclass
class UUIDMixin(BaseDataclass):
    id: uuid.UUID

    def __post_init__(self) -> None:
        self.id = validate_uuid(self.id) if isinstance(self.id, str) else self.id
        super().__post_init__()


@dataclass
class DateMixin(BaseDataclass):
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        self.validate_fields(
            {
                'created_at': validate_date,
                'updated_at': validate_date,
            }
        )
        super().__post_init__()


@dataclass
class Genre(UUIDMixin, DateMixin):
    name: str
    description: str


@dataclass
class FilmWork(UUIDMixin, DateMixin):
    title: str
    description: str
    creation_date: date
    rating: float
    type: str


@dataclass
class Person(UUIDMixin, DateMixin):
    full_name: str


@dataclass
class GenreFilmWork(UUIDMixin):
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime

    def __post_init__(self) -> None:
        self.validate_fields(
            {
                'created_at': validate_date,
                'genre_id': validate_uuid,
                'film_work_id': validate_uuid,
            }
        )
        super().__post_init__()


@dataclass
class PersonFilmWork(UUIDMixin):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime

    def __post_init__(self) -> None:
        self.validate_fields(
            {
                'created_at': validate_date,
                'person_id': validate_uuid,
                'film_work_id': validate_uuid,
            }
        )
        super().__post_init__()


@dataclass
class TableMapping:
    pg_table: str
    different_fields: Dict[str, str]
    dataclass: BaseDataclass
