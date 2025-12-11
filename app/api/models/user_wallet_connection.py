from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base
from app.api.models.enums import ConnectionMethod

class UserWalletConnection(Base):
    __tablename__ = "user_wallet_connections"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    method = Column(Enum(ConnectionMethod, name="connection_method"), nullable=False)
    email = Column(String(255))  # For email reader; null for api/csv
    status = Column(String(64))  # e.g., pending/connected/failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="wallet_connections")
