from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Схема для подписки
class SubscriptionBase(BaseModel):
    start_date: datetime
    end_date: datetime
    is_active: bool

# Схема для создания подписки
class SubscriptionCreate(SubscriptionBase):
    user_id: int
    subscription_type_id: int

# Схема для поиска подписок
class SubscriptionRead(SubscriptionBase):
    id: int
    user_id: int
    subscription_type_id: int

    model_config = ConfigDict(
        from_attributes=True
    )

# Выбор подписки
class SubscriptionUserSelect(BaseModel):
    subscription_type_id: int

# Схема для типов подписок
class SubscriptionTypeOut(BaseModel):
    id: int
    name: str
    price: int

    model_config = ConfigDict(
        from_attributes=True
    )

# Схема для оплаты
class SubscriptionPayment(BaseModel):
    success: bool = True

# Схема для изменения плана подписки
class SubscriptionUpdate(BaseModel):
    new_type_id: int
