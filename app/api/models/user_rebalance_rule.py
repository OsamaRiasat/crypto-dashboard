from sqlalchemy import Column, Integer, ForeignKey, Enum, CheckConstraint, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base
from app.api.models.enums import RebalanceFrequency

class UserRebalanceRule(Base):
    __tablename__ = "user_rebalance_rules"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_rebalance_rules_user_id"),
        CheckConstraint("threshold_pct BETWEEN 5 AND 25", name="ck_threshold_pct_range"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    frequency = Column(Enum(RebalanceFrequency, name="rebalance_frequency"), nullable=False)
    threshold_pct = Column(Integer, nullable=False)  # 5–25
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="rebalance_rules", uselist=False)
