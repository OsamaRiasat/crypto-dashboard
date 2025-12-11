from sqlalchemy import Column, Integer, ForeignKey, String, Numeric, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base

class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)  # e.g., Emergency Fund
    target_amount = Column(Numeric(14, 2), nullable=False)
    months = Column(Integer, nullable=False)  # Timeframe in months
    is_default = Column(Boolean, server_default="false", nullable=False)  # True for 12/36/60 default goals
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="goals")
