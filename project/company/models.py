from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from project.core.base.models import Base
from sqlalchemy.ext.associationproxy import association_proxy


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    memberships = relationship(
        "CompanyMembership",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    users = association_proxy("memberships", "user")
