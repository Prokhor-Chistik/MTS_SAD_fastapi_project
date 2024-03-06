import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books_sellers


# Тест на ручку создающую Продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Anton", "last_name": "Antonov", "password": "104aaa", "email": "aaa@mts.ru"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    assert result_data == {
        "id": result_data["id"],
        "first_name": "Anton",
        "last_name": "Antonov",
        #"password": "104aaa",
        "email": "aaa@mts.ru"
    }


# Тест на ручку получения списка Продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем Продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = books_sellers.Seller(first_name= "Anton", last_name= "Antonov", password= "104aaa", email= "aaa@mts.ru")
    seller_2 = books_sellers.Seller(first_name= "Ivan", last_name= "Ivanov", password= "104iii", email= "iii@mts.ru")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Anton", "last_name": "Antonov", "email": "aaa@mts.ru", "id": seller_1.id},
            {"first_name": "Ivan", "last_name": "Ivanov", "email": "iii@mts.ru", "id": seller_2.id}
        ]
    }


# Тест на ручку получения информации о конкретном Продавце
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем Продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = books_sellers.Seller(first_name= "Anton", last_name= "Antonov", password= "104aaa", email= "aaa@mts.ru")
    seller_2 = books_sellers.Seller(first_name= "Ivan", last_name= "Ivanov", password= "104iii", email= "iii@mts.ru")
    
    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Anton",
        "last_name": "Antonov",
        #"password": "104aaa",
        "email": "aaa@mts.ru",
        "id": seller_1.id
    }


# Тест на ручку удаления Продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем Продавца и его книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")
    db_session.add(_seller)
    await db_session.flush()

    book_1 = books_sellers.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=_seller.id)
    book_2 = books_sellers.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=_seller.id)
    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{_seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(books_sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    await db_session.flush()
    
    all_books = await db_session.execute(select(books_sellers.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления информации о Продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем Продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    _seller = books_sellers.Seller(first_name="Anton", last_name="Antonov", password="104aaa", email="aaa@mts.ru")

    db_session.add(_seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{_seller.id}",
        json={"first_name": "Anton", "last_name": "Antonov", "password": "104aaa", "email": "aaa@mts.ru", "id": _seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(books_sellers.Seller, _seller.id)
    assert res.first_name == "Anton"
    assert res.last_name == "Antonov"
    assert res.password == "104aaa"
    assert res.email == "aaa@mts.ru"
    assert res.id == _seller.id
