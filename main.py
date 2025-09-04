from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

app = FastAPI(title="Mi Biblioteca API")

class BookStatus(str, Enum):
    to_read = "to_read"
    reading = "reading"
    finished = "finished"
    paused = "paused"

class BookGenre(str, Enum):
    fiction = "fiction"
    non_fiction = "non_fiction"
    science = "science"
    biography = "biography"
    history = "history"
    technology = "technology"
    other = "other"


# MODELO BASE

class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: Optional[str] = None
    genre: Optional[BookGenre] = BookGenre.other
    pages: Optional[int] = None
    publication_year: Optional[int] = None
    status: Optional[BookStatus] = BookStatus.to_read
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None

    @validator("isbn")
    def validate_isbn(cls, v):
        if v and not (len(v) in [10, 13] and v.isdigit()):
            raise ValueError("ISBN debe tener 10 o 13 dígitos numéricos")
        return v


# BASE DE DATOS EN MEMORIA

books: List[Book] = []

# Agregamos 3 libros de ejemplo
books.extend([
    Book(id=1, title="Don Quijote de la Mancha", author="Cervantes", genre=BookGenre.fiction, pages=863, status=BookStatus.finished),
    Book(id=2, title="Sapiens", author="Yuval Noah Harari", genre=BookGenre.history, pages=498, status=BookStatus.finished),
    Book(id=3, title="Clean Code", author="Robert C. Martin", genre=BookGenre.technology, pages=464, status=BookStatus.reading),
])


# ENDPOINTS

@app.get("/")
def read_root():
    return {"message": "Mi Biblioteca API"}

@app.post("/books")
async def create_book(book: Book):
    book.id = len(books) + 1
    books.append(book)
    return {"message": "Libro creado", "book": book}

@app.get("/books")
def get_books(
    genre: Optional[BookGenre] = None,
    status: Optional[BookStatus] = None
):
    results = books
    if genre:
        results = [b for b in results if b.genre == genre]
    if status:
        results = [b for b in results if b.status == status]
    return results

@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):
    for i, book in enumerate(books):
        if book.id == book_id:
            updated_book.id = book_id
            books[i] = updated_book
            return {"message": "Libro actualizado", "book": updated_book}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.patch("/books/{book_id}")
def partial_update_book(book_id: int, updated_fields: dict):
    for book in books:
        if book.id == book_id:
            for key, value in updated_fields.items():
                if hasattr(book, key):
                    setattr(book, key, value)
            return {"message": "Libro actualizado parcialmente", "book": book}
    raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for i, book in enumerate(books):
        if book.id == book_id:
            deleted = books.pop(i)
            return {"message": "Libro eliminado", "book": deleted}
    raise HTTPException(status_code=404, detail="Libro no encontrado")


# ENDPOINTS DE BÚSQUEDA

@app.get("/books/search/title")
def search_by_title(title: str):
    return [b for b in books if title.lower() in b.title.lower()]

@app.get("/books/search/author")
def search_by_author(author: str):
    return [b for b in books if author.lower() in b.author.lower()]


# ENDPOINTS ASYNC

@app.get("/books/{book_id}/metadata")
async def get_metadata(book_id: int):
    for book in books:
        if book.id == book_id:
            return {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "metadata": {
                    "last_accessed": "2025-09-03",
                    "info": "Simulación async"
                }
            }
    raise HTTPException(status_code=404, detail="Libro no encontrado")

