from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.book import Book


class Category(SQLModel, table=True):
    """Category model for the library database"""

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(
        unique=True,
        index=True,
        min_length=2,
        max_length=50
    )

    books: List["Book"] = Relationship(
        back_populates="category"
    )


class CategoryCreate(SQLModel):
    """Model for creating a new category"""

    name: str = Field(
        min_length=2,
        max_length=50
    )