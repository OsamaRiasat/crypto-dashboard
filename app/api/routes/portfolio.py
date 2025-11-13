from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.api.services.portfolio import portfolio_service
from app.api.models.portfolio import (
    PortfolioSummary,
    OnboardingUpdate,
    OnboardingUpdateResponse,
)
from app.core.db import get_db
from app.core.security import get_current_user
from app.api.models.db import User, UserOnboarding, UserRiskAllocation

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """Get complete portfolio summary with total value and connected wallets count"""
    try:
        portfolio_data = await portfolio_service.get_portfolio_summary()
        return portfolio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio summary: {str(e)}")

@router.get("/total-value")
async def get_total_portfolio_value():
    """Get just the total portfolio value across all wallets"""
    try:
        portfolio_data = await portfolio_service.get_portfolio_summary()
        return {
            "total_portfolio_value_usd": portfolio_data.total_portfolio_value_usd,
            "connected_wallets_count": portfolio_data.connected_wallets_count,
            "last_updated": portfolio_data.last_updated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching total portfolio value: {str(e)}")

# Removed individual /size and /intent endpoints in favor of unified /update

@router.post("/update", response_model=OnboardingUpdateResponse)
def update_onboarding(
    payload: OnboardingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update onboarding fields (e.g., portfolio_size, intent, experience, allocation_preset, risk allocation). At least one field required."""
    user = current_user

    if (
        payload.portfolio_size is None
        and payload.intent is None
        and payload.experience is None
        and payload.allocation_preset is None
        and (payload.risk_allocation is None or (
            payload.risk_allocation.collateral_pct is None and
            payload.risk_allocation.growth_pct is None and
            payload.risk_allocation.wildcard_pct is None
        ))
    ):
        raise HTTPException(status_code=422, detail="Provide at least one field to update: portfolio_size, intent, experience, allocation_preset, or risk_allocation")

    onboarding = (
        db.query(UserOnboarding)
        .filter(UserOnboarding.user_id == user.id)
        .first()
    )
    if onboarding is None:
        onboarding = UserOnboarding(user_id=user.id)
        db.add(onboarding)

    if payload.portfolio_size is not None:
        onboarding.portfolio_size = payload.portfolio_size
    if payload.intent is not None:
        onboarding.intent = payload.intent
    if payload.experience is not None:
        onboarding.experience = payload.experience
    if payload.allocation_preset is not None:
        onboarding.allocation_preset = payload.allocation_preset

    # Risk allocation upsert
    risk_alloc = (
        db.query(UserRiskAllocation)
        .filter(UserRiskAllocation.user_id == user.id)
        .first()
    )
    if payload.risk_allocation is not None:
        ra = payload.risk_allocation
        if risk_alloc is None:
            # For creation, require all three percentages
            if ra.collateral_pct is None or ra.growth_pct is None or ra.wildcard_pct is None:
                raise HTTPException(status_code=422, detail="To set risk allocation for the first time, provide collateral_pct, growth_pct, and wildcard_pct")
            risk_alloc = UserRiskAllocation(
                user_id=user.id,
                collateral_pct=ra.collateral_pct,
                growth_pct=ra.growth_pct,
                wildcard_pct=ra.wildcard_pct,
            )
            db.add(risk_alloc)
        else:
            if ra.collateral_pct is not None:
                risk_alloc.collateral_pct = ra.collateral_pct
            if ra.growth_pct is not None:
                risk_alloc.growth_pct = ra.growth_pct
            if ra.wildcard_pct is not None:
                risk_alloc.wildcard_pct = ra.wildcard_pct

    db.commit()
    db.refresh(onboarding)
    if risk_alloc is not None:
        db.refresh(risk_alloc)

    return OnboardingUpdateResponse(
        user_id=user.id,
        portfolio_size=onboarding.portfolio_size,
        intent=onboarding.intent,
        experience=onboarding.experience,
        allocation_preset=onboarding.allocation_preset,
        risk_allocation=(
            None if risk_alloc is None else {
                "collateral_pct": risk_alloc.collateral_pct,
                "growth_pct": risk_alloc.growth_pct,
                "wildcard_pct": risk_alloc.wildcard_pct,
            }
        ),
    )
