import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(tags=["CPQ & Benchmarking Engine"])

@router.get("/api/categories", response_model=List[schemas.EquipmentCategoryResponse])
def get_categories(
    domain: Optional[models.DomainType] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.EquipmentCategory)
    if domain:
        query = query.filter(models.EquipmentCategory.domain == domain)
    return query.order_by(models.EquipmentCategory.name).all()

@router.get("/api/categories/{category_id}/rates", response_model=List[schemas.MasterRateResponse])
def get_category_rates(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.MasterRate).filter(models.MasterRate.category_id == category_id).all()

@router.post("/api/categories/{category_id}/valid-specs", response_model=schemas.ValidSpecsResponse)
def get_valid_specs(
    category_id: int,
    request: schemas.ValidSpecsRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    category = db.query(models.EquipmentCategory).filter(models.EquipmentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Equipment Category not found")

    # Fetch all master rates for this category
    rates = db.query(models.MasterRate).filter(models.MasterRate.category_id == category_id).all()
    
    selected_specs = request.selected_specs or {}
    
    # Filter rates that match all currently selected specification key-value pairs
    matching_rates = []
    for rate in rates:
        specs = rate.specifications or {}
        matches = True
        for k, v in selected_specs.items():
            if v is not None and str(v).strip() != "":
                # Compare as strings or exact types for robust matching
                if str(specs.get(k, "")).strip().lower() != str(v).strip().lower():
                    matches = False
                    break
        if matches:
            matching_rates.append(rate)

    # Build valid options dictionary for each key in spec_schema
    valid_options: Dict[str, List[Any]] = {}
    for key in category.spec_schema:
        options_set = set()
        for rate in matching_rates:
            val = (rate.specifications or {}).get(key)
            if val is not None and str(val).strip() != "":
                options_set.add(val)
        # Sort options cleanly
        try:
            valid_options[key] = sorted(list(options_set))
        except TypeError:
            valid_options[key] = sorted([str(x) for x in options_set])

    return schemas.ValidSpecsResponse(valid_options=valid_options)

@router.post("/api/benchmark", response_model=schemas.BenchmarkResponse)
def compute_benchmark(
    request: schemas.BenchmarkRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    category = db.query(models.EquipmentCategory).filter(models.EquipmentCategory.id == request.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Equipment Category not found")

    # Determine default annual escalation percentage
    escalation_pct = 0.045
    if request.project_id:
        proj = db.query(models.Project).filter(models.Project.id == request.project_id).first()
        if proj and proj.default_annual_escalation_pct is not None:
            escalation_pct = proj.default_annual_escalation_pct

    # Find matching MasterRate records
    rates = db.query(models.MasterRate).filter(models.MasterRate.category_id == request.category_id).all()
    matching_rates = []
    for rate in rates:
        specs = rate.specifications or {}
        matches = True
        for k, v in (request.specifications or {}).items():
            if v is not None and str(v).strip() != "":
                if str(specs.get(k, "")).strip().lower() != str(v).strip().lower():
                    matches = False
                    break
        if matches:
            matching_rates.append(rate)

    now = datetime.utcnow()
    results = []
    for rate in matching_rates:
        # Years Elapsed = (Current Date - quotation_date) / 365.25
        days_elapsed = (now - rate.quotation_date).days
        years_elapsed = max(0.0, days_elapsed / 365.25)
        
        # Multiplier = (1 + annual_escalation_pct) ^ Years Elapsed
        multiplier = (1.0 + escalation_pct) ** years_elapsed
        escalated_rate = round(rate.base_rate * multiplier, 2)

        results.append(schemas.BenchmarkRowResponse(
            rate_id=rate.id,
            vendor_name=rate.vendor_name,
            quotation_date=rate.quotation_date,
            base_rate=rate.base_rate,
            years_elapsed=round(years_elapsed, 2),
            escalation_multiplier=round(multiplier, 4),
            escalated_rate=escalated_rate,
            specifications=rate.specifications,
            remarks=rate.remarks or rate.specifications.get("Remarks") or ""
        ))

    return schemas.BenchmarkResponse(
        category_id=category.id,
        category_name=category.name,
        annual_escalation_pct_applied=escalation_pct,
        benchmarks=results
    )
