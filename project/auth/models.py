from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy

from project.core.base.models import Base

# Таблица с пользователями
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    memberships = relationship(
        "CompanyMembership",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="CompanyMembership.user_id",
    )
    companies = association_proxy("memberships", "company")