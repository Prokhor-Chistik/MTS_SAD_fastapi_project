import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books_sellers


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    # Создаем Продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")

    db_session.add(_seller)
    await db_session.flush()

    book_data = {
        "title": "Wrong Code",
        "author": "Robert Martin",
        "pages": 104,
        "year": 2007,
        "seller_id": _seller.id
    }
    book_response = await async_client.post("/api/v1/books/", json=book_data)
    assert book_response.status_code == status.HTTP_201_CREATED

    book_result_data = book_response.json()
    assert book_result_data == {
        "id": 1,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": _seller.id
    }


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем Продавца и книги вручную, а не через ручки, чтобы нам не попасться на ошибки которые
    # могут случиться в POST ручках

    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")
    db_session.add(_seller)
    await db_session.flush()

    book_1 = books_sellers.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=_seller.id)
    book_2 = books_sellers.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=_seller.id)
    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book_1.id, "count_pages": 104, "seller_id": _seller.id},
            {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book_2.id, "count_pages": 104, "seller_id": _seller.id},
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем Продавца и книги вручную, а не через ручку, чтобы нам не попасться на ошибки которые
    # могут случиться в POST ручках
    
    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")
    db_session.add(_seller)
    await db_session.flush()

    book_1 = books_sellers.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=_seller.id)
    book_2 = books_sellers.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=_seller.id)
    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book_1.id,
        "seller_id": _seller.id
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # Создаем Продавца и книгу вручную, а не через ручку, чтобы нам не попасться на ошибки которые
    # могут случиться в POST ручках
    
    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")
    db_session.add(_seller)
    await db_session.flush()

    book = books_sellers.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=_seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books_sellers.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаем Продавца и книгу вручную, а не через ручку, чтобы нам не попасться на ошибки которые
    # могут случиться в POST ручках
    
    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")
    db_session.add(_seller)
    await db_session.flush()

    book = books_sellers.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=_seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "seller_id": _seller.id, "book_id": book.id},
    )
    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books_sellers.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.seller_id == _seller.id
    assert res.id == book.id
