from fastapi import APIRouter, Form, Request
from typing import Literal, Optional

import app.config
from app.models.cost_estimate import CostEstimateInput
from app.services.cost_calculator import calculate_full_estimate
from app.storage.house_store import HouseStore
from app.storage.assets_store import AssetsStore

router = APIRouter(prefix="/cost-estimator", tags=["cost-estimator"])


@router.get("")
async def cost_estimator_page(request: Request):
    templates = request.app.state.templates
    assets_store = AssetsStore(app.config.MEMORY_DIR)
    assets = assets_store.read()

    return templates.TemplateResponse(
        request,
        "cost_estimator.html",
        {
            "house": None,
            "assets": assets,
            "result": None,
        },
    )


@router.get("/{house_id}")
async def cost_estimator_for_house(request: Request, house_id: str):
    templates = request.app.state.templates
    house_store = HouseStore(app.config.MEMORY_DIR)
    assets_store = AssetsStore(app.config.MEMORY_DIR)

    house = house_store.get(house_id)
    assets = assets_store.read()

    return templates.TemplateResponse(
        request,
        "cost_estimator.html",
        {
            "house": house,
            "assets": assets,
            "result": None,
        },
    )


@router.post("/calculate")
async def calculate(
    request: Request,
    house_id: Optional[str] = Form(default=None),
    purchase_price: int = Form(...),
    down_payment_mode: Literal["percent", "dollars"] = Form(default="percent"),
    down_payment_percent: Optional[float] = Form(default=None),
    down_payment_dollars: Optional[float] = Form(default=None),
    interest_rate: float = Form(...),
    loan_term_years: int = Form(...),
    annual_property_tax: float = Form(...),
    annual_insurance: float = Form(...),
    monthly_pmi_override: Optional[float] = Form(default=None),
    monthly_hoa: float = Form(default=0),
    monthly_heat: float = Form(default=0),
    monthly_water: float = Form(default=0),
    monthly_electric: float = Form(default=0),
    monthly_internet: float = Form(default=0),
    annual_salary: float = Form(default=0),
    monthly_take_home: Optional[float] = Form(default=None),
    monthly_loan_payments: float = Form(default=0),
    monthly_other_expenses: float = Form(default=0),
    savings: float = Form(default=0),
):
    templates = request.app.state.templates

    estimate_input = CostEstimateInput(
        house_id=house_id,
        purchase_price=purchase_price,
        down_payment_mode=down_payment_mode,
        down_payment_percent=down_payment_percent,
        down_payment_dollars=down_payment_dollars,
        interest_rate=interest_rate,
        loan_term_years=loan_term_years,
        annual_property_tax=annual_property_tax,
        annual_insurance=annual_insurance,
        monthly_pmi_override=monthly_pmi_override,
        monthly_hoa=monthly_hoa,
        monthly_heat=monthly_heat,
        monthly_water=monthly_water,
        monthly_electric=monthly_electric,
        monthly_internet=monthly_internet,
        annual_salary=annual_salary,
        monthly_take_home=monthly_take_home,
        monthly_loan_payments=monthly_loan_payments,
        monthly_other_expenses=monthly_other_expenses,
        savings=savings,
    )

    result = calculate_full_estimate(estimate_input)

    return templates.TemplateResponse(
        request,
        "partials/cost_result.html",
        {
            "result": result,
        },
    )
