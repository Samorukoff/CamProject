from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

from project.database import Base

# Таблица с пользователями
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    
    subscriptions = relationship("Subscription", back_populates="user")