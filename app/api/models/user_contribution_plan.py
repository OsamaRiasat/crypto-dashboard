from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, Enum, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base
from app.api.models.enums import ContributionFrequency

class UserContributionPlan(Base):
    __tablename__ = "user_contribution_plans"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_contribution_plans_user_id"),)

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)  # USD amount per input frequency
    frequency = Column(Enum(ContributionFrequency, name="contribution_frequency"), nullable=False)
    currency = Column(String(8), server_default="USD", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="contribution_plan", uselist=False)
