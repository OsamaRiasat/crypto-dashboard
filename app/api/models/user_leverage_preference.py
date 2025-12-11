from sqlalchemy import Column, Integer, ForeignKey, Boolean, CheckConstraint, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base

class UserLeveragePreference(Base):
    __tablename__ = "user_leverage_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_leverage_preferences_user_id"),
        CheckConstraint("leverage_pct BETWEEN 0 AND 35 OR leverage_pct IS NULL", name="ck_leverage_pct_range"),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    enabled = Column(Boolean, nullable=False, server_default="false")
    leverage_pct = Column(Integer)  # 0–35, null when disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="leverage_preferences", uselist=False)
