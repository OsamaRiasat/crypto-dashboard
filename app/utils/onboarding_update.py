from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal, InvalidOperation

from app.api.models.db import (
    UserOnboarding,
    UserRiskAllocation,
    UserSelectedAsset,
    UserRebalanceRule,
    UserContributionPlan,
    RebalanceFrequency,
    ContributionFrequency,
    UserGoal,
    UserLeveragePreference,
)


def ensure_onboarding(db: Session, user_id: int) -> UserOnboarding:
    onboarding = (
        db.query(UserOnboarding)
        .filter(UserOnboarding.user_id == user_id)
        .first()
    )
    if onboarding is None:
        onboarding = UserOnboarding(user_id=user_id)
        db.add(onboarding)
        db.flush()
    return onboarding


def update_onboarding_fields(onboarding: UserOnboarding, payload) -> None:
    if payload.portfolio_size is not None:
        onboarding.portfolio_size = payload.portfolio_size
    if payload.intent is not None:
        onboarding.intent = payload.intent
    if payload.experience is not None:
        onboarding.experience = payload.experience
    if payload.allocation_preset is not None:
        onboarding.allocation_preset = payload.allocation_preset


def upsert_risk_allocation(db: Session, user_id: int, payload) -> Optional[UserRiskAllocation]:
    if payload is None or payload.risk_allocation is None:
        return None
    ra = payload.risk_allocation
    risk_alloc = (
        db.query(UserRiskAllocation)
        .filter(UserRiskAllocation.user_id == user_id)
        .first()
    )
    if risk_alloc is None:
        if ra.collateral_pct is None or ra.growth_pct is None or ra.wildcard_pct is None:
            raise HTTPException(status_code=422, detail="To set risk allocation for the first time, provide collateral_pct, growth_pct, and wildcard_pct")
        risk_alloc = UserRiskAllocation(
            user_id=user_id,
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
    return risk_alloc


def normalize_rebalance_frequency(value: Optional[str]) -> Optional[RebalanceFrequency]:
    if value is None:
        return None
    try:
        return RebalanceFrequency[value]
    except KeyError:
        # allow lowercase string mapping
        mapping = {
            "daily": RebalanceFrequency.daily,
            "weekly": RebalanceFrequency.weekly,
            "monthly": RebalanceFrequency.monthly,
            "quarterly": RebalanceFrequency.quarterly,
        }
        if value.lower() in mapping:
            return mapping[value.lower()]
        raise HTTPException(status_code=422, detail=f"Invalid rebalancing.frequency: {value}")


def normalize_contrib_frequency(value: Optional[str]) -> Optional[ContributionFrequency]:
    if value is None:
        return None
    val = value.lower()
    if val == "bi-weekly":
        val = "biweekly"
    mapping = {
        "weekly": ContributionFrequency.weekly,
        "biweekly": ContributionFrequency.biweekly,
        "monthly": ContributionFrequency.monthly,
        "quarterly": ContributionFrequency.quarterly,
    }
    freq = mapping.get(val)
    if not freq:
        raise HTTPException(status_code=422, detail=f"Invalid contributions.frequency: {value}")
    return freq


def upsert_rebalance_rule(db: Session, user_id: int, payload) -> Optional[UserRebalanceRule]:
    if payload is None or payload.rebalancing is None:
        return None
    rb = payload.rebalancing
    rule = (
        db.query(UserRebalanceRule)
        .filter(UserRebalanceRule.user_id == user_id)
        .first()
    )
    freq = normalize_rebalance_frequency(rb.frequency) if rb.frequency is not None else None
    if rule is None:
        if freq is None or rb.margin_pct is None:
            raise HTTPException(status_code=422, detail="To set rebalancing for the first time, provide frequency and margin_pct")
        rule = UserRebalanceRule(
            user_id=user_id,
            frequency=freq,
            threshold_pct=rb.margin_pct,
        )
        db.add(rule)
    else:
        if freq is not None:
            rule.frequency = freq
        if rb.margin_pct is not None:
            rule.threshold_pct = rb.margin_pct
    return rule


def upsert_contribution_plan(db: Session, user_id: int, payload) -> Optional[UserContributionPlan]:
    if payload is None or payload.contributions is None:
        return None
    contrib = payload.contributions
    plan = (
        db.query(UserContributionPlan)
        .filter(UserContributionPlan.user_id == user_id)
        .first()
    )
    freq = normalize_contrib_frequency(contrib.frequency) if contrib.frequency is not None else None
    if plan is None:
        if contrib.amount_usd is None or freq is None:
            raise HTTPException(status_code=422, detail="To set contributions for the first time, provide amount_usd and frequency")
        plan = UserContributionPlan(
            user_id=user_id,
            amount=contrib.amount_usd,
            frequency=freq,
        )
        db.add(plan)
    else:
        if contrib.amount_usd is not None:
            plan.amount = contrib.amount_usd
        if freq is not None:
            plan.frequency = freq
    return plan


def replace_selected_assets(db: Session, user_id: int, assets: Optional[List[Dict[str, Any]]]) -> Optional[List[UserSelectedAsset]]:
    if assets is None:
        return None
    # Delete existing assets
    existing = (
        db.query(UserSelectedAsset)
        .filter(UserSelectedAsset.user_id == user_id)
        .all()
    )
    for a in existing:
        db.delete(a)
    # Insert new assets
    created: List[UserSelectedAsset] = []
    for item in assets:
        symbol = item.get("symbol")
        layer = item.get("layer")
        if not symbol or not layer:
            raise HTTPException(status_code=422, detail="Each selected asset must include symbol and layer")
        asset = UserSelectedAsset(user_id=user_id, symbol=symbol, layer=layer)
        db.add(asset)
        created.append(asset)
    return created


def upsert_goals(db: Session, user_id: int, goals: Optional[List[Dict[str, Any]]]) -> Optional[List[UserGoal]]:
    """Create or update user goals based on incoming payload.
    - Matches existing goals by exact name for the user.
    - Updates `target_amount` and `months` when found; otherwise creates a new goal (is_default=False).
    - Does not delete unspecified existing goals.
    """
    if goals is None:
        return None

    affected: List[UserGoal] = []
    for item in goals:
        name = item.get("name")
        target_amount = item.get("target_amount")
        months = item.get("months")
        if not name or target_amount is None or months is None:
            raise HTTPException(status_code=422, detail="Each goal must include name, target_amount, and months")
        try:
            amount_dec = Decimal(str(target_amount))
        except (InvalidOperation, ValueError):
            raise HTTPException(status_code=422, detail=f"Invalid target_amount for goal '{name}': {target_amount}")
        if months < 1:
            raise HTTPException(status_code=422, detail=f"Invalid months for goal '{name}': {months}")

        existing = (
            db.query(UserGoal)
            .filter(UserGoal.user_id == user_id, UserGoal.name == name)
            .first()
        )
        if existing is None:
            goal = UserGoal(user_id=user_id, name=name, target_amount=amount_dec, months=months, is_default=False)
            db.add(goal)
            affected.append(goal)
        else:
            existing.target_amount = amount_dec
            existing.months = months
            affected.append(existing)

    return affected


def upsert_leverage_preference(db: Session, user_id: int, payload) -> Optional[UserLeveragePreference]:
    """Create or update leverage preferences.
    - First-time set requires `enabled`.
    - If enabling leverage, `leverage_pct` must be provided (0–35).
    - If disabling leverage, `leverage_pct` is set to null.
    - Subsequent updates can toggle `enabled` or adjust `leverage_pct` when enabled.
    """
    if payload is None or getattr(payload, "leverage", None) is None:
        return None
    lv = payload.leverage
    pref = (
        db.query(UserLeveragePreference)
        .filter(UserLeveragePreference.user_id == user_id)
        .first()
    )

    def validate_pct(pct: Optional[int]):
        if pct is None:
            raise HTTPException(status_code=422, detail="When enabling leverage, provide leverage_pct")
        if pct < 0 or pct > 35:
            raise HTTPException(status_code=422, detail=f"Invalid leverage_pct: {pct}. Must be between 0 and 35")

    if pref is None:
        if lv.enabled is None:
            raise HTTPException(status_code=422, detail="To set leverage for the first time, provide enabled")
        if lv.enabled:
            validate_pct(lv.leverage_pct)
            pref = UserLeveragePreference(user_id=user_id, enabled=True, leverage_pct=lv.leverage_pct)
        else:
            pref = UserLeveragePreference(user_id=user_id, enabled=False, leverage_pct=None)
        db.add(pref)
    else:
        # Toggle enabled if provided
        if lv.enabled is not None:
            pref.enabled = lv.enabled
            if not lv.enabled:
                pref.leverage_pct = None
        # Adjust pct if provided
        if lv.leverage_pct is not None:
            if not pref.enabled and lv.enabled is not True:
                # Cannot set pct while disabled unless explicitly enabling in the same request
                raise HTTPException(status_code=422, detail="Cannot set leverage_pct when leverage is disabled. Provide enabled=true to enable.")
            validate_pct(lv.leverage_pct)
            pref.leverage_pct = lv.leverage_pct

    return pref