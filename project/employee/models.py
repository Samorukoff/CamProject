from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint,\
CheckConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from project.core.base.models import Base


class CompanyMembership(Base):
    __tablename__ = "company_memberships"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    role = Column(String, nullable=False)  # 'admin' | 'employee'
    is_owner = Column(Boolean, nullable=False, default=False)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"))
    invited_at = Column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_user_unique"),
        CheckConstraint("role IN ('admin','employee')", name="ck_company_role"),
    )

    company = relationship("Company", back_populates="memberships")
    user = relationship(
        "User",
        back_populates="memberships",
        foreign_keys=[user_id],
    )