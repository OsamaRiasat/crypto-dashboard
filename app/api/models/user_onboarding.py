from sqlalchemy import Column, Integer, ForeignKey, Enum, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base
from app.api.models.enums import Intent, ExperienceLevel, AllocationPreset

class UserOnboarding(Base):
    __tablename__ = "user_onboarding"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    portfolio_size = Column(Integer)  # Entry step: portfolio size in USD
    intent = Column(Enum(Intent, name="intent"), nullable=True)
    experience = Column(Enum(ExperienceLevel, name="experience_level"), nullable=True)
    allocation_preset = Column(Enum(AllocationPreset, name="allocation_preset"), nullable=True)  # Risk step selected preset

    onboarding_completed = Column(Boolean, nullable=False, server_default="false")
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="onboarding")
