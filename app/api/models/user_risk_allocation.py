from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base

class UserRiskAllocation(Base):
    __tablename__ = "user_risk_allocations"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_risk_allocations_user_id"),
        CheckConstraint("collateral_pct BETWEEN 0 AND 100", name="ck_collateral_pct_range"),
        CheckConstraint("growth_pct BETWEEN 0 AND 100", name="ck_growth_pct_range"),
        CheckConstraint("wildcard_pct BETWEEN 0 AND 100", name="ck_wildcard_pct_range"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    collateral_pct = Column(Integer, nullable=False)  # 0–100
    growth_pct = Column(Integer, nullable=False)      # 0–100
    wildcard_pct = Column(Integer, nullable=False)    # 0–100
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="risk_allocations", uselist=False)
