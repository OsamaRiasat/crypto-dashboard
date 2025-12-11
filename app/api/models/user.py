from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.api.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)  # Unique user id
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(64))  # Optional app role
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    onboarding = relationship(
        "UserOnboarding",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    wallet_connections = relationship(
        "UserWalletConnection",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    risk_allocations = relationship(
        "UserRiskAllocation",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    selected_assets = relationship(
        "UserSelectedAsset",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    rebalance_rules = relationship(
        "UserRebalanceRule",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    contribution_plan = relationship(
        "UserContributionPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    goals = relationship(
        "UserGoal",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    leverage_preferences = relationship(
        "UserLeveragePreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )
