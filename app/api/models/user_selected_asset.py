from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base
from app.api.models.enums import Layer

class UserSelectedAsset(Base):
    __tablename__ = "user_selected_assets"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    layer = Column(Enum(Layer, name="layer"), nullable=False)
    symbol = Column(String(64), nullable=False)  # e.g., BTC, ETH, SOL, ...
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="selected_assets")
