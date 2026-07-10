from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, SQLModel, select
from typing import List, Optional

from database.session import get_session, engine
from models.book import Book, BookCreate, BookUpdate
from models.category import Category, CategoryCreate
from datetime import datetime

# Create database tables
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Library API",
    description="A simple library management API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Welcome to the Library API"}


@app.post("/books", response_model=Book)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    db_book = Book(**book.model_dump())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    available: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """List all books with optional filters"""
    query = select(Book)

    if available is not None:
        query = query.where(Book.available == available)

    return session.exec(query.offset(skip).limit(limit)).all()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a specific book by ID"""
    book = session.get(Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.post("/categories", response_model=Category)
def create_category(
    category: CategoryCreate,
    session: Session = Depends(get_session)
):
    """Create a new category"""

    db_category = Category(**category.model_dump())

    session.add(db_category)
    session.commit()
    session.refresh(db_category)

    return db_category


@app.get("/books/search", response_model=List[Book])
def search_books(
    q: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Search for books by author or title"""

    query = select(Book)

    if author:
        query = query.where(Book.author.contains(author))

    if title:
        query = query.where(Book.title.contains(title))

    return session.exec(query).all()



@app.get("/categories", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    """List all categories"""
    categories = session.exec(select(Category)).all()
    return categories


@app.patch("/books/{book_id}", response_model=Book)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session)
):
    """Update a book"""

    book = session.get(Book, book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(book, field, value)

    book.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(book)

    return book