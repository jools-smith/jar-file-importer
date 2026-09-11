from dataclasses import dataclass, field
from enum import Enum


class ColumnType(Enum):
    REQUIRED = 1
    REQUIRED_NULL = 2
    NOT_REQUIRED = 4

    def is_required(self) -> bool:
        return self == ColumnType.REQUIRED or self == ColumnType.REQUIRED_NULL

    def is_nullable(self) -> bool:
        return self == ColumnType.NOT_REQUIRED or self == ColumnType.REQUIRED_NULL

@dataclass
class Column:
    name:str
    type:ColumnType

@dataclass(frozen=True)
class Row:
    values: dict[str, str | None] = field(default_factory=dict)

    @staticmethod
    def get_column_name(column: Column | str) -> str:
        return column.name if isinstance(column, Column) else column

    def add(self, column: Column | str, value:str | None = None) -> Row:
        self.values[self.get_column_name(column)] = value
        ## enable building!
        return self

    def get_column_value(self, column: Column | str) -> str | None:
        return self.values[self.get_column_name(column)]