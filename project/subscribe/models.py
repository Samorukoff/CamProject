from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String

from project.database import Base

# Таблица с подписками пользователей
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_type_id = Column(Integer, ForeignKey("subscription_types.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="subscriptions")
    subscription_type = relationship("SubscriptionType", back_populates="subscription")

# Таблица с видами подписок
class SubscriptionType(Base):
    __tablename__ = "subscription_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    company = Column(Integer, ForeignKey("companies.id"), nullable=False)

    subscription = relationship("Subscription", back_populates="subscription_type")