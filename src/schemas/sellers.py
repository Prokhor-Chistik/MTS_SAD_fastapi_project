from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller"]


# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str
    e_mail: str

    @field_validator("password")  # Валидатор, проверяет пароль на сложность
    @staticmethod
    def validate_password(val: str):
        if (any(chr.isdigit() for chr in val)) and (any(chr.isalpha() for chr in val)):
            raise PydanticCustomError("Validation error", "Password not correct!")
        return val
    
    @field_validator("e_mail")  # Валидатор, проверяет e-mail на корректность введенных данных
    @staticmethod
    def validate_e_mail(val: str):
        if ('@' not in val):
            raise PydanticCustomError("Validation error", "e-mail is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int
    e_mail: str


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
