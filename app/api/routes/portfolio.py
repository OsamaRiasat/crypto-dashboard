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
from app.api.models.db import User
from app.utils.onboarding_update import (
    ensure_onboarding,
    update_onboarding_fields,
    upsert_risk_allocation,
    replace_selected_assets,
    upsert_rebalance_rule,
    upsert_contribution_plan,
    upsert_goals,
    upsert_leverage_preference,
)

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
        and (payload.user_selected_assets is None or len(payload.user_selected_assets) == 0)
        and (payload.rebalancing is None or (payload.rebalancing.frequency is None and payload.rebalancing.margin_pct is None))
        and (payload.contributions is None or (payload.contributions.amount_usd is None and payload.contributions.frequency is None))
        and (payload.leverage is None or (payload.leverage.enabled is None and payload.leverage.leverage_pct is None))
        and (payload.goals is None or len(payload.goals) == 0)
    ):
        raise HTTPException(status_code=422, detail="Provide at least one field to update: portfolio_size, intent, experience, allocation_preset, risk_allocation, user_selected_assets, rebalancing, contributions, leverage, or goals")

    onboarding = ensure_onboarding(db, user.id)
    update_onboarding_fields(onboarding, payload)

    # Risk allocation upsert
    risk_alloc = upsert_risk_allocation(db, user.id, payload)

    # Rebalancing upsert
    rebalance_rule = upsert_rebalance_rule(db, user.id, payload)

    # Contributions upsert
    contrib_plan = upsert_contribution_plan(db, user.id, payload)

    # Leverage preference upsert
    leverage_pref = upsert_leverage_preference(db, user.id, payload)

    # Selected assets replace
    created_assets = replace_selected_assets(
        db,
        user.id,
        None if payload.user_selected_assets is None else [item.dict(by_alias=True) for item in payload.user_selected_assets]
    )

    # Goals upsert (create/update by name)
    affected_goals = upsert_goals(
        db,
        user.id,
        None if payload.goals is None else [g.dict() for g in payload.goals]
    )

    db.commit()
    db.refresh(onboarding)
    if risk_alloc is not None:
        db.refresh(risk_alloc)
    if rebalance_rule is not None:
        db.refresh(rebalance_rule)
    if contrib_plan is not None:
        db.refresh(contrib_plan)
    if leverage_pref is not None:
        db.refresh(leverage_pref)
    if created_assets is not None:
        for a in created_assets:
            db.refresh(a)
    if affected_goals is not None:
        for g in affected_goals:
            db.refresh(g)

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
        rebalancing=(
            None if rebalance_rule is None else {
                "frequency": getattr(rebalance_rule.frequency, "name", str(rebalance_rule.frequency)).lower(),
                "margin_pct": rebalance_rule.threshold_pct,
            }
        ),
        contributions=(
            None if contrib_plan is None else {
                "amount_usd": contrib_plan.amount,
                "frequency": getattr(contrib_plan.frequency, "name", str(contrib_plan.frequency)).lower(),
            }
        ),
        leverage=(
            None if leverage_pref is None else {
                "enabled": leverage_pref.enabled,
                "leverage_pct": leverage_pref.leverage_pct,
            }
        ),
        user_selected_assets=(
            None if created_assets is None else [
                {"symbol": a.symbol, "layer": a.layer}
                for a in created_assets
            ]
        ),
        goals=(
            None if affected_goals is None else [
                {
                    "name": g.name,
                    "target_amount": f"{g.target_amount:.2f}",
                    "months": g.months,
                }
                for g in affected_goals
            ]
        ),
    )
