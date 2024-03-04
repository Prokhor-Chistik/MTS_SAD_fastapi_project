from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = [
    "IncomingBook", "ReturnedAllBooks", "ReturnedBook",
    "IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks"
]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    year: int = 2024  # Пример присваивания дефолтного значения
    count_pages: int = Field(
        alias="pages",
        default=300,
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]

#=======================================================================================

# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str
    email: str

    # @field_validator("password")  # Валидатор, проверяет пароль на сложность
    # @staticmethod
    # def validate_password(val: str):
    #     if (not val.isalpha()) and (not val.isdigit()):
    #         raise PydanticCustomError("Validation error", "Password not correct!")
    #     return val
    
    @field_validator("email")  # Валидатор, проверяет e-mail на корректность введенных данных
    @staticmethod
    def validate_email(val: str):
        if ('@' not in val):
            raise PydanticCustomError("Validation error", "e-mail is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    password: str
    email: str



# Класс, исходящих данных с данными по книгам
class ReturnedSellerWithBooks(ReturnedSeller):
    books: list["ReturnedBook"]


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]