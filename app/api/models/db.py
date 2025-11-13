from __future__ import annotations

import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Intent(enum.Enum):
    growth = "growth"
    tax = "tax"
    learning = "learning"
    fun = "fun"

class ExperienceLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class Layer(enum.Enum):
    Collateral = "Collateral"
    Growth = "Growth"
    Wildcard = "Wildcard"

class AllocationPreset(enum.Enum):
    Conservative = "Conservative"
    Moderate = "Moderate"
    Aggressive = "Aggressive"
    YOLO = "YOLO"

class RebalanceFrequency(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"

class ContributionFrequency(enum.Enum):
    weekly = "weekly"
    biweekly = "biweekly"
    monthly = "monthly"
    quarterly = "quarterly"

class ConnectionMethod(enum.Enum):
    email = "email"
    api = "api"
    csv = "csv"

# ----- Tables -----

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

class UserWalletConnection(Base):
    __tablename__ = "user_wallet_connections"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    method = Column(Enum(ConnectionMethod, name="connection_method"), nullable=False)
    email = Column(String(255))  # For email reader; null for api/csv
    status = Column(String(64))  # e.g., pending/connected/failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="wallet_connections")

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

class UserSelectedAsset(Base):
    __tablename__ = "user_selected_assets"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    layer = Column(Enum(Layer, name="layer"), nullable=False)
    symbol = Column(String(64), nullable=False)  # e.g., BTC, ETH, SOL, ...
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="selected_assets")

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
